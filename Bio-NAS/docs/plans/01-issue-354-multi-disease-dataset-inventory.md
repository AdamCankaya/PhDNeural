# Plan 01: Identify and secure multi-disease datasets containing repeated molecular measurements over time (BRCA, Alzheimer's, Rheumatoid Arthritis, T2D, Epigenetic Aging).

## Issue reference

| Field | Value |
|-------|-------|
| Number | [354](https://github.com/AdamCankaya/PhDNeural/issues/354) |
| Title | [Y1 Q3 Fall 2026] Identify and secure multi-disease datasets containing repeated molecular measurements over time (BRCA, Alzheimer's, Rheumatoid Arthritis, T2D, Epigenetic Aging). |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/354 |
| Labels | `phd-sync, year-1, brca-anchor, phase-1, step-1, q3-2026` |
| Year / Quarter | 1 - Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure / Q3 Fall 2026 - Longitudinal Multi-Omic Cohort Sourcing |
| Phase | 1 - The Anchor (BRCA PoC) |
| Master-plan goal | Identify and secure multi-disease datasets with repeated molecular measurements over time. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** dataset inventory table (source, access method, license/ethics, sample counts by timepoint) for all five disease categories.
- [ ] **Acceptance:** every disease has at least one candidate cohort with ≥2 timepoints documented.
- [ ] **Upstream deps satisfied:** GDC/GEO/recount3 accounts; disease registry entries in `src/config/disease_registry.yaml`.


## Approach

Create a checked-in cohort inventory under `Bio-NAS/docs/data/` (e.g. `cohort_inventory.md` + CSV)
covering BRCA (TCGA/GDC), Alzheimer's, RA, T2D, and Epigenetic Aging. For each disease record
source portal, access method, license/ethics notes, modalities, and sample counts by timepoint.
Extend placeholder entries in `src/config/disease_registry.yaml` only with inventory-stable IDs
and documented source columns where already known (do not invent severity maps). Reuse guidance
from `docs/wiki/Data-Acquisition-BRCA.md` as the BRCA template for the other four diseases.

## Key files / areas to touch

- `src/config/disease_registry.yaml`
- `docs/wiki/Data-Acquisition-BRCA.md`
- `docs/data/cohort_inventory.md` (new)
- `phd_bio-nas_master_plan.md` (requirements source)

## Dependencies on other plans

- None (foundational / can start independently within its quarter constraints)

## Out of scope / owned by other plans

- Longitudinal visit pairing rules → plan 02 (#355)
- Feature axes / tensor layout → plans 03–07 (#356–#360)
- Other-4 full ETL wiring → deferred until Year 3 scaling gate (#374/#375)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> every disease has at least one candidate cohort with ≥2 timepoints documented.

Plus: linked PR(s) reference this plan path and issue #354; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

First plan in the roadmap. Unblocks matching (#355) and all BRCA-first ETL.

Recommended roadmap position: **01 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
