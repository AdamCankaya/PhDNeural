# Plan 13: Use Horizontally Scaled Workers via Slurm and HyperbandPruner.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [366](https://github.com/AdamCankaya/PhDNeural/issues/366) |
| Title | [Y2 Q1 Spring 2028] Use Horizontally Scaled Workers via Slurm and HyperbandPruner. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/366 |
| Labels | `phd-sync, year-2, phase-3, scaling, step-1, q1-2028` |
| Year / Quarter | 2 - Spatio-Temporal NAS Execution & Multi-Task Forecasting / Q1 Spring 2028 - Parallel Search Optimization |
| Phase | 3 - Scaling to the Comparative Matrix |
| Master-plan goal | Execute large-scale distributed spatio-temporal architecture search. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** Slurm job templates; HyperbandPruner wired; worker scale-out runbook.
- [ ] **Acceptance:** ≥2 concurrent workers report trials to the same study without corruption.
- [ ] **Upstream deps satisfied:** cluster account; shared storage for artifacts.


## Approach

Author Slurm job templates and wire `HyperbandPruner` into Optuna workers. Document scale-out in the
infrastructure runbook. Acceptance: ≥2 concurrent workers report trials to the same study without
corruption. Shared artifact storage path defined. Complements plan 12 (study logic) and plan 09 (DB).

## Key files / areas to touch

- Slurm job templates under `scripts/slurm/` (new)
- `docs/wiki/Infrastructure-Runbook.md`
- Optuna HyperbandPruner wiring in worker entrypoint

## Dependencies on other plans

- `08-issue-361-compute-stack-provisioning.md` (#361)
- `09-issue-362-dockerized-postgres-optuna.md` (#362)

## Out of scope / owned by other plans

- Compute stack install → plan 08 (#361)
- Optuna study objective / causal CV logic → plan 12 (#365)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> ≥2 concurrent workers report trials to the same study without corruption.

Plus: linked PR(s) reference this plan path and issue #366; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

Infra enabler for #365; implement templates before or in lockstep with the first large study.

Recommended roadmap position: **13 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
