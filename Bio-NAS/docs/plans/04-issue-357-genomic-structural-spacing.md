# Plan 04: Define genomic structural spacing.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [357](https://github.com/AdamCankaya/PhDNeural/issues/357) |
| Title | [Y1 Q4 Winter 2026] Define genomic structural spacing. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/357 |
| Labels | `phd-sync, year-1, brca-anchor, phase-1, step-1, q4-2026` |
| Year / Quarter | 1 - Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure / Q4 Winter 2026 - Spatio-Temporal Data Modalities |
| Phase | 1 - The Anchor (BRCA PoC) |
| Master-plan goal | Map spatial and temporal feature dimensions for multi-omic tensors. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** spacing/binning rules (bp windows, CpG neighborhood, chromosome boundaries) used by spatial modules.
- [ ] **Acceptance:** reproducible spacing config checked into repo with unit tests for edge cases (chromosome ends, missing coords).
- [ ] **Upstream deps satisfied:** reference genome build documented (e.g., GRCh38).


## Approach

Implement reproducible spacing/binning rules (bp windows, CpG neighborhood, chromosome boundaries)
as a checked-in config (e.g. `src/config/genomic_spacing.yaml`) plus pure helper functions under
`src/data/` (or `src/models/spatial/`) with unit tests for chromosome ends and missing coordinates.
Pin reference genome build (GRCh38) in docs. This config is the shared foundation for Track A/B
spatial modules in plan 10 — do not implement 1D-CNN/Transformer here.

## Key files / areas to touch

- `src/config/genomic_spacing.yaml` (new)
- `src/data/` or `src/models/spatial/` spacing helpers (new)
- `tests/` spacing edge-case unit tests (new)

## Dependencies on other plans

- `03-issue-356-spatial-temporal-feature-map.md` (#356)

## Out of scope / owned by other plans

- High-level spatial/temporal feature map spec → plan 03 (#356)
- 1D-CNN / Spatial Transformer modules → plan 10 (#363)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> reproducible spacing config checked into repo with unit tests for edge cases (chromosome ends, missing coords).

Plus: linked PR(s) reference this plan path and issue #357; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After feature-map axes are named; required before spatial NAS modules.

Recommended roadmap position: **04 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
