#!/usr/bin/env python3
"""Build TCGA-BRCA longitudinal matching artifacts (Plan 02 / issue #355).

Open GDC cases/samples metadata only — no controlled files and no omic downloads.

* ``--discover`` pages every TCGA-BRCA case that has a YAML later sample type.
* Default (no flag) reads case IDs from the ``--smoke-dir`` manifest.
* ``--fixture`` is offline GDC-shaped JSON (no network).

Writes under ``--out-dir``:
  visit_sequences.json, match_pairs.json, summary.json (schema_version 1)

``summary.json`` includes ``cohort_scope`` (``discover``, ``smoke``, or ``fixture``).
Exit 0 when artifacts are written even if n_match_pairs == 0.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config.load_config import brca_gdc_keys, load_longitudinal_keys
from src.data.brca_longitudinal_matching import (
    match_pairs_document,
    process_cohort,
    summarize_cohort,
    visit_sequences_document,
)

GDC_CASES = "https://api.gdc.cancer.gov/cases"
USER_AGENT = "Bio-NAS-brca-longitudinal-matching/0.1 (+https://github.com/AdamCankaya/PhDNeural)"
DEFAULT_OUT = Path("data/tcga/BRCA/longitudinal_matching")
DEFAULT_SMOKE_DIR = Path("data/tcga/BRCA")
DEFAULT_KEYS = ROOT / "src" / "config" / "longitudinal_keys.yaml"
DEFAULT_FIXTURE = ROOT / "tests" / "fixtures" / "gdc_brca_samples_mini.json"
DISCOVER_PAGE_SIZE = 100
_FALLBACK_FIELDS = (
    "case_id,submitter_id,samples.sample_id,samples.submitter_id,"
    "samples.sample_type,samples.days_to_collection"
)


def _log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        sys.stdout.buffer.write((msg + "\n").encode(enc, errors="replace"))
        sys.stdout.flush()


def gdc_get(url: str, timeout: int = 120) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def load_case_ids_from_smoke(smoke_dir: Path) -> list[str]:
    manifest = smoke_dir / "manifest.json"
    if not manifest.is_file():
        raise FileNotFoundError(f"Missing smoke manifest: {manifest}")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    ids: list[str] = []
    for row in data.get("cases") or data.get("cohort") or []:
        if isinstance(row, dict) and row.get("case_id"):
            ids.append(str(row["case_id"]))
    if not ids:
        for row in data.get("files") or []:
            if isinstance(row, dict) and row.get("case_id"):
                ids.append(str(row["case_id"]))
    return sorted(set(ids))


def gdc_cases_fields(gdc_keys: dict[str, Any]) -> str:
    return str(gdc_keys.get("gdc_cases_api_fields") or _FALLBACK_FIELDS)


def resolve_cohort_scope(*, fixture: bool, discover: bool) -> str:
    """Label written to ``summary.json`` (schema_version stays 1)."""
    if fixture:
        return "fixture"
    if discover:
        return "discover"
    return "smoke"


def discover_case_filters(gdc_keys: dict[str, Any]) -> dict[str, Any]:
    """GDC ``/cases`` filter: TCGA-BRCA AND later sample types from YAML.

    Normal→Primary-only cases are outside this query. No omic file filters.
    """
    project_id = str(gdc_keys.get("project_id") or "TCGA-BRCA")
    later_types = list((gdc_keys.get("match_pair") or {}).get("later_sample_types") or [])
    if not later_types:
        raise ValueError("match_pair.later_sample_types is empty; cannot build discover filter")
    return {
        "op": "and",
        "content": [
            {
                "op": "=",
                "content": {"field": "project.project_id", "value": project_id},
            },
            {
                "op": "in",
                "content": {"field": "samples.sample_type", "value": later_types},
            },
        ],
    }


def fetch_gdc_cases(case_ids: list[str], gdc_keys: dict[str, Any]) -> list[dict[str, Any]]:
    if not case_ids:
        return []
    filters = {"op": "in", "content": {"field": "case_id", "value": case_ids}}
    params = urllib.parse.urlencode(
        {
            "filters": json.dumps(filters),
            "fields": gdc_cases_fields(gdc_keys),
            "size": str(len(case_ids)),
        }
    )
    payload = gdc_get(f"{GDC_CASES}?{params}")
    return list(payload.get("data", {}).get("hits") or [])


def fetch_discover_cases(
    gdc_keys: dict[str, Any],
    *,
    page_size: int = DISCOVER_PAGE_SIZE,
) -> tuple[list[dict[str, Any]], int]:
    """Page GDC ``/cases`` until ``pagination.total`` is consumed. Metadata only."""
    filters = discover_case_filters(gdc_keys)
    fields = gdc_cases_fields(gdc_keys)
    hits: list[dict[str, Any]] = []
    offset = 0
    total: int | None = None
    while total is None or offset < total:
        params = urllib.parse.urlencode(
            {
                "filters": json.dumps(filters, separators=(",", ":")),
                "fields": fields,
                "from": str(offset),
                "size": str(page_size),
                "sort": "case_id:asc",
            }
        )
        payload = gdc_get(f"{GDC_CASES}?{params}")
        data = payload.get("data") or {}
        page = list(data.get("hits") or [])
        pagination = data.get("pagination") or {}
        if total is None:
            total = int(pagination.get("total", len(page)))
        if not page:
            break
        hits.extend(page)
        next_offset = offset + len(page)
        if next_offset <= offset:
            break
        offset = next_offset
    return hits, int(total if total is not None else len(hits))


def load_fixture(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "cases" in data:
        return list(data["cases"])
    raise ValueError(f"Unexpected fixture shape: {path}")


def sample_types_observed_histogram(
    cases: Sequence[dict[str, Any]],
    gdc_keys: dict[str, Any],
) -> dict[str, int]:
    """Count raw GDC ``sample_type`` values before ranked-sample filtering."""
    sample_cfg = gdc_keys.get("sample") or {}
    st_field = sample_cfg.get("sample_type_field", "sample_type")
    counts: Counter[str] = Counter()
    for case in cases:
        for row in case.get("samples") or []:
            if not isinstance(row, dict):
                continue
            st = row.get(st_field)
            if st:
                counts[str(st)] += 1
    return dict(sorted(counts.items()))


def write_artifacts(out_dir: Path, results: list[Any], summary: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "visit_sequences.json").write_text(
        json.dumps(visit_sequences_document(results), indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "match_pairs.json").write_text(
        json.dumps(match_pairs_document(results), indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build BRCA longitudinal matching artifacts.")
    p.add_argument("--out-dir", type=Path, default=Path(os.environ.get("BRCA_MATCHING_OUT", DEFAULT_OUT)))
    p.add_argument("--smoke-dir", type=Path, default=Path(os.environ.get("TCGA_SAMPLE_OUT", DEFAULT_SMOKE_DIR)))
    source = p.add_mutually_exclusive_group()
    source.add_argument("--fixture", type=Path, help="Offline GDC-shaped JSON (no network).")
    source.add_argument(
        "--discover",
        action="store_true",
        help=(
            "Page open GDC /cases for TCGA-BRCA samples whose sample_type is a YAML "
            "later type (Recurrent Tumor, Metastatic). Does not read the smoke manifest "
            "and does not download omic files."
        ),
    )
    p.add_argument(
        "--keys-yaml",
        type=Path,
        default=Path(os.environ.get("MATCHING_KEYS_YAML", DEFAULT_KEYS)),
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    keys = load_longitudinal_keys(args.keys_yaml)
    gdc_keys = brca_gdc_keys(keys)
    project_id = str(gdc_keys.get("project_id", "TCGA-BRCA"))

    cohort_scope = resolve_cohort_scope(fixture=bool(args.fixture), discover=bool(args.discover))
    n_cases_queried: int
    if args.fixture:
        _log(f"Loading fixture cases from {args.fixture}")
        raw_cases = load_fixture(args.fixture)
        n_cases_queried = len(raw_cases)
    elif args.discover:
        _log(
            f"Discovering {project_id} cases with later sample types "
            f"{list((gdc_keys.get('match_pair') or {}).get('later_sample_types') or [])}..."
        )
        try:
            raw_cases, n_cases_queried = fetch_discover_cases(gdc_keys)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            _log(f"GDC error: {exc}")
            return 1
        _log(f"GDC discover returned {len(raw_cases)} case(s) (pagination.total={n_cases_queried}).")
        if len(raw_cases) != n_cases_queried:
            _log(
                f"WARNING: collected {len(raw_cases)} hit(s) but pagination.total={n_cases_queried}."
            )
    else:
        case_ids = load_case_ids_from_smoke(args.smoke_dir)
        n_cases_queried = len(case_ids)
        _log(f"Querying GDC for {n_cases_queried} smoke case(s)...")
        try:
            raw_cases = fetch_gdc_cases(case_ids, gdc_keys)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            _log(f"GDC error: {exc}")
            return 1
        if len(raw_cases) < n_cases_queried:
            _log(
                f"WARNING: GDC returned {len(raw_cases)} case(s) for {n_cases_queried} requested IDs."
            )

    results = process_cohort(raw_cases, gdc_keys)
    summary = summarize_cohort(
        results,
        n_cases_queried=n_cases_queried,
        project_id=project_id,
    )
    summary["cohort_scope"] = cohort_scope
    summary["sample_types_observed"] = sample_types_observed_histogram(raw_cases, gdc_keys)
    try:
        write_artifacts(args.out_dir, results, summary)
    except OSError as exc:
        _log(f"Failed to write artifacts: {exc}")
        return 1

    _log(
        f"Wrote matching artifacts to {args.out_dir} "
        f"(cohort_scope={summary['cohort_scope']}, "
        f"n_match_pairs={summary['n_match_pairs']}, "
        f"n_visit_sequences={summary['n_visit_sequences']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
