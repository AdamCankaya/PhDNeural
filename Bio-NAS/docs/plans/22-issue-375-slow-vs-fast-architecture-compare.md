# Plan 22: Compare slow-progressing vs. fast-acting condition architectures.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [375](https://github.com/AdamCankaya/PhDNeural/issues/375) |
| Title | [Y3 Q1 Spring 2029] Compare slow-progressing vs. fast-acting condition architectures. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/375 |
| Labels | `phd-sync, thesis-deliverable, year-3, phase-4, step-1, q1-2029` |
| Year / Quarter | 3 - Spatio-Temporal Interpretability and Clinical Interface / Q1 Spring 2029 - Thesis Synthesis and Framework Release |
| Phase | 4 - Thesis Synthesis & Final Deliverables |
| Master-plan goal | Document discovery and prepare framework release notes. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** comparative analysis contrasting architecture preferences across disease tempos.
- [ ] **Acceptance:** quantitative table + qualitative discussion ready for thesis inclusion.
- [ ] **Upstream deps satisfied:** multi-disease study results (Phases 3-4).


## Approach

Compare architecture preferences for slow-progressing vs fast-acting conditions (Other 4 when gate
passes; else BRCA tempo analysis only). Produce quantitative table + qualitative discussion ready
for thesis inclusion. Depends on taxonomy framing from plan 21 and experiment logs from Year 2–3.

## Key files / areas to touch

- `docs/thesis/tempo_architecture_compare.md` (new)
- multi-disease study logs (post-gate) or BRCA fallback

## Dependencies on other plans

- `21-issue-374-structural-taxonomy-docs.md` (#374)

## Out of scope / owned by other plans

- Taxonomy chapter draft → plan 21 (#374)
- Scaling-gate evidence from plans 14–16 (#367–#369)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> quantitative table + qualitative discussion ready for thesis inclusion.

Plus: linked PR(s) reference this plan path and issue #375; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After taxonomy draft framing; feeds dissertation.

Recommended roadmap position: **22 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
