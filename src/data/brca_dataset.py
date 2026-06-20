"""TCGA-BRCA PyTorch Dataset with Stage 1 / Stage 2 output modes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import torch

from src.data.base_multiomic_dataset import BaseMultiOmicDataset, FusionMode
from src.data.clinical_time import (
    CLINICAL_STATIC_FEATURES,
    CLINICAL_TIME_FEATURES,
    LABEL_SOURCE_COLUMNS,
    TCGA_BRCA_TIME_COLUMN_MAP,
    apply_zscore,
    clinical_time_vector,
    extract_clinical_time_features,
    fit_zscore_stats,
)

# Re-export for callers that import from brca_dataset.
LABEL_FIELDS: tuple[str, ...] = ("phenotype", "severity")


class BrcaMultiOmicDataset(BaseMultiOmicDataset):
    """Load BRCA multi-omic features from HDF5 with leakage-safe preprocessing.

    Stage 1 (Early Fusion):
        Return a single flattened tensor
        X_fused = [methylation | transcriptomics | genomics | cnv | clinical].

    Stage 2 (Late Fusion):
        Return a dict of independent modality tensors for expert networks.

    Clinical inputs include Z-scored time tabular features only—severity/stage
    source columns are labels, never concatenated into the clinical branch.

    TODO:
        - Read Methylation, RNA-Seq, CNV, Somatic Mutation, Clinical from HDF5
        - Apply variance masks computed on 80% train partition only (top 10k CpGs)
        - Fit Z-score stats on train partition for clinical time + static features
        - Map TCGA labels via disease_registry.yaml phenotype/severity mappings
    """

    def __init__(
        self,
        hdf5_path: Path | str,
        fusion_mode: FusionMode = FusionMode.EARLY,
        split: str = "train",
        time_zscore_mean: torch.Tensor | None = None,
        time_zscore_std: torch.Tensor | None = None,
    ) -> None:
        super().__init__(hdf5_path=hdf5_path, fusion_mode=fusion_mode, split=split)
        self.time_zscore_mean = time_zscore_mean
        self.time_zscore_std = time_zscore_std
        # TODO: load sample IDs, feature indices, and labels for split

    @property
    def disease_id(self) -> str:
        return "brca"

    @property
    def n_severity_classes(self) -> int:
        return 4

    def __getitem__(self, index: int) -> dict[str, Any]:
        # TODO: load raw modality arrays for self._sample_ids[index]
        raise NotImplementedError("HDF5 loading not yet implemented")

    def _extract_clinical_time_features(
        self,
        raw_clinical: Mapping[str, Any],
    ) -> dict[str, float | None]:
        """Map TCGA clinical columns to canonical time tabular features."""
        return extract_clinical_time_features(
            raw_clinical,
            column_map=TCGA_BRCA_TIME_COLUMN_MAP,
        )

    def _build_clinical_tensor(
        self,
        raw_clinical: Mapping[str, Any],
    ) -> torch.Tensor:
        """Assemble clinical branch without severity/stage leakage."""
        for col in LABEL_SOURCE_COLUMNS:
            if col in raw_clinical:
                # Severity and phenotype source columns are labels only.
                pass

        time_vec = clinical_time_vector(raw_clinical, column_map=TCGA_BRCA_TIME_COLUMN_MAP)
        if self.time_zscore_mean is not None and self.time_zscore_std is not None:
            time_vec = apply_zscore(
                time_vec.reshape(1, -1),
                self.time_zscore_mean.numpy(),
                self.time_zscore_std.numpy(),
            ).reshape(-1)

        # TODO: append one-hot / Z-scored CLINICAL_STATIC_FEATURES (sex, ethnicity, etc.)
        _ = CLINICAL_STATIC_FEATURES
        return torch.tensor(time_vec, dtype=torch.float32)

    @staticmethod
    def fit_time_zscore(train_time_matrix) -> tuple[torch.Tensor, torch.Tensor]:
        """Fit Z-score stats on training partition time features only."""
        mean, std = fit_zscore_stats(train_time_matrix)
        return torch.tensor(mean, dtype=torch.float32), torch.tensor(std, dtype=torch.float32)

    def _pack_sample(
        self,
        modalities: dict[str, torch.Tensor],
        phenotype: int,
        severity: int,
    ) -> dict[str, Any]:
        """Return uniform Static MTL sample dict."""
        if self.fusion_mode == FusionMode.EARLY:
            features: torch.Tensor | dict[str, torch.Tensor] = self._concat_early(modalities)
        else:
            features = self._pack_late(modalities)

        return {
            "features": features,
            "labels": self.uniform_labels(phenotype=phenotype, severity=severity),
        }


__all__ = [
    "BrcaMultiOmicDataset",
    "FusionMode",
    "CLINICAL_TIME_FEATURES",
    "CLINICAL_STATIC_FEATURES",
    "LABEL_FIELDS",
]
