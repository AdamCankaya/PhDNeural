"""Tests for longitudinal_keys.yaml loader."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config.load_config import brca_gdc_keys, load_longitudinal_keys


class LongitudinalKeysTests(unittest.TestCase):
    def test_brca_gdc_required_sections(self) -> None:
        keys = load_longitudinal_keys()
        gdc = brca_gdc_keys(keys)
        self.assertEqual(gdc["project_id"], "TCGA-BRCA")
        self.assertIn("case_id_field", gdc["patient"])
        self.assertIn("primary", gdc["sample"]["time_fields"])
        rank = gdc["sample_type_rank"]
        for st in ("Solid Tissue Normal", "Primary Tumor", "Recurrent Tumor", "Metastatic"):
            self.assertIn(st, rank)
        self.assertLess(rank["Solid Tissue Normal"], rank["Primary Tumor"])
        self.assertLess(rank["Primary Tumor"], rank["Metastatic"])

    def test_ra_ea_stubs_present(self) -> None:
        keys = load_longitudinal_keys()
        self.assertEqual(keys["ra"]["status"], "stub")
        self.assertEqual(keys["epigenetic_aging"]["status"], "stub")


if __name__ == "__main__":
    unittest.main()
