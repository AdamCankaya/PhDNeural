# Plan 24: Release the complete open-source Python framework.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [377](https://github.com/AdamCankaya/PhDNeural/issues/377) |
| Title | [Y3 Q2 Summer 2029] Release the complete open-source Python framework. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/377 |
| Labels | `phd-sync, thesis-deliverable, year-3, phase-4, step-1, q2-2029` |
| Year / Quarter | 3 - Spatio-Temporal Interpretability and Clinical Interface / Q2 Summer 2029 - Thesis Defense |
| Phase | 4 - Thesis Synthesis & Final Deliverables |
| Master-plan goal | Finalize dissertation and release the open-source framework. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** tagged release, install docs, example notebooks, license/citation.
- [ ] **Acceptance:** clean clone → install → smoke demo on public sample data.
- [ ] **Upstream deps satisfied:** stable `src/` APIs; CI green on main.


## Approach

Tag a complete open-source Python framework release: install docs, example notebooks, license/citation,
Track A and Track B tooling for BRCA (Other 4 configs as available). Acceptance: clean clone → install →
smoke demo on public sample data; CI green on main. Builds on stable `src/` APIs and env/Postgres
foundations from Year 1 infra plans.

## Key files / areas to touch

- `README.md`
- example notebooks (new)
- GitHub Release / tag + CI workflows under `.github/`
- `LICENSE` / CITATION

## Dependencies on other plans

- `08-issue-361-compute-stack-provisioning.md` (#361)
- `09-issue-362-dockerized-postgres-optuna.md` (#362)
- `23-issue-376-finalize-dissertation.md` (#376)

## Out of scope / owned by other plans

- Dissertation content → plan 23 (#376)
- Stable env/Postgres foundations → plans 08–09 (#361–#362)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> clean clone → install → smoke demo on public sample data.

Plus: linked PR(s) reference this plan path and issue #377; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

Final engineering deliverable; after APIs stable and thesis content frozen enough to cite.

Recommended roadmap position: **24 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
