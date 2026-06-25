"""Abstract multi-omic dataset with uniform Static MTL label contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import Dataset


class FusionMode(str, Enum):
    """How samples are returned from __getitem__."""

    EARLY = "early"  # Stage 1: single concatenated tensor
    LATE = "late"  # Stage 2: dict of per-modality tensors


class BaseMultiOmicDataset(Dataset, ABC):
    """Shared dataset contract for all disease pipelines.

    Every cohort returns:
        {
            "features": Tensor | dict[str, Tensor],  # omic + clinical (no severity label)
            "labels": {
                "phenotype": int,            # 0 = Healthy, 1 = Diseased
                "severity": int,             # 0..K-1 ordinal; -1 = masked
            },
        }

    Severity/stage source columns must not appear in clinical inputs.
    """

    MODALITIES: tuple[str, ...] = ("methylation", "transcriptomics", "genomics", "cnv", "clinical")

    def __init__(
        self,
        hdf5_path: Path | str,
        fusion_mode: FusionMode = FusionMode.EARLY,
        split: str = "train",
    ) -> None:
        self.hdf5_path = Path(hdf5_path)
        self.fusion_mode = fusion_mode
        self.split = split
        self._sample_ids: list[str] = []

    @property
    @abstractmethod
    def disease_id(self) -> str:
        """Registry key (e.g. ``brca``, ``alzheimers``)."""

    @property
    @abstractmethod
    def n_severity_classes(self) -> int:
        """Ordinal severity cardinality K for this disease track."""

    def __len__(self) -> int:
        return len(self._sample_ids)

    @abstractmethod
    def __getitem__(self, index: int) -> dict[str, Any]:
        ...

    def _concat_early(self, modalities: dict[str, torch.Tensor]) -> torch.Tensor:
        """Stage 1: concatenate all modality tensors along feature dimension."""
        ordered = [modalities[m] for m in self.MODALITIES if m in modalities]
        return torch.cat(ordered, dim=-1)

    def _pack_late(self, modalities: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        """Stage 2: return isolated modality tensors."""
        return {m: modalities[m] for m in self.MODALITIES if m in modalities}

    @staticmethod
    def uniform_labels(phenotype: int, severity: int) -> dict[str, int]:
        """Build the canonical label dict shared across diseases."""
        return {"phenotype": int(phenotype), "severity": int(severity)}
