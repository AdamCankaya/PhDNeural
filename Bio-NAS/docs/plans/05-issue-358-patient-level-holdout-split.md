# Plan 05: Partition data by Patient ID (80/20 train/holdout split, strict temporal isolation).

## Issue reference

| Field | Value |
|-------|-------|
| Number | [358](https://github.com/AdamCankaya/PhDNeural/issues/358) |
| Title | [Y1 Q1 Spring 2027] Partition data by Patient ID (80/20 train/holdout split, strict temporal isolation). |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/358 |
| Labels | `phd-sync, year-1, abstraction, phase-2, step-1, q1-2027` |
| Year / Quarter | 1 - Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure / Q1 Spring 2027 - 4D Tensor Construction & Irregular Time-Step Normalization |
| Phase | 2 - Code Abstraction & Generalization |
| Master-plan goal | Construct a leakage-safe ETL pipeline producing irregular-time 4D tensors. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [ ] **Deliverables:** patient-level split files + loader that never peeks at holdout during fit.
- [ ] **Acceptance:** automated leakage tests (no patient ID overlap; no future-visit leakage into earlier steps).
- [ ] **Upstream deps satisfied:** finalized cohort tables from Year 1 Fall/Winter.


## Approach

Implement patient-level 80/20 split generation before any preprocessing. Persist split manifests
(patient IDs only) under a versioned path (e.g. `data/splits/brca_v1/`). Extend loaders so fit-time
transforms never peek at holdout. Add automated leakage tests: no patient ID overlap; no future-visit
leakage into earlier steps. Align with ADR-003/ADR-004 and existing `brca_dataset.py` / clinical_time
guardrails (`LABEL_SOURCE_COLUMNS`).

## Key files / areas to touch

- `src/data/brca_dataset.py`
- `src/data/base_multiomic_dataset.py`
- `data/splits/` manifests (new)
- `tests/` leakage tests (new)

## Dependencies on other plans

- `01-issue-354-multi-disease-dataset-inventory.md` (#354)
- `02-issue-355-longitudinal-matching-strategy.md` (#355)

## Out of scope / owned by other plans

- Cohort inventory & matching strategy → plans 01–02 (#354–#355)
- Holdout evaluation metrics tables → plan 14 (#367)
- Classical baselines on holdout → plan 16 (#369)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> automated leakage tests (no patient ID overlap; no future-visit leakage into earlier steps).

Plus: linked PR(s) reference this plan path and issue #358; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

After cohort tables/IDs exist; must precede any fit-time preprocessing or NAS.

Recommended roadmap position: **05 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
