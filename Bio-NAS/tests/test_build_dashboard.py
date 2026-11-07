"""Tests for static multi-disease dashboard generation."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_dashboard import (
    PLAN2_STEP_TITLE,
    build_html,
    disease_row,
    load_matching_summary,
    load_pipeline_steps,
    main,
    plan2_disclaimer,
    render_plan2_section,
    skipped_status,
    step_failures_for_disease,
)


class BuildDashboardTests(unittest.TestCase):
    def test_load_pipeline_steps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "pipeline_steps.log"
            log.write_text("BRCA toy NAS|0\nEpigenetic Aging public GEO sample (GSE87571)|1\n", encoding="utf-8")
            steps = load_pipeline_steps(log)
            self.assertEqual(steps, [("BRCA toy NAS", 0), ("Epigenetic Aging public GEO sample (GSE87571)", 1)])

    def test_epigenetic_aging_skip_hides_stale_nas(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            disease_dir = Path(tmp) / "epigenetic_aging"
            disease_dir.mkdir()
            (disease_dir / ".skipped").write_text("plan1_deferred\n", encoding="utf-8")
            (disease_dir / "nas_demo_results.json").write_text(
                json.dumps({"n_samples": 8, "best_architecture": {"validation_accuracy": 1.0, "hidden_width": 32}}),
                encoding="utf-8",
            )
            row = disease_row("Epigenetic Aging", disease_dir, "GEO", [], ("Epigenetic",))
            self.assertIn("Plan-1 demo", row[2])
            self.assertNotIn("DUA", row[2])
            self.assertEqual(row[4], "N/A")
            self.assertEqual(row[6], "N/A")

    def test_skipped_status_plan1_deferred(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "epigenetic_aging"
            path.mkdir()
            (path / ".skipped").write_text("plan1_deferred", encoding="utf-8")
            self.assertIn("Plan-1 demo", skipped_status(path) or "")

    def test_partial_geo_shows_nas_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            disease_dir = Path(tmp) / "ra"
            disease_dir.mkdir()
            (disease_dir / "nas_demo_results.json").write_text(
                json.dumps({"n_samples": 4, "best_architecture": {"validation_accuracy": 0.5, "hidden_width": 8}}),
                encoding="utf-8",
            )
            row = disease_row("RA", disease_dir, "GEO", [], ("RA",))
            self.assertEqual(row[2], "Partial")
            self.assertIn("0.50", row[6])

    def test_epigenetic_aging_ready_row(self) -> None:
        keywords = (
            "Epigenetic Aging",
            "GSE40279",
            "GSE87571",
            "GSE280465",
            "EA smoke",
            "EA toy",
            "EA public",
        )
        with tempfile.TemporaryDirectory() as tmp:
            disease_dir = Path(tmp) / "epigenetic_aging"
            disease_dir.mkdir()
            (disease_dir / ".ready").write_text("{}\n", encoding="utf-8")
            (disease_dir / "manifest.json").write_text(
                json.dumps({"n_cases": 8, "schema_version": 2}),
                encoding="utf-8",
            )
            (disease_dir / "nas_demo_results.json").write_text(
                json.dumps(
                    {
                        "n_samples": 8,
                        "best_architecture": {
                            "validation_accuracy": 0.75,
                            "hidden_width": 16,
                            "validation_loss": 0.42,
                        },
                    }
                ),
                encoding="utf-8",
            )
            row = disease_row("Epigenetic Aging", disease_dir, "GEO", [], keywords)
            self.assertEqual(row[2], "Ready")
            self.assertEqual(row[4], "8")
            self.assertIn("Methylation", row[5])
            self.assertIn("0.75", row[6])

    def test_epigenetic_aging_failed_verify_step(self) -> None:
        keywords = (
            "Epigenetic Aging",
            "GSE87571",
            "EA smoke",
            "EA toy",
            "EA public",
        )
        with tempfile.TemporaryDirectory() as tmp:
            disease_dir = Path(tmp) / "epigenetic_aging"
            disease_dir.mkdir()
            steps = [("EA smoke verify", 1)]
            row = disease_row("Epigenetic Aging", disease_dir, "GEO", steps, keywords)
            self.assertIn("Failed", row[2])
            self.assertIn("1 step", row[2])

    def test_ea_toy_nas_failure_matches_keywords(self) -> None:
        keywords = ("EA smoke", "EA toy", "GSE87571")
        failed = step_failures_for_disease([("EA toy NAS", 1)], keywords)
        self.assertEqual(failed, ["EA toy NAS"])

    def test_brca_matching_summary_in_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            brca = root / "tcga" / "BRCA" / "longitudinal_matching"
            brca.mkdir(parents=True)
            (brca / "summary.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "cohort_scope": "discover",
                        "n_match_pairs": 3,
                        "n_visit_sequences": 2,
                        "n_samples_dropped_unranked": 5,
                        "sample_types_observed": {"Primary Tumor": 8, "Blood Derived Normal": 2},
                    }
                ),
                encoding="utf-8",
            )
            dash = root / "dashboard"
            dash.mkdir()
            (dash / "pipeline_steps.log").write_text(f"{PLAN2_STEP_TITLE}|0\n", encoding="utf-8")
            html = "\n".join(build_html(root, load_pipeline_steps(dash / "pipeline_steps.log")))
            self.assertIn("Plan 1 — Multi-disease smoke cohorts", html)
            self.assertIn("Plan 2 — BRCA longitudinal matching", html)
            self.assertIn("n_match_pairs", html)
            self.assertIn("n_samples_dropped_unranked", html)
            self.assertIn("sample_types_observed", html)
            self.assertIn("<dt>cohort_scope</dt><dd>discover</dd>", html)
            self.assertIn("3", html)
            self.assertNotIn("often expected", html)

    def test_plan2_disclaimer_smoke_vs_discover(self) -> None:
        discover = plan2_disclaimer({"cohort_scope": "discover", "n_match_pairs": 4})
        self.assertIn("cohort_scope=discover", discover)
        self.assertNotIn("often expected", discover)
        smoke = plan2_disclaimer({"cohort_scope": "smoke", "n_match_pairs": 0})
        self.assertIn("often expected", smoke)
        self.assertIn("BRCA_MATCHING_SCOPE=smoke", smoke)
        empty_discover = "\n".join(
            render_plan2_section(
                {"cohort_scope": "discover", "n_match_pairs": 0, "schema_version": 1},
                [(PLAN2_STEP_TITLE, 0)],
            )
        )
        self.assertIn("not the expected smoke outcome", empty_discover)
        self.assertIn("<dt>cohort_scope</dt><dd>discover</dd>", empty_discover)

    def test_pipeline_steps_table_lists_all_steps(self) -> None:
        steps = [
            ("BRCA public GDC sample", 0),
            (PLAN2_STEP_TITLE, 0),
            ("BRCA toy NAS", 0),
        ]
        html = "\n".join(build_html(Path("data"), steps))
        for title, _ in steps:
            self.assertIn(title, html)

    def test_matching_step_failure_surfaces(self) -> None:
        keywords = ("BRCA", "longitudinal matching")
        steps = [(PLAN2_STEP_TITLE, 1)]
        failed = step_failures_for_disease(steps, keywords)
        self.assertEqual(failed, [PLAN2_STEP_TITLE])
        with tempfile.TemporaryDirectory() as tmp:
            disease_dir = Path(tmp) / "BRCA"
            disease_dir.mkdir()
            row = disease_row("TCGA-BRCA", disease_dir, "GDC", steps, keywords)
            self.assertIn("Failed", row[2])

    def test_load_matching_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brca = Path(tmp) / "BRCA" / "longitudinal_matching"
            brca.mkdir(parents=True)
            (brca / "summary.json").write_text('{"n_match_pairs": 0}', encoding="utf-8")
            data = load_matching_summary(Path(tmp) / "BRCA")
            self.assertEqual(data["n_match_pairs"], 0)


if __name__ == "__main__":
    unittest.main()
