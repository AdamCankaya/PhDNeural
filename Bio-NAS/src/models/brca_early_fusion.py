"""Stage 1 Early Fusion model: concatenation + Static MTL two-head baseline."""

from __future__ import annotations

import torch

from src.models.static_mtl_model import StaticMtlModel


class StaticMtlEarlyFusionModel(StaticMtlModel):
    """Early fusion wrapper: accepts concatenated X_fused from Stage 1 dataset.

    Architecture:
        1. Accept concatenated input X_fused (flat tensor from dataset)
        2. MLP trunk maps fused features to a dense latent vector
        3. Two independent heads:
           - phenotype_head: BCE (Healthy vs. Diseased)
           - severity_head: ordinal logits (0..K-1)

    TODO:
        - Wire trunk depth/width to Optuna search space
        - Implement forward() with torch.cat on modality dict if dict passed
        - Connect StaticMtlLoss in training loop
    """

    def forward(self, x_fused: torch.Tensor) -> dict[str, torch.Tensor]:
        return super().forward(x_fused)


class BrcaEarlyFusionModel(StaticMtlEarlyFusionModel):
    """Backward-compatible alias for BRCA Stage 1 early fusion baseline."""

    def __init__(
        self,
        input_dim: int,
        hidden_dims: tuple[int, ...] = (512, 256),
        latent_dim: int = 128,
        n_severity_classes: int = 4,
        n_stages: int | None = None,
        dropout: float = 0.2,
    ) -> None:
        # n_stages kept for transitional call sites; prefer n_severity_classes.
        k = n_severity_classes if n_stages is None else n_stages
        super().__init__(
            input_dim=input_dim,
            hidden_dims=hidden_dims,
            latent_dim=latent_dim,
            n_severity_classes=k,
            dropout=dropout,
        )


def concat_modalities(modalities: dict[str, torch.Tensor], order: tuple[str, ...]) -> torch.Tensor:
    """Concatenate modality tensors in a fixed order (Stage 1 helper)."""
    return torch.cat([modalities[m] for m in order if m in modalities], dim=-1)
