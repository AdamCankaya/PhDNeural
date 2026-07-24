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

The roadmap follows a **3-year quarterly calendar** (Fall 2026 → Summer 2029): twelve quarters grouped into Year 1–3, with Phase 1–4 retained as secondary metadata on every task. Every dashboard row and master-plan HTML entry links to its GitHub issue.

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
| Y1 Fall 2026 → Summer 2027 | Shared (A+B) | BRCA-first ETL/infra; All 5 inventory in Fall |
| Y2 Fall 2027 → Winter 2027 | Track A + Track B modules | BRCA spatial/temporal search space |
| Y2 Spring 2028 | Track A then Track B | BRCA Optuna studies |
| Y2 Summer 2028 | Track A vs B | BRCA holdout + ablations (**scaling gate**) |
| Y3 Fall 2028 → Winter 2028 | Track A + Track B | BRCA attribution + dashboard |
| Y3 Spring 2029 → Summer 2029 | Track A + Track B | Other 4 / All 5 taxonomy, thesis, OSS |

---

## 1. Project Goals

### Research question

**Does biological etiology dictate optimal neural architecture?**

The central hypothesis is that embedding biological constraints (Bio-NAS) into deep learning models outperforms unconstrained models. A BRCA-first vertical slice validates the dual-track algorithm before scaling to four additional functional categories (neurological, autoimmune, metabolic, and chromosomal).

### Roadmap timeline (3-year calendar)

| Year | Quarters | Focus | Track / cohort | Tasks |
|------|----------|-------|----------------|------:|
| **Year 1** | Fall 2026 → Summer 2027 | Longitudinal cohort sourcing, feature mapping, 4D ETL / Δt embeddings, compute + Postgres hub | Shared (A+B) · BRCA-first | 9 |
| **Year 2** | Fall 2027 → Summer 2028 | Spatial/temporal NAS modules, distributed Optuna search, holdout benchmarks & baselines | Track A+B → A vs B · BRCA | 8 |
| **Year 3** | Fall 2028 → Summer 2029 | Attribution maps, Streamlit trajectories, taxonomy synthesis, thesis & OSS release | Track A+B · BRCA then Other 4 / All 5 | 7 |
| | | | | **24** |

Authoritative checklist (per-task Track scope): [`phd_bio-nas_master_plan.md`](phd_bio-nas_master_plan.md).

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

| Category | Disease | Primary source |
|----------|---------|----------------|
| **Oncological (Anchor)** | Breast Invasive Carcinoma (BRCA) | [TCGA / GDC Portal](https://portal.gdc.cancer.gov/) |
| **Neurological** | Alzheimer's Disease | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) |
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

---

## License & citation

This repository documents an active PhD research program. Citation and licensing details will be added upon framework release.
