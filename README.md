# PhDNeural

> **Planning phase:** All roadmap tasks are tracked as open GitHub issues; none are marked done yet. Roadmap updates are **additive**—new bullets create new issues; existing issues stay open unless you explicitly pass `--close-stale` to the sync script.

**Two-Stage Multi-Omic Fusion Neural Architecture Search**

A PhD research program that builds a generalized, multi-task Neural Architecture Search (NAS) framework using a **vertical slice** methodology on Breast Invasive Carcinoma (BRCA). The roadmap is **additive by design**: vertical-slice foundation tasks (sourcing, infrastructure, architecture, Optuna NAS) remain tracked as first-class issues, while **two-stage fusion** (Stage 1 early concat baseline → Stage 2 stacked late fusion with OOF + ElasticNet) layers on top as an enhancement—not a replacement. The framework uses [Optuna](https://optuna.org/) for distributed NAS, ingests multi-omic patient data through a unified (then generalized) pipeline, and delivers **Static Multi-Task Learning (MTL)** models with an end-to-end [Streamlit](https://streamlit.io/) inference portal.

| Resource | Link |
|----------|------|
| Repository | [github.com/AdamCankaya/PhDNeural](https://github.com/AdamCankaya/PhDNeural) |
| Project board | [PhD Master Plan (Project #2)](https://github.com/AdamCankaya/PhDNeural/projects/2) |
| Live dashboard | [adamcankaya.github.io/PhDNeural/phd_timeline_dashboard.html](https://adamcankaya.github.io/PhDNeural/phd_timeline_dashboard.html) |
| Master plan | [phd_master_plan.md](phd_master_plan.md) |

The roadmap follows a **3-year academic calendar** (Summer 2026 → Spring 2029): nine semesters grouped into Year 1–3, with Phase 1–4 retained as secondary metadata on every task.

---

## Executive Strategy

Roadmap updates are **additive**: new work creates new GitHub issues; existing issues stay open unless you explicitly run sync with `--close-stale`. Two-stage fusion enhances Phase 1—it does not replace the vertical-slice BRCA foundation.

To minimize engineering risk and isolate computational bugs, the BRCA anchor pipeline follows a strict two-stage evolution:

| Stage | Approach | Purpose |
|-------|----------|---------|
| **Stage 1 — Early Fusion (Software Baseline)** | Immediate feature concatenation: $X_{\text{fused}} = [X_{\text{methylation}} \parallel X_{\text{transcriptomics}} \parallel X_{\text{genomics}} \parallel X_{\text{cnv}} \parallel X_{\text{clinical}}]$ through an MLP trunk | Stress-test HDF5 ingestion, PyTorch tensor formatting, two Static MTL heads (phenotype + severity), and distributed Optuna logging on Hetzner PostgreSQL |
| **Stage 2 — Stacked Late Fusion (Algorithmic Production)** | 4 modality-specific expert networks + ElasticNet meta-classifier on **Out-of-Fold (OOF)** predictions | Eliminate data leakage; learn interpretable biological weights via sparse $L_1/L_2$ coefficients |

![Two-Stage Stacked Late Fusion Architecture](docs/architecture-stacked-fusion.png)

---

## Static MTL Baseline

All five disease pipelines share the same **Static MTL baseline**: time-related variables are always tabular clinical inputs, and every cohort solves two prediction tasks—**phenotype** (Healthy vs. Diseased) and **severity** (ordinal, variable K per disease). Cox-PH prognostic modeling is deferred to a post-thesis optional extension (see [phd_master_plan.md](phd_master_plan.md) appendix).

### Time as tabular clinical inputs

| Feature | Description | BRCA example |
|---------|-------------|--------------|
| `age_at_sample` | Patient age at collection | TCGA `age_at_index` |
| `years_since_diagnosis` | Duration since first diagnosis | Derived from diagnosis date |
| `days_since_sample_collection` | Timeline offset within study | Study day / collection offset |
| `survival_days` | Observed follow-up duration | TCGA `days_to_death` / last follow-up |
| `time_since_last_visit` | Gap between visits | Derived (longitudinal cohorts) |

- Continuous time fields are **Z-scored on the training partition only** (no temporal sequences in the baseline).
- **Severity/stage labels must not appear in clinical inputs** (no tumor-stage leakage).
- Censoring indicators (e.g. `event_observed`) may be tabular inputs when survival duration is present.

### Two standardized tasks

| Task | Head | Loss | Target |
|------|------|------|--------|
| **Phenotype** | `phenotype_head` (1 logit) | Binary cross-entropy | `0=Healthy`, `1=Diseased` |
| **Severity** | `severity_head` (K logits) | Ordinal log-loss | `0..K-1` ordered (missing → mask) |

Per-disease mappings and `n_severity_classes` are defined in `src/config/disease_registry.yaml`.

### Stacking meta-features

Stage 2 OOF stacking: **4 modality experts × 2 tasks = 8 meta-features** per sample in $P_{\text{OOF}}$.

---

## 1. Project Goals

### Research question

**Does biological etiology dictate optimal neural architecture?**

The central hypothesis is that disease topology—localized oncological mutation burden (BRCA), systemic neurological degradation, immune-driven inflammation, metabolic dysregulation, and chromosomal developmental variation—should favor structurally different computational graphs. A BRCA-first vertical slice validates the full two-stage fusion pipeline before scaling to four additional categories.

### Roadmap timeline (3-year calendar)

| Year | Semesters | Focus |
|------|-----------|-------|
| **Year 1** (2026–2027) | Summer 2026, Fall 2026, Spring 2027 | BRCA anchor: TCGA sourcing, infrastructure, Static MTL architecture, Optuna NAS, Stage 1 early fusion, begin Stage 2 |
| **Year 2** (2027–2028) | Summer 2027, Fall 2027, Spring 2028 | Complete Stage 2 OOF stacking, `src/` scaffolds, code abstraction, 4-disease sourcing, distributed Optuna |
| **Year 3** (2028–2029) | Summer 2028, Fall 2028, Spring 2029 | Comparative taxonomy, SHAP interpretability, Streamlit portal, thesis synthesis & publication |

### Phase cross-reference (metadata)

| Phase | Theme |
|-------|-------|
| **Phase 1 — BRCA anchor** | Vertical-slice foundation (Steps 1–5, Stages 1–2) |
| **Phase 2 — Abstraction** | Refactor hardcoded BRCA code into a universal disease pipeline |
| **Phase 3 — Scaling** | Deploy generalized pipeline to Alzheimer's, RA, T2D, and Down syndrome |
| **Phase 4 — Thesis** | Comparative structural taxonomy, SHAP interpretability, and Streamlit patient portal |

### Objectives

| Objective | Description |
|-----------|-------------|
| **Stage 1 software baseline** | End-to-end early fusion on TCGA BRCA with 80/20 train/holdout split, variance masks on train only, two Static MTL heads, Optuna verification on Hetzner |
| **Stage 2 stacked fusion** | 4 expert nets (1D-CNN methylation, MLP RNA, sparse linear genomics/CNV), 5-fold OOF loop, ElasticNet meta-classifier with Optuna-tuned $\lambda$ and $\alpha$ |
| **Comparative NAS** | Run Optuna define-by-run NAS across five disease categories after abstraction |
| **Multi-omic ingestion** | Methylation, transcriptomics, genomics, CNVs, demographics; omit unavailable omic layers per cohort without breaking the network |
| **Distributed execution** | Central PostgreSQL study store on Hetzner; Slurm workers via GitHub Actions CI/CD |
| **Inference portal** | Streamlit web application for disease-track selection, patient data upload, and phenotype + severity prediction output |

---

## 2. Expected Input and Output

### Inputs (BRCA anchor, then generalized)

| Input type | Formats | Examples |
|------------|---------|----------|
| Raw omic files | `.CSV`, `.TXT`, VCF, HDF5 | Methylation beta-value matrices, RNA-Seq FPKM/TPM tables, somatic mutation VCFs, CNV log2 ratio files |
| Clinical / demographic tabular data | `.CSV`, tabular joins | Age, sex, ethnicity; **time tabular features** (`age_at_sample`, `years_since_diagnosis`, `days_since_sample_collection`, `survival_days`, `time_since_last_visit`) — Z-scored on train only |
| Labels & targets | Per-disease schema (`disease_registry.yaml`) | **Phenotype:** Healthy vs. Diseased; **Severity:** ordinal stage/severity (K varies by disease). Severity labels are **not** input features. |

**Preprocessing constraints (training set only):**

- Strict **20% holdout test set** extracted before any preprocessing
- Variance-based reduction to top 10,000 highly variable CpG sites computed **only on the 80% training partition**
- Demographics: Z-score standardization (continuous); one-hot encoding (categorical)

### Outputs

| Output | Description |
|--------|-------------|
| **Stage 1 early fusion model** | Concatenated MLP with two Static MTL heads (phenotype + severity); Optuna trial metadata in PostgreSQL |
| **Stage 2 stacked ensemble** | 4 expert networks + ElasticNet meta-classifier(s); sparse coefficient interpretability chart |
| **MTL predictions** | Phenotype probability (Healthy vs. Diseased) and predicted severity stage (ordinal) |
| **OOF meta-features** | Clean $P_{\text{OOF}}$ matrix (8 features: 4 experts × 2 tasks) covering full 80% train set with zero leakage |
| **Streamlit inference** | Interactive phenotype + severity predictions from uploaded patient demographics and available raw omic files |

---

## 3. Planned Phases

The roadmap is organized by **year and semester** in [phd_master_plan.md](phd_master_plan.md) (Summer 2026 → Spring 2029). Phase 1–4 remain as cross-reference metadata.

### Phase 1 — The Anchor (BRCA Proof of Concept)

**Theme:** Two-stage fusion evolution on TCGA BRCA before generalizing.

| Stage / Step | Focus | Key deliverables |
|--------------|-------|------------------|
| **Stage 1** | Early Fusion Proof-of-Concept | 20% holdout; train-only variance masks; HDF5 concat pipeline; MLP trunk; phenotype BCE + severity ordinal heads; Optuna verification on Hetzner |
| **Stage 2** | Stacking Late Fusion Upgrade | 4 expert nets; 5-fold OOF loop; ElasticNet meta-classifier (`penalty='elasticnet'`, `solver='saga'`); 8 meta-features; sparse coefficient interpretability |

### Phase 2 — Code Abstraction & Generalization

**Theme:** Transition BRCA-specific code into a universal disease pipeline.

| Step | Focus | Key deliverables |
|------|-------|------------------|
| **1** | Refactoring base classes | Dynamic omic-layer detection in `Dataset`; **configurable severity cardinality** via `disease_registry.yaml` |

### Phase 3 — Scaling to the Comparative Matrix

**Theme:** Run four parallel Optuna studies on the generalized pipeline.

| Step | Focus | Key deliverables |
|------|-------|------------------|
| **1** | Sourcing 4 pathologies | Alzheimer's (GEO), rheumatoid arthritis (GEO), type 2 diabetes (GEO/recountmethylation), Down syndrome (GEO) |
| **2** | High-throughput distributed execution | 4 parallel Optuna studies against Hetzner PostgreSQL |

### Phase 4 — Thesis Synthesis & Final Deliverables

**Theme:** Comparative analysis, interpretability, and patient-facing software.

| Step | Focus | Key deliverables |
|------|-------|------------------|
| **1** | Comparative analysis (core thesis) | Structural taxonomy; SHAP omic-layer importance |
| **2** | Patient-facing software app | Streamlit dashboard: disease track selection, multi-omic CSV upload, **phenotype + severity** output |

---

## 4. Technical Specifications

### Fusion architectures

| Stage | Architecture | Fusion mechanism |
|-------|-------------|------------------|
| **Stage 1 (Early Fusion)** | Single MLP trunk on concatenated features | $X_{\text{fused}} = \text{concat}(\text{all modalities})$ |
| **Stage 2 (Late Fusion)** | 4 isolated expert networks + meta-classifier | Expert predictions → $P_{\text{OOF}}$ (8 meta-features) → ElasticNet LogisticRegression |

### Expert networks (Stage 2)

| Modality | Expert architecture | Output |
|----------|---------------------|--------|
| **Methylation** | 1D-CNN | Phenotype + severity predictions |
| **Transcriptomics (RNA-Seq)** | Deep MLP | Phenotype + severity predictions |
| **Genomics / CNV** | Sparse linear network | Phenotype + severity predictions |

### OOF anti-leakage protocol

1. Hold out **20% test set** before any preprocessing.
2. On the remaining **80% train pool**, run **5-fold stratified CV** on phenotype labels.
3. For each fold $k$: train all 4 experts on folds $\neq k$; predict only on fold $k$.
4. Concatenate fold-$k$ predictions → complete **$P_{\text{OOF}}$** matrix (8 meta-features; no model ever predicts on its own training data).
5. Train ElasticNet meta-classifier(s) on $P_{\text{OOF}}$ for phenotype (and severity).
6. Retrain experts on full 80%; evaluate meta-classifier on locked 20% holdout.

### MTL heads & losses (Static baseline)

| Head | Loss | Target |
|------|------|--------|
| **Phenotype** | Binary cross-entropy | Healthy vs. Diseased |
| **Severity** | Ordinal log-loss | Ordered severity class `0..K-1` (masked when missing) |

> **Optional extension (post-thesis):** Cox-PH prognostic head — see appendix in [phd_master_plan.md](phd_master_plan.md).

### ElasticNet meta-classifier

| Setting | Value |
|---------|-------|
| Estimator | `LogisticRegression(penalty='elasticnet', solver='saga')` |
| Tuning | Optuna search over $\lambda$ (inverse `C`) and $\alpha$ (`l1_ratio`) |
| Interpretability | Inspect sparse non-zero coefficients $w$ for expert-network weights |

### Code structure

| Module | Path | Responsibility |
|--------|------|----------------|
| Disease registry | `src/config/disease_registry.yaml` | Per-disease phenotype/severity mappings and `n_severity_classes` |
| Clinical time features | `src/data/clinical_time.py` | Canonical time tabular extraction and train-only Z-scoring |
| Base dataset | `src/data/base_multiomic_dataset.py` | Abstract multi-omic `Dataset` with uniform label dict |
| BRCA dataset | `src/data/brca_dataset.py` | Stage 1/2 fusion modes; clinical inputs exclude severity labels |
| Static MTL model | `src/models/static_mtl_model.py` | Shared trunk + phenotype/severity heads |
| Early fusion model | `src/models/brca_early_fusion.py` | Stage 1 `torch.cat` + `StaticMtlEarlyFusionModel` |
| Losses | `src/models/losses.py` | `PhenotypeBCELoss`, `OrdinalSeverityLoss`, `StaticMtlLoss` |
| Cox-PH extension | `src/models/extensions/cox_prognostic.py` | Post-thesis prognostic stub (not in baseline) |
| Stacking pipeline | `src/pipelines/train_stacking.py` | Stage 2 5-fold OOF loop + ElasticNet meta-classifier (8 meta-features) |

### Disease categories (5 — BRCA first, then 4)

| Category | Disease | Primary source |
|----------|---------|----------------|
| **Oncological (anchor)** | Breast Invasive Carcinoma (BRCA) | [TCGA / GDC Portal](https://portal.gdc.cancer.gov/) |
| **Neurological** | Alzheimer's Disease | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) |
| **Autoimmune** | Rheumatoid Arthritis | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) |
| **Metabolic** | Type 2 Diabetes | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) / [recountmethylation](https://bioconductor.org/packages/recountmethylation/) |
| **Genetic / Developmental** | Down Syndrome | [NCBI GEO](https://www.ncbi.nlm.nih.gov/geo/) |

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
| **PyTorch** | [pytorch.org](https://pytorch.org/) | Early fusion MLP, expert networks, MTL heads |
| **Optuna** | [optuna.org](https://optuna.org/) | Define-by-run NAS, ElasticNet hyperparameter tuning, distributed study management |
| **scikit-learn** | [scikit-learn.org](https://scikit-learn.org/) | OOF stacking, ElasticNet meta-classifier, preprocessing |
| **XGBoost** | [xgboost.readthedocs.io](https://xgboost.readthedocs.io/) | Classical tree-based benchmark |
| **LightGBM** | [lightgbm.readthedocs.io](https://lightgbm.readthedocs.io/) | Classical tree-based benchmark |
| **PostgreSQL** | [postgresql.org](https://www.postgresql.org/) | Central Optuna study database (Hetzner) |
| **Docker** | [docker.com](https://www.docker.com/) | Containerized PostgreSQL hub |
| **Streamlit** | [streamlit.io](https://streamlit.io/) | Patient inference web portal |
| **SHAP** | [github.com/shap/shap](https://github.com/shap/shap) | Model interpretability |

### Repository tooling

| Component | Location | Purpose |
|-----------|----------|--------|
| Master plan | [phd_master_plan.md](phd_master_plan.md) | Authoritative two-stage roadmap and Static MTL baseline spec |
| Architecture diagram | [docs/architecture-stacked-fusion.png](docs/architecture-stacked-fusion.png) | Stage 2 stacked late fusion schematic |
| Timeline dashboard | [phd_timeline_dashboard.html](phd_timeline_dashboard.html) | Interactive 3-year semester progress tracker ([live](https://adamcankaya.github.io/PhDNeural/phd_timeline_dashboard.html)) |
| GitHub Projects sync | `scripts/sync_phd_to_github.py` | Sync plan tasks to [project board #2](https://github.com/AdamCankaya/PhDNeural/projects/2); sets **Year**, **Semester**, **Phase**, and **Step** fields |
| Setup guide | [GITHUB_PROJECTS_SETUP.md](GITHUB_PROJECTS_SETUP.md) | GitHub Projects v2 configuration and sync workflow |
| CI sync workflow | `.github/workflows/sync-phd-plan.yml` | Manual GitHub Actions re-sync trigger |

---

## License & citation

This repository documents an active PhD research program. Citation and licensing details will be added upon framework release (Phase 4).
