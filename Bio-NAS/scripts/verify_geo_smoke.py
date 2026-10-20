#!/usr/bin/env python3
"""Verify GEO RA smoke cohort on disk against pinned expectations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

DEFAULT_SMOKE_DIR = Path("data/ra")
DEFAULT_EXPECTED = Path("docs/data/smoke_expected_ra.json")


def _fail(msg: str) -> int:
    print(f"verify_geo_smoke: FAIL — {msg}", file=sys.stderr)
    return 1


def verify(smoke_dir: Path, expected: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ready = smoke_dir / ".ready"
    manifest_path = smoke_dir / "manifest.json"
    demo_path = smoke_dir / "demographics.json"
    files_dir = smoke_dir / "files"

    if not ready.is_file():
        errors.append("missing .ready marker")
    if not manifest_path.is_file():
        errors.append("missing manifest.json")
    if not demo_path.is_file():
        errors.append("missing demographics.json")
    if errors:
        return errors

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    demographics = json.loads(demo_path.read_text(encoding="utf-8"))

    if manifest.get("schema_version") != expected.get("schema_version"):
        errors.append(
            f"schema_version {manifest.get('schema_version')} != "
            f"{expected.get('schema_version')}"
        )
    if manifest.get("accession") != expected.get("accession"):
        errors.append("accession mismatch")

    n_cases = int(manifest.get("n_cases") or 0)
    if n_cases < int(expected.get("n_cases_min", 5)):
        errors.append(f"n_cases {n_cases} below minimum")
    if n_cases > int(expected.get("n_cases_max", 10)):
        errors.append(f"n_cases {n_cases} above maximum")

    cohort = manifest.get("cohort") or []
    if len(cohort) != n_cases:
        errors.append("cohort length != n_cases")

    labels = {int(row.get("label", -99)) for row in demographics}
    required = set(expected.get("required_label_values") or [0, 1])
    if not required.issubset(labels):
        errors.append(f"demographics labels {sorted(labels)} missing {sorted(required)}")

    for entry in cohort:
        case_id = entry.get("case_id")
        meth_name = entry.get("methylation_file_name")
        if not case_id or not meth_name:
            errors.append("cohort entry missing case_id or methylation_file_name")
            continue
        meth_path = files_dir / meth_name
        if not meth_path.is_file():
            errors.append(f"missing methylation file for {case_id}: {meth_name}")

    return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--smoke-dir",
        type=Path,
        default=Path(os.environ.get("RA_SAMPLE_OUT", str(DEFAULT_SMOKE_DIR))),
    )
    p.add_argument(
        "--expected",
        type=Path,
        default=Path(os.environ.get("RA_SMOKE_EXPECTED_JSON", str(DEFAULT_EXPECTED))),
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    smoke_dir = args.smoke_dir.resolve()
    if not args.expected.is_file():
        return _fail(f"expected JSON not found: {args.expected}")
    expected = json.loads(args.expected.read_text(encoding="utf-8"))
    errors = verify(smoke_dir, expected)
    if errors:
        return _fail("; ".join(errors))
    print(f"verify_geo_smoke: OK ({smoke_dir})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
