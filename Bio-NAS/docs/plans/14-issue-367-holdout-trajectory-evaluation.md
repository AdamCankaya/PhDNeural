# Plan 14: Evaluate architectures on 20% holdout trajectories.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [367](https://github.com/AdamCankaya/PhDNeural/issues/367) |
| Title | [Y2 Q2 Summer 2028] Evaluate architectures on 20% holdout trajectories. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/367 |
| Labels | `phd-sync, year-2, phase-3, scaling, step-1, q2-2028` |
| Year / Quarter | 2 - Spatio-Temporal NAS Execution & Multi-Task Forecasting / Q2 Summer 2028 - Structural Taxonomy & Baseline Benchmarking |
| Phase | 3 - Scaling to the Comparative Matrix |
| Master-plan goal | Benchmark searched architectures against baselines and ablations. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** holdout evaluation script + metrics table for best NAS architectures.
- [ ] **Acceptance:** metrics published for frozen holdout only; confidence intervals or bootstrap noted.
- [ ] **Upstream deps satisfied:** completed Optuna studies; locked holdout split.


## Approach

Build holdout evaluation script that loads frozen best Track A and Track B architectures, scores only
the locked 20% patient holdout from plan 05, and emits a metrics table with CI/bootstrap notes plus
Track A vs B delta (scaling-gate evidence). Never refit on holdout. Store results under experiment logs
using `docs/wiki/Experiment-Log-Template.md`.

## Key files / areas to touch

- `src/pipelines/eval_holdout.py` (new)
- `docs/wiki/Experiment-Log-Template.md`
- `data/splits/` locked manifests

## Dependencies on other plans

- `05-issue-358-patient-level-holdout-split.md` (#358)
- `12-issue-365-causal-cv-architecture-search.md` (#365)

## Out of scope / owned by other plans

- Locked patient split → plan 05 (#358)
- Ablation study design → plan 15 (#368)
- Classical RF/XGBoost baselines → plan 16 (#369)
- Attribution / dashboard → plans 17–20 (#370–#373)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> metrics published for frozen holdout only; confidence intervals or bootstrap noted.

Plus: linked PR(s) reference this plan path and issue #367; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After best trials exist; produces scaling-gate evidence for Year 3 Other-4 work.

Recommended roadmap position: **14 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
