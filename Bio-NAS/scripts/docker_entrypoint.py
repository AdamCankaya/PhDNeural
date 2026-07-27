#!/usr/bin/env python3
"""Docker entrypoint: BRCA open chain + optional ADNI scaffold.

Chain:
  1. Open PoC-minimum TCGA-BRCA sample at $TCGA_SAMPLE_OUT (meth betas + STAR
     RNA + clinical for ~5–10 joint cases)
  2. Plan-1 open inventory verification → $INVENTORY_VERIFY_OUT
  3. Optional methylation-only toy NAS smoke (skip with SKIP_NAS_DEMO=1)
  4. ADNI (LONI) sample scaffold → $ADNI_SAMPLE_OUT (skip/exit 0 without
     credentials; account + DUA in progress — no controlled scrape)
  5. Optional AD meth-only toy NAS when ADNI sample ``.ready`` present
     (skip with SKIP_AD_NAS_DEMO=1)

Download happens at container start (not image build). No GDC login / token —
open ``access=open`` API only. ADNI credentials from host ``.env`` only —
never baked into the image. Controlled/dbGaP deferred.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def _log(msg: str) -> None:
    print(msg, flush=True)


def _truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def main() -> int:
    data_dir = Path(os.environ.get("TCGA_SAMPLE_OUT", "/data/tcga/BRCA"))
    verify_dir = Path(
        os.environ.get("INVENTORY_VERIFY_OUT", "/data/tcga/inventory_verification")
    )
    adni_dir = Path(os.environ.get("ADNI_SAMPLE_OUT", "/data/adni"))
    _log("=== Bio-NAS Docker entrypoint ===")
    _log(f"Data path (inside container): {data_dir}")
    _log(f"Inventory verify path: {verify_dir}")
    _log(f"ADNI path (inside container): {adni_dir}")
    _log(
        "Plan-1 chain: BRCA download → inventory verification → "
        "optional meth-only toy NAS → ADNI scaffold → optional AD NAS."
    )

    download = SCRIPTS / "download_tcga_brca_sample.py"
    verify = SCRIPTS / "verify_cohort_inventory_open.py"
    train = SCRIPTS / "train_nas_demo.py"
    adni_download = SCRIPTS / "download_adni_sample.py"
    ad_train = SCRIPTS / "train_nas_ad_demo.py"

    # Prefer image-baked expected pins; fall back to default path in script.
    expected = Path(
        os.environ.get(
            "SMOKE_EXPECTED_JSON",
            "/app/docs/data/smoke_expected.json",
        )
    )

    _log("--- Step 1/5: GDC open-access download (skip if .ready) ---")
    r1 = subprocess.run([sys.executable, str(download)], check=False)
    if r1.returncode != 0:
        _log("Download failed; aborting.")
        return r1.returncode

    _log("--- Step 2/5: open inventory verification (GDC public API) ---")
    verify_cmd = [
        sys.executable,
        str(verify),
        "--out-dir",
        str(verify_dir),
        "--smoke-dir",
        str(data_dir),
    ]
    if expected.is_file():
        verify_cmd.extend(["--expected", str(expected)])
    if _truthy("INVENTORY_VERIFY_DRY_RUN"):
        verify_cmd.append("--dry-run")
    r2 = subprocess.run(verify_cmd, check=False)
    if r2.returncode != 0:
        _log("Inventory verification failed; aborting.")
        return r2.returncode

    if _truthy("SKIP_NAS_DEMO"):
        _log("--- Step 3/5: BRCA toy NAS skipped (SKIP_NAS_DEMO) ---")
    else:
        _log("--- Step 3/5: BRCA toy NAS (methylation-only smoke) ---")
        r3 = subprocess.run([sys.executable, str(train)], check=False)
        if r3.returncode != 0:
            _log("Training/NAS demo failed.")
            return r3.returncode

    _log(
        "--- Step 4/5: ADNI scaffold "
        "(skip/exit 0 without credentials; account+DUA in progress) ---"
    )
    r4 = subprocess.run([sys.executable, str(adni_download)], check=False)
    if r4.returncode != 0:
        _log("ADNI scaffold step failed (non-BRCA); aborting.")
        return r4.returncode

    if _truthy("SKIP_AD_NAS_DEMO"):
        _log("--- Step 5/5: AD toy NAS skipped (SKIP_AD_NAS_DEMO) ---")
    else:
        _log(
            "--- Step 5/5: AD toy NAS "
            "(methylation-only; skips if no ADNI .ready sample) ---"
        )
        r5 = subprocess.run([sys.executable, str(ad_train)], check=False)
        if r5.returncode != 0:
            _log("AD training/NAS demo failed.")
            return r5.returncode

    _log("=== Bio-NAS Docker run complete ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
