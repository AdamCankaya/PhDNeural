#!/usr/bin/env python3
"""ADNI (LONI) sample download scaffold — Plan 01 Alzheimer's slice.

Controlled-access cohort. **No secrets in the image.** Credentials (when
available) come from the host via Compose ``env_file: .env`` / environment:

  ADNI_USER / ADNI_PASSWORD   — LONI IDA login (after ADNI account + DUA)
  ADNI_SKIP=1                — force skip even if credentials are set

Until ADNI/LONI account + Data Use Agreement are approved, this script
**refuses to download** and exits 0 (non-fatal skip) so the BRCA Plan-1
chain keeps working.

When credentials are present, still no automated LONI scrape — prints the
manual/outside-Docker steps and expected layout under ``./data/adni`` →
``/data/adni``. Real bulk/sample pull is post-DUA.

Usage:
  python scripts/download_adni_sample.py
  python scripts/download_adni_sample.py --out-dir /data/adni
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_OUT = Path("data/adni")
READY_MARKER = ".ready"
SKIP_MARKER = ".skipped"
STATUS_JSON = "adni_access_status.json"
USER_AGENT = "Bio-NAS-adni-sample/0.1 (+https://github.com/AdamCankaya/PhDNeural)"

# PoC-minimum modalities once DUA is approved (inventory-aligned).
POC_MODALITIES = [
    "DNA methylation (EPIC blood)",
    "clinical / cognitive labels",
    "genotype / GWAS (optional join)",
]


def _log(msg: str) -> None:
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, "encoding", None) or "utf-8"
        sys.stdout.buffer.write((msg + "\n").encode(enc, errors="replace"))
        sys.stdout.flush()


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def credentials_present() -> bool:
    user = os.environ.get("ADNI_USER", "").strip()
    password = os.environ.get("ADNI_PASSWORD", "").strip()
    return bool(user and password)


def write_status(out_dir: Path, payload: dict[str, Any]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / STATUS_JSON
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path(os.environ.get("ADNI_SAMPLE_OUT", str(DEFAULT_OUT))),
        help=f"ADNI sample root (default: {DEFAULT_OUT} or $ADNI_SAMPLE_OUT)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    out_dir = args.out_dir.resolve()
    ready = out_dir / READY_MARKER
    now = datetime.now(timezone.utc).isoformat()

    _log(f"ADNI sample out: {out_dir}")
    _log(
        "Controlled ADNI/LONI data — account + DUA required. "
        "Never bake credentials into the Docker image."
    )

    if ready.is_file():
        _log(f"Found {ready.name}; skipping ADNI download step.")
        return 0

    if _truthy("ADNI_SKIP"):
        payload = {
            "cohort": "ADNI",
            "source_portal": "LONI IDA",
            "status": "skipped_forced",
            "reason": "ADNI_SKIP set",
            "account_dua_status": "in_progress",
            "verified_at": now,
            "expected_host_path": "data/adni",
            "expected_container_path": "/data/adni",
            "poc_modalities": POC_MODALITIES,
            "user_agent": USER_AGENT,
        }
        status_path = write_status(out_dir, payload)
        (out_dir / SKIP_MARKER).write_text(
            "ADNI_SKIP=1\n", encoding="utf-8"
        )
        _log(f"ADNI skip forced (ADNI_SKIP). Status → {status_path}")
        return 0

    if not credentials_present():
        payload = {
            "cohort": "ADNI",
            "source_portal": "LONI IDA",
            "status": "skipped_account_pending",
            "reason": (
                "ADNI_USER / ADNI_PASSWORD absent. "
                "ADNI/LONI account + Data Use Agreement are in progress "
                "(user applying). No controlled download can succeed yet."
            ),
            "account_dua_status": "in_progress",
            "credentials_env": ["ADNI_USER", "ADNI_PASSWORD"],
            "outside_docker_steps": [
                "Apply for ADNI / LONI IDA account at https://adni.loni.usc.edu/",
                "Complete and receive approval for the ADNI Data Use Agreement",
                "Place ADNI_USER and ADNI_PASSWORD in host Bio-NAS/.env "
                "(gitignored; compose env_file) — never commit secrets",
                "Manually stage a tiny methylation + clinical sample under "
                "data/adni/ (or extend this script post-DUA)",
            ],
            "verified_at": now,
            "expected_layout_after_dua": {
                "manifest.json": "sample catalog (schema TBD post-DUA)",
                "files/": "EPIC methylation + clinical extracts",
                ".ready": "download-complete marker",
            },
            "poc_modalities": POC_MODALITIES,
            "user_agent": USER_AGENT,
        }
        status_path = write_status(out_dir, payload)
        (out_dir / SKIP_MARKER).write_text(
            "account_pending\n", encoding="utf-8"
        )
        _log(
            "SKIP: ADNI/LONI credentials absent — account + DUA in progress. "
            "No bulk/sample download attempted."
        )
        _log(f"Wrote {status_path}")
        _log(
            "After DUA approval: set ADNI_USER/ADNI_PASSWORD in host .env, "
            "rebuild is not required for .env-only changes; "
            "recreate container with docker compose up."
        )
        return 0

    # Credentials present — still scaffold-only (no LONI scrape / login).
    payload = {
        "cohort": "ADNI",
        "source_portal": "LONI IDA",
        "status": "scaffold_no_download",
        "reason": (
            "Credentials env present, but automated LONI sample download is "
            "not wired. Do not scrape behind login. Stage data manually under "
            "data/adni/ after DUA, or extend this script with an approved "
            "LONI client workflow."
        ),
        "account_dua_status": "credentials_env_set_verify_dua_manually",
        "credentials_detected": True,
        "verified_at": now,
        "expected_host_path": "data/adni",
        "expected_container_path": "/data/adni",
        "poc_modalities": POC_MODALITIES,
        "user_agent": USER_AGENT,
    }
    status_path = write_status(out_dir, payload)
    (out_dir / SKIP_MARKER).write_text(
        "scaffold_no_download\n", encoding="utf-8"
    )
    _log(
        "Credentials env detected, but ADNI download remains scaffold-only "
        "(no automated LONI pull). Exit 0 so BRCA chain continues."
    )
    _log(f"Wrote {status_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
