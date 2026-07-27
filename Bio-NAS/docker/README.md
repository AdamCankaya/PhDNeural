# Docker — Plan-1 TCGA-BRCA sample + inventory verify + toy NAS

Minimal harness that builds a slim Python image from [`Dockerfile`](Dockerfile), then on **first container start**:

1. Downloads a **tiny open-access** TCGA-BRCA cohort from the [GDC API](https://api.gdc.cancer.gov) (~5–10 joint meth+RNA cases + clinical)
2. Runs open **inventory verification** (public GDC project / Level-3 modality counts) → host mount
3. Runs a simple MLP architecture-search demo on **methylation features only**

No GDC login / dbGaP token. Not full-cohort ETL (see Plan 07 / [Data Acquisition BRCA](../docs/wiki/Data-Acquisition-BRCA.md)). Plan 1 inventory + open-artifact reproducibility: [docs/plans/01-issue-354-multi-disease-dataset-inventory.md](../docs/plans/01-issue-354-multi-disease-dataset-inventory.md). Multi-omic **Intermediate Fusion NAS** is planned in [ROADMAP § Intermediate Fusion](../docs/plans/ROADMAP.md#intermediate-fusion-nas-multi-omic-supersedes-early-raw-concat) — not this toy demo.

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

1. **Build** installs Python deps only (no TCGA data baked into the image).
2. **First `docker compose up` / `docker run`** queries GDC for ~5–10 BRCA cases that have **both** open methylation and RNA, and downloads:
   - Clinical biotab + case demographics / AJCC labels
   - Methylation beta-value files (Illumina Human Methylation 450 SeSAMe Level-3)
   - RNA-seq gene expression (STAR counts) for the same cases (PoC-minimum completeness; **not** used by the toy train path)
3. **Then** runs `scripts/verify_cohort_inventory_open.py` — public GDC API spot-check for TCGA-BRCA; writes `inventory_verification/`.
4. **Then** runs `scripts/train_nas_demo.py` — toy NAS over a few MLP widths with leave-one-out CV on **methylation features + stage labels only** (skip with `SKIP_NAS_DEMO=1`).
5. Re-runs skip download when `/data/tcga/BRCA/.ready` exists. If the download schema changes (manifest `schema_version`), delete `.ready` (and optionally `files/`) for a fresh pull.

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

### Manual: `docker build` + `docker run`

```powershell
cd Bio-NAS
docker build -f docker\Dockerfile -t bio-nas-demo:local .
docker run --rm -v "${PWD}/data/tcga:/data/tcga" bio-nas-demo:local
```

## Expected Plan-1 host outputs

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

## Data volume (host ↔ container)

Compose bind-mounts host `./data/tcga` to container `/data/tcga`:

| Side | Path |
|------|------|
| Host (Windows) | `Bio-NAS\data\tcga\…` |
| Container | `/data/tcga/…` |

`data/tcga/` is gitignored so GDC downloads are not committed.

## Env knobs

| Variable | Default | Meaning |
|----------|---------|---------|
| `TCGA_SAMPLE_OUT` | `/data/tcga/BRCA` | Smoke cohort root |
| `TCGA_SAMPLE_N_CASES` | `8` | Target patients (clamped 5–10) |
| `TCGA_SAMPLE_MAX_BYTES` | `1572864000` (~1.5 GB) | Soft download budget |
| `INVENTORY_VERIFY_OUT` | `/data/tcga/inventory_verification` | Verify artifact dir |
| `SMOKE_EXPECTED_JSON` | `/app/docs/data/smoke_expected.json` | Pinned smoke expectations |
| `SKIP_NAS_DEMO` | (unset) | Set `1` to skip toy NAS |
| `INVENTORY_VERIFY_DRY_RUN` | (unset) | Set `1` to skip GDC network in verify |

## Viewing results

**Primary (UI):** [Dozzle](https://dozzle.dev/) at [http://localhost:8080](http://localhost:8080) — live logs for `bio-nas-demo`. Starts with `docker compose up`.

**CLI:**

```bash
cd Bio-NAS
docker compose logs bio-nas-demo
```

**On the host:** open `data/tcga/BRCA/nas_demo_results.json` and `data/tcga/inventory_verification/verification.json`.

## Access / auth

Open-access GDC endpoints only (`access=open`). **No login, token, or dbGaP approval** is required. Controlled/dbGaP data is deferred. Other-4 DUA cohorts are **not** fetched by this image — see [`docs/data/cohort_inventory.md`](../docs/data/cohort_inventory.md).

## Without Docker

```bash
pip install -r docker/requirements.txt
python scripts/download_tcga_brca_sample.py --out-dir data/tcga/BRCA
python scripts/verify_cohort_inventory_open.py --out-dir data/tcga/inventory_verification
python scripts/train_nas_demo.py --data-dir data/tcga/BRCA
```

Prefer Compose for the supported Plan-1 path. Dry-run verify (no network):

```bash
python scripts/verify_cohort_inventory_open.py --dry-run --out-dir data/tcga/inventory_verification
```
