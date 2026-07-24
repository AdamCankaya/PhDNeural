# Plan 19: Build interactive `streamlit` interface.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [372](https://github.com/AdamCankaya/PhDNeural/issues/372) |
| Title | [Y3 Q4 Winter 2028] Build interactive `streamlit` interface. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/372 |
| Labels | `phd-sync, thesis-deliverable, year-3, phase-4, step-1, q4-2028` |
| Year / Quarter | 3 - Spatio-Temporal Interpretability and Clinical Interface / Q4 Winter 2028 - The Trajectory Dashboard Application |
| Phase | 4 - Thesis Synthesis & Final Deliverables |
| Master-plan goal | Build an interactive clinical trajectory interface. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** Streamlit app loading model outputs and patient trajectories.
- [ ] **Acceptance:** local demo runbook; auth/PII constraints documented.
- [ ] **Upstream deps satisfied:** inference artifacts; holdout demo cohort.


## Approach

Build Streamlit app shell that loads inference artifacts and patient trajectories, with a Track A vs
Track B toggle. Document local demo runbook and auth/PII constraints. Plotting of risk curves and
attribution snippets is owned by plan 20 (may land stubs/hooks here only).

## Key files / areas to touch

- `apps/trajectory_dashboard/` or `src/app/` Streamlit entry (new)
- demo runbook in `docs/wiki/`
- inference artifact loader

## Dependencies on other plans

- `14-issue-367-holdout-trajectory-evaluation.md` (#367)

## Out of scope / owned by other plans

- Risk curve / forecast plots → plan 20 (#373)
- Attribution snippet embedding → plans 17–18 (#370–#371)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> local demo runbook; auth/PII constraints documented.

Plus: linked PR(s) reference this plan path and issue #372; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After holdout inference artifacts exist; can stub before #373 plots.

Recommended roadmap position: **19 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
