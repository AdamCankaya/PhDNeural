# PhD Master Roadmap: Two-Stage Multi-Omic Fusion for BRCA Baseline

## Core Objective
Develop a generalized, multi-task Neural Architecture Search (NAS) framework using a **vertical slice** methodology on Breast Invasive Carcinoma (BRCA). Phase 1 follows a strict **two-stage evolution**: Stage 1 stress-tests ingestion, PyTorch, multi-task heads, and Optuna logging via **Early Fusion (concatenation)**; Stage 2 upgrades to a **Stacked Late Fusion Ensemble** with modality-specific expert networks and an ElasticNet meta-classifier trained on clean Out-of-Fold predictions. Once validated, the pipeline abstracts and scales across four additional disease categories for comparative analysis.

---

## Phase 1: The Anchor (BRCA Proof of Concept)

### Stage 1: Early Fusion Proof-of-Concept
**Goal:** Establish an end-to-end software baseline using immediate feature concatenation to stress-test data ingestion, PyTorch tensor formatting, multi-task heads, and distributed Optuna logging without algorithmic complexity.
* **Data Splitting & Leakage Guardrails:** Isolate a strict **20% Holdout Test Set** from the TCGA-BRCA cohort prior to any scaling, normalization, or feature selection.
* **Variance Masks (Train Only):** Compute variance-based dimensionality reduction to select the top 10,000 highly variable methylation CpG sites **strictly within the 80% training partition** to prevent test-set leakage.
* **Concatenation Architecture:** Build a unified PyTorch HDF5 pipeline reading Methylation, RNA-Seq, CNV, Somatic Mutation, and Clinical features; fuse via $X_{\text{fused}} = [X_{\text{methylation}} \parallel X_{\text{transcriptomics}} \parallel X_{\text{genomics}} \parallel X_{\text{cnv}} \parallel X_{\text{clinical}}]$ through an MLP trunk into a dense latent vector.
* **Multi-Task Output Heads:** Branch the latent vector into three independent heads:
    * *Diagnostic Head:* Binary Cross-Entropy (Tumor vs. Normal control).
    * *Staging Head:* Ordinal Log-Loss (Stages I–IV).
    * *Prognostic Head:* Cox Proportional Hazards Negative Log-Partial Likelihood (survival timelines with right-censored data).
* **Optuna Verification:** Connect the early fusion model to the Dockerized PostgreSQL database on the Hetzner server and execute a small Optuna search space to verify parallel workers can read, train, and log metrics successfully.

### Stage 2: Stacking Late Fusion Upgrade
**Goal:** Refactor the validated Stage 1 pipeline into a modular Late Fusion architecture with rigorous OOF stacking and an interpretable ElasticNet meta-classifier—eliminating data leakage entirely.
* **Modality-Specific Expert Networks:** Discard immediate concatenation; instantiate 4 isolated feature extraction networks (1D-CNN for Methylation, deep MLP for RNA-Seq, sparse linear for Genomics/CNV); each expert outputs independent multi-task predictions.
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

---

## Implementation Targets
* `src/data/brca_dataset.py` — PyTorch Dataset switching between flat concatenated tensor (Stage 1) and modality dict (Stage 2).
* `src/models/brca_early_fusion.py` — Stage 1 `torch.cat` model with MLP trunk and three MTL heads (BCE, ordinal, Cox-PH).
* `src/pipelines/train_stacking.py` — Stage 2 five-fold OOF loop and sklearn ElasticNet meta-classifier on $P_{\text{OOF}}$.
