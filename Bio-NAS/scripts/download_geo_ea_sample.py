#!/usr/bin/env python3
"""Download a tiny open-access epigenetic aging cohort from GEO GSE87571 (series-matrix).

GSE87571 smoke (Plan-1 — locked parsing):
  - FTP matrix: .../GSE87571/GSE87571_series_matrix.txt.gz
  - Sample columns: ``!Sample_geo_accession`` (GSM IDs), stable sort for selection
  - Age from ``!Sample_characteristics_ch1`` lines matching ``age: <int>`` (case-insensitive)
  - Binary smoke label: age < 50 → 0 (younger), age >= 50 → 1 (older)
  - Beta table: rows under ``!series_matrix_table_begin``; probe IDs in ``ID_REF``;
    GSM columns hold numeric beta values in [0, 1].

Writes BRCA-shaped artifacts: ``manifest.json``, ``demographics.json``, ``files/*_methylation.tsv``,
``.ready``. Idempotent unless ``--force``. On schema change, delete ``.ready`` and ``files/``.

Usage:
  python scripts/download_geo_ea_sample.py
  python scripts/download_geo_ea_sample.py --out-dir /data/epigenetic_aging
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_ACCESSION = "GSE87571"
DEFAULT_OUT = Path("data/epigenetic_aging")
DEFAULT_N_SAMPLES = 8
DEFAULT_MAX_PROBES = 200
READY_MARKER = ".ready"
USER_AGENT = "Bio-NAS-geo-ea-sample/0.1 (+https://github.com/AdamCankaya/PhDNeural)"
_AGE_RE = re.compile(r"age:\s*(\d+)", re.IGNORECASE)


def _log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        sys.stdout.buffer.write((msg + "\n").encode(enc, errors="replace"))
        sys.stdout.flush()


def matrix_url(accession: str) -> str:
    prefix = accession[:-3] + "nnn"
    return (
        f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{accession}/matrix/"
        f"{accession}_series_matrix.txt.gz"
    )


def _strip_geo_field(raw: str) -> str:
    return raw.strip().strip('"').strip()


def parse_age_from_characteristic(value: str) -> int | None:
    """Parse integer years from a GEO characteristic line (e.g. ``age: 72``)."""
    if not value:
        return None
    match = _AGE_RE.search(value.strip())
    if not match:
        return None
    return int(match.group(1))


def age_to_label(age: int) -> int:
    """Map chronological age to binary smoke label (0=younger, 1=older)."""
    return 0 if age < 50 else 1


def _phenotype_for_label(label: int) -> str:
    return "younger" if label == 0 else "older"


def parse_series_matrix_metadata(
    lines: list[str],
) -> tuple[list[str], list[str], list[int | None], list[dict[str, str]]]:
    """Return (gsm_ids, titles, ages, extra_chars) aligned per sample."""
    gsm_ids: list[str] = []
    titles: list[str] = []
    ages: list[int | None] = []
    extras: list[dict[str, str]] = []

    for line in lines:
        if not line.startswith("!Sample_"):
            continue
        key, *rest = line.split("\t")
        values = [_strip_geo_field(x) for x in rest]
        if key == "!Sample_geo_accession":
            gsm_ids = values
        elif key == "!Sample_title":
            titles = values
        elif key == "!Sample_characteristics_ch1" and values:
            if not gsm_ids:
                continue
            if not ages:
                ages = [None] * len(gsm_ids)
            if not extras:
                extras = [{} for _ in gsm_ids]
            for i, raw in enumerate(values):
                if i >= len(gsm_ids) or not raw:
                    continue
                parsed_age = parse_age_from_characteristic(raw)
                if parsed_age is not None:
                    ages[i] = parsed_age
                    continue
                low = raw.lower()
                if ":" in raw:
                    field, val = raw.split(":", 1)
                    field = field.strip().lower()
                    val = val.strip()
                    if field in ("gender", "sex"):
                        extras[i]["gender"] = val
                    elif field in ("tissue", "tissue type"):
                        extras[i]["tissue"] = val
                    elif field == "disease state":
                        extras[i]["disease_state"] = val

    if not gsm_ids:
        raise RuntimeError("GEO matrix missing !Sample_geo_accession")
    if not ages or all(a is None for a in ages):
        raise RuntimeError(
            "GEO matrix missing age characteristics (expected lines like 'age: 72')"
        )
    if not titles:
        titles = [""] * len(gsm_ids)
    if len(titles) != len(gsm_ids):
        raise RuntimeError("GSM count mismatch vs title metadata")
    if len(ages) != len(gsm_ids):
        raise RuntimeError("GSM count mismatch vs age metadata")
    return gsm_ids, titles, ages, extras


def select_stratified_gsms(
    gsm_ids: list[str],
    ages: list[int | None],
    n_samples: int,
) -> list[str]:
    """Pick ``n_samples`` GSMs with both age-bin classes when possible."""
    n_samples = max(5, min(10, n_samples))
    labeled: list[tuple[str, int]] = []
    for gsm, age in zip(gsm_ids, ages):
        if age is None:
            continue
        labeled.append((gsm, age_to_label(age)))
    if len(labeled) < 5:
        raise RuntimeError(f"Need >=5 samples with parseable age, found {len(labeled)}")

    by_class: dict[int, list[str]] = {0: [], 1: []}
    for gsm, lab in labeled:
        by_class[lab].append(gsm)
    for lab in by_class:
        by_class[lab].sort()

    if not by_class[0] or not by_class[1]:
        raise RuntimeError(
            "Stratified selection impossible: need both age bins (<50 and >=50)"
        )
    min_per_class = 2
    if n_samples < min_per_class * 2:
        raise RuntimeError(
            f"n_samples={n_samples} too small for stratified smoke (need >= {min_per_class * 2})"
        )
    if len(by_class[0]) < min_per_class or len(by_class[1]) < min_per_class:
        raise RuntimeError(
            f"Need >={min_per_class} samples per age bin; found "
            f"younger={len(by_class[0])}, older={len(by_class[1])}"
        )

    chosen: list[str] = []
    for cls in (0, 1):
        for _ in range(min_per_class):
            if by_class[cls]:
                chosen.append(by_class[cls].pop(0))

    while len(chosen) < n_samples:
        progressed = False
        for cls in (0, 1):
            if by_class[cls] and len(chosen) < n_samples:
                chosen.append(by_class[cls].pop(0))
                progressed = True
        if not progressed:
            break

    if len(chosen) < n_samples:
        remaining = sorted(g for g, _ in labeled if g not in chosen)
        for gsm in remaining:
            if len(chosen) >= n_samples:
                break
            chosen.append(gsm)

    age_by_gsm = dict(zip(gsm_ids, ages, strict=False))
    labels_chosen = {age_to_label(int(age_by_gsm[gsm])) for gsm in chosen if age_by_gsm.get(gsm) is not None}
    if labels_chosen != {0, 1}:
        raise RuntimeError(
            f"Stratified selection produced single-class labels: {sorted(labels_chosen)}"
        )
    return sorted(chosen)


def fetch_and_materialize(
    accession: str,
    out_dir: Path,
    *,
    n_samples: int,
    max_probes: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    url = matrix_url(accession)
    _log(f"Fetching {url}")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    meta_lines: list[str] = []
    table_header: list[str] = []
    selected_gsms: list[str] = []
    col_indices: list[int] = []
    probes: list[str] = []
    betas_by_gsm: dict[str, list[tuple[str, float]]] = {}

    with urllib.request.urlopen(req, timeout=180) as resp:
        with gzip.GzipFile(fileobj=resp) as archive:
            in_table = False
            for raw in archive:
                line = raw.decode("utf-8", errors="replace").rstrip("\n\r")
                if not in_table:
                    if line == "!series_matrix_table_begin":
                        gsm_ids, titles, ages, _extras = parse_series_matrix_metadata(
                            meta_lines
                        )
                        selected_gsms = select_stratified_gsms(gsm_ids, ages, n_samples)
                        _log(
                            f"Selected {len(selected_gsms)} sample(s): "
                            f"{', '.join(selected_gsms)}"
                        )
                        betas_by_gsm = {g: [] for g in selected_gsms}
                        in_table = True
                        continue
                    meta_lines.append(line)
                    continue

                if line == "!series_matrix_table_end":
                    break
                fields = line.split("\t")
                if not table_header:
                    table_header = [_strip_geo_field(f) for f in fields]
                    gsm_to_idx = {name: i for i, name in enumerate(table_header)}
                    col_indices = []
                    for gsm in selected_gsms:
                        if gsm not in gsm_to_idx:
                            raise RuntimeError(f"GSM {gsm} missing from matrix header")
                        col_indices.append(gsm_to_idx[gsm])
                    continue

                if len(fields) <= max(col_indices, default=[0]):
                    continue
                probe = _strip_geo_field(fields[0])
                if not probe or probe.upper() == "ID_REF":
                    continue
                try:
                    row_vals = [float(_strip_geo_field(fields[i])) for i in col_indices]
                except ValueError:
                    continue
                probes.append(probe)
                for gsm, beta in zip(selected_gsms, row_vals):
                    betas_by_gsm[gsm].append((probe, beta))
                if len(probes) >= max_probes:
                    break

    if len(probes) < 10:
        raise RuntimeError("Too few numeric probe rows parsed from GEO matrix")

    files_dir = out_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)
    cohort: list[dict[str, str]] = []
    demographics: list[dict[str, Any]] = []
    gsm_ids, titles, ages, extras = parse_series_matrix_metadata(meta_lines)
    meta_by_gsm = {
        g: (ages[i], titles[i] if i < len(titles) else "", extras[i] if i < len(extras) else {})
        for i, g in enumerate(gsm_ids)
    }

    for gsm in selected_gsms:
        fname = f"{gsm}_methylation.tsv"
        dest = files_dir / fname
        with dest.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write("probe\tbeta_value\n")
            for probe, beta in betas_by_gsm[gsm]:
                fh.write(f"{probe}\t{beta}\n")
        age, title, extra = meta_by_gsm.get(gsm, (None, "", {}))
        if age is None:
            raise RuntimeError(f"Missing age for selected GSM {gsm}")
        lab = age_to_label(age)
        phenotype = _phenotype_for_label(lab)
        cohort.append(
            {
                "case_id": gsm,
                "geo_accession": gsm,
                "methylation_file_name": fname,
                "sample_title": title,
            }
        )
        demo_row: dict[str, Any] = {
            "case_id": gsm,
            "geo_accession": gsm,
            "age": age,
            "phenotype": phenotype,
            "label": lab,
        }
        if extra.get("gender"):
            demo_row["gender"] = extra["gender"]
        if extra.get("tissue"):
            demo_row["tissue"] = extra["tissue"]
        if extra.get("disease_state"):
            demo_row["disease_state"] = extra["disease_state"]
        demographics.append(demo_row)
    return cohort, demographics


def write_manifest(
    out_dir: Path,
    accession: str,
    cohort: list[dict[str, str]],
    demographics: list[dict[str, Any]],
    url: str,
) -> None:
    manifest = {
        "project": accession,
        "accession": accession,
        "source": url,
        "access": "open",
        "schema_version": 2,
        "n_cases": len(cohort),
        "poc_modalities": ["methylation_beta", "clinical_labels"],
        "note": (
            "Tiny open GEO GSE87571 cohort for Docker smoke / NAS demo. "
            "Binary labels from chronological age bins (<50 vs >=50) for pipeline "
            "validation only — not epigenetic age acceleration or disease status. "
            "Multi-GEO harmonization (GSE40279, GSE280465) deferred (Plan 07)."
        ),
        "cohort": cohort,
        "demographics": demographics,
        "files": [
            {
                "file_name": entry["methylation_file_name"],
                "label": "methylation",
                "case_id": entry["case_id"],
                "geo_accession": entry["case_id"],
                "local_path": str(out_dir / "files" / entry["methylation_file_name"]),
            }
            for entry in cohort
        ],
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "demographics.json").write_text(
        json.dumps(demographics, indent=2) + "\n", encoding="utf-8"
    )
    _log(f"Wrote {out_dir / 'manifest.json'} and demographics.json")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path(os.environ.get("EPIGENETIC_AGING_SAMPLE_OUT", str(DEFAULT_OUT))),
    )
    p.add_argument(
        "--n-samples",
        type=int,
        default=int(os.environ.get("EA_SAMPLE_N", DEFAULT_N_SAMPLES)),
    )
    p.add_argument("--max-probes", type=int, default=DEFAULT_MAX_PROBES)
    p.add_argument("--accession", default=DEFAULT_ACCESSION)
    p.add_argument("--force", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    out_dir = args.out_dir.resolve()
    n_samples = max(5, min(10, int(args.n_samples)))
    accession = args.accession
    marker = out_dir / READY_MARKER

    _log(f"Output directory: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    if marker.exists() and not args.force:
        _log(
            f"Data already present ({marker}); skipping download. "
            "Delete .ready (and files/) to refresh."
        )
        return 0

    cohort, demographics = fetch_and_materialize(
        accession,
        out_dir,
        n_samples=n_samples,
        max_probes=args.max_probes,
    )
    url = matrix_url(accession)
    write_manifest(out_dir, accession, cohort, demographics, url)
    marker.write_text(
        json.dumps(
            {
                "accession": accession,
                "schema_version": 2,
                "n_cases": len(cohort),
                "poc_modalities": ["methylation_beta", "clinical_labels"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _log(f"Wrote ready marker: {marker}")
    _log(f"Done -> {out_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 — top-level CLI
        _log(f"ERROR: {exc}")
        raise SystemExit(1) from exc
