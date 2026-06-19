# PhDNeural

**Comparative Neural Architecture Search for Multi-Task, Multi-Omic Disease Prediction**

A three-year PhD research program to discover whether biological etiology dictates optimal neural architecture across five disease categories. The framework uses [Optuna](https://optuna.org/) for distributed NAS, ingests multi-omic patient data through five independent ETL pipelines, and delivers Multi-Task Learning (MTL) models with an end-to-end [Streamlit](https://streamlit.io/) inference portal.

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

The central hypothesis is that disease topology—localized oncological mutation burden, systemic neurological degradation, immune-driven inflammation, metabolic dysregulation, and chromosomal developmental variation—should favor structurally different computational graphs. Comparative NAS across five independent pipelines will test whether optimal architectures cluster by etiology (e.g., self-attention for systemic diseases vs. spatial convolutions for localized cancers).

### Objectives

| Objective | Description |
|-----------|-------------|
| **Comparative NAS** | Run Optuna define-by-run NAS independently across five disease categories to discover category-specific optimal architectures |
| **Multi-omic ingestion** | Ingest methylation, transcriptomics, genomics (SNPs/mutations), CNVs, and demographics via five disease-specific ETL pipelines that preserve modality availability per cohort |
| **Multi-Task Learning** | Train unified models with three heads: disease presence (diagnostic), staging (ordinal severity), and prognostic survival (timeline regression) |
| **Distributed execution** | Coordinate parallel NAS trials across university Slurm clusters through a central PostgreSQL study store (`load_if_exists=True`) |
| **Inference portal** | Deliver a Streamlit web application as the final software artifact for disease-category selection, patient data upload, and MTL prediction output |

---

## 2. Expected Input and Output

### Inputs (per disease pipeline)

Each of the five pipelines accepts disease-specific raw and clinical inputs. Pipelines omit omic layers that are unavailable for a given cohort without breaking shared framework code.

| Input type | Formats | Examples |
|------------|---------|----------|
| Raw omic files | `.CSV`, `.TXT`, VCF | Methylation beta-value matrices, RNA-Seq FPKM/TPM tables, somatic mutation VCFs, CNV log2 ratio files |
| Processed tensors | HDF5 (post-ETL) | Partitioned multi-modal tensors serialized after normalization and feature selection |
| Clinical / demographic tabular data | `.CSV`, tabular joins | Age, sex, ethnicity, and disease-specific covariates |
| Labels & targets | Per-pipeline schema | Tumor stage (BRCA), cognitive score (Alzheimer's), survival days, disease presence, severity ordinals |

**Preprocessing constraints (training set only):**

- Strict **20% holdout test set** extracted before any preprocessing
- Demographics: Z-score standardization (continuous); one-hot encoding (categorical)
- Methylation / transcriptomics: variance-based reduction to top 10,000 highly variable features

### Outputs

| Output | Description |
|--------|-------------|
| **NAS-discovered architectures** | Optimal multi-branched PyTorch models per disease category, stored with trial metadata in PostgreSQL |
| **MTL predictions** | Disease probability (diagnostic head), predicted stage (ordinal head), prognostic timeline (regression head) |
| **Benchmark metrics** | ROC-AUC (classification tasks), MSE (prognostic regression) vs. XGBoost and ElasticNet baselines on tabular/methylation features |
| **SHAP interpretability** | Feature importance maps per omic layer and demographic variable, stratified by disease category |
| **Streamlit inference** | Interactive predictions with confidence scores from uploaded patient demographics and available raw omic files |

---

## 3. Planned Phases

The roadmap spans three years grouped into three phases. Semester breakdowns follow [phd_master_plan.md](phd_master_plan.md).

### Phase 1 — Year 1: Data Sourcing & Multi-Omic ETL

**Theme:** Secure cohorts, build five independent pipelines, and provision the distributed NAS infrastructure.

| Semester | Focus | Key deliverables |
|----------|-------|------------------|
| **Fall** | 5-category disease selection & sourcing | Curate BRCA (TCGA), Alzheimer's, rheumatoid arthritis, type 2 diabetes, and Down syndrome cohorts; document available omic modalities per disease |
| **Spring** | 5 independent pipelines & normalization | 20% holdout split; five PyTorch `Dataset` classes; dynamic normalization on 80% training data; HDF5 partitioned storage |
| **Summer** | Software stack & PostgreSQL hub | Core Python stack (`torch`, `optuna`, `scikit-learn`, `xgboost`, `h5py`, `pandas`, `numpy`); Dockerized PostgreSQL + `psycopg2-binary` for distributed trial tracking |

### Phase 2 — Year 2: Distributed NAS & Multi-Task Execution

**Theme:** Define the searchable architecture toolkit, execute distributed Optuna NAS, and benchmark against classical models.

| Semester | Focus | Key deliverables |
|----------|-------|------------------|
| **Fall** | Multi-omic architecture toolkit | Multi-branched network body (tabular, epigenomic/transcriptomic, genomic/CNV); early and intermediate fusion modules; three MTL output heads |
| **Spring** | Execution & K-fold cross-validation | Optuna objective with 5-fold CV on 80% training set; MTL loss weight tuning; Slurm deployment with `HyperbandPruner` |
| **Summer** | Holdout evaluation & benchmarking | Retrain optimal architecture per disease on full 80%; evaluate on untouched 20% holdout; XGBoost and ElasticNet baselines |

### Phase 3 — Year 3: Synthesis & Final Deliverables

**Theme:** Interpretability, clinical-facing software, and thesis synthesis.

| Semester | Focus | Key deliverables |
|----------|-------|------------------|
| **Fall** | Interpretability & patient portal | SHAP feature importance per omic layer; Streamlit inference app (disease selection, file upload, MTL output) |
| **Spring & Summer** | Thesis defense & publication | Structural taxonomy analysis (e.g., Transformers vs. CNNs by etiology); open-source NAS framework release; submission to computational biology venues (e.g., ISMB, NeurIPS) |

---

## 4. Technical Specifications

### Disease categories (5)

| Category | Disease | Primary source | Etiology profile |
|----------|---------|----------------|------------------|
| **Oncological** | Breast Invasive Carcinoma (BRCA) | [TCGA / GDC Portal](https://portal.gdc.cancer.gov/) | Localized, high mutational burden |
| **Neurological** | Alzheimer's Disease | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) | Systemic, progressive structural degradation |
| **Autoimmune** | Rheumatoid Arthritis | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) | Systemic, immune-driven inflammation |
| **Metabolic** | Type 2 Diabetes | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) / [recountmethylation](https://bioconductor.org/packages/recountmethylation/) | Lifestyle, lipid/insulin driven |
| **Genetic / Developmental** | Down Syndrome | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) | Innate chromosomal variation |

### Data modalities

| Modality | Representation | Typical source | Notes |
|----------|----------------|----------------|-------|
| **Demographics** | Age, sex, ethnicity (tabular) | Clinical records | Z-score / one-hot encoding; present in all pipelines |
| **Clinical targets** | Disease-specific labels | Cohort metadata | Stage, cognitive score, survival days, etc. |
| **Epigenomic** | Methylation beta-values (0.0–1.0 at CpG sites) | Illumina arrays, recountmethylation | Anchor modality; top 10k variable CpGs after ETL |
| **Transcriptomic** | RNA-Seq FPKM or TPM (continuous) | GEO, TCGA | Top 10k variable genes; **may be omitted** per pipeline |
| **Genomic** | SNPs / somatic mutations (sparse binary) | VCF files | Sparse linear branch input; availability varies by cohort |
| **Structural (CNV)** | Copy number log2 ratios (continuous) | Array or sequencing CNV calls | **May be omitted** per pipeline |

**Per-pipeline omic availability:** Each disease pipeline is independent. If a cohort lacks an omic layer (e.g., no RNA-Seq for rheumatoid arthritis), that branch is omitted at the dataset and NAS levels—Optuna conditionally skips unavailable branches via define-by-run logic.

### Structural models & branches (Optuna-assembled)

| Component | Candidate architectures | Role |
|-----------|------------------------|------|
| **Tabular branch** | MLP, TabNet | Demographics and clinical covariates |
| **Epigenomic / transcriptomic branch** | 1D-CNN, Transformer Encoder | Dense continuous omic sequences |
| **Genomic / CNV branch** | Sparse linear layers | High-dimensional sparse mutation matrices; continuous CNV ratios |
| **Fusion** | Early (concatenation), Intermediate (cross-attention) | Combine active branch representations |
| **MTL heads** | Diagnostic (softmax), Staging (ordinal classification), Prognostic (linear regression) | Simultaneous multi-task output |

### Optuna search space (define-by-run)

Optuna dynamically constructs architectures per trial. The search space is conditional on which omic layers exist for each disease pipeline.

#### Architecture topology

| Hyperparameter | Search range / choices | Notes |
|----------------|------------------------|-------|
| Branch inclusion | Include / skip per omic layer | Conditional on pipeline availability |
| Tabular encoder | `MLP` \| `TabNet` | Demographics branch |
| Sequence encoder | `1D-CNN` \| `Transformer` | Methylation and/or transcriptomic branch |
| Genomic encoder | Sparse linear (width tuned) | Applied when mutation data present |
| Fusion strategy | `early_concat` \| `cross_attention` | Governs multi-branch integration |
| Hidden layers (per branch) | 1–4 layers | Depth per active branch |
| Layer width | e.g., 64, 128, 256, 512, 1024 | Per-layer; branch-specific |
| Activation function | `ReLU`, `GELU`, `LeakyReLU`, `SiLU` | Per-branch or shared |
| Dropout rate | 0.0–0.5 | Per-branch regularization |

#### Sequence-model specifics

| Hyperparameter | Search range / choices | Applies to |
|----------------|------------------------|------------|
| CNN kernel sizes | 3, 5, 7, 11 | 1D-CNN branch |
| CNN filter counts | 32–256 (per layer) | 1D-CNN branch |
| Transformer layers | 1–6 | Transformer branch |
| Attention heads | 2, 4, 8 | Transformer branch |
| Embedding dimension | 64–512 | Transformer branch |

#### Training & MTL

| Hyperparameter | Search range / choices | Notes |
|----------------|------------------------|-------|
| Learning rate | log-uniform ~1e-5–1e-2 | Adam / AdamW optimizer |
| Batch size | 16, 32, 64, 128 | Subject to GPU memory |
| Weight decay | 1e-6–1e-3 | L2 regularization |
| MTL loss weights | Tuned per head (diagnostic, staging, prognostic) | Combined weighted loss; Optuna objective |
| Epochs / budget | Capped per trial | Early-stopped by pruner |

#### NAS orchestration

| Setting | Value / method |
|---------|----------------|
| Cross-validation | 5-fold on 80% training set |
| Pruner | `HyperbandPruner` — terminate unpromising trials early |
| Study backend | PostgreSQL (distributed, `load_if_exists=True`) |
| Execution | Slurm cluster job arrays pointed at central study DB |
| Final selection | Best trial per disease → retrain on full 80% → evaluate on 20% holdout |

---

## 5. Data Sources & Open Source Software

### Data sources

| Resource | URL | Use in PhDNeural |
|----------|-----|------------------|
| **TCGA / GDC Portal** | [portal.gdc.cancer.gov](https://portal.gdc.cancer.gov/) | BRCA multi-omic and clinical data |
| **NCBI GEO** | [ncbi.nlm.nih.gov/geo](https://www.ncbi.nlm.nih.gov/geo/) | Alzheimer's, rheumatoid arthritis, type 2 diabetes, Down syndrome cohorts |
| **recountmethylation** | [bioconductor.org/packages/recountmethylation](https://bioconductor.org/packages/recountmethylation/) | Compiled public methylation array data (GEO-derived); database at [methylation.recount.bio](https://methylation.recount.bio/) |
| **Illumina Infinium Methylation Arrays** | [illumina.com — Infinium Methylation Arrays](https://www.illumina.com/products/by-type/microarray-kits/infinium-methylation-arrays.html) | Platform reference for beta-value methylation arrays (HM450K, EPIC/HM850K) |

### Software stack

| Package / tool | URL | Role |
|----------------|-----|------|
| **PyTorch** | [pytorch.org](https://pytorch.org/) | Multi-branched MTL model implementation |
| **Optuna** | [optuna.org](https://optuna.org/) | Define-by-run NAS, pruning, distributed study management |
| **scikit-learn** | [scikit-learn.org](https://scikit-learn.org/) | Preprocessing, baselines, evaluation utilities |
| **XGBoost** | [xgboost.readthedocs.io](https://xgboost.readthedocs.io/) | Classical tree-based benchmark |
| **pandas** | [pandas.pydata.org](https://pandas.pydata.org/) | Tabular data handling |
| **numpy** | [numpy.org](https://numpy.org/) | Numerical operations |
| **h5py** | [h5py.org](https://www.h5py.org/) | HDF5 serialized tensor I/O |
| **PostgreSQL** | [postgresql.org](https://www.postgresql.org/) | Central Optuna study database |
| **psycopg2-binary** | [pypi.org/project/psycopg2-binary](https://pypi.org/project/psycopg2-binary/) | PostgreSQL Python driver |
| **Docker** | [docker.com](https://www.docker.com/) | Containerized PostgreSQL hub deployment |
| **Streamlit** | [streamlit.io](https://streamlit.io/) | Patient inference web portal |
| **SHAP** | [github.com/shap/shap](https://github.com/shap/shap) | Model interpretability and feature attribution |

### Repository tooling

| Component | Location | Purpose |
|-----------|----------|---------|
| Master plan | [phd_master_plan.md](phd_master_plan.md) | Authoritative 3-year roadmap and task checklist |
| Timeline dashboard | [phd_timeline_dashboard.html](phd_timeline_dashboard.html) | Interactive progress tracker ([live](https://adamcankaya.github.io/PhDNeural/phd_timeline_dashboard.html)) |
| GitHub Projects sync | `scripts/sync_phd_to_github.py` | Sync plan tasks to [project board #2](https://github.com/AdamCankaya/PhDNeural/projects/2) |
| Setup guide | [GITHUB_PROJECTS_SETUP.md](GITHUB_PROJECTS_SETUP.md) | GitHub Projects v2 configuration and sync workflow |
| CI sync workflow | `.github/workflows/sync-phd-plan.yml` | Manual GitHub Actions re-sync trigger |

---

## License & citation

This repository documents an active PhD research program. Citation and licensing details will be added upon framework release (Year 3, Spring/Summer).
