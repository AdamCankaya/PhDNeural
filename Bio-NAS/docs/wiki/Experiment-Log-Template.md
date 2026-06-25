# Experiment Log Template

Use this template to record reproducible experiments. Copy the table into a lab notebook, issue comment, or local log file.

## Run record

| Field | Value |
|-------|-------|
| **Date** | YYYY-MM-DD |
| **Linked issue** | [#NNN](https://github.com/AdamCankaya/PhDNeural/issues/NNN) or sync-id |
| **Commit** | `abc1234` (short SHA) |
| **Split version** | e.g. `brca-80-20-v1`, seed, holdout patient IDs hash |
| **Stage** | Stage 1 early fusion / Stage 2 OOF / baseline |
| **Optuna study** | Study name + storage URL (PostgreSQL) |
| **Model config** | Architecture, hyperparameters, loss weights |

## Holdout metrics (required for baseline runs)

| Metric | Phenotype | Severity |
|--------|-----------|----------|
| **Primary metric** | e.g. AUROC | e.g. ordinal accuracy / QWK |
| **Value** | | |
| **95% CI** | optional | optional |
| **Classical baseline delta** | vs. XGBoost/LightGBM/ElasticNet | |

## Training details

| Field | Value |
|-------|-------|
| Train pool size | |
| Holdout size | |
| Fold scheme | 5-fold stratified on phenotype (if CV) |
| Epochs / early stopping | |
| Hardware | e.g. Slurm partition, GPU type |

## Notes

Free-form observations: data quirks, failed trials, leakage checks, links to artifacts (checkpoints, plots).

---

## Example entry

| Field | Value |
|-------|-------|
| Date | 2027-04-15 |
| Linked issue | #42 — Stage 1 Optuna verification |
| Commit | `a1b2c3d` |
| Split version | `brca-80-20-v1` |
| Optuna study | `brca-stage1-v0` @ Hetzner PostgreSQL |
| Phenotype holdout AUROC | 0.91 |
| Severity holdout QWK | 0.68 |
| Notes | First successful parallel worker log; 20 trials completed |

## Related pages

- [Workflow](Workflow) — link experiments to closed issues
- [Static MTL Baseline](Static-MTL-Baseline) — metric definitions
- [FAQ and Troubleshooting](FAQ-and-Troubleshooting)
