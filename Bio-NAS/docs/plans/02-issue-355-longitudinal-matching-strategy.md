# Plan 02: Source longitudinal tracking options focusing on primary vs. recurrent match points.

> **Status: BRCA slice complete (2026-11-02)** — Plan 2 Docker step, matching strategy doc, YAML join keys, unit tests, and dashboard section landed for issue #355. RA/EA templates remain stubs.
>
> **Follow-up (2026-11-02):** drop unranked GDC `sample_type` rows before visit ordering so mixed biospecimen lists (e.g. Blood Derived Normal + Primary) do not exclude entire smoke cases; see `matching_strategy.md` § Sample filtering and `CHANGELOG.md`.
>
> **Prerequisites satisfied:** [`cohort_inventory.md`](../data/cohort_inventory.md) + [`01-issue-354-multi-disease-dataset-inventory.md`](01-issue-354-multi-disease-dataset-inventory.md) (Complete); reproducible `docker compose up --build` for BRCA inventory verify + RA/EA toy NAS ([`docker/README.md`](../../docker/README.md)).
>
> **First implementation slice:** prototype BRCA open GDC barcode pairing (case/sample IDs) → draft `docs/data/matching_strategy.md` § BRCA + seed `src/config/longitudinal_keys.yaml` join keys (no full omic ETL).

## Issue reference

| Field | Value |
|-------|-------|
| Number | [355](https://github.com/AdamCankaya/PhDNeural/issues/355) |
| Title | [Y1 Q3 Fall 2026] Source longitudinal tracking options focusing on primary vs. recurrent match points. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/355 |
| Labels | `phd-sync, year-1, brca-anchor, phase-1, step-1, q3-2026` |
| Year / Quarter | 1 - Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure / Q3 Fall 2026 - Longitudinal Multi-Omic Cohort Sourcing |
| Phase | 1 - The Anchor (BRCA PoC) |
| Master-plan goal | Identify and secure multi-disease datasets with repeated molecular measurements over time. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**:

- [x] **Deliverables:** matching strategy note (patient ID schemes, primary/recurrent or visit pairing rules) per disease — **BRCA complete** in [`docs/data/matching_strategy.md`](../data/matching_strategy.md); RA/EA stubs in YAML.
- [x] **Acceptance:** documented join keys and exclusion rules that preserve temporal order — [`src/config/longitudinal_keys.yaml`](../../src/config/longitudinal_keys.yaml) + [`src/data/brca_longitudinal_matching.py`](../../src/data/brca_longitudinal_matching.py).
- [x] **Upstream deps satisfied:** cohort-specific clinical/metadata dictionaries.


## Approach

Author a matching-strategy note (per disease) defining patient ID schemes, primary/recurrent or
visit pairing rules, join keys, and exclusion rules that preserve temporal order. Prototype the
BRCA primary/recurrent pairing first (TCGA case/sample barcodes), then template the Other 4.
Encode join-key constants in a small config module (e.g. `src/config/longitudinal_keys.yaml`)
consumed later by ETL — do not yet implement the full tensor pipeline.

**Plan 1/2 open-focus (BRCA):** matching work uses **open / non-controlled** GDC metadata and
barcodes (cases/samples APIs, clinical fields). **No controlled/dbGaP data** and **no full omic
dump** are required for Plan 02 — metadata-level pairing is enough; full-cohort meth/RNA ETL
stays Plan 07. PoC modality context remains open Level-3 meth + RNA + clinical/labels.

## Key files / areas to touch

- `src/config/longitudinal_keys.yaml` (new)
- `docs/data/matching_strategy.md` (new)
- `src/data/clinical_time.py` (timestamp column conventions)

## Dependencies on other plans

- `01-issue-354-multi-disease-dataset-inventory.md` (#354)

## Out of scope / owned by other plans

- Dataset inventory & access accounts → plan 01 (#354)
- Full-cohort BRCA omic ETL / HDF5 → plan 07 (#360)
- Controlled/dbGaP downloads → deferred (not required for open barcode/metadata matching)
- Patient-level 80/20 split files → plan 05 (#358)
- Δt embedding module → plan 06 (#359)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> documented join keys and exclusion rules that preserve temporal order.

Plus: linked PR(s) reference this plan path and issue #355; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

**Verification (BRCA slice):**

- `python -m unittest discover -s tests` (from `Bio-NAS/`)
- `docker compose up --build` → `data/tcga/BRCA/longitudinal_matching/` + pipeline log step `BRCA longitudinal matching (GDC metadata)|0`
- Dashboard: `data/dashboard/dashboard.html` Plan 2 section

## Rough sequencing notes

Immediately after inventory. Enables timestamps for Δt and longitudinal tensors.

Recommended roadmap position: **02 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
