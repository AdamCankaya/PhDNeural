"""Offline tests for GSE87571 supplementary matrix beta parsing."""
from __future__ import annotations

import gzip
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "gse87571_suppl_mini"
sys.path.insert(0, str(ROOT / "scripts"))

from download_geo_ea_sample import (  # noqa: E402
    _parse_beta,
    _scan_series_matrix_gz,
    parse_supplementary_matrix_betas,
    select_stratified_gsms,
)


class DownloadGeoEaSupplTests(unittest.TestCase):
    def test_parse_beta_sentinels(self) -> None:
        self.assertIsNone(_parse_beta("NA"))
        self.assertIsNone(_parse_beta("null"))
        self.assertIsNone(_parse_beta(""))
        self.assertIsNone(_parse_beta('"NA"'))
        self.assertAlmostEqual(_parse_beta("0.5123"), 0.5123)

    def test_empty_series_matrix_table_triggers_suppl_path(self) -> None:
        with gzip.open(FIXTURE_DIR / "series_matrix_mini.txt.gz", "rb") as archive:
            (
                _meta,
                selected_gsms,
                col_indices,
                probes,
                _betas,
                table_row_count,
            ) = _scan_series_matrix_gz(archive, n_samples=6, max_probes=200)
        self.assertEqual(table_row_count, 1)
        self.assertEqual(len(probes), 0)
        self.assertEqual(len(selected_gsms), 6)
        self.assertEqual(col_indices, [1, 2, 3, 4, 5, 6])

        with gzip.open(FIXTURE_DIR / "matrix1of2_mini.txt.gz", "rb") as archive:
            probes, betas_by_gsm = parse_supplementary_matrix_betas(
                archive,
                col_indices=col_indices,
                selected_gsms=selected_gsms,
                max_probes=12,
            )
        self.assertGreaterEqual(len(probes), 10)
        for gsm in selected_gsms:
            self.assertEqual(len(betas_by_gsm[gsm]), len(probes))
            for probe, beta in betas_by_gsm[gsm]:
                self.assertTrue(probe.startswith("cg"))
                self.assertGreaterEqual(beta, 0.0)
                self.assertLessEqual(beta, 1.0)

    def test_gsm_header_alignment_indices(self) -> None:
        gsm_ids = ["GSM_A1", "GSM_A2", "GSM_B1", "GSM_B2", "GSM_C1", "GSM_C2"]
        ages = [42, 45, 55, 60, 48, 62]
        chosen = select_stratified_gsms(gsm_ids, ages, 6)
        self.assertEqual(len(chosen), 6)
        with gzip.open(FIXTURE_DIR / "series_matrix_mini.txt.gz", "rb") as archive:
            _meta, selected, col_indices, *_rest = _scan_series_matrix_gz(
                archive, n_samples=6, max_probes=5
            )
        idx_by_gsm = dict(zip(selected, col_indices))
        for gsm in chosen:
            self.assertIn(gsm, idx_by_gsm)
            self.assertGreater(idx_by_gsm[gsm], 0)


if __name__ == "__main__":
    unittest.main()
