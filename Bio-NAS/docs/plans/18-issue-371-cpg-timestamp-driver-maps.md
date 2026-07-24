# Plan 18: Extract maps identifying CpG sites and timestamps driving disease progression predictions.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [371](https://github.com/AdamCankaya/PhDNeural/issues/371) |
| Title | [Y3 Q3 Fall 2028] Extract maps identifying CpG sites and timestamps driving disease progression predictions. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/371 |
| Labels | `phd-sync, thesis-deliverable, year-3, phase-4, step-1, q3-2028` |
| Year / Quarter | 3 - Spatio-Temporal Interpretability and Clinical Interface / Q3 Fall 2028 - Spatio-Temporal Interpretability |
| Phase | 4 - Thesis Synthesis & Final Deliverables |
| Master-plan goal | Attribute predictions to spatial sites and timepoints. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** ranked site/time maps + export (CSV/Parquet) and summary figures.
- [ ] **Acceptance:** top-k drivers reviewable per disease trajectory example.
- [ ] **Upstream deps satisfied:** attribution pipeline; genomic annotations.


## Approach

Consume attribution tensors from plan 17; join genomic annotations from plans 03–04 to produce ranked
CpG/site and timestamp driver maps (CSV/Parquet + summary figures). Include Track B biological
plausibility note against pathway priors. Top-k drivers must be reviewable per trajectory example.

## Key files / areas to touch

- `src/interpretability/driver_maps.py` (new)
- annotation joins from feature map / spacing configs
- export + figure scripts under `scripts/` or `docs/figures/`

## Dependencies on other plans

- `03-issue-356-spatial-temporal-feature-map.md` (#356)
- `04-issue-357-genomic-structural-spacing.md` (#357)
- `17-issue-370-multidim-attribution-pipeline.md` (#370)

## Out of scope / owned by other plans

- Attribution tensor API → plan 17 (#370)
- Genomic coordinate annotations from plans 03–04 (#356–#357)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> top-k drivers reviewable per disease trajectory example.

Plus: linked PR(s) reference this plan path and issue #371; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

Directly after attribution API lands.

Recommended roadmap position: **18 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
