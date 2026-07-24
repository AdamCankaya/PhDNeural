# Plan 16: Compare with longitudinal Random Forests/XGBoost.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [369](https://github.com/AdamCankaya/PhDNeural/issues/369) |
| Title | [Y2 Q2 Summer 2028] Compare with longitudinal Random Forests/XGBoost. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/369 |
| Labels | `phd-sync, year-2, phase-3, scaling, step-1, q2-2028` |
| Year / Quarter | 2 - Spatio-Temporal NAS Execution & Multi-Task Forecasting / Q2 Summer 2028 - Structural Taxonomy & Baseline Benchmarking |
| Phase | 3 - Scaling to the Comparative Matrix |
| Master-plan goal | Benchmark searched architectures against baselines and ablations. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** classical baseline pipelines on comparable flattened/windowed features.
- [ ] **Acceptance:** baseline metrics on identical holdout; fair feature budget documented.
- [ ] **Upstream deps satisfied:** tabular feature export from tensors/metadata.


## Approach

Implement classical longitudinal baselines (Random Forest / XGBoost, optionally ElasticNet) on
flattened/windowed features exported from tensors/metadata with a documented fair feature budget.
Evaluate on the identical holdout as plan 14. These are track-agnostic external controls for the
scaling gate — not Optuna search trials.

## Key files / areas to touch

- `src/pipelines/baselines_longitudinal.py` (new)
- feature export helpers from HDF5 metadata
- identical holdout manifests from plan 05

## Dependencies on other plans

- `05-issue-358-patient-level-holdout-split.md` (#358)
- `07-issue-360-four-d-tensor-hdf5.md` (#360)
- `14-issue-367-holdout-trajectory-evaluation.md` (#367)

## Out of scope / owned by other plans

- Holdout split & NAS metrics → plans 05/14 (#358/#367)
- Tensor/feature export helpers from plan 07 (#360)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> baseline metrics on identical holdout; fair feature budget documented.

Plus: linked PR(s) reference this plan path and issue #369; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

Parallel with #368 once holdout + feature export available.

Recommended roadmap position: **16 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
