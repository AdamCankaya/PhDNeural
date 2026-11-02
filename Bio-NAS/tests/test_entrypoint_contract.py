"""Regression guard: Plan 1 docker/entrypoint.sh must invoke key scripts."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRYPOINT = ROOT / "docker" / "entrypoint.sh"


class EntrypointContractTests(unittest.TestCase):
    def test_entrypoint_includes_inventory_verify_and_adni_scaffold(self) -> None:
        text = ENTRYPOINT.read_text(encoding="utf-8")
        self.assertIn("verify_cohort_inventory_open.py", text)
        self.assertIn("download_adni_sample.py", text)
        self.assertIn("train_nas_ad_demo.py", text)


if __name__ == "__main__":
    unittest.main()
