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

    def test_entrypoint_includes_brca_longitudinal_matching(self) -> None:
        text = ENTRYPOINT.read_text(encoding="utf-8")
        self.assertIn("build_brca_longitudinal_matching.py", text)
        self.assertIn("SKIP_BRCA_MATCHING", text)
        self.assertIn("--discover", text)
        self.assertIn("BRCA_MATCHING_SCOPE", text)
        self.assertIn("--smoke-dir", text)


if __name__ == "__main__":
    unittest.main()
