"""Post-thesis optional extension: Cox-PH prognostic head.

NOT wired into the Static MTL baseline. Survival duration (``survival_days``)
remains a tabular clinical input in the comparative baseline; this module is a
placeholder for future prognostic survival modeling after thesis validation.
"""

from __future__ import annotations

import torch
import torch.nn as nn

# TODO (post-thesis):
#   - Implement Cox partial likelihood loss
#   - Add prognostic_head to a separate PrognosticMtlModel subclass
#   - Extend stacking to 4 experts × 3 tasks = 12 meta-features
#   - Expose prognostic timeline outputs in Streamlit

PROGNOSTIC_HEAD_NAME = "prognostic"


class CoxPrognosticHead(nn.Module):
    """Linear risk score head for Cox-PH survival modeling (extension stub)."""

    def __init__(self, latent_dim: int) -> None:
        super().__init__()
        self.risk_head = nn.Linear(latent_dim, 1)

    def forward(self, latent: torch.Tensor) -> torch.Tensor:
        return self.risk_head(latent).squeeze(-1)
