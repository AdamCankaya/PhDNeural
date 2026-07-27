# Docker — TCGA-BRCA sample + toy NAS

Minimal harness that builds a slim Python image from [`Dockerfile`](Dockerfile), downloads a **tiny open-access** TCGA-BRCA cohort from the [GDC API](https://api.gdc.cancer.gov) on **first container start**, then runs a simple MLP architecture-search demo. No GDC login / dbGaP token. Not full-cohort ETL (see Plan 07 / [Data Acquisition BRCA](../docs/wiki/Data-Acquisition-BRCA.md)). Plan 1 inventory + open-artifact reproducibility target: [docs/plans/01-issue-354-multi-disease-dataset-inventory.md](../docs/plans/01-issue-354-multi-disease-dataset-inventory.md) (this image is the smoke baseline; Plan 1 extends it beyond toy NAS). Multi-omic **Intermediate Fusion NAS** (branch→concat→post-fusion; phased Optuna) is planned in [ROADMAP § Intermediate Fusion](../docs/plans/ROADMAP.md#intermediate-fusion-nas-multi-omic-supersedes-early-raw-concat) (plans 07/10/12) — not this toy demo.

**Docker-first:** New Bio-NAS executable work should run in this container (or an extension of it), not as a host-only workflow. High-level Windows deploy steps also live in the [Bio-NAS README § Deploy with Docker](../README.md#5-deploy-with-docker-windows).

## Windows: Docker Desktop (prerequisite)

Bio-NAS on Windows uses **Docker Desktop** to build the Dockerfile and run the image.

1. **Download** Docker Desktop for Windows: [Install Docker Desktop on Windows](https://docs.docker.com/desktop/setup/install/windows-install/).
2. **Install** it (enable the **WSL 2** backend when prompted; reboot if asked).
3. **Start** Docker Desktop from the Start menu and wait until the engine status is **Running**.
4. **Verify** in PowerShell:

```powershell
docker version
docker compose version
```

Leave Docker Desktop running for all build/run steps below. If `docker` cannot connect to the engine, open Docker Desktop and wait for it to finish starting.

## What it does

1. **Build** installs Python deps only (no TCGA data baked into the image).
2. **First `docker compose up` / `docker run`** queries GDC for ~5–10 BRCA cases and downloads:
   - Clinical biotab + case demographics (age, gender, race, stage, …)
   - RNA-seq gene expression (STAR counts) for those cases
   - Small methylation files when they fit the size budget
3. **Then** runs `scripts/train_nas_demo.py` (toy NAS over a few MLP widths with leave-one-out CV).
4. Re-runs skip download when `/data/tcga/BRCA/.ready` exists (idempotent; with Compose this marker lives on the host mount).

## Build & run (load Dockerfile → run image)

Compose lives at **`Bio-NAS/docker-compose.yml`** (repo subdirectory). Running `docker compose` from the parent `PhD/` tree fails with `no configuration file provided: not found`. The image is built from **`docker/Dockerfile`**.

### Recommended: Docker Compose

From `Bio-NAS/` (required for the short form). Compose **loads the Dockerfile**, builds `bio-nas-demo:local`, then runs the container:

```powershell
cd Bio-NAS          # if your shell is in PhD/ or PhDNeural/
docker compose up --build
```

From the parent `PhD/` / `PhDNeural/` checkout:

```powershell
docker compose -f Bio-NAS/docker-compose.yml up --build
```

After changing `docker-compose.yml` (including the data volume) or `docker/Dockerfile`, recreate with the same command: `docker compose up --build`. Compose does not migrate data that already exists only inside a previous container filesystem — copy it out with `docker cp` first if you need it, or let the next run re-download into the host mount.

### Manual: `docker build` + `docker run`

Same Dockerfile, without Compose (still from `Bio-NAS/`). Bind-mount the host data path:

```powershell
cd Bio-NAS
docker build -f docker\Dockerfile -t bio-nas-demo:local .
docker run --rm -v "${PWD}/data/tcga:/data/tcga" bio-nas-demo:local
```

On older `cmd.exe` shells, use `-v "%cd%/data/tcga:/data/tcga"` instead of `${PWD}`.

## Data volume (host ↔ container)

Compose bind-mounts host `./data/tcga` to container `/data/tcga`, matching `$TCGA_SAMPLE_OUT` (`/data/tcga/BRCA`):

```yaml
volumes:
  - ./data/tcga:/data/tcga
```

| Side | Path |
|------|------|
| Host (Windows) | `Bio-NAS\data\tcga\BRCA` (e.g. `C:\PhD\Bio-NAS\data\tcga\BRCA`) |
| Container | `/data/tcga/BRCA` (`$TCGA_SAMPLE_OUT`) |

Browse downloads and `nas_demo_results.json` directly in Explorer under the host folder. `data/tcga/` is gitignored so GDC downloads are not committed.

## Viewing results

**Primary (UI):** [Dozzle](https://dozzle.dev/) at [http://localhost:8080](http://localhost:8080) — live logs for `bio-nas-demo` and other Compose containers. Starts with `docker compose up`; keeps running after the one-shot demo exits (`restart: unless-stopped`). Open the `bio-nas-demo` container in the UI to follow download + toy NAS stdout.

**CLI:** container stdout also streams during `docker compose up`; afterward:

```bash
cd Bio-NAS   # if needed
docker compose logs bio-nas-demo
# or: docker logs <container-id>   # from `docker ps -a`
```

**On the host (Compose mount):** open `data/tcga/BRCA/nas_demo_results.json` (also `manifest.json`, `demographics.json`, `files/`).

**Inside the container** (same tree via the mount): `/data/tcga/BRCA/…`

```bash
docker compose ps -a
# Optional: copy or peek if you are not using the bind mount
docker cp <container-name-or-id>:/data/tcga/BRCA/nas_demo_results.json .
docker start <container-name-or-id>
docker exec <container-name-or-id> cat /data/tcga/BRCA/nas_demo_results.json
```

## Data path (inside container)

| Path | Role |
|------|------|
| `/data/tcga/BRCA/` | Cohort root (`$TCGA_SAMPLE_OUT`) |
| `/data/tcga/BRCA/files/` | Downloaded GDC files |
| `/data/tcga/BRCA/manifest.json` | File IDs, case list, metadata |
| `/data/tcga/BRCA/demographics.json` | Patient demographics from GDC cases API |
| `/data/tcga/BRCA/.ready` | Marker that download completed |
| `/data/tcga/BRCA/nas_demo_results.json` | Toy NAS summary after training |

Typical catalog size is tens of MB (budget default ~80 MB), well under a couple hundred MB.

## Access / auth

Open-access GDC endpoints only (`access=open`). **No login, token, or dbGaP approval** is required for this smoke demo.

## Without Docker

```bash
pip install -r docker/requirements.txt
python scripts/download_tcga_brca_sample.py --out-dir data/tcga/BRCA
python scripts/train_nas_demo.py --data-dir data/tcga/BRCA
```

Local downloads under `data/tcga/` are gitignored and are never baked into the image.
