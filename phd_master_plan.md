# PhD Master Roadmap: Vertical Slice + Two-Stage Multi-Omic Fusion (BRCA Anchor)

## Core Objective
Develop a generalized, multi-task Neural Architecture Search (NAS) framework using a **vertical slice** methodology on Breast Invasive Carcinoma (BRCA). Engineering proceeds in two additive layers: first, the full end-to-end BRCA pipeline (sourcing, infrastructure, architecture, Optuna NAS); second, a **two-stage fusion evolution**—Stage 1 stress-tests ingestion via **Early Fusion (concatenation)**, Stage 2 upgrades to a **Stacked Late Fusion Ensemble** with modality-specific expert networks and an ElasticNet meta-classifier on clean Out-of-Fold predictions. Once validated, the pipeline abstracts and scales across four additional disease categories for comparative analysis.

---

## Phase 1: The Anchor (BRCA Proof of Concept)

### Step 1: BRCA Multi-Omic Sourcing & Split
**Goal:** Acquire the most feature-dense dataset to stress-test every branch of the neural network.
* **Source:** TCGA (Level 3 Open Access).
* **Target Modalities:** Methylation (Beta-values), Transcriptomics (RNA-Seq), Genomics (Somatic Mutations), CNVs, and Clinical Demographics.
* **The Strict Boundary:** Immediately split the BRCA dataset into an **80% Training/Validation Set** and a locked **20% Holdout Test Set** before any preprocessing.
* **HDF5 Storage:** Serialize aligned, preprocessed multi-modal tensors into partitioned HDF5 databases for memory-mapped PyTorch ingestion.

### Step 2: Infrastructure & Database Orchestration
**Goal:** Establish the remote environments required for distributed Optuna execution.
* **Central Hub:** Deploy a Dockerized PostgreSQL instance on your Hetzner Linux server to act as the permanent, centralized Optuna study hub.
* **CI/CD Pipeline:** Configure a GitHub Actions runner to orchestrate and deploy your PyTorch worker scripts natively from your repository to your university's Slurm compute clusters.

### Step 3: Engineering the Multi-Task Architecture
**Goal:** Write the PyTorch modules that handle multi-modal fusion and multi-task learning.
* **Input Branches:** Construct flexible ingestion layers for dense continuous data (1D-CNNs/Transformers for Methylation/RNA) and sparse data (Linear layers for Genomics).
* **Diagnostic Head (Cross-Entropy Loss):** Tumor vs. Normal matched tissue.
* **Staging Head (Ordinal Loss):** Stage I, II, III, or IV.
* **Prognostic Head (Cox-PH Loss):** Survival timeline (Days to Live) accounting for censored data.

### Step 4: Optuna NAS & Baseline Benchmarking
**Goal:** Execute the search space specifically for BRCA on the 80% Training Set using 5-Fold Cross Validation.
* **Neural Search (Optuna):** Tune the 5 deep learning topologies (MLP, 1D-CNN, Transformer, TabNet, Cross-Attention Fusion) to find the optimal BRCA network. Have Optuna dynamically weigh the multi-task loss functions.
* **Classical Baselines:** Train XGBoost, LightGBM, and ElasticNet strictly on the tabular/methylation data to establish a performance floor.
* **The PoC Validation:** Evaluate the single best Optuna-discovered model against the classical baselines using the locked 20% Holdout Test Set.

### Stage 1: Early Fusion Proof-of-Concept
**Goal:** Establish an end-to-end software baseline using immediate feature concatenation to stress-test data ingestion, PyTorch tensor formatting, multi-task heads, and distributed Optuna logging without algorithmic complexity.
* **Data Splitting & Leakage Guardrails:** Isolate a strict **20% Holdout Test Set** from the TCGA-BRCA cohort prior to any scaling, normalization, or feature selection.
* **Variance Masks (Train Only):** Compute variance-based dimensionality reduction to select the top 10,000 highly variable methylation CpG sites **strictly within the 80% training partition** to prevent test-set leakage.
* **Concatenation Architecture:** Build a unified PyTorch HDF5 pipeline reading Methylation, RNA-Seq, CNV, Somatic Mutation, and Clinical features; fuse via $X_{\text{fused}} = [X_{\text{methylation}} \parallel X_{\text{transcriptomics}} \parallel X_{\text{genomics}} \parallel X_{\text{cnv}} \parallel X_{\text{clinical}}]$ through an MLP trunk into a dense latent vector.
* **Diagnostic Head (Early Fusion):** Binary Cross-Entropy (Tumor vs. Normal control).
* **Staging Head (Early Fusion):** Ordinal Log-Loss (Stages I–IV).
* **Prognostic Head (Early Fusion):** Cox Proportional Hazards Negative Log-Partial Likelihood (survival timelines with right-censored data).
* **Optuna Verification:** Connect the early fusion model to the Dockerized PostgreSQL database on the Hetzner server and execute a small Optuna search space to verify parallel workers can read, train, and log metrics successfully.

### Stage 2: Stacking Late Fusion Upgrade
**Goal:** Refactor the validated Stage 1 pipeline into a modular Late Fusion architecture with rigorous OOF stacking and an interpretable ElasticNet meta-classifier—eliminating data leakage entirely.
* **Methylation Expert (1D-CNN):** Train an isolated 1D-CNN feature extractor on methylation beta-values; output independent multi-task predictions.
* **Transcriptomics Expert (Deep MLP):** Train an isolated deep MLP on RNA-Seq expression; output independent multi-task predictions.
* **Genomics Expert (Sparse Linear):** Train an isolated sparse linear network on somatic mutation features; output independent multi-task predictions.
* **CNV Expert (Sparse Linear):** Train an isolated sparse linear network on copy-number variation features; output independent multi-task predictions.
* **Rigorous Stacking Cross-Validation (OOF):** Divide the 80% training pool into 5 folds; for each fold $k$, train all 4 expert networks on the remaining 4 folds and generate predictions on fold $k$; concatenate validation predictions across all folds to construct a complete **Clean Out-of-Fold Predictions** matrix ($P_{\text{OOF}}$) for the entire 80% dataset.
* **ElasticNet Meta-Classifier Integration:** Train a downstream **Logistic Regression with ElasticNet Regularization** (`penalty='elasticnet'`, `solver='saga'`) on $P_{\text{OOF}}$ with true biological labels; tune $\lambda$ and $\alpha$ via Optuna; extract sparse non-zero coefficients ($w$) to chart how much weight each omic expert network receives for diagnostic outcomes.

---

## Phase 2: Code Abstraction & Generalization

### Step 1: Refactoring the Base Classes
**Goal:** Transition the hardcoded BRCA script into a universal disease pipeline.
* **Abstract Data Loaders:** Refactor the PyTorch `Dataset` class so it dynamically counts the number of available omic layers. If a dataset is missing RNA-Seq, the loader simply drops that tensor branch without crashing the network.
* **Dynamic Output Heads:** Ensure the MTL heads adapt to the clinical data available (e.g., swapping "Tumor Stage" for "Cognitive Score").

---

## Phase 3: Scaling to the Comparative Matrix

### Step 1: Sourcing the 4 Distinct Pathologies
**Goal:** Gather the datasets that represent the remaining functional disease categories.
* **Neurological:** Alzheimer's Disease (GEO) - Focus on progressive structural shifts.
* **Autoimmune:** Rheumatoid Arthritis (GEO) - Focus on systemic inflammation.
* **Metabolic:** Type 2 Diabetes (GEO / `recountmethylation`) - Focus on lifestyle-driven epigenetic markers.
* **Genetic:** Down Syndrome (GEO) - Focus on innate chromosomal baseline differences.

### Step 2: High-Throughput Distributed Execution
**Goal:** Push the generalized pipeline to the university cluster.
* Run 4 parallel Optuna studies pointing to the Hetzner PostgreSQL database.
* Because the infrastructure and code were proven in Phase 1, this phase is strictly computational execution and monitoring.

---

## Phase 4: Thesis Synthesis & Final Deliverables

### Step 1: The Comparative Analysis (The Core Thesis)
**Goal:** Mine the Optuna database to answer the primary research question.
* **Structural Taxonomy:** Map the final architectures against the disease types. Compare if localized, highly mutated cancers (BRCA) inherently select spatial architectures (CNNs) while systemic, slow-progressing conditions (Alzheimer's) favor self-attention mechanisms (Transformers) or classical models.
* **Interpretability:** Use SHAP to determine which specific omic layers carried the most predictive weight across different disease categories.

### Step 2: The Patient-Facing Software App
**Goal:** Deliver a production-ready diagnostic UI.
* Build a `streamlit` web dashboard.
* Users select a disease track, upload multi-omic `.CSV` data, and receive a phenotype probability, severity stage, and prognostic timeline powered by the highly optimized models.
* **Publication:** Open-source the multi-pipeline PyTorch NAS framework and submit comparative findings to a computational biology or applied machine learning venue.

---

## Implementation Targets
**Goal:** Scaffold core `src/` modules that implement the two-stage fusion pipeline.
* `src/data/brca_dataset.py` — PyTorch Dataset switching between flat concatenated tensor (Stage 1) and modality dict (Stage 2).
* `src/models/brca_early_fusion.py` — Stage 1 `torch.cat` model with MLP trunk and three MTL heads (BCE, ordinal, Cox-PH).
* `src/pipelines/train_stacking.py` — Stage 2 five-fold OOF loop and sklearn ElasticNet meta-classifier on $P_{\text{OOF}}$.

---

## Timeline Mapping

| Academic Year | Phases | Focus | Task Count |
|---------------|--------|-------|------------|
| **Year 1** | Phase 1 (Steps 1–4, Stages 1–2, Implementation Targets) | BRCA anchor vertical slice: TCGA sourcing, 80/20 split, HDF5 storage, PostgreSQL hub, GitHub Actions/Slurm CI/CD, MTL architecture, Optuna NAS baselines, Stage 1 early fusion (leakage guardrails, variance masks, concat + three heads), Stage 2 late fusion (expert nets, OOF stacking, ElasticNet meta-classifier), implementation scaffolds | 29 |
| **Year 2** | Phase 2 + Phase 3 | Code abstraction (dynamic omic loaders, adaptive MTL heads); scale to 4 diseases (Alzheimer's, RA, T2D, Down Syndrome); distributed Optuna on Slurm via Hetzner PostgreSQL | 8 |
| **Year 3** | Phase 4 | Comparative architecture taxonomy, SHAP interpretability, Streamlit patient portal, thesis synthesis, publication | 5 |
