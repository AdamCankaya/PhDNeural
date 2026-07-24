# Plan 23: Finalize dissertation.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [376](https://github.com/AdamCankaya/PhDNeural/issues/376) |
| Title | [Y3 Q2 Summer 2029] Finalize dissertation. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/376 |
| Labels | `phd-sync, thesis-deliverable, year-3, phase-4, step-1, q2-2029` |
| Year / Quarter | 3 - Spatio-Temporal Interpretability and Clinical Interface / Q2 Summer 2029 - Thesis Defense |
| Phase | 4 - Thesis Synthesis & Final Deliverables |
| Master-plan goal | Finalize dissertation and release the open-source framework. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** defense draft, slides, and response-to-committee checklist.
- [ ] **Acceptance:** committee-ready PDF; all chapters cite frozen experiment IDs.
- [ ] **Upstream deps satisfied:** synthesis documents; completed experiments.


## Approach

Finalize dissertation: defense draft, slides, response-to-committee checklist. All chapters cite
frozen experiment IDs from prior plans. Reports BRCA dual-track result and any Other 4 extensions.
OSS packaging is plan 24 — keep release mechanics out of this plan.

## Key files / areas to touch

- thesis/defense artifacts under `docs/thesis/` (new)
- experiment ID index linking to Optuna studies

## Dependencies on other plans

- `21-issue-374-structural-taxonomy-docs.md` (#374)
- `22-issue-375-slow-vs-fast-architecture-compare.md` (#375)

## Out of scope / owned by other plans

- Taxonomy & tempo analysis → plans 21–22 (#374–#375)
- OSS release tagging / install docs → plan 24 (#377)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> committee-ready PDF; all chapters cite frozen experiment IDs.

Plus: linked PR(s) reference this plan path and issue #376; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

Near end; consolidates all experiment-backed chapters.

Recommended roadmap position: **23 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
