"""Stage 1 Early Fusion model: concatenation + MLP trunk + three MTL heads."""

from __future__ import annotations

import torch
import torch.nn as nn


class BrcaEarlyFusionModel(nn.Module):
    """Early fusion baseline for BRCA multi-omic multi-task learning.

    Architecture:
        1. Accept concatenated input X_fused (Stage 1 flat tensor from dataset)
        2. MLP trunk maps fused features to a dense latent vector
        3. Three independent heads:
           - Diagnostic: BCE (tumor vs. normal)
           - Staging: ordinal logits (stages I–IV)
           - Prognostic: Cox-PH risk score

    TODO:
        - Wire trunk depth/width to Optuna search space
        - Implement forward() with torch.cat on modality inputs if dict passed
        - Return dict of head outputs for multi-task loss computation
        - Add survival loss helper for Cox-PH head
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: tuple[int, ...] = (512, 256),
        latent_dim: int = 128,
        n_stages: int = 4,
    ) -> None:
        super().__init__()
        layers: list[nn.Module] = []
        prev = input_dim
        for hidden in hidden_dims:
            layers.extend([nn.Linear(prev, hidden), nn.ReLU(), nn.Dropout(0.2)])
            prev = hidden
        layers.append(nn.Linear(prev, latent_dim))
        self.trunk = nn.Sequential(*layers)

        self.diagnostic_head = nn.Linear(latent_dim, 1)
        self.staging_head = nn.Linear(latent_dim, n_stages)
        self.prognostic_head = nn.Linear(latent_dim, 1)

    def forward(self, x_fused: torch.Tensor) -> dict[str, torch.Tensor]:
        latent = self.trunk(x_fused)
        return {
            "diagnostic": self.diagnostic_head(latent).squeeze(-1),
            "staging": self.staging_head(latent),
            "prognostic": self.prognostic_head(latent).squeeze(-1),
        }
