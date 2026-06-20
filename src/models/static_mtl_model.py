"""Shared Static MTL trunk and two-task heads for all disease pipelines."""

from __future__ import annotations

import torch
import torch.nn as nn


class StaticMtlModel(nn.Module):
    """MLP trunk with phenotype (BCE) and severity (ordinal) heads.

    The same topology is reused across diseases; only ``n_severity_classes`` (K)
    and label mappings differ per cohort (see disease_registry.yaml).
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dims: tuple[int, ...] = (512, 256),
        latent_dim: int = 128,
        n_severity_classes: int = 4,
        dropout: float = 0.2,
    ) -> None:
        super().__init__()
        self.n_severity_classes = n_severity_classes

        layers: list[nn.Module] = []
        prev = input_dim
        for hidden in hidden_dims:
            layers.extend([nn.Linear(prev, hidden), nn.ReLU(), nn.Dropout(dropout)])
            prev = hidden
        layers.append(nn.Linear(prev, latent_dim))
        self.trunk = nn.Sequential(*layers)

        self.phenotype_head = nn.Linear(latent_dim, 1)
        self.severity_head = nn.Linear(latent_dim, n_severity_classes)

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        latent = self.trunk(x)
        return {
            "phenotype": self.phenotype_head(latent).squeeze(-1),
            "severity": self.severity_head(latent),
        }
