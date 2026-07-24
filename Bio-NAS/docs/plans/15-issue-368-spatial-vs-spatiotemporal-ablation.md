# Plan 15: Ablation study: Spatial vs. Spatio-Temporal predictive gain.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [368](https://github.com/AdamCankaya/PhDNeural/issues/368) |
| Title | [Y2 Q2 Summer 2028] Ablation study: Spatial vs. Spatio-Temporal predictive gain. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/368 |
| Labels | `phd-sync, year-2, phase-3, scaling, step-1, q2-2028` |
| Year / Quarter | 2 - Spatio-Temporal NAS Execution & Multi-Task Forecasting / Q2 Summer 2028 - Structural Taxonomy & Baseline Benchmarking |
| Phase | 3 - Scaling to the Comparative Matrix |
| Master-plan goal | Benchmark searched architectures against baselines and ablations. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** controlled ablation comparing spatial-only vs full spatio-temporal models.
- [ ] **Acceptance:** same data splits/seeds; delta metrics documented with interpretation.
- [ ] **Upstream deps satisfied:** spatial and temporal modules; evaluation harness.


## Approach

Run controlled ablations: spatial-only vs full spatio-temporal models for Track A and Track B where
applicable, same splits/seeds as plan 14. Document delta metrics and interpretation. Reuse the
evaluation harness from plan 14; do not reimplement holdout locking.

## Key files / areas to touch

- `src/pipelines/eval_ablation.py` (new)
- `src/models/spatial/`
- `src/models/temporal/`
- reuse eval harness from plan 14

## Dependencies on other plans

- `10-issue-363-spatial-cnn-transformer-modules.md` (#363)
- `11-issue-364-temporal-progression-modules.md` (#364)
- `14-issue-367-holdout-trajectory-evaluation.md` (#367)

## Out of scope / owned by other plans

- Shared holdout eval harness → plan 14 (#367)
- Spatial / temporal module implementations → plans 10–11 (#363–#364)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> same data splits/seeds; delta metrics documented with interpretation.

Plus: linked PR(s) reference this plan path and issue #368; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After eval harness exists; shares seeds/splits with #367.

Recommended roadmap position: **15 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
