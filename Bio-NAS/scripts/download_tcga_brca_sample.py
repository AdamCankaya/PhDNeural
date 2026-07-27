#!/usr/bin/env python3
"""Download a tiny open-access TCGA-BRCA cohort from the GDC API.

Selects ~5–10 cases that have **both** open methylation beta values and
RNA-seq (STAR counts), plus clinical/labels (biotab + cases API demographics).
PoC-minimum open Level-3 modalities only — no controlled/dbGaP files, no token.

Idempotent: skips work when ``.ready`` marker exists (or files match catalog).
If selection schema changes (e.g. meth required), delete ``.ready`` (and
optionally ``files/``) for a fresh pull.

Usage:
  python scripts/download_tcga_brca_sample.py
  python scripts/download_tcga_brca_sample.py --out-dir /data/tcga/BRCA
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

GDC_FILES = "https://api.gdc.cancer.gov/files"
GDC_DATA = "https://api.gdc.cancer.gov/data"
GDC_CASES = "https://api.gdc.cancer.gov/cases"
PROJECT = "TCGA-BRCA"
DEFAULT_OUT = Path("data/tcga/BRCA")
DEFAULT_N_CASES = 8
# Sample-scale budget: ~N Illumina 450K SeSAMe meth betas (~12–14 MB each) + STAR RNA + clinical.
# Not the full ~1098-case cohort (that is Plan 07). Soft cap leaves headroom if file sizes grow.
DEFAULT_MAX_BYTES = 1500 * 1024 * 1024
READY_MARKER = ".ready"
USER_AGENT = "Bio-NAS-tcga-brca-sample/0.3 (+https://github.com/AdamCankaya/PhDNeural)"
# Prefer Illumina 450K SeSAMe betas (~12–14 MB); HM27 is a last-resort fallback.
METH_PLATFORM_450 = "Illumina Human Methylation 450"
METH_PLATFORM_27 = "Illumina Human Methylation 27"


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


def gdc_query(
    endpoint: str,
    filters: dict[str, Any],
    *,
    fields: str,
    size: int = 10,
    sort: str = "file_size:asc",
) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {
            "filters": json.dumps(filters),
            "fields": fields,
            "size": str(size),
            "sort": sort,
        }
    )
    return gdc_get(f"{endpoint}?{params}")["data"]["hits"]


def and_filters(*parts: dict[str, Any]) -> dict[str, Any]:
    return {"op": "and", "content": list(parts)}


def project_open() -> list[dict[str, Any]]:
    return [
        {
            "op": "in",
            "content": {"field": "cases.project.project_id", "value": [PROJECT]},
        },
        {"op": "in", "content": {"field": "access", "value": ["open"]}},
    ]


def _case_ids_from_hit(hit: dict[str, Any]) -> tuple[str | None, str | None]:
    cases = hit.get("cases") or []
    if not cases:
        return None, None
    case = cases[0]
    return case.get("case_id"), case.get("submitter_id")


def _annotate(hit: dict[str, Any], label: str) -> dict[str, Any]:
    case_id, submitter_id = _case_ids_from_hit(hit)
    hit["_label"] = label
    hit["_case_id"] = case_id
    hit["_submitter_id"] = submitter_id or case_id
    return hit


def select_clinical(*, budget: int) -> tuple[list[dict[str, Any]], int]:
    fields = "file_id,file_name,file_size,data_type,data_format,data_category"
    clinical = gdc_query(
        GDC_FILES,
        and_filters(
            *project_open(),
            {"op": "in", "content": {"field": "data_category", "value": ["Clinical"]}},
            {"op": "in", "content": {"field": "data_format", "value": ["BCR Biotab"]}},
            {
                "op": "in",
                "content": {
                    "field": "file_name",
                    "value": ["nationwidechildrens.org_clinical_patient_brca.txt"],
                },
            },
        ),
        fields=fields,
        size=1,
    )
    if not clinical:
        clinical = gdc_query(
            GDC_FILES,
            and_filters(
                *project_open(),
                {
                    "op": "in",
                    "content": {"field": "data_category", "value": ["Clinical"]},
                },
                {
                    "op": "in",
                    "content": {"field": "data_format", "value": ["BCR Biotab"]},
                },
            ),
            fields=fields,
            size=3,
            sort="file_size:asc",
        )
    selected: list[dict[str, Any]] = []
    remaining = budget
    for hit in clinical[:1]:
        size = int(hit["file_size"])
        if size > remaining:
            _log(f"  skip clinical (budget): {hit['file_name']}")
            break
        hit["_label"] = "clinical"
        selected.append(hit)
        remaining -= size
        _log(
            f"  select [clinical] {hit['file_name']} "
            f"({size / 1e6:.2f} MB) id={hit['file_id']}"
        )
    return selected, remaining


def _index_expression_by_case() -> dict[str, dict[str, Any]]:
    """Map case_id -> smallest open STAR Counts expression file."""
    fields = (
        "file_id,file_name,file_size,data_type,data_format,data_category,"
        "cases.case_id,cases.submitter_id"
    )
    hits = gdc_query(
        GDC_FILES,
        and_filters(
            *project_open(),
            {
                "op": "in",
                "content": {
                    "field": "data_type",
                    "value": ["Gene Expression Quantification"],
                },
            },
            {
                "op": "in",
                "content": {
                    "field": "analysis.workflow_type",
                    "value": ["STAR - Counts"],
                },
            },
        ),
        fields=fields,
        size=200,
        sort="file_size:asc",
    )
    if not hits:
        hits = gdc_query(
            GDC_FILES,
            and_filters(
                *project_open(),
                {
                    "op": "in",
                    "content": {
                        "field": "data_type",
                        "value": ["Gene Expression Quantification"],
                    },
                },
            ),
            fields=fields,
            size=200,
            sort="file_size:asc",
        )

    by_case: dict[str, dict[str, Any]] = {}
    for hit in hits:
        case_id, submitter_id = _case_ids_from_hit(hit)
        if not case_id:
            continue
        size = int(hit["file_size"])
        prev = by_case.get(case_id)
        if prev is None or size < int(prev["file_size"]):
            by_case[case_id] = _annotate(hit, "gene_expression")
            by_case[case_id]["_submitter_id"] = submitter_id or case_id
    return by_case


def _meth_rank(hit: dict[str, Any]) -> tuple[int, int]:
    """Lower is better: prefer 450K, then HM27, then other; then smaller files."""
    platform = hit.get("platform") or ""
    if platform == METH_PLATFORM_450:
        pref = 0
    elif platform == METH_PLATFORM_27:
        pref = 1
    else:
        pref = 2
    return pref, int(hit["file_size"])


def _index_methylation_by_case() -> dict[str, dict[str, Any]]:
    """Map case_id -> preferred open Methylation Beta Value file (450K first)."""
    fields = (
        "file_id,file_name,file_size,data_type,data_format,data_category,"
        "platform,cases.case_id,cases.submitter_id"
    )

    def _ingest(hits: list[dict[str, Any]], by_case: dict[str, dict[str, Any]]) -> None:
        for hit in hits:
            case_id, submitter_id = _case_ids_from_hit(hit)
            if not case_id:
                continue
            annotated = _annotate(hit, "methylation")
            annotated["_submitter_id"] = submitter_id or case_id
            prev = by_case.get(case_id)
            if prev is None or _meth_rank(annotated) < _meth_rank(prev):
                by_case[case_id] = annotated

    by_case: dict[str, dict[str, Any]] = {}
    # Query 450K explicitly — sorting all meth by size:asc only returns tiny HM27.
    hits_450 = gdc_query(
        GDC_FILES,
        and_filters(
            *project_open(),
            {
                "op": "in",
                "content": {
                    "field": "data_type",
                    "value": ["Methylation Beta Value"],
                },
            },
            {
                "op": "in",
                "content": {"field": "platform", "value": [METH_PLATFORM_450]},
            },
        ),
        fields=fields,
        size=400,
        sort="cases.submitter_id:asc",
    )
    _ingest(hits_450, by_case)

    if len(by_case) < 20:
        hits_any = gdc_query(
            GDC_FILES,
            and_filters(
                *project_open(),
                {
                    "op": "in",
                    "content": {
                        "field": "data_type",
                        "value": ["Methylation Beta Value"],
                    },
                },
            ),
            fields=fields,
            size=400,
            sort="file_size:desc",
        )
        _ingest(hits_any, by_case)

    return by_case


def select_joint_meth_rna_cases(
    *,
    n_cases: int,
    budget: int,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], int]:
    """Pick cases with both open meth betas and STAR RNA; pin via submitter_id sort."""
    _log("Indexing open STAR expression and Methylation Beta Value files...")
    expr_by_case = _index_expression_by_case()
    meth_by_case = _index_methylation_by_case()
    joint = sorted(
        set(expr_by_case) & set(meth_by_case),
        key=lambda cid: (
            str(expr_by_case[cid].get("_submitter_id") or cid),
            cid,
        ),
    )
    _log(
        f"  joint open meth+RNA cases available in query window: {len(joint)} "
        f"(expr={len(expr_by_case)}, meth={len(meth_by_case)})"
    )

    selected: list[dict[str, Any]] = []
    cohort: list[dict[str, str]] = []
    remaining = budget

    for case_id in joint:
        meth = meth_by_case[case_id]
        expr = expr_by_case[case_id]
        pair_size = int(meth["file_size"]) + int(expr["file_size"])
        if pair_size > remaining:
            _log(
                f"  skip case (budget): "
                f"{meth.get('_submitter_id') or case_id} "
                f"(meth+RNA {pair_size / 1e6:.1f} MB > remaining "
                f"{remaining / 1e6:.1f} MB)"
            )
            continue

        selected.append(meth)
        selected.append(expr)
        remaining -= pair_size
        submitter = str(meth.get("_submitter_id") or expr.get("_submitter_id") or case_id)
        cohort.append(
            {
                "case_id": case_id,
                "submitter_id": submitter,
                "methylation_file_id": meth["file_id"],
                "methylation_file_name": meth["file_name"],
                "expression_file_id": expr["file_id"],
                "expression_file_name": expr["file_name"],
            }
        )
        _log(
            f"  select [meth+rna] case={submitter} "
            f"meth={meth['file_name']} ({int(meth['file_size']) / 1e6:.2f} MB) "
            f"rna={expr['file_name']} ({int(expr['file_size']) / 1e6:.2f} MB)"
        )
        if len(cohort) >= n_cases:
            break

    if len(cohort) < 5:
        raise RuntimeError(
            f"Could only select {len(cohort)} BRCA cases with open meth+RNA; "
            "need at least 5. Raise TCGA_SAMPLE_MAX_BYTES or check GDC API."
        )
    return selected, cohort, remaining


def fetch_case_demographics(case_ids: list[str]) -> list[dict[str, Any]]:
    """Pull open demographic fields from the GDC cases endpoint."""
    fields = (
        "case_id,submitter_id,demographic.gender,demographic.race,"
        "demographic.ethnicity,demographic.year_of_birth,"
        "diagnoses.age_at_diagnosis,diagnoses.ajcc_pathologic_stage,"
        "diagnoses.primary_diagnosis,project.project_id"
    )
    hits = gdc_query(
        GDC_CASES,
        and_filters(
            {
                "op": "in",
                "content": {"field": "project.project_id", "value": [PROJECT]},
            },
            {"op": "in", "content": {"field": "case_id", "value": case_ids}},
        ),
        fields=fields,
        size=len(case_ids),
        sort="submitter_id:asc",
    )
    rows: list[dict[str, Any]] = []
    for hit in hits:
        demo = hit.get("demographic") or {}
        diagnoses = hit.get("diagnoses") or []
        dx = diagnoses[0] if diagnoses else {}
        rows.append(
            {
                "case_id": hit.get("case_id"),
                "submitter_id": hit.get("submitter_id"),
                "gender": demo.get("gender"),
                "race": demo.get("race"),
                "ethnicity": demo.get("ethnicity"),
                "year_of_birth": demo.get("year_of_birth"),
                "age_at_diagnosis": dx.get("age_at_diagnosis"),
                "ajcc_pathologic_stage": dx.get("ajcc_pathologic_stage"),
                "primary_diagnosis": dx.get("primary_diagnosis"),
            }
        )
    return rows


def download_file(file_id: str, dest: Path, expected_size: int) -> str:
    """Download one GDC file. Returns 'skipped' | 'downloaded'."""
    if dest.exists() and expected_size and dest.stat().st_size == expected_size:
        return "skipped"
    if dest.exists() and dest.stat().st_size > 0:
        _log(
            f"  re-download (size mismatch: local={dest.stat().st_size}, "
            f"expected={expected_size}): {dest.name}"
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    url = f"{GDC_DATA}/{file_id}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=600) as resp, tmp.open("wb") as out:
            total = 0
            while True:
                chunk = resp.read(1024 * 256)
                if not chunk:
                    break
                out.write(chunk)
                total += len(chunk)
                if total and total % (2 * 1024 * 1024) < 256 * 1024:
                    _log(f"    ... {dest.name}: {total / 1e6:.1f} MB")
        tmp.replace(dest)
    except urllib.error.HTTPError as exc:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise RuntimeError(
            f"HTTP {exc.code} downloading {file_id}: {exc.reason}"
        ) from exc
    except Exception:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
        raise

    actual = dest.stat().st_size
    if expected_size and actual != expected_size:
        _log(
            f"  warning: size {actual} != catalog {expected_size} for {dest.name}"
        )
    return "downloaded"


def write_manifest(
    out_dir: Path,
    files: list[dict[str, Any]],
    cohort: list[dict[str, str]],
    demographics: list[dict[str, Any]],
) -> None:
    manifest = {
        "project": PROJECT,
        "source": "https://api.gdc.cancer.gov",
        "access": "open",
        "schema_version": 2,
        "n_cases": len(cohort),
        "poc_modalities": [
            "methylation_beta",
            "rna_star_counts",
            "clinical_labels",
        ],
        "note": (
            "Tiny open-access BRCA cohort for Docker smoke / NAS demo "
            "(PoC-minimum: meth + RNA + clinical). Controlled/dbGaP deferred. "
            "Not the full TCGA-BRCA cohort (Plan 07). Selection prefers cases "
            "with both meth and RNA; ordered by submitter_id for stability. "
            "Toy NAS uses methylation features only."
        ),
        "cohort": cohort,
        "demographics": demographics,
        "files": [
            {
                "file_id": f["file_id"],
                "file_name": f["file_name"],
                "file_size": f["file_size"],
                "data_type": f.get("data_type"),
                "data_format": f.get("data_format"),
                "data_category": f.get("data_category"),
                "platform": f.get("platform"),
                "label": f.get("_label"),
                "case_id": f.get("_case_id"),
                "submitter_id": f.get("_submitter_id"),
                "local_path": str(out_dir / "files" / f["file_name"]),
            }
            for f in files
        ],
    }
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    _log(f"Wrote {path}")

    demo_path = out_dir / "demographics.json"
    demo_path.write_text(
        json.dumps(demographics, indent=2) + "\n", encoding="utf-8"
    )
    _log(f"Wrote {demo_path}")


def select_sample_files(
    *,
    n_cases: int,
    max_bytes: int,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    _log(
        f"Querying GDC for open {PROJECT} cohort "
        f"(~{n_cases} cases with meth+RNA+clinical, "
        f"budget <= {max_bytes / 1e6:.1f} MB)..."
    )
    selected: list[dict[str, Any]] = []
    clinical, budget = select_clinical(budget=max_bytes)
    selected.extend(clinical)

    joint, cohort, _budget = select_joint_meth_rna_cases(
        n_cases=n_cases, budget=budget
    )
    selected.extend(joint)

    if not selected:
        raise RuntimeError("GDC returned no selectable open TCGA-BRCA files.")
    return selected, cohort


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path(os.environ.get("TCGA_SAMPLE_OUT", str(DEFAULT_OUT))),
        help=f"Output directory (default: {DEFAULT_OUT} or $TCGA_SAMPLE_OUT)",
    )
    p.add_argument(
        "--n-cases",
        type=int,
        default=int(os.environ.get("TCGA_SAMPLE_N_CASES", DEFAULT_N_CASES)),
        help=f"Target number of patients (default: {DEFAULT_N_CASES})",
    )
    p.add_argument(
        "--max-bytes",
        type=int,
        default=int(os.environ.get("TCGA_SAMPLE_MAX_BYTES", DEFAULT_MAX_BYTES)),
        help=f"Approximate download budget in bytes (default: {DEFAULT_MAX_BYTES})",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if .ready marker exists",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    out_dir = args.out_dir.resolve()
    n_cases = max(5, min(10, int(args.n_cases)))
    max_bytes = args.max_bytes
    marker = out_dir / READY_MARKER

    _log(f"Output directory: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    files_dir = out_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    if marker.exists() and not args.force:
        _log(
            f"Data already present ({marker}); skipping download. "
            "If you need the meth+RNA schema (v2), delete .ready "
            "(and optionally files/) then re-run."
        )
        return 0

    files, cohort = select_sample_files(n_cases=n_cases, max_bytes=max_bytes)
    total_catalog = sum(int(f["file_size"]) for f in files)
    _log(
        f"Selected {len(files)} file(s) for {len(cohort)} case(s), "
        f"catalog total ~{total_catalog / 1e6:.2f} MB"
    )

    case_ids = [c["case_id"] for c in cohort]
    _log(f"Fetching demographics for {len(case_ids)} case(s)...")
    demographics = fetch_case_demographics(case_ids)

    downloaded = skipped = 0
    for hit in files:
        dest = files_dir / hit["file_name"]
        _log(f"Fetching {hit['file_name']} ...")
        status = download_file(hit["file_id"], dest, int(hit["file_size"]))
        if status == "skipped":
            skipped += 1
            _log(f"  skip (already present): {dest}")
        else:
            downloaded += 1
            _log(f"  saved: {dest} ({dest.stat().st_size / 1e6:.2f} MB)")

    write_manifest(out_dir, files, cohort, demographics)
    marker.write_text(
        json.dumps(
            {
                "project": PROJECT,
                "schema_version": 2,
                "n_cases": len(cohort),
                "n_files": len(files),
                "catalog_bytes": total_catalog,
                "poc_modalities": [
                    "methylation_beta",
                    "rna_star_counts",
                    "clinical_labels",
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _log(f"Wrote ready marker: {marker}")
    _log(
        f"Done. downloaded={downloaded}, skipped={skipped}, "
        f"catalog_total~{total_catalog / 1e6:.2f} MB -> {out_dir}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 — top-level CLI
        _log(f"ERROR: {exc}")
        raise SystemExit(1) from exc
