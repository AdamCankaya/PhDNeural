"""Load YAML configuration under ``src/config/``."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_CONFIG_DIR = Path(__file__).resolve().parent
_DEFAULT_LONGITUDINAL_KEYS = _CONFIG_DIR / "longitudinal_keys.yaml"


def load_yaml(path: Path | str) -> dict[str, Any]:
    """Parse a YAML file into a dict."""
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at root of {p}")
    return data


def load_longitudinal_keys(path: Path | str | None = None) -> dict[str, Any]:
    """Load ``longitudinal_keys.yaml`` (or override path)."""
    return load_yaml(path or _DEFAULT_LONGITUDINAL_KEYS)


def brca_gdc_keys(keys: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the ``brca.gdc`` section; raise if missing."""
    keys = keys or load_longitudinal_keys()
    try:
        section = keys["brca"]["gdc"]
    except KeyError as exc:
        raise KeyError("longitudinal_keys.yaml missing brca.gdc section") from exc
    if not isinstance(section, dict):
        raise ValueError("brca.gdc must be a mapping")
    return section
