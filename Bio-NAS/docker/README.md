# Docker — Plan-1 public multi-disease CPU toy NAS + static dashboard

Minimal harness that builds a CPU-only Python image from [`Dockerfile`](Dockerfile), then sequentially:

1. Downloads tiny public samples for **BRCA** (GDC), **RA** (GSE71841), and **Epigenetic Aging** (GSE40279, GSE87571, GSE280465).
2. Runs one independent CPU toy NAS per active disease and writes each `nas_demo_results.json` to its mounted directory.
3. Skips **Alzheimer's/ADNI** and **T2D/KORA** instead of downloading protected data.
4. Builds `data/dashboard/dashboard.html`, aggregating the toy results.

ADNI and KORA are skipped by default because they require controlled access. No controlled-data credential is used or stored by the image. Toy NAS results validate the workflow only; they are not clinical evidence. Copy [`.env.example`](../.env.example) to `.env` to adjust skip flags or enable the optional GitHub Repository Dispatch.

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

1. **Build** installs Python deps only (no TCGA/ADNI data baked into the image).
2. **First `docker compose up` / `docker run`** queries GDC for ~5–10 BRCA cases that have **both** open methylation and RNA, and downloads:
   - Clinical biotab + case demographics / AJCC labels
   - Methylation beta-value files (Illumina Human Methylation 450 SeSAMe Level-3)
   - RNA-seq gene expression (STAR counts) for the same cases (PoC-minimum completeness; **not** used by the toy train path)
3. **Then** runs `scripts/verify_cohort_inventory_open.py` — public GDC API spot-check for TCGA-BRCA; writes `inventory_verification/` (ADNI listed under `skipped_controlled` — post-DUA).
4. **Then** runs `scripts/train_nas_demo.py` — toy NAS over a few MLP widths with leave-one-out CV on **methylation features + stage labels only** (skip with `SKIP_NAS_DEMO=1`).
5. **Then** runs `scripts/download_adni_sample.py` — ADNI scaffold. Without `ADNI_USER`/`ADNI_PASSWORD`, writes `adni_access_status.json` (`skipped_account_pending`) and exits 0. **Account + DUA in progress** — no controlled download attempted.
6. **Then** runs `scripts/train_nas_ad_demo.py` — AD meth NAS only if `data/adni/.ready` + methylation files exist; otherwise skip exit 0.
7. Re-runs skip BRCA download when `/data/tcga/BRCA/.ready` exists. If the download schema changes (manifest `schema_version`), delete `.ready` (and optionally `files/`) for a fresh pull.

Selection prefers joint meth+RNA cases ordered by `submitter_id`. Full ~1098-case cohort ETL is **Plan 07**, not this smoke.

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

Pinned smoke expectations (schema / ranges / labels — not live file content hashes): [`docs/data/smoke_expected.json`](../docs/data/smoke_expected.json).

Typical catalog size for ~8 joint cases is on the order of **~100–200 MB**. Still sample-scale — not the full cohort.

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
| `SMOKE_EXPECTED_JSON` | `/app/docs/data/smoke_expected.json` | Pinned smoke expectations |
| `ADNI_SAMPLE_OUT` | `/data/adni` | ADNI scaffold / sample root |
| `ADNI_USER` / `ADNI_PASSWORD` | (unset) | Host `.env` only after DUA — never in image |
| `ADNI_SKIP` | (unset) | Set `1` to force ADNI skip |
| `SKIP_NAS_DEMO` | (unset) | Set `1` to skip BRCA toy NAS |
| `SKIP_AD_NAS_DEMO` | (unset) | Set `1` to skip AD toy NAS |
| `INVENTORY_VERIFY_DRY_RUN` | (unset) | Set `1` to skip GDC network in verify |

## Viewing results

**Primary (UI):** [Dozzle](https://dozzle.dev/) at [http://localhost:8080](http://localhost:8080) — live logs for `bio-nas-demo`. Starts with `docker compose up`.

**CLI:**

```bash
cd Bio-NAS
docker compose logs bio-nas-demo
```

**On the host:** open `data/tcga/BRCA/nas_demo_results.json`, `data/tcga/inventory_verification/verification.json`, and `data/adni/adni_access_status.json`.

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
