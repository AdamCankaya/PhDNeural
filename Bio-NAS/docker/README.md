# Docker — TCGA-BRCA sample + toy NAS

Minimal harness that builds a slim Python image, downloads a **tiny open-access** TCGA-BRCA cohort from the [GDC API](https://api.gdc.cancer.gov) on **first container start**, then runs a simple MLP architecture-search demo. No GDC login / dbGaP token. Not full-cohort ETL (see Plan 07 / [Data Acquisition BRCA](../docs/wiki/Data-Acquisition-BRCA.md)).

## What it does

1. **Build** installs Python deps only (no TCGA data baked into the image).
2. **First `docker compose up` / `docker run`** queries GDC for ~5–10 BRCA cases and downloads:
   - Clinical biotab + case demographics (age, gender, race, stage, …)
   - RNA-seq gene expression (STAR counts) for those cases
   - Small methylation files when they fit the size budget
3. **Then** runs `scripts/train_nas_demo.py` (toy NAS over a few MLP widths with leave-one-out CV).
4. Re-runs skip download when `/data/tcga/BRCA/.ready` exists (idempotent within the same container filesystem).

## Build & run

From the Bio-NAS directory:

```bash
docker compose up --build
```

Or without Compose:

```bash
docker build -f docker/Dockerfile -t bio-nas-demo:local .
docker run --rm bio-nas-demo:local
```

No data volume mounts are used — files live only inside the container.

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
