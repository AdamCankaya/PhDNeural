"""TCGA-BRCA PyTorch Dataset with Stage 1 / Stage 2 output modes."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import Dataset


class FusionMode(str, Enum):
    """How samples are returned from __getitem__."""

    EARLY = "early"  # Stage 1: single concatenated tensor
    LATE = "late"  # Stage 2: dict of per-modality tensors


class BrcaMultiOmicDataset(Dataset):
    """Load BRCA multi-omic features from HDF5 with leakage-safe preprocessing.

    Stage 1 (Early Fusion):
        Return a single flattened tensor
        X_fused = [methylation | transcriptomics | genomics | cnv | clinical].

    Stage 2 (Late Fusion):
        Return a dict of independent modality tensors for expert networks.

    TODO:
        - Read Methylation, RNA-Seq, CNV, Somatic Mutation, Clinical from HDF5
        - Apply variance masks computed on 80% train partition only (top 10k CpGs)
        - Support fusion_mode switch via constructor argument
        - Attach diagnostic, staging, and prognostic labels per sample
    """

    MODALITIES = ("methylation", "transcriptomics", "genomics", "cnv", "clinical")

    def __init__(
        self,
        hdf5_path: Path | str,
        fusion_mode: FusionMode = FusionMode.EARLY,
        split: str = "train",
    ) -> None:
        self.hdf5_path = Path(hdf5_path)
        self.fusion_mode = fusion_mode
        self.split = split
        # TODO: load sample IDs, feature indices, and labels for split
        self._sample_ids: list[str] = []

    def __len__(self) -> int:
        return len(self._sample_ids)

    def __getitem__(self, index: int) -> dict[str, Any]:
        # TODO: load raw modality arrays for self._sample_ids[index]
        raise NotImplementedError("HDF5 loading not yet implemented")

    def _concat_early(self, modalities: dict[str, torch.Tensor]) -> torch.Tensor:
        """Stage 1: concatenate all modality tensors along feature dimension."""
        ordered = [modalities[m] for m in self.MODALITIES if m in modalities]
        return torch.cat(ordered, dim=-1)

    def _pack_late(self, modalities: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        """Stage 2: return isolated modality tensors."""
        return {m: modalities[m] for m in self.MODALITIES if m in modalities}
