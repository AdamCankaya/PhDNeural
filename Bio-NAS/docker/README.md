# Docker — Plan-1 public multi-disease CPU toy NAS + static dashboard

Minimal harness that builds a CPU-only Python image from [`Dockerfile`](Dockerfile), then sequentially runs the **unified Plan 1 chain** in [`entrypoint.sh`](entrypoint.sh). **Active engineering smokes:** BRCA, RA, and epigenetic aging (EA). **Deferred by default:** ADNI (Alzheimer's) and KORA (T2D) until controlled access completes.

1. **BRCA (GDC):** tiny open TCGA-BRCA sample → **inventory verification** (public GDC API) → **Plan 2 longitudinal matching** (`build_brca_longitudinal_matching.py`) → optional CPU toy NAS (`train_toy_nas_cpu.py --brca`).
2. **Alzheimer's (ADNI):** `download_adni_sample.py` scaffold (status JSON; no controlled download without DUA) → optional `train_nas_ad_demo.py` when `.ready` exists.
3. **RA (GEO GSE71841):** download → `verify_geo_smoke.py` → optional toy NAS.
4. **T2D (KORA):** honest skip (project agreement required).
5. **Epigenetic Aging (GEO GSE87571):** series-matrix metadata + supplementary `matrix1of2` betas → verify → optional toy NAS.
6. **Dashboard:** `build_dashboard.py` → `data/dashboard/dashboard.html`.
7. **Optional:** GitHub `repository_dispatch` when `GITHUB_DISPATCH_ENABLED=1`.

ADNI and KORA controlled paths stay skipped by default. No controlled-data credential is stored in the image. Toy NAS metrics validate orchestration only. Copy [`.env.example`](../.env.example) to `.env` for skip flags or dispatch.

**Docker-first:** New Bio-NAS executable work should run in this container (or an extension of it), not as a host-only workflow. High-level Windows deploy steps: [Bio-NAS README § Deploy with Docker](../README.md#5-deploy-with-docker-windows). Agent rule: when Dockerfile / `COPY`'d scripts / requirements change, rebuild with `docker compose up --build` ([`.cursor/rules/docker-rebuild-notify.mdc`](../.cursor/rules/docker-rebuild-notify.mdc)).

## Windows: Docker Desktop (prerequisite)

1. **Download** Docker Desktop for Windows: [Install Docker Desktop on Windows](https://docs.docker.com/desktop/setup/install/windows-install/).
2. **Install** it (enable the **WSL 2** backend when prompted; reboot if asked).
3. **Start** Docker Desktop and wait until the engine status is **Running**.
4. **Verify** in PowerShell:

```powershell
docker version
docker compose version
```

Leave Docker Desktop running for all build/run steps below.

## What it does

Entrypoint order matches the numbered list above. Details:

1. **Build** installs Python deps only (no cohort data baked into the image).
2. **BRCA download** queries GDC for ~5–10 cases with **both** open methylation and RNA (clinical biotab + meth betas + STAR RNA — RNA not used by toy NAS).
3. **Inventory verify** — `scripts/verify_cohort_inventory_open.py` spot-checks TCGA-BRCA via the public GDC API → `data/tcga/inventory_verification/` (`INVENTORY_VERIFY_DRY_RUN=1` skips network).
4. **BRCA longitudinal matching (Plan 2 / #355)** — `scripts/build_brca_longitudinal_matching.py` defaults to `BRCA_MATCHING_SCOPE=discover`: pages open GDC `/cases` metadata for TCGA-BRCA samples whose type is Recurrent Tumor or Metastatic (no omic download) → `data/tcga/BRCA/longitudinal_matching/` (`visit_sequences.json`, `match_pairs.json`, `summary.json` with `cohort_scope`). Set `BRCA_MATCHING_SCOPE=smoke` to keep the 8-case smoke manifest. Skip with `SKIP_BRCA_MATCHING=1`. Zero match pairs are **expected only for smoke**.
5. **BRCA toy NAS** — `train_toy_nas_cpu.py --brca` (skip with `SKIP_BRCA_NAS=1` or legacy `SKIP_NAS_DEMO=1`).
6. **ADNI scaffold** — `scripts/download_adni_sample.py` writes `adni_access_status.json` when credentials absent; `ADNI_SKIP=1` forces skip.
7. **AD toy NAS** — `train_nas_ad_demo.py` only when `data/adni/.ready` exists (skip with `SKIP_AD_NAS_DEMO=1`).
8. **RA / EA** — GEO downloads, `verify_geo_smoke.py`, optional per-disease toy NAS.
9. **T2D** — writes `.skipped` marker; enabling controlled KORA requires explicit out-of-band agreement (entrypoint refuses `SKIP_T2D=0` today).
10. **Dashboard** — always built last; includes **pipeline steps table**, **Plan 1 disease summary** (issue #354), **Plan 2 matching summary** (#355), and disease rows (`data/dashboard/dashboard.html`).
11. Re-runs skip BRCA/RA/EA downloads when each disease `.ready` exists.

Selection prefers joint meth+RNA BRCA cases ordered by `submitter_id`. Full ~1098-case cohort ETL is **Plan 07**, not this smoke.

## Build & run

Compose lives at **`Bio-NAS/docker-compose.yml`**. Running `docker compose` from the parent `PhD/` tree fails unless you pass `-f Bio-NAS/docker-compose.yml`.

### Recommended: Docker Compose

```powershell
cd Bio-NAS
docker compose up --build
```

From the parent `PhD/` / `PhDNeural/` checkout:

```powershell
docker compose -f Bio-NAS/docker-compose.yml up --build
```

After changing `docker/Dockerfile`, `docker/requirements.txt`, or any script/`COPY`'d file, rebuild with `docker compose up --build`.

Optional host `.env` (gitignored) for post-DUA ADNI credentials — Compose loads it when present:

```env
# After ADNI/LONI account + DUA approval only — never commit
ADNI_USER=your_loni_user
ADNI_PASSWORD=your_loni_password
```

### Manual: `docker build` + `docker run`

```powershell
cd Bio-NAS
docker build -f docker\Dockerfile -t bio-nas-demo:local .
docker run --rm -v "${PWD}/data/tcga:/data/tcga" -v "${PWD}/data/adni:/data/adni" bio-nas-demo:local
```

## Expected Plan-1 host outputs (BRCA)

| Host path (under `Bio-NAS/`) | Role |
|------------------------------|------|
| `data/tcga/BRCA/manifest.json` | Smoke catalog (`schema_version` 2, joint cases, file IDs) |
| `data/tcga/BRCA/demographics.json` | Case demographics / AJCC |
| `data/tcga/BRCA/files/` | Downloaded meth betas + STAR RNA + clinical biotab |
| `data/tcga/BRCA/.ready` | Download-complete marker |
| `data/tcga/BRCA/nas_demo_results.json` | Toy NAS summary (`modality: methylation_beta`) |
| `data/tcga/inventory_verification/verification.json` | GDC open inventory verify (`overall_status: ok`) |
| `data/tcga/inventory_verification/verification_summary.csv` | Flat TCGA-BRCA summary row |
| `data/tcga/BRCA/longitudinal_matching/summary.json` | Plan 2 matching counts (`schema_version` 1) |
| `data/tcga/BRCA/longitudinal_matching/visit_sequences.json` | Ordered visits (`visit_index`) for multi-sample cases |
| `data/tcga/BRCA/longitudinal_matching/match_pairs.json` | Directed anchor→later pairs (may be empty on smoke) |
| `data/dashboard/dashboard.html` | Static dashboard — **pipeline steps table** + **Plan 1 section** + disease table + **Plan 2 section** |

Pinned smoke expectations (schema / ranges / labels — not live file content hashes): [`docs/data/smoke_expected.json`](../docs/data/smoke_expected.json). Matching summary pins: [`docs/data/smoke_expected_matching.json`](../docs/data/smoke_expected_matching.json). Strategy doc: [`docs/data/matching_strategy.md`](../docs/data/matching_strategy.md).

Typical catalog size for ~8 joint cases is on the order of **~100–200 MB**. Still sample-scale — not the full cohort.

## Expected Plan-1 host outputs (RA)

| Host path (under `Bio-NAS/`) | Role |
|------------------------------|------|
| `data/ra/manifest.json` | Smoke catalog (`schema_version` 2, GSE71841, GSM cohort) |
| `data/ra/demographics.json` | Healthy vs RA labels (`sample type: Control/Case`) |
| `data/ra/files/` | Per-GSM `*_methylation.tsv` (`probe`, `beta_value`) |
| `data/ra/.ready` | Download-complete marker |
| `data/ra/nas_demo_results.json` | Toy NAS summary (`best_architecture.validation_accuracy`) |

Pinned smoke expectations: [`docs/data/smoke_expected_ra.json`](../docs/data/smoke_expected_ra.json). Verified in-container by `scripts/verify_geo_smoke.py` after download.

Wiki: [`docs/wiki/Data-Acquisition-RA.md`](../docs/wiki/Data-Acquisition-RA.md).

## Expected Plan-1 host outputs (Epigenetic Aging)

| Host path (under `Bio-NAS/`) | Role |
|------------------------------|------|
| `data/epigenetic_aging/manifest.json` | Smoke catalog (`schema_version` 2, GSE87571, GSM cohort, `beta_source`) |
| `data/epigenetic_aging/demographics.json` | Age-bin labels (`age` &lt; 50 vs ≥ 50) |
| `data/epigenetic_aging/files/` | Per-GSM `*_methylation.tsv` (`probe`, `beta_value`) |
| `data/epigenetic_aging/.ready` | Download-complete marker |
| `data/epigenetic_aging/nas_demo_results.json` | Toy NAS summary (`best_architecture.validation_accuracy`) |

Pinned smoke expectations: [`docs/data/smoke_expected_ea.json`](../docs/data/smoke_expected_ea.json). Verified in-container by `scripts/verify_geo_smoke.py` after download. First run downloads supplementary `GSE87571_matrix1of2.txt.gz` (one-time large transfer); idempotent re-runs use `.ready`.

Wiki: [`docs/wiki/Data-Acquisition-EA.md`](../docs/wiki/Data-Acquisition-EA.md).

If `data/epigenetic_aging/.skipped` exists from an older Plan-1 run (`plan1_deferred`), **delete it** before re-running compose so the dashboard shows EA as Ready (same artifact set as RA for a Ready row).

Legacy `GSE*_features.tsv` trees from older entrypoints are not produced by the current pipeline.

## Expected Plan-1 host outputs (Alzheimer's / ADNI)

| Host path (under `Bio-NAS/`) | Role |
|------------------------------|------|
| `data/adni/adni_access_status.json` | Scaffold status (`skipped_account_pending` while DUA in progress) |
| `data/adni/.skipped` | Marker that controlled download was not performed |
| `data/adni/.ready` + `files/` + `nas_demo_results.json` | **Only after** DUA + staged sample — not expected yet |

**Blocker:** ADNI/LONI account + Data Use Agreement **in progress** (user applying). No real ADNI bulk/sample download can succeed until approval.

## Data volume (host ↔ container)

| Side | Path |
|------|------|
| Host (Windows) BRCA | `Bio-NAS\data\tcga\…` |
| Container BRCA | `/data/tcga/…` |
| Host (Windows) ADNI | `Bio-NAS\data\adni\…` |
| Container ADNI | `/data/adni/…` |

`data/tcga/` and `data/adni/` are gitignored so downloads are not committed.

## Env knobs

| Variable | Default | Meaning |
|----------|---------|---------|
| `TCGA_SAMPLE_OUT` | `/data/tcga/BRCA` | BRCA smoke cohort root |
| `TCGA_SAMPLE_N_CASES` | `8` | Target patients (clamped 5–10) |
| `TCGA_SAMPLE_MAX_BYTES` | `1572864000` (~1.5 GB) | Soft download budget |
| `INVENTORY_VERIFY_OUT` | `/data/tcga/inventory_verification` | Verify artifact dir |
| `SMOKE_EXPECTED_JSON` | `/app/docs/data/smoke_expected.json` | Pinned BRCA smoke expectations |
| `RA_SAMPLE_OUT` | `/data/ra` | RA smoke cohort root |
| `RA_SAMPLE_N` | `8` | Target GSM samples (clamped 5–10) |
| `RA_SMOKE_EXPECTED_JSON` | `/app/docs/data/smoke_expected_ra.json` | Pinned RA smoke expectations |
| `SKIP_RA_NAS` | `0` | Set `1` to skip RA toy NAS |
| `EPIGENETIC_AGING_SAMPLE_OUT` | `/data/epigenetic_aging` | EA smoke cohort root |
| `EA_SAMPLE_N` | `8` | Target GSM samples (clamped 5–10) |
| `EA_SMOKE_EXPECTED_JSON` | `/app/docs/data/smoke_expected_ea.json` | Pinned EA smoke expectations |
| `SKIP_EPIGENETIC_AGING_NAS` | `0` | Set `1` to skip EA toy NAS (download + verify still run) |
| `ADNI_SAMPLE_OUT` | `/data/adni` | ADNI scaffold / sample root |
| `ADNI_USER` / `ADNI_PASSWORD` | (unset) | Host `.env` only after DUA — never in image |
| `ADNI_SKIP` | (unset) | Set `1` to force ADNI skip |
| `SKIP_NAS_DEMO` | (unset) | Set `1` to skip BRCA toy NAS |
| `SKIP_AD_NAS_DEMO` | (unset) | Set `1` to skip AD toy NAS |
| `INVENTORY_VERIFY_DRY_RUN` | (unset) | Set `1` to skip GDC network in verify |
| `SKIP_BRCA_MATCHING` | `0` | Set `1` to skip Plan 2 GDC metadata matching |
| `BRCA_MATCHING_SCOPE` | `discover` | `discover` pages TCGA-BRCA cases with a later sample type; `smoke` uses the 8-case manifest |
| `BRCA_MATCHING_OUT` | `/data/tcga/BRCA/longitudinal_matching` | Matching artifact directory |
| `MATCHING_KEYS_YAML` | `/app/src/config/longitudinal_keys.yaml` | Join keys override |

## Viewing results

**Toy NAS dashboard (HTML):** after every run (even when individual disease steps fail), open **`data/dashboard/dashboard.html`** on the host. Includes a **full pipeline steps table**, a **Plan 1 — Multi-disease smoke cohorts** heading before the disease table, a **Plan 2 — BRCA longitudinal matching** section (from `summary.json`, including `cohort_scope` and drop counters when present). A non-empty discover run is not described as an expected all-zero smoke result. Failed steps are at the top, and per-disease rows (TCGA-BRCA includes a **Longitudinal matching** column). Step details: `data/dashboard/pipeline_steps.log`. The container may exit with code **1** when some steps failed even though the dashboard was written.

**Logs UI:** [Dozzle](https://dozzle.dev/) at [http://localhost:8080](http://localhost:8080) — live logs for `bio-nas-demo`. Starts with `docker compose up`.

**CLI:**

```bash
cd Bio-NAS
docker compose logs bio-nas-demo
```

**On the host:** `data/dashboard/dashboard.html`, plus `data/tcga/BRCA/nas_demo_results.json`, `data/tcga/inventory_verification/verification.json`, and `data/adni/adni_access_status.json`.

## Access / auth

- **BRCA:** Open-access GDC endpoints only (`access=open`). **No login, token, or dbGaP approval** is required.
- **ADNI:** Controlled. Account + DUA **in progress**. Credentials via host `.env` after approval — **never** bake into Dockerfile. Scaffold skips without credentials. No login scrape.

See [`docs/data/cohort_inventory.md`](../docs/data/cohort_inventory.md) and [Data Acquisition Alzheimer's](../docs/wiki/Data-Acquisition-Alzheimer's.md).

## Without Docker

```bash
pip install -r docker/requirements.txt
python scripts/download_tcga_brca_sample.py --out-dir data/tcga/BRCA
python scripts/verify_cohort_inventory_open.py --out-dir data/tcga/inventory_verification
python scripts/train_nas_demo.py --data-dir data/tcga/BRCA
python scripts/download_adni_sample.py --out-dir data/adni
python scripts/train_nas_ad_demo.py --data-dir data/adni
```

Prefer Compose for the supported Plan-1 path. Dry-run verify (no network):

```bash
python scripts/verify_cohort_inventory_open.py --dry-run --out-dir data/tcga/inventory_verification
```
