# Plan 12: Execute large-scale spatio-temporal architecture search with Causal Cross-Validation.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [365](https://github.com/AdamCankaya/PhDNeural/issues/365) |
| Title | [Y2 Q1 Spring 2028] Execute large-scale spatio-temporal architecture search with Causal Cross-Validation. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/365 |
| Labels | `phd-sync, year-2, phase-3, scaling, step-1, q1-2028` |
| Year / Quarter | 2 - Spatio-Temporal NAS Execution & Multi-Task Forecasting / Q1 Spring 2028 - Parallel Search Optimization |
| Phase | 3 - Scaling to the Comparative Matrix |
| Master-plan goal | Execute large-scale distributed spatio-temporal architecture search. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** Optuna study configs, causal CV splitter, trial metrics schema (loss, AUROC/C-index as applicable).
- [ ] **Acceptance:** ≥1 full study completes on BRCA (or primary cohort) with reproducible seed and stored best trial.
- [ ] **Upstream deps satisfied:** Postgres Optuna storage; Slurm workers; train tensors.


## Approach

Define Optuna study configs for BRCA Track A then Track B (distinct study names), causal CV splitter
compatible with patient-level splits, and trial metrics schema (Static MTL losses + AUROC / ordinal
metrics as applicable; C-index only if prognostic extension enabled later). Persist best trials to
Postgres. Reuse `PhenotypeBCELoss` / `OrdinalSeverityLoss` / `StaticMtlLoss` from `src/models/losses.py`.
Horizontal worker mechanics belong to plan 13 — this plan owns search space composition + study logic.

## Key files / areas to touch

- `src/pipelines/` Optuna study entrypoints (new/extend)
- `src/models/losses.py`
- `src/models/brca_early_fusion.py` (training loop patterns)
- study YAML/JSON configs (new)

## Dependencies on other plans

- `07-issue-360-four-d-tensor-hdf5.md` (#360)
- `09-issue-362-dockerized-postgres-optuna.md` (#362)
- `10-issue-363-spatial-cnn-transformer-modules.md` (#363)
- `11-issue-364-temporal-progression-modules.md` (#364)

## Out of scope / owned by other plans

- Postgres storage → plan 09 (#362)
- Slurm + HyperbandPruner wiring → plan 13 (#366)
- Holdout-only final metrics → plan 14 (#367)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> ≥1 full study completes on BRCA (or primary cohort) with reproducible seed and stored best trial.

Plus: linked PR(s) reference this plan path and issue #365; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After modules + Postgres; run Track A then Track B (or parallel distinct studies). Use plan 13 workers before large-scale runs.

Recommended roadmap position: **12 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
