# Plan 20: Render health trajectories and risk forecasting curves.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [373](https://github.com/AdamCankaya/PhDNeural/issues/373) |
| Title | [Y3 Q4 Winter 2028] Render health trajectories and risk forecasting curves. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/373 |
| Labels | `phd-sync, thesis-deliverable, year-3, phase-4, step-1, q4-2028` |
| Year / Quarter | 3 - Spatio-Temporal Interpretability and Clinical Interface / Q4 Winter 2028 - The Trajectory Dashboard Application |
| Phase | 4 - Thesis Synthesis & Final Deliverables |
| Master-plan goal | Build an interactive clinical trajectory interface. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** plots for observed vs predicted risk over time with uncertainty bands if available.
- [ ] **Acceptance:** at least one end-to-end patient view from load → forecast → attribution snippet.
- [ ] **Upstream deps satisfied:** Streamlit shell; attribution exports.


## Approach

Render observed vs predicted health trajectories and risk forecasting curves (uncertainty bands if
available) inside the Streamlit app from plan 19. Deliver at least one end-to-end patient view:
load → forecast → attribution snippet (using exports from plans 17–18).

## Key files / areas to touch

- Streamlit plotting components (extend plan 19 app)
- attribution export readers from plans 17–18

## Dependencies on other plans

- `18-issue-371-cpg-timestamp-driver-maps.md` (#371)
- `19-issue-372-streamlit-trajectory-shell.md` (#372)

## Out of scope / owned by other plans

- Streamlit app shell / auth notes → plan 19 (#372)
- Attribution exports → plans 17–18 (#370–#371)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> at least one end-to-end patient view from load → forecast → attribution snippet.

Plus: linked PR(s) reference this plan path and issue #373; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After Streamlit shell + attribution exports.

Recommended roadmap position: **20 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
