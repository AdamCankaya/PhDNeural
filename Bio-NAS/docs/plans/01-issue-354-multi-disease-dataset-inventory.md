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

## Status split (BRCA vs Other-4)

| Slice | Status | What “done” means |
|-------|--------|-------------------|
| **BRCA Plan-1** | **Complete** (2026-07-27) | Primary locked to TCGA-BRCA open Level-3; GDC API spot-check (`verified_gdc_api`); Docker chain download → inventory verify → optional toy NAS; expected pins + docs. Controlled/dbGaP deferred. |
| **Other-4 Plan-1** | **Remaining** | Alzheimer's / RA / T2D / Epigenetic Aging primaries still unlocked; DUA/account steps outside Docker; #354 stays open until Other-4 locks + any open-GEO verify extensions land. |

Do **not** block BRCA Plan-1 closure on Other-4 locks.

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**, plus a Plan-01 Docker reproducibility path (delivery mechanism — not a substitute for inventory / Other-4 lock decisions):

- [x] **Deliverables:** dataset inventory table (source, access method, license/ethics, sample counts by timepoint) for all five disease categories. → `docs/data/cohort_inventory.md` + `.csv` (draft 2026-07-24; **TCGA-BRCA verified 2026-07-27**; Other-4 portal counts still TBD / unverified).
- [x] **Acceptance (inventory):** every disease has at least one candidate cohort with ≥2 timepoints documented. (BRCA via AURORA pairs + sparse TCGA multi-sample; Other-4 via ADNI / GSE138747 / KORA or GSE184050 / LBC1936 or SATSA.)
- [x] **Acceptance (reproducible Docker path) — BRCA open slice:** a newcomer can clone Bio-NAS, run `docker compose up --build`, and obtain open BRCA smoke + inventory verification artifacts on the host mount (see [Acceptance criteria](#acceptance-criteria)). Other-4 open-GEO verify optional later; controlled cohorts remain outside Docker.
- [ ] **Upstream deps satisfied (issue-wide):** disease registry entries in `src/config/disease_registry.yaml`. *(BRCA primary locked to TCGA-BRCA **open Level-3** — no GDC token required. Controlled/dbGaP deferred. Registry has BRCA mappings; Other-4 + Epigenetic Aging naming still placeholders.)*

**Selection progress (inventory is source of truth):**

- [x] BRCA primary locked → **TCGA-BRCA (GDC) open Level-3**; AURORA US kept as longitudinal-molecular alternate (controlled deferred).
- [ ] Alzheimer's / RA / T2D / Epigenetic Aging primaries still recommended-unlocked (see inventory clarifying questions).

**Plan 1/2 open-focus decisions (encoded):**

- [x] **PoC minimum modalities (open Level-3 only):** methylation betas + RNA (STAR counts) + clinical/labels. Controlled/dbGaP deferred until later.
- [x] **GDC download token:** not required for open data; not a Plan 1/2 blocker; do not bake tokens into Docker. Little/no advantage for open API smoke/metadata (optional portal bulk UX later).
- [x] Storage on host mount (`./data/tcga` → `/data/tcga`).
- [x] Full-cohort bulk ETL deferred to **Plan 07**.
- [x] Pin/stabilize smoke selection (joint meth+RNA cases ordered by `submitter_id`; manifests on mount).
- [x] Plan 02 may use GDC metadata/barcodes without a full omic dump.

**Docker / repro progress (BRCA):**

- [x] Slim image + Compose: open-access TCGA-BRCA sample (~5–10 joint meth+RNA cases + clinical) → host mount `./data/tcga` → **methylation-only** toy NAS demo.
- [x] Inventory verification script + artifacts: `scripts/verify_cohort_inventory_open.py` → `/data/tcga/inventory_verification/` (`verification.json`, `verification_summary.csv`).
- [x] Entrypoint chain: download → inventory verification → optional toy NAS (`SKIP_NAS_DEMO=1` to skip; `INVENTORY_VERIFY_DRY_RUN=1` for offline dry-run).
- [x] Expected pins: `docs/data/smoke_expected.json` (schema_version 2, case/file ranges, PoC labels) — checked by the verify script when `manifest.json` is present.
- [x] Newcomer docs: [`docker/README.md`](../../docker/README.md) + this plan list expected Plan-1 host outputs (smoke + verification).


## Approach

Create a checked-in cohort inventory under `Bio-NAS/docs/data/` (e.g. `cohort_inventory.md` + CSV)
covering BRCA (TCGA/GDC), Alzheimer's, RA, T2D, and Epigenetic Aging. For each disease record
source portal, access method, license/ethics notes, modalities, and sample counts by timepoint.
Extend placeholder entries in `src/config/disease_registry.yaml` only with inventory-stable IDs
and documented source columns where already known (do not invent severity maps). Reuse guidance
from `docs/wiki/Data-Acquisition-BRCA.md` as the BRCA template for the other four diseases.

**BRCA decision (2026-07-24):** primary = TCGA-BRCA (GDC open Level-3). True longitudinal molecular repeats remain weak on TCGA; AURORA US stays inventory alternate for Plan 02 pairing.

**PoC modality minimum (Plan 1/2):** open Level-3 **methylation betas + RNA + clinical/labels** only. Mutations/CNV/miRNA/RPPA and controlled BAM/raw are out of scope for the PoC smoke and Plan 1/2 matching work. Controlled/dbGaP remains documented in the inventory but **deferred**.

**Docker delivery (Plan 1):** treat the existing Bio-NAS Docker setup as the **reproducibility vehicle** for open Plan-1 artifacts — not as a replacement for locking Other-4 primaries, ethics/DUAs, or full controlled-access cohorts. When the BRCA slice is done, anyone with Docker should be able to download the Dockerfile (and related compose/docs) and reproduce the documented open BRCA results without portal accounts. Controlled-access work stays documented in the inventory with explicit “outside Docker” steps.

**Smoke vs full ETL:** Compose downloads a **few patients** (~5–10) with joint open meth+RNA+clinical, runs inventory verification against the public GDC API, and runs a **meth-only** toy NAS. Full-cohort BRCA ETL / HDF5 → **Plan 07**.

**Project-wide rule:** all Bio-NAS plan coding follows Docker-first implementation — see [`.cursor/rules/docker-first-implementation.mdc`](../../.cursor/rules/docker-first-implementation.mdc) and [`ROADMAP.md` § Docker-first](ROADMAP.md#docker-first-all-plans). Plan 1’s Docker sections below are the template; extend entrypoint/requirements/compose rather than host-only scripts.

## Key files / areas to touch

- `src/config/disease_registry.yaml`
- `docs/wiki/Data-Acquisition-BRCA.md`
- `docs/data/cohort_inventory.md` (+ `.csv`)
- `docs/data/smoke_expected.json` — pinned smoke schema / ranges
- `phd_bio-nas_master_plan.md` (requirements source)
- `docker/Dockerfile`, `docker-compose.yml`, `docker/README.md` — repro entry for newcomers
- `scripts/docker_entrypoint.py`, `scripts/download_tcga_brca_sample.py`, `scripts/verify_cohort_inventory_open.py`, `scripts/train_nas_demo.py`

## Dependencies on other plans

- None (foundational / can start independently within its quarter constraints)
- Note: Plan 09 (#362) is a separate Dockerized Postgres/Optuna stack; do not conflate with this Plan-1 sample/inventory repro image.

## Out of scope / owned by other plans

- Longitudinal visit pairing rules → plan 02 (#355)
- Feature axes / tensor layout → plans 03–07 (#356–#360)
- Other-4 full ETL wiring → deferred until Year 3 scaling gate (#374/#375)
- Full-cohort BRCA ETL / large downloads → Plan 07 / Data-Acquisition-BRCA (Docker here stays sample + inventory verification scale)
- Controlled/dbGaP downloads → deferred (document only for Plan 1/2)
- Real NAS science / Optuna studies → later plans; the toy MLP in today’s image is a **smoke test only** (methylation features)

## What “reproduce the results” means

For **Plan 1 (BRCA open slice)**, “anyone can reproduce” means a clean checkout + Docker yields the **inventory verification and open-sample artifacts** documented below — **not** full controlled-access cohorts, and **not** publication-grade NAS science.

| In scope via Docker (must be reproducible) | Outside Docker (document only; credentials/DUAs) |
|--------------------------------------------|--------------------------------------------------|
| Documented `docker compose up --build` (from `Bio-NAS/`) | ADNI/LONI DUA downloads |
| Open TCGA-BRCA GDC sample — ~5–10 cases with meth betas + STAR RNA + clinical/labels under the host mount | KORA.PASST / project-agreement data |
| Regenerated inventory verification from **public** GDC API (`inventory_verification/`) | LBC1936 / EGA DAC, Synapse DUC, dbGaP controlled BAM/raw |
| Manifests, sample ID lists, and pinned schema expectations (`smoke_expected.json`) | Locking Other-4 primaries / ethics board steps (human decisions) |
| README + this plan pointing newcomers at Dockerfile, compose, and expected output paths | Full multi-disease ETL or Year-3 scaling cohorts |

## Acceptance criteria

Satisfied when **all** of the following hold:

1. **Issue inventory acceptance** (unchanged #354 core):
   > every disease has at least one candidate cohort with ≥2 timepoints documented.

2. **Reproducible Docker path (Plan-1 BRCA delivery):**
   - Documented `docker compose up --build` (or equivalent) from `Bio-NAS/`.
   - Container downloads open TCGA-BRCA meth+RNA+clinical sample and writes inventory verification outputs.
   - Outputs land on `./data/tcga` → `/data/tcga` (BRCA smoke + `inventory_verification/`).
   - [`docker/README.md`](../../docker/README.md) and this plan both list expected Plan-1 outputs.

3. Linked PR(s) reference this plan path and issue #354.

**Issue #354** remains open until Other-4 primary locks (and optional open-GEO verify) are done — BRCA slice alone does not close the issue.

## Ordered Docker work items (for Plan-1 repro)

Prefer extending the existing entrypoint and scripts over inventing a parallel system.

1. [x] **Document the contract** (docs-first): in `docker/README.md` + this plan, spell out Plan-1 expected host outputs vs smoke-only toy NAS.
2. [x] **Pin / stabilize the open BRCA smoke sample:** joint meth+RNA case selection ordered by `submitter_id` in `scripts/download_tcga_brca_sample.py`; manifests on the host mount (`schema_version` 2).
3. [x] **Inventory verification script:** `scripts/verify_cohort_inventory_open.py` — GDC project stats + PoC Level-3 open modality counts for TCGA-BRCA; artifacts under `/data/tcga/inventory_verification/`.
4. [x] **Wire verification into entrypoint:** download → inventory verification → (optional) toy NAS.
5. [x] **Compose / image:** `docker/Dockerfile` `COPY`s smoke + verify scripts + `smoke_expected.json`; sample-scale `TCGA_SAMPLE_MAX_BYTES` (~1.5 GB); no secrets/tokens in the image.
6. [x] **Honesty pass (smoke):** README states DUAs/controlled cohorts are **not** fetched by Docker; token optional/not required for open Plan 1/2.
7. [x] **Checksum / expected-hash note:** `docs/data/smoke_expected.json` pins schema_version, case/file ranges, PoC modalities, and required file labels (live GDC file content hashes not pinned — portal drift).
8. [ ] **Other-4 primary lock decisions** + portal spot-checks in the inventory (human / clarifying questions).

## Expected Plan-1 host outputs (BRCA)

After `docker compose up --build` from `Bio-NAS/`:

| Host path | What to check |
|-----------|---------------|
| `data/tcga/BRCA/manifest.json` | `schema_version: 2`, `n_cases` in 5–10, labels clinical/methylation/gene_expression |
| `data/tcga/BRCA/demographics.json` | One row per smoke case |
| `data/tcga/BRCA/files/` | Meth betas + STAR RNA + clinical biotab |
| `data/tcga/BRCA/.ready` | Download marker (`schema_version` 2) |
| `data/tcga/BRCA/nas_demo_results.json` | Toy NAS summary (`modality: methylation_beta`) — unless `SKIP_NAS_DEMO=1` |
| `data/tcga/inventory_verification/verification.json` | `overall_status: ok`, TCGA-BRCA `verified_gdc_api` (or `dry_run_skipped`) |
| `data/tcga/inventory_verification/verification_summary.csv` | Flat summary row for TCGA-BRCA |

Dry-run verify only (no GDC network): set `INVENTORY_VERIFY_DRY_RUN=1` or run `python scripts/verify_cohort_inventory_open.py --dry-run`.

## Rough sequencing notes

First plan in the roadmap. Unblocks matching (#355) and all BRCA-first ETL.

Recommended roadmap position: **01 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

Suggested local order: **BRCA Docker + GDC verify done** → Other-4 lock decisions + portal spot-checks → optional GEO verify extension → leave #354 open until Other-4 acceptance.

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
