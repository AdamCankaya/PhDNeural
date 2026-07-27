# PhDNeural Wiki

Welcome to the **PhDNeural** project wiki — a published mirror of documentation under [`docs/wiki/`](https://github.com/AdamCankaya/PhDNeural/tree/main/Bio-NAS/docs/wiki) in the repository.

> **Planning phase:** **24** roadmap checklist items, each with a 1:1 open GitHub issue (`label:phd-sync`) containing implementation requirements. Sync with `--update-existing`; prune orphans with `--close-stale --prune-project`.

## Quick links

| Resource | Link |
|----------|------|
| Repository | [github.com/AdamCankaya/PhDNeural](https://github.com/AdamCankaya/PhDNeural) |
| Project board | [PhD Master Plan (Project #2)](https://github.com/users/AdamCankaya/projects/2) |
| Issues (`phd-sync`) | [Open roadmap issues](https://github.com/AdamCankaya/PhDNeural/issues?q=label%3Aphd-sync+is%3Aopen) |
| Pages landing | [adamcankaya.github.io/PhDNeural/Bio-NAS/](https://adamcankaya.github.io/PhDNeural/Bio-NAS/) |
| Live dashboard | [phd_bio-nas_timeline_dashboard.html](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html) |
| Master plan (HTML) | [phd_bio-nas_master_plan.html](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html) |
| Master plan (source) | [phd_bio-nas_master_plan.md](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/phd_bio-nas_master_plan.md) |
| README | [Bio-NAS/README.md](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/README.md) |
| Deploy (Docker) | [README § Deploy with Docker (Windows)](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/README.md#5-deploy-with-docker-windows) · [docker/README.md](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/docker/README.md) |

## Deploy with Docker (quick start)

Bio-NAS runs **inside Docker**. On Windows:

1. Install and start [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) (WSL 2 backend recommended). Wait until the engine is **Running**.
2. Clone the repo and open a terminal in `Bio-NAS/`.
3. Load the Dockerfile and run the image via Compose:

```powershell
cd Bio-NAS
docker compose up --build
```

Or build/run manually: `docker build -f docker\Dockerfile -t bio-nas-demo:local .` then `docker run --rm -v "${PWD}/data/tcga:/data/tcga" bio-nas-demo:local`.

First run downloads a tiny open-access TCGA-BRCA sample and runs the toy NAS demo; results appear under `Bio-NAS\data\tcga\BRCA` on the host. Full steps and troubleshooting: [Bio-NAS README § 5](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/README.md#5-deploy-with-docker-windows) and [docker/README.md](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/docker/README.md).

## Research overview

**Spatio-Temporal Dual-Track Multi-Omic Fusion & Bio-NAS** — BRCA as the anchor cohort, scaling toward five disease categories over a **3-year academic calendar** (Fall 2026 → Summer 2029).

| Track | Approach | Purpose |
|-------|----------|---------|
| **Track A — Standard NAS (Control)** | Unconstrained hyperparameter / architecture search | Mathematical efficiency baseline |
| **Track B — Bio-NAS (Innovation)** | Pathway-constrained layers (KEGG/Reactome) | Biological priors for accuracy, interpretability, sparsity |

**Scaling gate:** Years 1–2 run Track A and Track B on **BRCA**. Year 3 dual-track work on the **Other 4** (Alzheimer’s, RA, T2D, Epigenetic Aging) is justified when BRCA holdout shows a Track B advantage.

| Period | Track scope | Cohort |
|--------|-------------|--------|
| Y1 | Shared (A+B) | BRCA-first ETL/infra; All 5 inventory |
| Y2 modules + search | Track A + Track B → Track A then B | BRCA |
| Y2 Summer benchmarks | Track A vs B | BRCA (**scaling gate**) |
| Y3 Fall–Winter | Track A + Track B | BRCA attribution + dashboard |
| Y3 Spring–Summer | Track A + Track B | Other 4 / All 5 → thesis + OSS |

Every timeline item on the dashboard and master-plan HTML links to its GitHub issue. Per-task Track scope lives in the [master plan](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/phd_bio-nas_master_plan.md); design rationale is in the [FAQ](FAQ-and-Troubleshooting).

## Wiki navigation

| Page | Description |
|------|-------------|
| [Workflow](Workflow) | Master plan → dashboard / HTML → GitHub sync loop |
| [Roadmap and Tracking](Roadmap-and-Tracking) | 3-year quarter calendar, 24 tasks, issue format, labels |
| [Static MTL Baseline](Static-MTL-Baseline) | Multi-task prediction contract |
| [Code Map and Status](Code-Map-and-Status) | `src/` implementation status |
| [Glossary](Glossary) | Track A/B, scaling gate, Bio-NAS keywords |
| [Infrastructure Runbook](Infrastructure-Runbook) | Hetzner PostgreSQL, Docker Desktop / Compose, Slurm CI/CD |
| [Data Acquisition BRCA](Data-Acquisition-BRCA) | TCGA sourcing, HDF5, disease registry, Docker smoke |
| [Architecture Decisions](Architecture-Decisions) | ADRs for Bio-NAS and MTL design |
| [Experiment Log Template](Experiment-Log-Template) | Reproducible experiment records |
| [FAQ and Troubleshooting](FAQ-and-Troubleshooting) | Research design + sync/dashboard FAQs |
