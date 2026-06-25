"""Canonical clinical time features for the Static MTL baseline.

Time-related fields are continuous tabular inputs in the clinical modality.
They are Z-scored on the training partition only (no temporal sequences).
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

# Canonical time-as-tabular feature names (order preserved for tensor concat).
CLINICAL_TIME_FEATURES: tuple[str, ...] = (
    "age_at_sample",
    "years_since_diagnosis",
    "days_since_sample_collection",
    "survival_days",
    "time_since_last_visit",
)

# Non-time clinical demographics (Z-scored or one-hot encoded separately).
CLINICAL_STATIC_FEATURES: tuple[str, ...] = (
    "sex",
    "ethnicity",
    "race",
    "event_observed",  # censoring indicator when survival_days is present
)

# TCGA-BRCA source column → canonical time feature mapping.
TCGA_BRCA_TIME_COLUMN_MAP: dict[str, str] = {
    "age_at_index": "age_at_sample",
    "days_to_diagnosis": "years_since_diagnosis",  # converted to years in extractor
    "days_to_collection": "days_since_sample_collection",
    "days_to_death": "survival_days",
    "days_to_last_follow_up": "survival_days",
    "days_since_last_visit": "time_since_last_visit",
}

# Columns that must never appear in clinical inputs (labels only).
LABEL_SOURCE_COLUMNS: frozenset[str] = frozenset(
    {
        "ajcc_pathologic_tumor_stage",
        "sample_type",
        "diagnosis",
        "cdr_score",
        "das28_score",
        "hba1c_percent",
        "severity_proxy",
    }
)


def extract_clinical_time_features(
    raw_clinical: Mapping[str, Any],
    column_map: Mapping[str, str] | None = None,
) -> dict[str, float | None]:
    """Map cohort-specific clinical columns to canonical time tabular features.

    Missing or non-numeric values return None so callers can impute or mask.
    """
    column_map = column_map or TCGA_BRCA_TIME_COLUMN_MAP
    out: dict[str, float | None] = {name: None for name in CLINICAL_TIME_FEATURES}

    for source_col, canonical in column_map.items():
        if source_col not in raw_clinical:
            continue
        value = _to_float(raw_clinical[source_col])
        if value is None:
            continue

        if canonical == "years_since_diagnosis" and source_col == "days_to_diagnosis":
            value = value / 365.25
        elif canonical == "survival_days" and source_col == "days_to_last_follow_up":
            # Prefer explicit death time when both are present.
            if out["survival_days"] is not None:
                continue

        out[canonical] = value

    return out


def clinical_time_vector(
    raw_clinical: Mapping[str, Any],
    column_map: Mapping[str, str] | None = None,
    fill_value: float = 0.0,
) -> np.ndarray:
    """Return a fixed-order vector of canonical time features."""
    features = extract_clinical_time_features(raw_clinical, column_map=column_map)
    return np.array(
        [features[name] if features[name] is not None else fill_value for name in CLINICAL_TIME_FEATURES],
        dtype=np.float64,
    )


def fit_zscore_stats(
    feature_matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute per-feature mean and std on the training partition only."""
    mean = np.nanmean(feature_matrix, axis=0)
    std = np.nanstd(feature_matrix, axis=0)
    std = np.where(std < 1e-8, 1.0, std)
    return mean, std


def apply_zscore(
    feature_matrix: np.ndarray,
    mean: Sequence[float] | np.ndarray,
    std: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Apply train-fitted Z-score normalization."""
    mean_arr = np.asarray(mean, dtype=np.float64)
    std_arr = np.asarray(std, dtype=np.float64)
    return (feature_matrix - mean_arr) / std_arr


# Aliases used by package exports.
zscore_fit = fit_zscore_stats
zscore_transform = apply_zscore


class ClinicalTimeFeatureExtractor:
    """Thin wrapper around canonical time feature extraction and Z-scoring."""

    def __init__(self, column_map: Mapping[str, str] | None = None) -> None:
        self.column_map = column_map or TCGA_BRCA_TIME_COLUMN_MAP
        self._mean: np.ndarray | None = None
        self._std: np.ndarray | None = None

    def extract(self, raw_clinical: Mapping[str, Any]) -> dict[str, float | None]:
        return extract_clinical_time_features(raw_clinical, column_map=self.column_map)

    def vector(self, raw_clinical: Mapping[str, Any], fill_value: float = 0.0) -> np.ndarray:
        return clinical_time_vector(raw_clinical, column_map=self.column_map, fill_value=fill_value)

    def fit(self, feature_matrix: np.ndarray) -> ClinicalTimeFeatureExtractor:
        self._mean, self._std = fit_zscore_stats(feature_matrix)
        return self

    def transform(self, feature_matrix: np.ndarray) -> np.ndarray:
        if self._mean is None or self._std is None:
            raise RuntimeError("Call fit() on training data before transform().")
        return apply_zscore(feature_matrix, self._mean, self._std)


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (float, int, np.floating, np.integer)):
        if np.isnan(float(value)):
            return None
        return float(value)
    text = str(value).strip()
    if not text or text.lower() in {"na", "nan", "none", "[not available]"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None
