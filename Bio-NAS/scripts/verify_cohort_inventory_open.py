#!/usr/bin/env python3
"""Verify open cohort-inventory rows via public APIs (Plan 01 / issue #354).

Queries the GDC public API for TCGA-BRCA project + Level-3 PoC modality
counts (methylation betas, STAR RNA, clinical). Optionally checks a local
smoke ``manifest.json`` against pinned expectations.

Writes machine-readable artifacts under
``$INVENTORY_VERIFY_OUT`` (default ``/data/tcga/inventory_verification/``).

No GDC token / dbGaP. Controlled cohorts are skipped (documented only).

Usage:
  python scripts/verify_cohort_inventory_open.py
  python scripts/verify_cohort_inventory_open.py --dry-run
  python scripts/verify_cohort_inventory_open.py --out-dir data/tcga/inventory_verification
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GDC_API = "https://api.gdc.cancer.gov"
PROJECT = "TCGA-BRCA"
USER_AGENT = "Bio-NAS-inventory-verify/0.1 (+https://github.com/AdamCankaya/PhDNeural)"
DEFAULT_OUT = Path("data/tcga/inventory_verification")
DEFAULT_SMOKE_DIR = Path("data/tcga/BRCA")
DEFAULT_EXPECTED = Path("docs/data/smoke_expected.json")
ARTIFACT_SCHEMA = 1

# Soft floors for "spot-check passed" (GDC counts drift slightly over time).
MIN_CASES = 1000
MIN_METH_CASES = 1000
MIN_RNA_CASES = 1000
MIN_CLINICAL_CASES = 1000


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


def gdc_count(endpoint: str, filters: dict[str, Any]) -> int:
    params = urllib.parse.urlencode(
        {
            "filters": json.dumps(filters),
            "size": "0",
        }
    )
    payload = gdc_get(f"{endpoint}?{params}")
    return int(payload["data"]["pagination"]["total"])


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


def verify_tcga_brca(*, dry_run: bool) -> dict[str, Any]:
    """Spot-check TCGA-BRCA via GDC projects + files endpoints."""
    project_url = (
        f"{GDC_API}/projects/{PROJECT}"
        "?expand=summary,summary.data_categories,summary.experimental_strategies"
    )
    result: dict[str, Any] = {
        "cohort_name": "TCGA-BRCA",
        "source_portal": "GDC",
        "accession_or_id": PROJECT,
        "query_url": project_url,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "access": "open",
        "status": "pending",
        "checks": {},
        "notes": [],
    }

    if dry_run:
        result["status"] = "dry_run_skipped"
        result["notes"].append("Network skipped (--dry-run).")
        return result

    try:
        project = gdc_get(project_url)["data"]
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError) as exc:
        result["status"] = "error"
        result["error"] = str(exc)
        return result

    summary = project.get("summary") or {}
    case_count = int(summary.get("case_count") or 0)
    file_count = int(summary.get("file_count") or 0)
    data_categories = {
        row["data_category"]: {
            "case_count": int(row.get("case_count") or 0),
            "file_count": int(row.get("file_count") or 0),
        }
        for row in (summary.get("data_categories") or [])
        if row.get("data_category")
    }
    experimental = {
        row["experimental_strategy"]: {
            "case_count": int(row.get("case_count") or 0),
            "file_count": int(row.get("file_count") or 0),
        }
        for row in (summary.get("experimental_strategies") or [])
        if row.get("experimental_strategy")
    }

    # PoC Level-3 open file counts (cases with matching open files).
    meth_filters = and_filters(
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
            "content": {
                "field": "data_category",
                "value": ["DNA Methylation"],
            },
        },
    )
    rna_filters = and_filters(
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
    )
    clinical_filters = and_filters(
        *project_open(),
        {
            "op": "in",
            "content": {"field": "data_category", "value": ["Clinical"]},
        },
        {
            "op": "in",
            "content": {"field": "data_format", "value": ["BCR Biotab"]},
        },
    )

    meth_files = gdc_count(f"{GDC_API}/files", meth_filters)
    rna_files = gdc_count(f"{GDC_API}/files", rna_filters)
    clinical_files = gdc_count(f"{GDC_API}/files", clinical_filters)

    # Distinct cases with open meth / RNA (via cases endpoint + files filter).
    meth_cases = gdc_count(
        f"{GDC_API}/cases",
        and_filters(
            {
                "op": "in",
                "content": {"field": "project.project_id", "value": [PROJECT]},
            },
            {
                "op": "in",
                "content": {
                    "field": "files.data_type",
                    "value": ["Methylation Beta Value"],
                },
            },
            {
                "op": "in",
                "content": {"field": "files.access", "value": ["open"]},
            },
        ),
    )
    rna_cases = gdc_count(
        f"{GDC_API}/cases",
        and_filters(
            {
                "op": "in",
                "content": {"field": "project.project_id", "value": [PROJECT]},
            },
            {
                "op": "in",
                "content": {
                    "field": "files.data_type",
                    "value": ["Gene Expression Quantification"],
                },
            },
            {
                "op": "in",
                "content": {
                    "field": "files.analysis.workflow_type",
                    "value": ["STAR - Counts"],
                },
            },
            {
                "op": "in",
                "content": {"field": "files.access", "value": ["open"]},
            },
        ),
    )

    checks = {
        "project_case_count": {
            "value": case_count,
            "min_expected": MIN_CASES,
            "pass": case_count >= MIN_CASES,
        },
        "project_file_count": {
            "value": file_count,
            "min_expected": 10000,
            "pass": file_count >= 10000,
        },
        "open_meth_beta_files": {
            "value": meth_files,
            "min_expected": MIN_METH_CASES,
            "pass": meth_files >= MIN_METH_CASES,
        },
        "open_star_rna_files": {
            "value": rna_files,
            "min_expected": MIN_RNA_CASES,
            "pass": rna_files >= MIN_RNA_CASES,
        },
        "open_clinical_biotab_files": {
            "value": clinical_files,
            "min_expected": 1,
            "pass": clinical_files >= 1,
        },
        "cases_with_open_meth_beta": {
            "value": meth_cases,
            "min_expected": MIN_METH_CASES,
            "pass": meth_cases >= MIN_METH_CASES,
        },
        "cases_with_open_star_rna": {
            "value": rna_cases,
            "min_expected": MIN_RNA_CASES,
            "pass": rna_cases >= MIN_RNA_CASES,
        },
        "summary_dna_methylation_cases": {
            "value": (data_categories.get("DNA Methylation") or {}).get(
                "case_count", 0
            ),
            "min_expected": MIN_METH_CASES,
            "pass": (data_categories.get("DNA Methylation") or {}).get(
                "case_count", 0
            )
            >= MIN_METH_CASES,
        },
        "summary_transcriptome_cases": {
            "value": (data_categories.get("Transcriptome Profiling") or {}).get(
                "case_count", 0
            ),
            "min_expected": MIN_RNA_CASES,
            "pass": (data_categories.get("Transcriptome Profiling") or {}).get(
                "case_count", 0
            )
            >= MIN_RNA_CASES,
        },
        "summary_clinical_cases": {
            "value": (data_categories.get("Clinical") or {}).get("case_count", 0),
            "min_expected": MIN_CLINICAL_CASES,
            "pass": (data_categories.get("Clinical") or {}).get("case_count", 0)
            >= MIN_CLINICAL_CASES,
        },
    }

    all_pass = all(c["pass"] for c in checks.values())
    result.update(
        {
            "status": "verified_gdc_api" if all_pass else "verification_failed",
            "project_id": project.get("project_id"),
            "name": project.get("name"),
            "summary": {
                "case_count": case_count,
                "file_count": file_count,
                "data_categories": data_categories,
                "experimental_strategies": experimental,
            },
            "poc_level3_open": {
                "methylation_beta_files": meth_files,
                "star_rna_files": rna_files,
                "clinical_biotab_files": clinical_files,
                "cases_with_meth_beta": meth_cases,
                "cases_with_star_rna": rna_cases,
            },
            "checks": checks,
            "inventory_fields": {
                "n_subjects_approx": f"~{case_count} cases (GDC summary)",
                "n_samples_approx": (
                    f"meth cases ~{meth_cases}; STAR RNA cases ~{rna_cases}; "
                    f"project files ~{file_count}"
                ),
                "verification_status": (
                    "verified_gdc_api" if all_pass else "verification_failed"
                ),
            },
            "notes": [
                "Open Level-3 PoC modalities: methylation betas + STAR RNA + clinical.",
                "Controlled/dbGaP not queried.",
                "Counts are live GDC totals and may drift slightly over time.",
            ],
        }
    )
    return result


def check_smoke_manifest(
    smoke_dir: Path,
    expected_path: Path,
) -> dict[str, Any]:
    """Validate local smoke manifest against pinned schema / range expectations."""
    out: dict[str, Any] = {
        "smoke_dir": str(smoke_dir),
        "expected_path": str(expected_path),
        "status": "skipped",
        "checks": {},
    }
    if not expected_path.is_file():
        out["status"] = "no_expected_file"
        out["notes"] = [f"Missing expected pins: {expected_path}"]
        return out

    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    manifest_path = smoke_dir / "manifest.json"
    if not manifest_path.is_file():
        out["status"] = "no_local_manifest"
        out["notes"] = [
            f"No {manifest_path}; run download step first (or skip pin check)."
        ]
        return out

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks: dict[str, Any] = {}

    exp_schema = expected.get("schema_version")
    got_schema = manifest.get("schema_version")
    checks["schema_version"] = {
        "expected": exp_schema,
        "actual": got_schema,
        "pass": got_schema == exp_schema,
    }

    n_cases = int(manifest.get("n_cases") or 0)
    n_min = int(expected.get("n_cases_min", 5))
    n_max = int(expected.get("n_cases_max", 10))
    checks["n_cases_range"] = {
        "expected": f"{n_min}..{n_max}",
        "actual": n_cases,
        "pass": n_min <= n_cases <= n_max,
    }

    files = manifest.get("files") or []
    n_files = len(files)
    f_min = int(expected.get("n_files_min", 1))
    checks["n_files_min"] = {
        "expected_min": f_min,
        "actual": n_files,
        "pass": n_files >= f_min,
    }

    poc = set(manifest.get("poc_modalities") or [])
    exp_poc = set(expected.get("poc_modalities") or [])
    checks["poc_modalities"] = {
        "expected": sorted(exp_poc),
        "actual": sorted(poc),
        "pass": exp_poc.issubset(poc),
    }

    labels = {f.get("label") for f in files}
    for label in expected.get("required_file_labels") or []:
        checks[f"has_label_{label}"] = {
            "expected": label,
            "pass": label in labels,
        }

    all_pass = all(c.get("pass") for c in checks.values())
    out["status"] = "pass" if all_pass else "fail"
    out["checks"] = checks
    out["manifest_project"] = manifest.get("project")
    out["manifest_n_cases"] = n_cases
    out["manifest_n_files"] = n_files
    return out


def write_artifacts(out_dir: Path, payload: dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "verification.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _log(f"Wrote {json_path}")

    # Flat CSV summary for inventory sync / spreadsheet use.
    rows = payload.get("cohorts") or []
    csv_path = out_dir / "verification_summary.csv"
    lines = [
        "cohort_name,source_portal,accession_or_id,status,"
        "case_count,meth_cases,rna_cases,verified_at"
    ]
    for row in rows:
        summary = row.get("summary") or {}
        poc = row.get("poc_level3_open") or {}
        lines.append(
            ",".join(
                [
                    str(row.get("cohort_name", "")),
                    str(row.get("source_portal", "")),
                    str(row.get("accession_or_id", "")),
                    str(row.get("status", "")),
                    str(summary.get("case_count", "")),
                    str(poc.get("cases_with_meth_beta", "")),
                    str(poc.get("cases_with_star_rna", "")),
                    str(row.get("verified_at", "")),
                ]
            )
        )
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    _log(f"Wrote {csv_path}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path(
            os.environ.get("INVENTORY_VERIFY_OUT", str(DEFAULT_OUT))
        ),
        help=f"Artifact directory (default: {DEFAULT_OUT} or $INVENTORY_VERIFY_OUT)",
    )
    p.add_argument(
        "--smoke-dir",
        type=Path,
        default=Path(os.environ.get("TCGA_SAMPLE_OUT", str(DEFAULT_SMOKE_DIR))),
        help="Local smoke cohort dir with manifest.json",
    )
    p.add_argument(
        "--expected",
        type=Path,
        default=Path(
            os.environ.get("SMOKE_EXPECTED_JSON", str(DEFAULT_EXPECTED))
        ),
        help="Pinned smoke expectations JSON",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip network GDC queries; still write dry-run artifacts",
    )
    p.add_argument(
        "--skip-smoke-check",
        action="store_true",
        help="Do not validate local smoke manifest pins",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _log("=== Plan 01 open inventory verification ===")
    _log(f"Out dir: {args.out_dir}")
    if args.dry_run:
        _log("Mode: dry-run (no GDC network calls)")

    brca = verify_tcga_brca(dry_run=args.dry_run)
    _log(f"TCGA-BRCA status: {brca.get('status')}")
    for name, check in (brca.get("checks") or {}).items():
        if isinstance(check, dict) and "pass" in check:
            mark = "PASS" if check["pass"] else "FAIL"
            _log(f"  [{mark}] {name}: {check.get('value', check)}")

    smoke: dict[str, Any] | None = None
    if not args.skip_smoke_check:
        smoke = check_smoke_manifest(args.smoke_dir, args.expected)
        _log(f"Smoke pin check: {smoke.get('status')}")

    payload = {
        "schema_version": ARTIFACT_SCHEMA,
        "plan": "01-issue-354-multi-disease-dataset-inventory",
        "issue": 354,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": bool(args.dry_run),
        "cohorts": [brca],
        "skipped_controlled": [
            {
                "cohort_name": "ADNI (LONI)",
                "selection_status": "locked",
                "reason": (
                    "Controlled ADNI/LONI — no public login-free API. "
                    "Account + DUA in progress; inventory verify is post-DUA. "
                    "Docker scaffold: scripts/download_adni_sample.py → /data/adni."
                ),
            },
            {
                "cohort_name": "AURORA US / AURORA BIG / KORA / LBC1936 / ROSMAP / dbGaP",
                "reason": "Controlled or DUA — outside Docker Plan-1 open verify path",
            },
        ],
        "smoke_manifest_check": smoke,
        "overall_status": (
            "ok"
            if brca.get("status") in {"verified_gdc_api", "dry_run_skipped"}
            and (
                smoke is None
                or smoke.get("status")
                in {"pass", "skipped", "no_local_manifest", "no_expected_file"}
            )
            else "failed"
        ),
    }

    # Treat missing local smoke as non-fatal (verify can run before download
    # in isolation); fail hard only on GDC verify failure or smoke pin fail.
    if brca.get("status") == "verification_failed":
        payload["overall_status"] = "failed"
    if smoke and smoke.get("status") == "fail":
        payload["overall_status"] = "failed"
    if brca.get("status") == "error":
        payload["overall_status"] = "failed"

    write_artifacts(args.out_dir, payload)
    _log(f"Overall: {payload['overall_status']}")
    return 0 if payload["overall_status"] in {"ok"} else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 — top-level CLI
        _log(f"ERROR: {exc}")
        raise SystemExit(1) from exc
