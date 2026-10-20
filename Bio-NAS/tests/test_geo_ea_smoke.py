"""GEO EA smoke tests — no live NCBI FTP."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "geo_ea_smoke"
sys.path.insert(0, str(ROOT / "scripts"))

from download_geo_ea_sample import age_to_label, parse_age_from_characteristic  # noqa: E402
from train_nas_demo import N_CPGS, load_ea_cohort  # noqa: E402
from verify_geo_smoke import verify  # noqa: E402


class GeoEaSmokeTests(unittest.TestCase):
    def test_age_parsing_and_labels(self) -> None:
        self.assertEqual(parse_age_from_characteristic("age: 42"), 42)
        self.assertEqual(parse_age_from_characteristic("Age: 72"), 72)
        self.assertIsNone(parse_age_from_characteristic("gender: female"))
        self.assertEqual(age_to_label(49), 0)
        self.assertEqual(age_to_label(50), 1)

    def test_load_ea_cohort_shape(self) -> None:
        x, y, case_ids = load_ea_cohort(FIXTURE, n_cpgs=N_CPGS)
        self.assertEqual(x.shape[0], 6)
        self.assertGreaterEqual(x.shape[1], 10)
        self.assertEqual(len(case_ids), 6)
        self.assertGreaterEqual(len(np.unique(y)), 2)
        self.assertEqual(len(np.bincount(y)), 2)

    def test_verify_geo_smoke_fixture(self) -> None:
        expected = json.loads(
            (ROOT / "docs" / "data" / "smoke_expected_ea.json").read_text(encoding="utf-8")
        )
        errors = verify(FIXTURE, expected)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
