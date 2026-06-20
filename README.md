# PhDNeural

**Vertical Slice Multi-Task Neural Architecture Search**

A PhD research program that builds a generalized, multi-task Neural Architecture Search (NAS) framework using a **vertical slice** methodology: engineer the complete end-to-end multi-omic pipeline for Breast Invasive Carcinoma (BRCA) first, then abstract and deploy across four additional disease categories for comparative analysis. The framework uses [Optuna](https://optuna.org/) for distributed NAS, ingests multi-omic patient data through a unified (then generalized) pipeline, and delivers Multi-Task Learning (MTL) models with an end-to-end [Streamlit](https://streamlit.io/) inference portal.

| Resource | Link |
|----------|------|
| Repository | [github.com/AdamCankaya/PhDNeural](https://github.com/AdamCankaya/PhDNeural) |
| Project board | [PhD Master Plan (Project #2)](https://github.com/AdamCankaya/PhDNeural/projects/2) |
| Live dashboard | [adamcankaya.github.io/PhDNeural/phd_timeline_dashboard.html](https://adamcankaya.github.io/PhDNeural/phd_timeline_dashboard.html) |
| Master plan | [phd_master_plan.md](phd_master_plan.md) |

---

## 1. Project Goals

### Research question

**Does biological etiology dictate optimal neural architecture?**

The central hypothesis is that disease topology—localized oncological mutation burden (BRCA), systemic neurological degradation, immune-driven inflammation, metabolic dysregulation, and chromosomal developmental variation—should favor structurally different computational graphs. A BRCA-first vertical slice validates the full pipeline before scaling to four additional categories to test whether optimal architectures cluster by etiology (e.g., self-attention for systemic diseases vs. spatial convolutions for localized cancers).

### Vertical slice strategy

| Stage | Approach |
|-------|----------|
| **Phase 1 — BRCA anchor** | Build and validate the complete multi-omic, multi-task pipeline on TCGA BRCA data only |
| **Phase 2 — Abstraction** | Refactor hardcoded BRCA code into a universal disease pipeline with dynamic omic branches and MTL heads |
| **Phase 3 — Scaling** | Deploy generalized pipeline to Alzheimer's, rheumatoid arthritis, type 2 diabetes, and Down syndrome |
| **Phase 4 — Thesis** | Comparative structural taxonomy, SHAP interpretability, and Streamlit patient portal |

### Objectives

| Objective | Description |
|-----------|-------------|
| **BRCA proof of concept** | End-to-end pipeline on TCGA BRCA with 80/20 train/holdout split, 5-fold CV NAS, and classical baselines |
| **Comparative NAS** | Run Optuna define-by-run NAS across five disease categories after abstraction to discover category-specific optimal architectures |
| **Multi-omic ingestion** | Ingest methylation, transcriptomics, genomics (SNPs/mutations), CNVs, and demographics; omit unavailable omic layers per cohort without breaking the network |
| **Multi-Task Learning** | Three heads: diagnostic (tumor vs. normal), staging (ordinal severity), and prognostic survival (Cox-PH loss for censored data) |
| **Distributed execution** | Central PostgreSQL study store on Hetzner; Slurm workers via GitHub Actions CI/CD |
| **Inference portal** | Streamlit web application for disease-track selection, patient data upload, and MTL prediction output |

---

## 2. Expected Input and Output

### Inputs (BRCA anchor, then generalized)

| Input type | Formats | Examples |
|------------|---------|----------|
| Raw omic files | `.CSV`, `.TXT`, VCF | Methylation beta-value matrices, RNA-Seq FPKM/TPM tables, somatic mutation VCFs, CNV log2 ratio files |
| Clinical / demographic tabular data | `.CSV`, tabular joins | Age, sex, ethnicity, tumor stage, survival days |
| Labels & targets | Per-disease schema | Tumor vs. normal (diagnostic), stage I–IV (ordinal), days to live with censoring (prognostic) |

**Preprocessing constraints (training set only):**

- Strict **20% holdout test set** extracted before any preprocessing (BRCA first; same rule per disease in Phase 3)
- Demographics: Z-score standardization (continuous); one-hot encoding (categorical)
- Methylation / transcriptomics: variance-based reduction to top 10,000 highly variable features

### Outputs

| Output | Description |
|--------|-------------|
| **NAS-discovered architectures** | Optimal multi-branched PyTorch models per disease category, stored with trial metadata in PostgreSQL |
| **MTL predictions** | Disease probability (diagnostic head), predicted stage (ordinal head), prognostic timeline (Cox-PH head) |
| **Benchmark metrics** | ROC-AUC (classification tasks), concordance index / survival metrics (prognostic) vs. XGBoost, LightGBM, and ElasticNet baselines on tabular/methylation features |
| **SHAP interpretability** | Feature importance maps per omic layer and demographic variable, stratified by disease category |
| **Streamlit inference** | Interactive predictions from uploaded patient demographics and available raw omic files |

---

## 3. Planned Phases

The roadmap follows four phases in [phd_master_plan.md](phd_master_plan.md).

### Phase 1 — The Anchor (BRCA Proof of Concept)

**Theme:** Build and validate the complete vertical slice on TCGA BRCA before generalizing.

| Step | Focus | Key deliverables |
|------|-------|------------------|
| **1** | BRCA multi-omic sourcing & split | TCGA Level 3 data (methylation, RNA-Seq, mutations, CNVs, demographics); 80/20 train/holdout split before preprocessing |
| **2** | Infrastructure & database orchestration | Dockerized PostgreSQL on Hetzner; GitHub Actions → Slurm worker deployment |
| **3** | Multi-task architecture engineering | Input branches (1D-CNN/Transformer for dense omics, linear for sparse genomics); three MTL heads with cross-entropy, ordinal, and Cox-PH losses |
| **4** | Optuna NAS & baseline benchmarking | Tune 5 topologies (MLP, 1D-CNN, Transformer, TabNet, Cross-Attention Fusion); XGBoost, LightGBM, ElasticNet baselines; holdout PoC validation |

### Phase 2 — Code Abstraction & Generalization

**Theme:** Transition BRCA-specific code into a universal disease pipeline.

| Step | Focus | Key deliverables |
|------|-------|------------------|
| **1** | Refactoring base classes | Dynamic omic-layer detection in `Dataset`; adaptive MTL heads for disease-specific clinical targets |

### Phase 3 — Scaling to the Comparative Matrix

**Theme:** Run four parallel Optuna studies on the generalized pipeline.

| Step | Focus | Key deliverables |
|------|-------|------------------|
| **1** | Sourcing 4 pathologies | Alzheimer's (GEO), rheumatoid arthritis (GEO), type 2 diabetes (GEO/recountmethylation), Down syndrome (GEO) |
| **2** | High-throughput distributed execution | 4 parallel Optuna studies against Hetzner PostgreSQL; monitoring only (infrastructure proven in Phase 1) |

### Phase 4 — Thesis Synthesis & Final Deliverables

**Theme:** Comparative analysis, interpretability, and patient-facing software.

| Step | Focus | Key deliverables |
|------|-------|------------------|
| **1** | Comparative analysis (core thesis) | Structural taxonomy (CNNs vs. Transformers vs. classical by etiology); SHAP omic-layer importance |
| **2** | Patient-facing software app | Streamlit dashboard: disease track selection, multi-omic CSV upload, phenotype/stage/prognosis output |

---

## 4. Technical Specifications

### Disease categories (5 — BRCA first, then 4)

| Category | Disease | Primary source | Etiology profile |
|----------|---------|----------------|------------------|
| **Oncological (anchor)** | Breast Invasive Carcinoma (BRCA) | [TCGA / GDC Portal](https://portal.gdc.cancer.gov/) | Localized, high mutational burden |
| **Neurological** | Alzheimer's Disease | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) | Systemic, progressive structural degradation |
| **Autoimmune** | Rheumatoid Arthritis | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) | Systemic, immune-driven inflammation |
| **Metabolic** | Type 2 Diabetes | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) / [recountmethylation](https://bioconductor.org/packages/recountmethylation/) | Lifestyle, lipid/insulin driven |
| **Genetic / Developmental** | Down Syndrome | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) | Innate chromosomal variation |

### Data modalities

| Modality | Representation | Typical source | Notes |
|----------|----------------|----------------|-------|
| **Demographics** | Age, sex, ethnicity (tabular) | Clinical records | Z-score / one-hot encoding |
| **Clinical targets** | Disease-specific labels | Cohort metadata | Stage, cognitive score, survival days, etc. |
| **Epigenomic** | Methylation beta-values (0.0–1.0 at CpG sites) | TCGA, Illumina arrays | Top 10k variable CpGs after ETL |
| **Transcriptomic** | RNA-Seq FPKM or TPM (continuous) | TCGA, GEO | Top 10k variable genes; **may be omitted** per cohort |
| **Genomic** | SNPs / somatic mutations (sparse binary) | VCF files | Sparse linear branch input |
| **Structural (CNV)** | Copy number log2 ratios (continuous) | Array or sequencing CNV calls | **May be omitted** per cohort |

### Neural search topologies (5)

| Topology | Role |
|----------|------|
| **MLP** | Tabular demographics and fused representations |
| **1D-CNN** | Dense continuous omic sequences (methylation, RNA-Seq) |
| **Transformer** | Self-attention over omic feature sequences |
| **TabNet** | Attentive tabular encoding for demographics/clinical covariates |
| **Cross-Attention Fusion** | Intermediate multi-branch integration |

### MTL heads & losses

| Head | Loss | Target |
|------|------|--------|
| **Diagnostic** | Cross-entropy | Tumor vs. normal matched tissue |
| **Staging** | Ordinal loss | Stage I, II, III, or IV |
| **Prognostic** | Cox proportional hazards (Cox-PH) | Survival timeline (days to live) with censored data |

### Classical baselines

| Model | Data | Purpose |
|-------|------|---------|
| **XGBoost** | Tabular + methylation | Performance floor |
| **LightGBM** | Tabular + methylation | Performance floor |
| **ElasticNet** | Tabular + methylation | Linear performance floor |

### Optuna search space (define-by-run)

| Setting | Value / method |
|---------|----------------|
| Cross-validation | 5-fold on 80% training set (BRCA in Phase 1) |
| MTL loss weights | Tuned per head by Optuna objective |
| Pruner | `HyperbandPruner` — terminate unpromising trials early |
| Study backend | PostgreSQL on Hetzner (`load_if_exists=True`) |
| Execution | Slurm cluster job arrays via GitHub Actions CI/CD |
| Final selection | Best trial → retrain on full 80% → evaluate on 20% holdout |

---

## 5. Data Sources & Open Source Software

### Data sources

| Resource | URL | Use in PhDNeural |
|----------|-----|------------------|
| **TCGA / GDC Portal** | [portal.gdc.cancer.gov](https://portal.gdc.cancer.gov/) | BRCA anchor multi-omic and clinical data |
| **NCBI GEO** | [ncbi.nlm.nih.gov/geo](https://www.ncbi.nlm.nih.gov/geo/) | Phase 3 disease cohorts |
| **recountmethylation** | [bioconductor.org/packages/recountmethylation](https://bioconductor.org/packages/recountmethylation/) | Type 2 diabetes methylation data |

### Software stack

| Package / tool | URL | Role |
|----------------|-----|------|
| **PyTorch** | [pytorch.org](https://pytorch.org/) | Multi-branched MTL model implementation |
| **Optuna** | [optuna.org](https://optuna.org/) | Define-by-run NAS, pruning, distributed study management |
| **scikit-learn** | [scikit-learn.org](https://scikit-learn.org/) | Preprocessing, baselines, evaluation utilities |
| **XGBoost** | [xgboost.readthedocs.io](https://xgboost.readthedocs.io/) | Classical tree-based benchmark |
| **LightGBM** | [lightgbm.readthedocs.io](https://lightgbm.readthedocs.io/) | Classical tree-based benchmark |
| **PostgreSQL** | [postgresql.org](https://www.postgresql.org/) | Central Optuna study database (Hetzner) |
| **Docker** | [docker.com](https://www.docker.com/) | Containerized PostgreSQL hub |
| **Streamlit** | [streamlit.io](https://streamlit.io/) | Patient inference web portal |
| **SHAP** | [github.com/shap/shap](https://github.com/shap/shap) | Model interpretability |

### Repository tooling

| Component | Location | Purpose |
|-----------|----------|---------|
| Master plan | [phd_master_plan.md](phd_master_plan.md) | Authoritative vertical-slice roadmap and task checklist |
| Timeline dashboard | [phd_timeline_dashboard.html](phd_timeline_dashboard.html) | Interactive 4-phase progress tracker ([live](https://adamcankaya.github.io/PhDNeural/phd_timeline_dashboard.html)) |
| GitHub Projects sync | `scripts/sync_phd_to_github.py` | Sync plan tasks to [project board #2](https://github.com/AdamCankaya/PhDNeural/projects/2) |
| Setup guide | [GITHUB_PROJECTS_SETUP.md](GITHUB_PROJECTS_SETUP.md) | GitHub Projects v2 configuration and sync workflow |
| CI sync workflow | `.github/workflows/sync-phd-plan.yml` | Manual GitHub Actions re-sync trigger |

---

## License & citation

This repository documents an active PhD research program. Citation and licensing details will be added upon framework release (Phase 4).
