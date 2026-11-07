"""Unit tests for BRCA longitudinal matching core library."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config.load_config import brca_gdc_keys, load_longitudinal_keys
from src.data.brca_longitudinal_matching import (
    build_match_pairs,
    filter_ranked_samples,
    normalize_gdc_case,
    order_visits,
    process_case,
    process_cohort,
    summarize_cohort,
)

FIXTURE = ROOT / "tests" / "fixtures" / "gdc_brca_samples_mini.json"


class BrcaLongitudinalMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gdc_keys = brca_gdc_keys(load_longitudinal_keys())
        raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.cases = raw["cases"]

    def test_order_visits_single_sample_excluded(self) -> None:
        case = normalize_gdc_case(self.cases[0], self.gdc_keys)
        visits, reason = order_visits(case["samples"], self.gdc_keys)
        self.assertEqual(visits, [])
        self.assertEqual(reason, "single_sample_case")

    def test_order_visits_days_and_rank(self) -> None:
        case = normalize_gdc_case(self.cases[1], self.gdc_keys)
        enriched = [{**s, "case_id": case["case_id"], "submitter_id": case["submitter_id"]} for s in case["samples"]]
        visits, reason = order_visits(enriched, self.gdc_keys)
        self.assertIsNone(reason)
        self.assertEqual(len(visits), 2)
        self.assertEqual(visits[0].sample_type, "Solid Tissue Normal")
        self.assertEqual(visits[1].sample_type, "Primary Tumor")

    def test_ambiguous_duplicate_primary_excluded(self) -> None:
        case = normalize_gdc_case(self.cases[3], self.gdc_keys)
        enriched = [{**s, "case_id": case["case_id"], "submitter_id": case["submitter_id"]} for s in case["samples"]]
        _, reason = order_visits(enriched, self.gdc_keys)
        self.assertEqual(reason, "ambiguous_duplicate_sample_type_without_time")

    def test_filter_ranked_samples_drops_unranked(self) -> None:
        case = normalize_gdc_case(self.cases[5], self.gdc_keys)
        enriched = [{**s, "case_id": case["case_id"], "submitter_id": case["submitter_id"]} for s in case["samples"]]
        ranked, n_dropped = filter_ranked_samples(enriched, self.gdc_keys)
        self.assertEqual(n_dropped, 1)
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["sample_type"], "Primary Tumor")

    def test_unranked_mixed_case_not_missing_time_and_rank(self) -> None:
        case = normalize_gdc_case(self.cases[5], self.gdc_keys)
        result = process_case(case, self.gdc_keys)
        self.assertTrue(result.excluded)
        self.assertEqual(result.exclusion_reason, "single_sample_case")
        self.assertNotEqual(result.exclusion_reason, "missing_time_and_rank")
        self.assertEqual(result.n_samples_dropped_unranked, 1)

    def test_summarize_includes_dropped_unranked(self) -> None:
        results = process_cohort(self.cases, self.gdc_keys)
        summary = summarize_cohort(results, n_cases_queried=len(self.cases))
        self.assertGreaterEqual(summary["n_samples_dropped_unranked"], 1)

    def test_build_match_pairs_primary_to_met(self) -> None:
        results = process_cohort(self.cases, self.gdc_keys)
        summary = summarize_cohort(results, n_cases_queried=len(self.cases))
        self.assertGreaterEqual(summary["n_match_pairs"], 2)
        self.assertGreaterEqual(summary["n_visit_sequences"], 3)
        pair_types = {
            (p.anchor_sample_type, p.later_sample_type)
            for r in results
            for p in r.pairs
        }
        self.assertIn(("Primary Tumor", "Metastatic"), pair_types)

    def test_rank_fallback_without_days(self) -> None:
        case = normalize_gdc_case(self.cases[2], self.gdc_keys)
        enriched = [{**s, "case_id": case["case_id"], "submitter_id": case["submitter_id"]} for s in case["samples"]]
        visits, reason = order_visits(enriched, self.gdc_keys)
        self.assertIsNone(reason)
        self.assertEqual(visits[0].sample_type, "Primary Tumor")
        self.assertEqual(visits[1].sample_type, "Metastatic")
        pairs = build_match_pairs(visits, self.gdc_keys)
        self.assertEqual(len(pairs), 1)


if __name__ == "__main__":
    unittest.main()
