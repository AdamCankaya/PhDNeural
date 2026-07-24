# Plan 07: Construct 4D tensors: (Batch, Time_Steps, Spatial_Features, Channels).

## Issue reference

| Field | Value |
|-------|-------|
| Number | [360](https://github.com/AdamCankaya/PhDNeural/issues/360) |
| Title | [Y1 Q1 Spring 2027] Construct 4D tensors: (Batch, Time_Steps, Spatial_Features, Channels). |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/360 |
| Labels | `phd-sync, year-1, abstraction, phase-2, step-1, q1-2027` |
| Year / Quarter | 1 - Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure / Q1 Spring 2027 - 4D Tensor Construction & Irregular Time-Step Normalization |
| Phase | 2 - Code Abstraction & Generalization |
| Master-plan goal | Construct a leakage-safe ETL pipeline producing irregular-time 4D tensors. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** HDF5 (or equivalent) writer/reader for `(B, T, S, C)` tensors plus metadata sidecars.
- [ ] **Acceptance:** round-trip equality tests; documented channel layout per omic.
- [ ] **Upstream deps satisfied:** feature map + Δt embedding from prior items.


## Approach

Complete HDF5 (or equivalent) writer/reader for `(B, T, S, C)` tensors plus metadata sidecars
(patient ID, visit times, Δt, channel legend). Finish the TODO HDF5 path in `src/data/brca_dataset.py`
and align with `docs/wiki/Data-Acquisition-BRCA.md`. Round-trip equality tests required.
Preserve Stage 1 flat-concat vs Stage 2 modality-dict modes already sketched in the dataset API;
4D spatio-temporal tensors are the NAS path while static MTL baseline remains compatible.

## Key files / areas to touch

- `src/data/brca_dataset.py` (HDF5 TODO)
- `docs/wiki/Data-Acquisition-BRCA.md`
- HDF5 writer utilities under `src/data/` (new)
- `tests/` round-trip tests (new)

## Dependencies on other plans

- `03-issue-356-spatial-temporal-feature-map.md` (#356)
- `04-issue-357-genomic-structural-spacing.md` (#357)
- `05-issue-358-patient-level-holdout-split.md` (#358)
- `06-issue-359-delta-t-embedding.md` (#359)

## Out of scope / owned by other plans

- Feature map & spacing → plans 03–04 (#356–#357)
- Split / leakage tests → plan 05 (#358)
- Δt embedding module API → plan 06 (#359)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> round-trip equality tests; documented channel layout per omic.

Plus: linked PR(s) reference this plan path and issue #360; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After feature map, spacing, split, and Δt contract; foundational artifact for Year 2.

Recommended roadmap position: **07 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
