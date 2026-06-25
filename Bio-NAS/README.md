# PhDNeural: Spatio-Temporal Bio-NAS

> **Planning phase:** All roadmap tasks are tracked as open GitHub issues; none are marked done yet. Roadmap updates are **additive**—new bullets create new issues; existing issues stay open unless you explicitly pass `--close-stale` to the sync script.

**Spatio-Temporal Dual-Track Multi-Omic Fusion & Bio-NAS**

A three-year PhD research program that investigates whether Biologically-Informed Neural Architecture Search (Bio-NAS)—where neural pathways are constrained by known human anatomy (e.g., Gene Regulatory Networks)—outperforms unconstrained, mathematical optimization in multi-omic disease prediction, now utilizing a Spatio-Temporal framework. The thesis will establish Breast Invasive Carcinoma (BRCA) as the anchor dataset before conducting a comparative A/B test across four additional, distinct pathologies.

| Resource | Link |
|----------|------|
| Repository | [github.com/AdamCankaya/PhDNeural](https://github.com/AdamCankaya/PhDNeural) |
| Wiki | [github.com/AdamCankaya/PhDNeural/wiki](https://github.com/AdamCankaya/PhDNeural/wiki) |
| Project board | [PhD Master Plan (Project #2)](https://github.com/AdamCankaya/PhDNeural/projects/2) |
| Live dashboard | [adamcankaya.github.io/PhDNeural/phd_bio-nas_timeline_dashboard.html](https://adamcankaya.github.io/PhDNeural/phd_bio-nas_timeline_dashboard.html) |
| Master plan | [phd_bio-nas_master_plan.md](phd_bio-nas_master_plan.md) |

The roadmap follows a **3-year quarterly calendar**: twelve quarters grouped into Year 1–3, with Phase 1–4 retained as secondary metadata on every task.

---

## Executive Strategy

Roadmap updates are **additive**: new work creates new GitHub issues; existing issues stay open unless you explicitly run sync with `--close-stale`. 

To effectively test the core hypothesis, the framework executes a rigid **Dual-Track A/B Test**:

| Track | Approach | Purpose |
|-------|----------|---------|
| **Track A — Standard NAS (The Control)** | Unconstrained search space (layers, nodes, dropout) optimizing purely for mathematical efficiency. | Establish a robust performance baseline using state-of-the-art Late Fusion techniques and Optuna-driven hyperparameter tuning. |
| **Track B — Bio-NAS (The Innovation)** | Constrain artificial synapses using biological blueprints (KEGG, Reactome) translated into binary Adjacency Matrices (`MaskedLinear` layers). | Force Optuna to select and optimize true biological pathways. Determine if biological priors increase predictive accuracy, interpretability, and computational sparsity. |

---

## 1. Project Goals

### Research question

**Does biological etiology dictate optimal neural architecture?**

The central hypothesis is that embedding biological constraints (Bio-NAS) into deep learning models outperforms unconstrained models. A BRCA-first vertical slice validates the dual-track algorithm before scaling to four additional functional categories (neurological, autoimmune, metabolic, and chromosomal).

### Roadmap timeline (3-year calendar)

| Year | Quarters | Focus |
|------|-----------|-------|
| **Year 1** | Q1, Q2, Q3, Q4 | BRCA anchor: TCGA sourcing, infrastructure, Track A Control, Track B Bio-NAS invention, First Validation |
| **Year 2** | Q1, Q2, Q3, Q4 | Sourcing & Dual-Track execution across Alzheimer's, Rheumatoid Arthritis, Type 2 Diabetes, and Down Syndrome |
| **Year 3** | Q1, Q2, Q3, Q4 | Performance audits, LLM-driven interpretability, taxonomy mapping, thesis synthesis |

### Objectives

| Objective | Description |
|-----------|-------------|
| **Track A Control** | Standard Late Fusion meta-classifier with unconstrained Optuna hyperparameter optimization. |
| **Track B Bio-NAS** | PyTorch `MaskedLinear` layers guided by binary Adjacency Matrices built from KEGG/Reactome biological blueprints. |
| **A/B Validation** | Direct comparative performance audit (Accuracy, ROC-AUC, C-Index) across 5 diseases (10 optimization studies). |
| **Multi-omic ingestion** | Methylation, transcriptomics, genomics, CNVs, clinical data via automated PyTorch HDF5 ETL pipelines. |
| **LLM Interpretability** | Extract highly-weighted pathways from the Bio-NAS models and use LLMs to summarize the mechanistic biological reasons for selection. |

---

## 2. Expected Input and Output

### Inputs

| Input type | Formats | Examples |
|------------|---------|----------|
| Raw omic files | `.CSV`, `.TXT`, VCF, HDF5 | Methylation beta-value matrices, RNA-Seq FPKM/TPM tables, somatic mutation VCFs, CNV log2 ratio files |
| Biological Blueprints | APIs / `.CSV` | KEGG pathways, Reactome networks |
| Clinical / demographic | `.CSV`, tabular joins | Age, sex, ethnicity, staging |

**Preprocessing constraints:**
- Strict **20% holdout test set** extracted before any preprocessing to prevent data leakage.
- Demographics: Z-score standardization (continuous); one-hot encoding (categorical).

### Outputs

| Output | Description |
|--------|-------------|
| **Track A Models** | 5 highly optimized unconstrained multi-omic prediction models. |
| **Track B Models** | 5 Bio-NAS constrained multi-omic prediction models with biologically interpretable weightings. |
| **LLM Summaries** | AI-generated mechanistic explanations for why specific biological networks were activated to predict specific diseases. |
| **Comparative Metrics** | F1-Score, ROC-AUC, GPU Memory reduction, Parameter reduction statistics. |

---

## 3. Disease Categories (Comparative Matrix)

| Category | Disease | Primary source |
|----------|---------|----------------|
| **Oncological (Anchor)** | Breast Invasive Carcinoma (BRCA) | [TCGA / GDC Portal](https://portal.gdc.cancer.gov/) |
| **Neurological** | Alzheimer's Disease | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) |
| **Autoimmune** | Rheumatoid Arthritis | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) |
| **Metabolic** | Type 2 Diabetes | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) / [recount3](https://bioconductor.org/) |
| **Genetic / Chromosomal** | Down Syndrome | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) |

---

## 4. Software Stack

| Package / tool | URL | Role |
|----------------|-----|------|
| **PyTorch** | [pytorch.org](https://pytorch.org/) | ETL pipelines, MaskedLinear layers, Neural architectures |
| **Optuna** | [optuna.org](https://optuna.org/) | Standard NAS tuning and Bio-NAS pathway selection |
| **HDF5 / h5py** | [h5py.org](https://www.h5py.org/) | High-performance multi-omic data storage |
| **KEGG / Reactome** | [kegg.jp](https://www.kegg.jp/) | Biological blueprints for network constraints |
| **LLM APIs (e.g. Gemini)** | | Mechanistic pathway interpretation |

### Repository tooling

| Component | Location | Purpose |
|-----------|----------|--------|
| Master plan | [phd_bio-nas_master_plan.md](phd_bio-nas_master_plan.md) | Authoritative Bio-NAS dual-track roadmap |
| Timeline dashboard | [phd_bio-nas_timeline_dashboard.html](phd_bio-nas_timeline_dashboard.html) | Interactive 3-year quarterly progress tracker ([live](https://adamcankaya.github.io/PhDNeural/phd_bio-nas_timeline_dashboard.html)) |
| GitHub Projects sync | `scripts/sync_phd_to_github.py` | Sync plan tasks to [project board #2](https://github.com/AdamCankaya/PhDNeural/projects/2); sets **Year**, **Quarter**, **Phase**, and **Step** fields |
| Setup guide | [GITHUB_PROJECTS_BIO-NAS_SETUP.md](GITHUB_PROJECTS_BIO-NAS_SETUP.md) | GitHub Projects v2 configuration and sync workflow |
| CI sync workflow | `.github/workflows/sync-phd-plan.yml` | Manual GitHub Actions re-sync trigger |

---

## License & citation

This repository documents an active PhD research program. Citation and licensing details will be added upon framework release.
