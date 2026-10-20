#!/usr/bin/env python3
"""Download a tiny open-access RA cohort from GEO GSE71841 (series-matrix).

GSE71841 spike (M1 — locked parsing):
  - FTP matrix: .../GSE71841/GSE71841_series_matrix.txt.gz
  - Sample columns: ``!Sample_geo_accession`` (GSM IDs), stable sort for selection
  - Healthy vs RA: ``!Sample_characteristics_ch1`` line ``sample type: Control`` (0)
    vs ``sample type: Case`` (1). Title lines mention "Rheumatoid Arthritis" for cases.
  - Beta table: rows under ``!series_matrix_table_begin``; probe IDs in ``ID_REF``;
    GSM columns hold numeric beta values in [0, 1].

Writes BRCA-shaped artifacts: ``manifest.json``, ``demographics.json``, ``files/*_methylation.tsv``,
``.ready``. Idempotent unless ``--force``. On schema change, delete ``.ready`` and ``files/``.

Usage:
  python scripts/download_geo_ra_sample.py
  python scripts/download_geo_ra_sample.py --out-dir /data/ra
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_ACCESSION = "GSE71841"
DEFAULT_OUT = Path("data/ra")
DEFAULT_N_SAMPLES = 8
DEFAULT_MAX_PROBES = 200
READY_MARKER = ".ready"
USER_AGENT = "Bio-NAS-geo-ra-sample/0.1 (+https://github.com/AdamCankaya/PhDNeural)"


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


def sample_type_to_label(sample_type: str) -> int:
    """Map GSE71841 ``sample type: *`` characteristic to binary label."""
    st = sample_type.lower()
    if "control" in st:
        return 0
    if "case" in st:
        return 1
    return -1


def parse_series_matrix_metadata(
    lines: list[str],
) -> tuple[list[str], list[str], list[str]]:
    """Return (gsm_ids, sample_types, titles) aligned per sample."""
    gsm_ids: list[str] = []
    sample_types: list[str] = []
    titles: list[str] = []
    for line in lines:
        if not line.startswith("!Sample_"):
            continue
        key, *rest = line.split("\t")
        values = [_strip_geo_field(x) for x in rest]
        if key == "!Sample_geo_accession":
            gsm_ids = values
        elif key == "!Sample_title":
            titles = values
        elif key == "!Sample_characteristics_ch1" and rest:
            joined = _strip_geo_field(rest[0]) if len(rest) == 1 else ""
            # Multiple characteristics lines share the same key; pick sample type row.
            if any(values) and all("sample type:" in v.lower() for v in values if v):
                sample_types = values
    if not gsm_ids:
        raise RuntimeError("GEO matrix missing !Sample_geo_accession")
    if not sample_types:
        raise RuntimeError(
            "GEO matrix missing sample type characteristics "
            "(expected 'sample type: Case' / 'sample type: Control')"
        )
    if len(sample_types) != len(gsm_ids):
        raise RuntimeError("GSM count mismatch vs sample type metadata")
    if not titles:
        titles = [""] * len(gsm_ids)
    return gsm_ids, sample_types, titles


def select_gsm_ids(
    gsm_ids: list[str],
    sample_types: list[str],
    n_samples: int,
) -> list[str]:
    """Pick ``n_samples`` GSMs with both classes when possible; sort for stability."""
    n_samples = max(5, min(10, n_samples))
    labeled: list[tuple[str, int]] = []
    for gsm, st in zip(gsm_ids, sample_types):
        lab = sample_type_to_label(st)
        if lab < 0:
            continue
        labeled.append((gsm, lab))
    if len(labeled) < 5:
        raise RuntimeError(f"Need >=5 labeled samples, found {len(labeled)}")

    by_class: dict[int, list[str]] = {0: [], 1: []}
    for gsm, lab in labeled:
        by_class[lab].append(gsm)
    for lab in by_class:
        by_class[lab].sort()

    chosen: list[str] = []
    while len(chosen) < n_samples:
        progressed = False
        for cls in (0, 1):
            if by_class[cls] and len(chosen) < n_samples:
                chosen.append(by_class[cls].pop(0))
                progressed = True
        if not progressed:
            break
    # Fill remainder from any class (sorted) if budget not met
    if len(chosen) < n_samples:
        remaining = sorted(
            g for g, _ in labeled if g not in chosen
        )
        for gsm in remaining:
            if len(chosen) >= n_samples:
                break
            chosen.append(gsm)
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
                        gsm_ids, sample_types, titles = parse_series_matrix_metadata(
                            meta_lines
                        )
                        selected_gsms = select_gsm_ids(
                            gsm_ids, sample_types, n_samples
                        )
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
                    gsm_to_idx = {
                        name: i for i, name in enumerate(table_header)
                    }
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
    gsm_ids, sample_types, titles = parse_series_matrix_metadata(meta_lines)
    meta_by_gsm = {g: (st, t) for g, st, t in zip(gsm_ids, sample_types, titles)}

    for gsm in selected_gsms:
        fname = f"{gsm}_methylation.tsv"
        dest = files_dir / fname
        with dest.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write("probe\tbeta_value\n")
            for probe, beta in betas_by_gsm[gsm]:
                fh.write(f"{probe}\t{beta}\n")
        st, title = meta_by_gsm.get(gsm, ("", ""))
        lab = sample_type_to_label(st)
        phenotype = "Healthy" if lab == 0 else "RA"
        cohort.append(
            {
                "case_id": gsm,
                "geo_accession": gsm,
                "methylation_file_name": fname,
                "sample_title": title,
            }
        )
        demographics.append(
            {
                "case_id": gsm,
                "geo_accession": gsm,
                "sample_type": st.split(":", 1)[-1].strip() if ":" in st else st,
                "phenotype": phenotype,
                "disease_status": phenotype,
                "label": lab,
            }
        )
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
            "Tiny open GEO GSE71841 cohort for Docker smoke / NAS demo. "
            "Labels from sample type (Control=Healthy, Case=RA). "
            "DAS28 severity and multi-study harmonization deferred (Plan 07)."
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
        default=Path(os.environ.get("RA_SAMPLE_OUT", str(DEFAULT_OUT))),
    )
    p.add_argument(
        "--n-samples",
        type=int,
        default=int(os.environ.get("RA_SAMPLE_N", DEFAULT_N_SAMPLES)),
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
