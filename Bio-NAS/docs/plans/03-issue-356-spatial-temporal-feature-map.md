# Plan 03: Map spatial dimension (sequence coordinates, CpG sites) and temporal dimension (longitudinal intervals).

## Issue reference

| Field | Value |
|-------|-------|
| Number | [356](https://github.com/AdamCankaya/PhDNeural/issues/356) |
| Title | [Y1 Q4 Winter 2026] Map spatial dimension (sequence coordinates, CpG sites) and temporal dimension (longitudinal intervals). |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/356 |
| Labels | `phd-sync, year-1, brca-anchor, phase-1, step-1, q4-2026` |
| Year / Quarter | 1 - Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure / Q4 Winter 2026 - Spatio-Temporal Data Modalities |
| Phase | 1 - The Anchor (BRCA PoC) |
| Master-plan goal | Map spatial and temporal feature dimensions for multi-omic tensors. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** feature map spec covering spatial axes (genomic coordinates / CpG / gene indices) and temporal axes (visit index, calendar time, Δt).
- [ ] **Acceptance:** written mapping covering methylation, transcriptomics, and at least one additional omic modality.
- [ ] **Upstream deps satisfied:** Level-3 matrices or equivalent processed tables from Fall 2026 sourcing.


## Approach

Produce a feature-map specification covering spatial axes (genomic coordinates / CpG / gene indices)
and temporal axes (visit index, calendar time, Δt). BRCA-first; schema must generalize to Other 4.
Document channel layout expectations for methylation, transcriptomics, and ≥1 additional omic.
Store the spec in `docs/data/feature_map_spec.md` and mirror machine-readable axis names in
`src/config/` so plan 07 can implement HDF5 without re-deciding conventions.

## Key files / areas to touch

- `docs/data/feature_map_spec.md` (new)
- `src/config/` axis/channel constants (new or extend)
- `docs/wiki/Data-Acquisition-BRCA.md`

## Dependencies on other plans

- `01-issue-354-multi-disease-dataset-inventory.md` (#354)
- `02-issue-355-longitudinal-matching-strategy.md` (#355)

## Out of scope / owned by other plans

- bp / CpG neighborhood spacing config + edge-case tests → plan 04 (#357)
- HDF5 `(B,T,S,C)` writer/reader → plan 07 (#360)
- Δt PyTorch module → plan 06 (#359)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> written mapping covering methylation, transcriptomics, and at least one additional omic modality.

Plus: linked PR(s) reference this plan path and issue #356; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After sourcing docs exist; parallelizable with late #355 polish.

Recommended roadmap position: **03 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
