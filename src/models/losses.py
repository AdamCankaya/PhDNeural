"""Static MTL loss functions: phenotype BCE + ordinal severity with masking."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class PhenotypeBCELoss(nn.Module):
    """Binary cross-entropy for Healthy (0) vs. Diseased (1)."""

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        return F.binary_cross_entropy_with_logits(logits, targets.float())


class OrdinalSeverityLoss(nn.Module):
    """Cumulative-link style ordinal log-loss over K ordered severity classes.

    Uses K-1 binary subtasks: P(Y > k) for k in 0..K-2.
    Samples with severity == -1 are masked out.
    """

    def __init__(self, n_severity_classes: int) -> None:
        super().__init__()
        if n_severity_classes < 2:
            raise ValueError("n_severity_classes must be >= 2 for ordinal loss")
        self.n_severity_classes = n_severity_classes

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        mask = targets >= 0
        if not mask.any():
            return logits.new_zeros(())

        logits = logits[mask]
        targets = targets[mask].long()

        k_minus_1 = self.n_severity_classes - 1
        cumulative_targets = torch.stack(
            [(targets > k).float() for k in range(k_minus_1)],
            dim=1,
        )
        cumulative_logits = logits[:, :k_minus_1]
        return F.binary_cross_entropy_with_logits(cumulative_logits, cumulative_targets)


class StaticMtlLoss(nn.Module):
    """Weighted sum of phenotype BCE and masked ordinal severity loss."""

    def __init__(
        self,
        n_severity_classes: int,
        w_phenotype: float = 0.5,
        w_severity: float = 0.5,
    ) -> None:
        super().__init__()
        self.w_phenotype = w_phenotype
        self.w_severity = w_severity
        self.phenotype_loss = PhenotypeBCELoss()
        self.severity_loss = OrdinalSeverityLoss(n_severity_classes)

    def forward(
        self,
        outputs: dict[str, torch.Tensor],
        labels: dict[str, torch.Tensor],
    ) -> dict[str, torch.Tensor]:
        loss_phenotype = self.phenotype_loss(outputs["phenotype"], labels["phenotype"])
        loss_severity = self.severity_loss(outputs["severity"], labels["severity"])
        total = self.w_phenotype * loss_phenotype + self.w_severity * loss_severity
        return {
            "total": total,
            "phenotype": loss_phenotype,
            "severity": loss_severity,
        }
