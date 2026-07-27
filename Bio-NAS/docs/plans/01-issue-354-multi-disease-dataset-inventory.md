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

Maps 1:1 to the issue **Implementation requirements**, plus a Plan-01 Docker reproducibility path (delivery mechanism — not a substitute for inventory / Other-4 lock decisions):

- [x] **Deliverables:** dataset inventory table (source, access method, license/ethics, sample counts by timepoint) for all five disease categories. → `docs/data/cohort_inventory.md` + `.csv` (draft 2026-07-24; portal counts still TBD / unverified).
- [x] **Acceptance (inventory):** every disease has at least one candidate cohort with ≥2 timepoints documented. (BRCA via AURORA pairs + sparse TCGA multi-sample; Other-4 via ADNI / GSE138747 / KORA or GSE184050 / LBC1936 or SATSA.)
- [ ] **Acceptance (reproducible Docker path):** a newcomer can clone Bio-NAS, run the documented Compose flow, and obtain Plan-1-relevant open artifacts + verification outputs on the host mount (see [Acceptance criteria](#acceptance-criteria) and [What “reproduce the results” means](#what-reproduce-the-results-means)). *Today’s Docker image is a TCGA-BRCA open sample + toy NAS smoke test — not yet the full Plan-1 repro path.*
- [ ] **Upstream deps satisfied:** GDC/GEO/recount3 accounts; disease registry entries in `src/config/disease_registry.yaml`. *(User has no portal accounts yet. BRCA primary locked to TCGA-BRCA open Level-3 — create **GDC first**. Registry has BRCA mappings; Other-4 + Epigenetic Aging naming still placeholders.)*

**Selection progress (inventory is source of truth):**

- [x] BRCA primary locked → **TCGA-BRCA (GDC)**; AURORA US kept as longitudinal-molecular alternate.
- [ ] Alzheimer's / RA / T2D / Epigenetic Aging primaries still recommended-unlocked (see inventory clarifying questions).

**Docker / repro progress:**

- [x] Slim image + Compose: open-access TCGA-BRCA sample (~5–10 cases) → host mount `./data/tcga` → toy NAS demo. Docs: [`docker/README.md`](../../docker/README.md), [`docker/Dockerfile`](../../docker/Dockerfile), [`docker-compose.yml`](../../docker-compose.yml).
- [ ] Entrypoint extended beyond smoke demo for Plan-1 inventory verification artifacts (open GDC/GEO pieces + regenerated inventory tables / checksums — see [Ordered Docker work items](#ordered-docker-work-items-for-plan-1-repro)).
- [ ] Newcomer-facing README/plan pointer: Dockerfile + compose + **expected Plan-1 outputs** (not only toy NAS JSON).


## Approach

Create a checked-in cohort inventory under `Bio-NAS/docs/data/` (e.g. `cohort_inventory.md` + CSV)
covering BRCA (TCGA/GDC), Alzheimer's, RA, T2D, and Epigenetic Aging. For each disease record
source portal, access method, license/ethics notes, modalities, and sample counts by timepoint.
Extend placeholder entries in `src/config/disease_registry.yaml` only with inventory-stable IDs
and documented source columns where already known (do not invent severity maps). Reuse guidance
from `docs/wiki/Data-Acquisition-BRCA.md` as the BRCA template for the other four diseases.

**BRCA decision (2026-07-24):** primary = TCGA-BRCA (GDC open Level-3). True longitudinal molecular repeats remain weak on TCGA; AURORA US stays inventory alternate for Plan 02 pairing.

**Docker delivery (Plan 1):** treat the existing Bio-NAS Docker setup as the **reproducibility vehicle** for open Plan-1 artifacts — not as a replacement for locking Other-4 primaries, ethics/DUAs, or full controlled-access cohorts. When Plan 1 is done, anyone with Docker should be able to download the Dockerfile (and related compose/docs) and reproduce the documented open results without portal accounts for those open pieces. Controlled-access work stays documented in the inventory with explicit “outside Docker” steps.

**Project-wide rule:** all Bio-NAS plan coding follows Docker-first implementation — see [`.cursor/rules/docker-first-implementation.mdc`](../../.cursor/rules/docker-first-implementation.mdc) and [`ROADMAP.md` § Docker-first](ROADMAP.md#docker-first-all-plans). Plan 1’s Docker sections below are the template; extend entrypoint/requirements/compose rather than host-only scripts.

## Key files / areas to touch

- `src/config/disease_registry.yaml`
- `docs/wiki/Data-Acquisition-BRCA.md`
- `docs/data/cohort_inventory.md` (+ `.csv`)
- `phd_bio-nas_master_plan.md` (requirements source)
- `docker/Dockerfile`, `docker-compose.yml`, `docker/README.md` — repro entry for newcomers
- `scripts/docker_entrypoint.py`, `scripts/download_tcga_brca_sample.py` — extend for Plan-1 artifacts (prefer these over a parallel pipeline)
- (new as needed) inventory regeneration / verification script(s) under `scripts/`, invoked from the same entrypoint

## Dependencies on other plans

- None (foundational / can start independently within its quarter constraints)
- Note: Plan 09 (#362) is a separate Dockerized Postgres/Optuna stack; do not conflate with this Plan-1 sample/inventory repro image.

## Out of scope / owned by other plans

- Longitudinal visit pairing rules → plan 02 (#355)
- Feature axes / tensor layout → plans 03–07 (#356–#360)
- Other-4 full ETL wiring → deferred until Year 3 scaling gate (#374/#375)
- Full-cohort BRCA ETL / large downloads → Plan 07 / Data-Acquisition-BRCA (Docker here stays sample + inventory verification scale)
- Real NAS science / Optuna studies → later plans; the toy MLP in today’s image is a **smoke test only**

## What “reproduce the results” means

For **Plan 1**, “anyone can reproduce” means a clean checkout + Docker yields the **inventory verification and open-sample artifacts** documented below — **not** full controlled-access cohorts, and **not** publication-grade NAS science.

| In scope via Docker (must be reproducible) | Outside Docker (document only; credentials/DUAs) |
|--------------------------------------------|--------------------------------------------------|
| Documented `docker compose up --build` (from `Bio-NAS/`) | ADNI/LONI DUA downloads |
| Open TCGA-BRCA GDC sample (pinned case/file IDs or equivalent) under the host mount | KORA.PASST / project-agreement data |
| Regenerated inventory verification tables/counts from **public** APIs (GDC and/or GEO metadata for open series cited in the inventory) | LBC1936 / EGA DAC, Synapse DUC, dbGaP controlled BAM/raw |
| Manifests, sample ID lists, and checksums (or documented expected hashes) for those open artifacts | Locking Other-4 primaries / ethics board steps (human decisions) |
| README + this plan pointing newcomers at Dockerfile, compose, and expected output paths | Full multi-disease ETL or Year-3 scaling cohorts |

Honest boundary today: Compose already reproduces a **tiny open BRCA sample + toy NAS** (`data/tcga/BRCA/manifest.json`, `nas_demo_results.json`, etc.). Plan-1 completion additionally requires regenerable **inventory verification** artifacts for the open pieces of the five-disease inventory — still without pretending the container holds ADNI/KORA/LBC1936.

## Acceptance criteria

Satisfied when **all** of the following hold:

1. **Issue inventory acceptance** (unchanged #354 core):
   > every disease has at least one candidate cohort with ≥2 timepoints documented.

2. **Reproducible Docker path (Plan-1 delivery):**
   - Documented `docker compose up --build` (or equivalent `docker build` / `docker run` with the same bind mount) from `Bio-NAS/`.
   - On first run, the container downloads Plan-1-relevant **open** sample/inventory artifacts needed to reproduce documented results (at minimum: open TCGA-BRCA sample already wired; plus inventory verification outputs for public-API pieces).
   - Outputs land on the mounted host path (`./data/tcga` → `/data/tcga`, and/or a clearly documented sibling under that mount, e.g. inventory verification JSON/CSV).
   - [`docker/README.md`](../../docker/README.md) and this plan both point newcomers at Dockerfile + compose + **expected Plan-1 outputs** (paths + what to check).

3. Linked PR(s) reference this plan path and issue #354; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

**Do not close #354** until inventory locks / upstream deps and the Docker repro path are actually done — this plan update only clarifies the bar.

## Ordered Docker work items (for Plan-1 repro)

Prefer extending the existing entrypoint and scripts over inventing a parallel system.

1. **Document the contract** (docs-first): in `docker/README.md` + this plan, spell out Plan-1 expected host outputs vs smoke-only toy NAS (partially done; keep in sync as scripts land).
2. **Pin the open BRCA sample:** stabilize case/file selection in `scripts/download_tcga_brca_sample.py` (or a pinned manifest checked into repo) so two runs produce the same sample IDs; record expected checksums or content hashes for `manifest.json` / key files.
3. **Inventory verification script:** add e.g. `scripts/verify_cohort_inventory_open.py` (name flexible) that regenerates open-portal counts/metadata for inventory rows that are publicly queryable (GDC project stats for TCGA-BRCA; GEO Series metadata for open accessions such as GSE138747 / GSE184050 where APIs allow). Write machine-readable verification artifacts to the mounted volume (e.g. `/data/tcga/inventory_verification/`).
4. **Wire into entrypoint:** extend `scripts/docker_entrypoint.py` to run download → inventory verification → (optional) toy NAS; keep toy NAS as a non-blocking smoke step or behind an env flag if verification is the Plan-1 success path.
5. **Compose / image:** ensure `docker/Dockerfile` `COPY`s any new scripts; pin Python deps versions already listed in `docker/requirements.txt` as needed for API clients; no secrets in the image.
6. **Honesty pass:** README must state clearly that DUAs/controlled cohorts are **not** fetched by Docker; point to `docs/data/cohort_inventory.md` for account/DUA next steps. Docker remains the delivery/repro mechanism — locking Other-4 and ethics stay inventory work.

## Rough sequencing notes

First plan in the roadmap. Unblocks matching (#355) and all BRCA-first ETL.

Recommended roadmap position: **01 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

Suggested local order: finish Other-4 lock decisions + portal spot-checks in the inventory → implement Docker work items 2–5 → update README expected-outputs table → PR referencing #354 (leave issue open until acceptance above is met).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.
