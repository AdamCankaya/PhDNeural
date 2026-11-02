"""Regression guard: Plan 1 docker/entrypoint.sh must invoke key scripts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRYPOINT = ROOT / "docker" / "entrypoint.sh"


def test_entrypoint_includes_inventory_verify_and_adni_scaffold() -> None:
    text = ENTRYPOINT.read_text(encoding="utf-8")
    assert "verify_cohort_inventory_open.py" in text
    assert "download_adni_sample.py" in text
    assert "train_nas_ad_demo.py" in text
