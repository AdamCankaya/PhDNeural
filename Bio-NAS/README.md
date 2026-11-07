# PhDNeural: Spatio-Temporal Bio-NAS

> **Planning phase:** The roadmap has **24** checklist items. Each item maps **1:1** to an open GitHub issue (`label:phd-sync`) with implementation requirements. After plan edits, run sync with `--update-existing`; use `--close-stale --prune-project` to drop issues no longer in the plan.

**Spatio-Temporal Dual-Track Multi-Omic Fusion & Bio-NAS**

A three-year PhD research program that investigates whether Biologically-Informed Neural Architecture Search (Bio-NAS)—where neural pathways are constrained by known human anatomy (e.g., Gene Regulatory Networks)—outperforms unconstrained, mathematical optimization in multi-omic disease prediction, now utilizing a Spatio-Temporal framework. The thesis will establish Breast Invasive Carcinoma (BRCA) as the anchor dataset before conducting a comparative A/B test across four additional, distinct pathologies.

| Resource | Link |
|----------|------|
| Repository | [github.com/AdamCankaya/PhDNeural](https://github.com/AdamCankaya/PhDNeural) |
| Wiki | [github.com/AdamCankaya/PhDNeural/wiki](https://github.com/AdamCankaya/PhDNeural/wiki) |
| Project board | [PhD Master Plan (Project #2)](https://github.com/users/AdamCankaya/projects/2) |
| Issues (`phd-sync`) | [24 open roadmap issues](https://github.com/AdamCankaya/PhDNeural/issues?q=label%3Aphd-sync+is%3Aopen) |
| Live dashboard | [adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html) |
| Master plan (HTML) | [adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html) |
| Master plan (source) | [phd_bio-nas_master_plan.md](phd_bio-nas_master_plan.md) |
| Pages landing | [adamcankaya.github.io/PhDNeural/Bio-NAS/](https://adamcankaya.github.io/PhDNeural/Bio-NAS/) |

The roadmap follows a **3-year quarterly calendar** (Summer 2026 kickoff → Spring 2029): nine active semester blocks grouped into Year 1–3, with Phase 1–4 retained as secondary metadata on every task. Every dashboard row and master-plan HTML entry links to its GitHub issue.

Active development focuses on **BRCA**, **RA**, and **epigenetic aging (EA)** using open or available public cohorts. **Alzheimer's (ADNI)** and **T2D (KORA)** remain documented in the inventory with locked primary choices but are **out of scope for implementation** until controlled-access approvals complete.

---

## Executive Strategy

Roadmap updates create or update `phd-sync` issues from [`phd_bio-nas_master_plan.md`](phd_bio-nas_master_plan.md). Nested requirement bullets under each checklist item become the issue **Implementation requirements** section and appear on the live dashboard.

To effectively test the core hypothesis, the framework executes a rigid **Dual-Track A/B Test**:

| Track | Approach | Purpose |
|-------|----------|---------|
| **Track A — Standard NAS (The Control)** | Unconstrained search space (layers, nodes, dropout) optimizing purely for mathematical efficiency. | Establish a robust performance baseline using state-of-the-art Late Fusion techniques and Optuna-driven hyperparameter tuning. |
| **Track B — Bio-NAS (The Innovation)** | Constrain artificial synapses using biological blueprints (KEGG, Reactome) translated into binary Adjacency Matrices (`MaskedLinear` layers). | Force Optuna to select and optimize true biological pathways. Determine if biological priors increase predictive accuracy, interpretability, and computational sparsity. |

### Track × cohort schedule

Year 1–2 complete a **BRCA dual-track vertical slice**. Year 3 work on the Other 4 pathologies is justified when BRCA holdout results show a **Track B advantage** (accuracy, interpretability, and/or sparsity). See the authoritative table in [`phd_bio-nas_master_plan.md`](phd_bio-nas_master_plan.md).

| Quarter | Track scope | Cohort |
|---------|-------------|--------|
| Y1 Summer 2026 → Fall 2027 | Shared (A+B) | Kickoff + **Active 3** inventory/ETL; AD/T2D deferred |
| Y2 Spring 2028 → Fall 2028 | Track A+B → A vs B | BRCA NAS + holdout (**scaling gate**) |
| Y3 Spring 2029 | Track A + Track B | Attribution, dashboard, taxonomy, thesis, OSS |

---

## 1. Project Goals

### Research question

**Does biological etiology dictate optimal neural architecture?**

The central hypothesis is that embedding biological constraints (Bio-NAS) into deep learning models outperforms unconstrained models. A BRCA-first vertical slice validates the dual-track algorithm before scaling to four additional functional categories (neurological, autoimmune, metabolic, and chromosomal).

### Roadmap timeline (3-year calendar)

| Year | Quarters | Focus | Track / cohort | Tasks |
|------|----------|-------|----------------|------:|
| **Year 1** | Summer 2026 → Fall 2027 | Kickoff, cohort sourcing (Fall 2026), feature mapping, 4D ETL / Δt embeddings, compute + Postgres hub | Shared (A+B) · **Active 3** | 13 |
| **Year 2** | Spring 2028 → Fall 2028 | Spatial/temporal NAS modules, distributed Optuna search, holdout benchmarks & baselines | Track A+B → A vs B · BRCA | 8 |
| **Year 3** | Spring 2029 | Attribution maps, Streamlit trajectories, taxonomy synthesis, thesis & OSS release | Track A+B · BRCA + Active 3 when access allows | 8 |
| | | | | **24** |

Authoritative checklist (per-task Track scope): [`phd_bio-nas_master_plan.md`](phd_bio-nas_master_plan.md).

> **Roadmap focus (Fall 2026 / Nov 2026):** **Plan 1 complete** — **Active 3** inventory + public Docker CPU toy smoke (BRCA, RA, EA) + static dashboard; five-disease **inventory** documented with AD/T2D access deferred. **Plan 2 BRCA slice complete** — longitudinal join keys and exclusion rules ([`docs/plans/02-issue-355-longitudinal-matching-strategy.md`](docs/plans/02-issue-355-longitudinal-matching-strategy.md)); RA/EA remain stubs. **Next:** Plan 3 feature map.

### Objectives

| Objective | Description |
|-----------|-------------|
| **Spatio-temporal NAS** | Optuna-driven search over spatial (1D-CNN / Spatial Transformer) and temporal (ConvLSTM/GRU / attention) modules. |
| **Causal evaluation** | Patient-level 80/20 holdout, causal CV, and Δt embeddings for irregular intervals. |
| **Multi-omic ingestion** | Methylation, transcriptomics, and related modalities via HDF5 `(B, T, S, C)` tensors. |
| **Interpretability** | Captum/SHAP attribution over CpG sites and timestamps; Streamlit trajectory UI. |
| **Comparative matrix** | Scale from BRCA anchor toward Alzheimer's, RA, T2D, and chromosomal/epigenetic aging cohorts. |

---

## 2. Expected Input and Output

### Inputs

| Input type | Formats | Examples |
|------------|---------|----------|
| Raw omic files | `.CSV`, `.TXT`, VCF, HDF5 | Methylation beta-value matrices, RNA-Seq FPKM/TPM tables, somatic mutation VCFs, CNV log2 ratio files |
| Biological Blueprints | APIs / `.CSV` | KEGG pathways, Reactome networks |
| Clinical / demographic | `.CSV`, tabular joins | Age, sex, ethnicity, staging, visit timestamps |

**Preprocessing constraints:**
- Strict **20% holdout test set** extracted before any preprocessing to prevent data leakage.
- Demographics: Z-score standardization (continuous); one-hot encoding (categorical).

### Outputs

| Output | Description |
|--------|-------------|
| **Searched architectures** | Best spatio-temporal networks per disease study stored via Optuna. |
| **Benchmarks** | Holdout metrics vs spatial-only ablations and longitudinal RF/XGBoost baselines. |
| **Attribution maps** | CpG/time drivers exported for thesis and Streamlit views. |
| **Open-source framework** | Tagged Python release with install docs and smoke demos. |

---

## 3. Disease Categories (Comparative Matrix)

> **Note:** All five disease **primaries are locked in the inventory**; **Active 3** (BRCA, RA, EA) drives current Docker/engineering work. Alzheimer's (ADNI) and T2D (KORA) remain **deferred** pending controlled access.

| Category | Disease | Primary source |
|----------|---------|----------------|
| **Oncological (Anchor)** | Breast Invasive Carcinoma (BRCA) | [TCGA / GDC Portal](https://portal.gdc.cancer.gov/) |
| **Neurological** | Alzheimer's Disease | [ADNI / LONI](https://adni.loni.usc.edu/data-samples/adni-data/) (primary **locked**; account+DUA in progress) |
| **Autoimmune** | Rheumatoid Arthritis | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) |
| **Metabolic** | Type 2 Diabetes | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) / [recount3](https://bioconductor.org/) |
| **Aging / Epigenetic** | Epigenetic Aging cohorts | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) / related biobanks |

---

## 4. Software Stack

| Package / tool | URL | Role |
|----------------|------|------|
| **PyTorch** | [pytorch.org](https://pytorch.org/) | ETL pipelines, spatial/temporal modules, MaskedLinear (Bio-NAS) |
| **Optuna** | [optuna.org](https://optuna.org/) | Distributed architecture search + Hyperband |
| **tsai / sktime** | | Temporal/deep learning utilities |
| **HDF5 / h5py** | [h5py.org](https://www.h5py.org/) | High-performance multi-omic tensor storage |
| **captum / shap** | | Multi-dimensional attribution |
| **Streamlit** | | Trajectory dashboard |
| **KEGG / Reactome** | [kegg.jp](https://www.kegg.jp/) | Biological blueprints for network constraints |
| **Docker** | [docker.com](https://www.docker.com/) | Primary runtime for demos, ETL smoke tests, and reproducible experiments |

**Docker-first:** Prefer running Bio-NAS workloads inside the project container (`docker/Dockerfile`, `docker-compose.yml`) rather than a host-only Python venv. Details: [`docker/README.md`](docker/README.md).

### Repository tooling

| Component | Location | Purpose |
|-----------|----------|--------|
| Master plan (source) | [phd_bio-nas_master_plan.md](phd_bio-nas_master_plan.md) | Authoritative 24-item roadmap |
| Master plan (HTML) | [phd_bio-nas_master_plan.html](phd_bio-nas_master_plan.html) | Published plan with issue links ([live](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html)) |
| Timeline dashboard | [phd_bio-nas_timeline_dashboard.html](phd_bio-nas_timeline_dashboard.html) | Interactive tracker ([live](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html)) |
| Embed / render | `scripts/embed_dashboard_plan.py`, `scripts/render_master_plan_html.py` | Regenerate dashboard + HTML plan from markdown + sync state |
| GitHub Projects sync | `scripts/sync_phd_to_github.py` | Sync plan tasks to [project board #2](https://github.com/users/AdamCankaya/projects/2) |
| Tests | `tests/test_phd_parser.py` | Parser / requirements / 24-task contract |
| Setup guide | [GITHUB_PROJECTS_BIO-NAS_SETUP.md](GITHUB_PROJECTS_BIO-NAS_SETUP.md) | GitHub Projects v2 configuration and sync workflow |
| Changelog | [CHANGELOG.md](CHANGELOG.md) | Notable documentation and tooling changes |

### Sync after plan edits

```powershell
cd Bio-NAS
python -m unittest discover -s tests -v
python scripts/sync_phd_to_github.py --update-existing --close-stale --prune-project
python scripts/embed_dashboard_plan.py
```

## 5. Deploy with Docker (Windows)

Bio-NAS is meant to run **inside Docker**. On Windows, install and start **Docker Desktop**, then build the image from [`docker/Dockerfile`](docker/Dockerfile) and run it (Compose is the recommended path).

### Step 1 — Install Docker Desktop

1. Download **Docker Desktop for Windows** from [https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/).
2. Run the installer. Enable the **WSL 2** backend when prompted (recommended).
3. Finish setup and **reboot** if the installer asks you to.
4. Launch **Docker Desktop** from the Start menu and wait until the engine shows **Running** (whale icon steady in the system tray).
5. Confirm in PowerShell or Windows Terminal:

```powershell
docker version
docker compose version
```

Both commands should print client/server (or Compose) version info without connection errors.

### Step 2 — Clone the repository

```powershell
git clone https://github.com/AdamCankaya/PhDNeural.git
cd PhDNeural\Bio-NAS
```

Compose and the Dockerfile live under **`Bio-NAS/`** (not the parent `PhDNeural/` / `PhD/` root).

### Step 3 — Load the Dockerfile and build the image

The image is defined by [`docker/Dockerfile`](docker/Dockerfile). Compose wires that file via [`docker-compose.yml`](docker-compose.yml).

**Recommended (Compose — builds from the Dockerfile automatically):**

```powershell
cd PhDNeural\Bio-NAS   # if you are not already here
docker compose up --build
```

**Manual equivalent (build the Dockerfile, then run the image):**

```powershell
cd PhDNeural\Bio-NAS
docker build -f docker\Dockerfile -t bio-nas-demo:local .
docker run --rm -v "${PWD}/data/tcga:/data/tcga" -v "${PWD}/data/adni:/data/adni" bio-nas-demo:local
```

From a parent checkout that contains `Bio-NAS/`:

```powershell
docker compose -f Bio-NAS/docker-compose.yml up --build
```

### Step 4 — What the container does

On first run, the entrypoint (`docker/entrypoint.sh`):

1. Downloads a tiny **open-access** TCGA-BRCA sample from the GDC API (~5–10 joint meth+RNA cases + clinical; no login / token).
2. Writes data under `Bio-NAS\data\tcga\BRCA` and verifies inventory via the public GDC API → `data\tcga\inventory_verification\`.
3. **Plan 2:** builds BRCA longitudinal matching artifacts from an open GDC metadata discover query (default `BRCA_MATCHING_SCOPE=discover`; `smoke` keeps the 8-case manifest) → `data\tcga\BRCA\longitudinal_matching\` (`SKIP_BRCA_MATCHING=1` to skip).
4. Runs optional CPU toy NAS for **BRCA**, then the **ADNI scaffold** under `data\adni\` (status JSON while DUA pending).
5. Downloads and verifies public **RA** (GSE71841) and **Epigenetic Aging** (GSE87571) GEO smokes; runs optional toy NAS per disease; **skips T2D/KORA** by default.
6. Builds the static dashboard at `Bio-NAS\data\dashboard\dashboard.html` (pipeline steps, Plan 2 matching summary, BRCA + RA + EA rows when successful).

Re-runs skip downloads when each disease `.ready` marker already exists.

### Step 5 — View results on Windows

| Location | Path |
|----------|------|
| **Toy NAS dashboard** | `Bio-NAS\data\dashboard\dashboard.html` (always regenerated; lists failed steps if any) |
| Host (Explorer) BRCA | `Bio-NAS\data\tcga\BRCA\`, `Bio-NAS\data\tcga\inventory_verification\`, `Bio-NAS\data\tcga\BRCA\longitudinal_matching\` |
| Host (Explorer) RA / EA | `Bio-NAS\data\ra\`, `Bio-NAS\data\epigenetic_aging\` |
| Host (Explorer) ADNI | `Bio-NAS\data\adni\` (`adni_access_status.json` while DUA pending) |
| Key files | `nas_demo_results.json`, `manifest.json`, `demographics.json`, `files\`, `verification.json`, `adni_access_status.json` |
| Logs | Dozzle UI at [http://localhost:8080](http://localhost:8080), or `docker compose logs bio-nas-demo` |

Full contract, volumes, and troubleshooting: [`docker/README.md`](docker/README.md). Alzheimer's acquisition: [`docs/wiki/Data-Acquisition-Alzheimer's.md`](docs/wiki/Data-Acquisition-Alzheimer's.md).
### Notes

- Keep **Docker Desktop running** whenever you build or run containers.
- After changing `docker-compose.yml` or the Dockerfile, recreate with `docker compose up --build`.
- Host-only `pip install` is a fallback for development; see “Without Docker” in [`docker/README.md`](docker/README.md). Prefer the container for reproducible demos.

---

## License & citation

This repository documents an active PhD research program. Citation and licensing details will be added upon framework release.
