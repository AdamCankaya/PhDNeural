# PhD Master Roadmap: Vertical Slice + Two-Stage Multi-Omic Fusion (BRCA Anchor)

## Core Objective
Develop a generalized, multi-task Neural Architecture Search (NAS) framework using a **vertical slice** methodology on Breast Invasive Carcinoma (BRCA). Engineering proceeds in two additive layers: first, the full end-to-end BRCA pipeline (sourcing, infrastructure, architecture, Optuna NAS); second, a **two-stage fusion evolution**—Stage 1 stress-tests ingestion via **Early Fusion (concatenation)**, Stage 2 upgrades to a **Stacked Late Fusion Ensemble** with modality-specific expert networks and an ElasticNet meta-classifier on clean Out-of-Fold predictions. Once validated, the pipeline abstracts and scales across four additional disease categories for comparative analysis.

---

## Static MTL Baseline

All five disease pipelines share a **Static Multi-Task Learning (MTL) baseline**: time-related variables are always tabular clinical inputs, and every cohort solves the same two prediction tasks. This contract ensures Optuna studies across diseases optimize an identical mathematical problem (two weighted losses, same head topology).

### Time as Input Context (Uniform)

Time-related fields are **continuous tabular features** in the `clinical` modality—Z-scored on the training partition only (same leakage guardrails as other demographics). The baseline does **not** model patient timelines as sequences (no RNN/Transformer over visit-level time series).

| Feature | Description | BRCA example |
|---------|-------------|--------------|
| `age_at_sample` | Patient age at collection | TCGA `age_at_index` |
| `years_since_diagnosis` | Duration since first diagnosis | Derived from diagnosis date |
| `days_since_sample_collection` | Timeline offset within study | Study day / collection offset |
| `survival_days` | Observed follow-up duration | TCGA `days_to_death` / last follow-up |
| `time_since_last_visit` | Gap between visits | Derived (longitudinal cohorts) |

Censoring indicators (e.g. `event_observed`) may appear as tabular inputs when survival duration is present, but are **not** a baseline prediction target.

### Two Standardized Tasks

| Task | Head | Loss | Canonical label | Per-disease mapping |
|------|------|------|-----------------|---------------------|
| **Phenotype** | `phenotype_head` (1 logit) | Binary cross-entropy | `0=Healthy`, `1=Diseased` | BRCA: normal vs. tumor; AD: control vs. AD; etc. |
| **Severity** | `severity_head` (K logits) | Ordinal log-loss | `0..K-1` ordered | BRCA: Stage I–IV (K=4); AD: CDR/MMSE bands; T2D: HbA1c brackets; RA: DAS28 tiers |

Per-disease label mappings and `n_severity_classes` (variable K) are defined in `src/config/disease_registry.yaml`. Samples without severity labels mask the ordinal loss.

### Input / Label Separation (No Severity Leakage)

**Severity and stage source columns are labels only**—they must not appear in the clinical input concatenation branch. This fixes tumor-stage leakage where stage was previously listed as both a clinical feature and an ordinal target.

### Stacking Meta-Features

Stage 2 OOF stacking concatenates expert predictions across both tasks: **4 modality experts × 2 tasks = 8 meta-features** per sample in $P_{\text{OOF}}$.

---

## Year 1: BRCA Anchor & Two-Stage Fusion (2026–2027)
> Phases: 1

### Summer 2026 Semester: TCGA Sourcing & Data Foundation
**Phase:** 1 | **Goal:** Acquire the most feature-dense dataset to stress-test every branch of the neural network.

#### Step 1: BRCA Multi-Omic Sourcing & Split
**Goal:** Acquire the most feature-dense dataset to stress-test every branch of the neural network.
* **Source:** TCGA (Level 3 Open Access).
* **Target Modalities:** Methylation (Beta-values), Transcriptomics (RNA-Seq), Genomics (Somatic Mutations), CNVs, and Clinical Demographics.
* **The Strict Boundary:** Immediately split the BRCA dataset into an **80% Training/Validation Set** and a locked **20% Holdout Test Set** before any preprocessing.
* **HDF5 Storage:** Serialize aligned, preprocessed multi-modal tensors into partitioned HDF5 databases for memory-mapped PyTorch ingestion.

### Fall 2026 Semester: Infrastructure & Static MTL Architecture
**Phase:** 1 | **Goal:** Establish distributed execution infrastructure and engineer the multi-task neural architecture.

#### Step 2: Infrastructure & Database Orchestration
**Goal:** Establish the remote environments required for distributed Optuna execution.
* **Central Hub:** Deploy a Dockerized PostgreSQL instance on your Hetzner Linux server to act as the permanent, centralized Optuna study hub.
* **CI/CD Pipeline:** Configure a GitHub Actions runner to orchestrate and deploy your PyTorch worker scripts natively from your repository to your university's Slurm compute clusters.

#### Step 3: Engineering the Multi-Task Architecture
**Goal:** Write the PyTorch modules that handle multi-modal fusion and multi-task learning.
* **Input Branches:** Construct flexible ingestion layers for dense continuous data (1D-CNNs/Transformers for Methylation/RNA) and sparse data (Linear layers for Genomics).
* **Phenotype Head (Binary Cross-Entropy Loss):** Healthy vs. Diseased (BRCA: tumor vs. normal matched tissue).
* **Severity Head (Ordinal Loss):** Stage I, II, III, or IV (K=4 for BRCA; configurable per disease).

### Spring 2027 Semester: NAS Benchmarking & Early Fusion Baseline
**Phase:** 1 | **Goal:** Execute Optuna NAS, establish classical baselines, validate the PoC holdout, and build the Stage 1 early fusion pipeline; begin Stage 2 expert networks.

#### Step 4: Optuna NAS & Baseline Benchmarking
**Goal:** Execute the search space specifically for BRCA on the 80% Training Set using 5-Fold Cross Validation.
* **Neural Search (Optuna):** Tune the 5 deep learning topologies (MLP, 1D-CNN, Transformer, TabNet, Cross-Attention Fusion) to find the optimal BRCA network. Have Optuna dynamically weigh the multi-task loss functions.
* **Classical Baselines:** Train XGBoost, LightGBM, and ElasticNet strictly on the tabular/methylation data to establish a performance floor.
* **The PoC Validation:** Evaluate the single best Optuna-discovered model against the classical baselines using the locked 20% Holdout Test Set.

#### Stage 1: Early Fusion Proof-of-Concept
**Goal:** Establish an end-to-end software baseline using immediate feature concatenation to stress-test data ingestion, PyTorch tensor formatting, multi-task heads, and distributed Optuna logging without algorithmic complexity.
* **Data Splitting & Leakage Guardrails:** Isolate a strict **20% Holdout Test Set** from the TCGA-BRCA cohort prior to any scaling, normalization, or feature selection.
* **Variance Masks (Train Only):** Compute variance-based dimensionality reduction to select the top 10,000 highly variable methylation CpG sites **strictly within the 80% training partition** to prevent test-set leakage.
* **Concatenation Architecture:** Build a unified PyTorch HDF5 pipeline reading Methylation, RNA-Seq, CNV, Somatic Mutation, and Clinical features; fuse via $X_{\text{fused}} = [X_{\text{methylation}} \parallel X_{\text{transcriptomics}} \parallel X_{\text{genomics}} \parallel X_{\text{cnv}} \parallel X_{\text{clinical}}]$ through an MLP trunk into a dense latent vector.
* **Phenotype Head (Early Fusion):** Binary Cross-Entropy (Healthy vs. Diseased; BRCA: tumor vs. normal control).
* **Severity Head (Early Fusion):** Ordinal Log-Loss (Stages I–IV; K configurable via disease registry).
* **Optuna Verification:** Connect the early fusion model to the Dockerized PostgreSQL database on the Hetzner server and execute a small Optuna search space to verify parallel workers can read, train, and log metrics successfully.

#### Stage 2: Stacking Late Fusion Upgrade (Begin)
**Goal:** Begin training isolated modality expert networks for the stacked late fusion ensemble.
* **Methylation Expert (1D-CNN):** Train an isolated 1D-CNN feature extractor on methylation beta-values; output independent multi-task predictions.
* **Transcriptomics Expert (Deep MLP):** Train an isolated deep MLP on RNA-Seq expression; output independent multi-task predictions.

---

## Year 2: Abstraction & Comparative Scaling (2027–2028)
> Phases: 2, 3

### Summer 2027 Semester: Complete Stacked Fusion & Implementation Scaffolds
**Phase:** 1 | **Goal:** Finish Stage 2 OOF stacking with ElasticNet meta-classifier and scaffold core `src/` modules.

#### Stage 2: Stacking Late Fusion Upgrade (Complete)
**Goal:** Refactor the validated Stage 1 pipeline into a modular Late Fusion architecture with rigorous OOF stacking and an interpretable ElasticNet meta-classifier—eliminating data leakage entirely.
* **Genomics Expert (Sparse Linear):** Train an isolated sparse linear network on somatic mutation features; output independent multi-task predictions.
* **CNV Expert (Sparse Linear):** Train an isolated sparse linear network on copy-number variation features; output independent multi-task predictions.
* **Rigorous Stacking Cross-Validation (OOF):** Divide the 80% training pool into 5 folds; for each fold $k$, train all 4 expert networks on the remaining 4 folds and generate predictions on fold $k$; concatenate validation predictions across all folds to construct a complete **Clean Out-of-Fold Predictions** matrix ($P_{\text{OOF}}$) for the entire 80% dataset.
* **ElasticNet Meta-Classifier Integration:** Train downstream **Logistic Regression with ElasticNet Regularization** (`penalty='elasticnet'`, `solver='saga'`) meta-models on $P_{\text{OOF}}$ (8 meta-features: 4 experts × 2 tasks) with true biological labels; tune $\lambda$ and $\alpha$ via Optuna; extract sparse non-zero coefficients ($w$) to chart how much weight each omic expert network receives for phenotype and severity outcomes.

#### Step 5: Implementation Targets
**Goal:** Scaffold core `src/` modules that implement the two-stage fusion pipeline.
* `src/config/disease_registry.yaml` — Per-disease phenotype/severity label mappings and `n_severity_classes`.
* `src/data/clinical_time.py` — Normalize raw dates/durations into canonical Z-scored time tabular features.
* `src/data/brca_dataset.py` — PyTorch Dataset switching between flat concatenated tensor (Stage 1) and modality dict (Stage 2); clinical inputs exclude severity labels.
* `src/models/brca_early_fusion.py` — Stage 1 `torch.cat` model with MLP trunk and two Static MTL heads (phenotype BCE, severity ordinal).
* `src/models/losses.py` — `PhenotypeBCELoss` and `OrdinalSeverityLoss` for the two-task baseline.
* `src/pipelines/train_stacking.py` — Stage 2 five-fold OOF loop and sklearn ElasticNet meta-classifier on $P_{\text{OOF}}$ (4 experts × 2 tasks = 8 meta-features).

### Fall 2027 Semester: Code Abstraction & Disease Sourcing
**Phases:** 2, 3 | **Goal:** Refactor BRCA code into a universal pipeline and source four comparative disease cohorts.

#### Step 1: Refactoring the Base Classes
**Phase:** 2
**Goal:** Transition the hardcoded BRCA script into a universal disease pipeline.
* **Abstract Data Loaders:** Refactor the PyTorch `Dataset` class so it dynamically counts the number of available omic layers. If a dataset is missing RNA-Seq, the loader simply drops that tensor branch without crashing the network.
* **Configurable Severity Cardinality:** Keep the same ordinal `severity_head` topology across diseases; vary K and per-cohort label mapping via `disease_registry.yaml` (e.g., BRCA Stage I–IV vs. Alzheimer's CDR/MMSE bands).

#### Step 1: Sourcing the 4 Distinct Pathologies
**Phase:** 3
**Goal:** Gather the datasets that represent the remaining functional disease categories.
* **Neurological:** Alzheimer's Disease (GEO) - Focus on progressive structural shifts.
* **Autoimmune:** Rheumatoid Arthritis (GEO) - Focus on systemic inflammation.
* **Metabolic:** Type 2 Diabetes (GEO / `recountmethylation`) - Focus on lifestyle-driven epigenetic markers.
* **Genetic:** Down Syndrome (GEO) - Focus on innate chromosomal baseline differences.

### Spring 2028 Semester: Distributed Optuna Execution
**Phase:** 3 | **Goal:** Push the generalized pipeline to the university cluster with parallel Optuna studies.

#### Step 2: High-Throughput Distributed Execution
**Goal:** Push the generalized pipeline to the university cluster.
* Run 4 parallel Optuna studies pointing to the Hetzner PostgreSQL database.
* Because the infrastructure and code were proven in Phase 1, this phase is strictly computational execution and monitoring.

---

## Year 3: Thesis & Deliverables (2028–2029)
> Phases: 4

### Summer 2028 Semester: Comparative Analysis & Interpretability
**Phase:** 4 | **Goal:** Mine the Optuna database to answer the primary research question.

#### Step 1: The Comparative Analysis (The Core Thesis)
**Goal:** Mine the Optuna database to answer the primary research question.
* **Structural Taxonomy:** Map the final architectures against the disease types. Compare if localized, highly mutated cancers (BRCA) inherently select spatial architectures (CNNs) while systemic, slow-progressing conditions (Alzheimer's) favor self-attention mechanisms (Transformers) or classical models.
* **Interpretability:** Use SHAP to determine which specific omic layers carried the most predictive weight across different disease categories.

### Fall 2028 Semester: Patient-Facing Software Portal
**Phase:** 4 | **Goal:** Deliver a production-ready diagnostic UI.

#### Step 2: The Patient-Facing Software App
**Goal:** Deliver a production-ready diagnostic UI.
* Build a `streamlit` web dashboard.
* Users select a disease track, upload multi-omic `.CSV` data, and receive a phenotype probability and severity stage powered by the highly optimized Static MTL models.

### Spring 2029 Semester: Thesis Synthesis & Publication
**Phase:** 4 | **Goal:** Finalize thesis deliverables and open-source the framework.

#### Step 2: The Patient-Facing Software App (Publication)
**Goal:** Open-source the multi-pipeline framework and submit comparative findings.
* **Publication:** Open-source the multi-pipeline PyTorch NAS framework and submit comparative findings to a computational biology or applied machine learning venue.

---

## Timeline Mapping

| Year | Semester | Phase(s) | Focus | Tasks |
|------|----------|----------|-------|-------|
| **Year 1** | Summer 2026 | 1 | TCGA sourcing, modalities, 80/20 split, HDF5 storage | 4 |
| **Year 1** | Fall 2026 | 1 | PostgreSQL hub, GitHub Actions/Slurm CI/CD; MTL input branches + phenotype/severity heads | 5 |
| **Year 1** | Spring 2027 | 1 | Optuna NAS + classical baselines + PoC holdout; Stage 1 early fusion; begin Stage 2 expert nets | 11 |
| **Year 2** | Summer 2027 | 1 | Complete Stage 2 (OOF + ElasticNet); implementation scaffolds (`src/` modules) | 10 |
| **Year 2** | Fall 2027 | 2, 3 | Abstract loaders + severity registry; source Alzheimer's, RA, T2D, Down Syndrome | 6 |
| **Year 2** | Spring 2028 | 3 | 4 parallel Optuna studies on Slurm | 2 |
| **Year 3** | Summer 2028 | 4 | Structural taxonomy + SHAP interpretability | 2 |
| **Year 3** | Fall 2028 | 4 | Streamlit patient portal | 2 |
| **Year 3** | Spring 2029 | 4 | Thesis synthesis + publication | 1 |

---

## Optional Extension: Prognostic Survival Modeling (Cox-PH)

**Scope:** Post-thesis optional work—not part of the five-pipeline comparative NAS baseline.

A third **prognostic head** using Cox Proportional Hazards negative log-partial likelihood can be added after the Static MTL baseline is validated. Survival duration (`survival_days`) remains a tabular clinical input in the baseline; Cox-PH would treat censored time-to-event as an additional prediction target. This extension enables prognostic timeline outputs in Streamlit and a 4-experts × 3-tasks = 12 meta-feature stacking variant, but is deferred to keep all Optuna studies comparable on the shared two-task contract.
