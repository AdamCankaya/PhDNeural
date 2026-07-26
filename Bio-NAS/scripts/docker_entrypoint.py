#!/usr/bin/env python3
"""Docker entrypoint: download TCGA-BRCA sample if needed, then run NAS demo.

Chain: ensure data at $TCGA_SAMPLE_OUT → toy training/NAS.
Download happens at container start (not image build). No GDC login required
for open-access files.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def _log(msg: str) -> None:
    print(msg, flush=True)


def main() -> int:
    data_dir = Path(os.environ.get("TCGA_SAMPLE_OUT", "/data/tcga/BRCA"))
    _log("=== Bio-NAS Docker entrypoint ===")
    _log(f"Data path (inside container): {data_dir}")

    download = SCRIPTS / "download_tcga_brca_sample.py"
    train = SCRIPTS / "train_nas_demo.py"

    _log("--- Step 1/2: GDC open-access download (skip if .ready) ---")
    r1 = subprocess.run([sys.executable, str(download)], check=False)
    if r1.returncode != 0:
        _log("Download failed; aborting.")
        return r1.returncode

    _log("--- Step 2/2: toy NAS / training demo ---")
    r2 = subprocess.run([sys.executable, str(train)], check=False)
    if r2.returncode != 0:
        _log("Training/NAS demo failed.")
        return r2.returncode

    _log("=== Bio-NAS Docker run complete ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
