# PhD Master Roadmap: "Vertical Slice" Multi-Task Neural Architecture Search

## Core Objective
Develop a generalized, multi-task Neural Architecture Search (NAS) framework. The project will be built using a "Vertical Slice" methodology: engineering the complete, end-to-end multi-omic pipeline exclusively for Breast Invasive Carcinoma (BRCA) first. Once validated, this baseline architecture will be abstracted and deployed across 4 additional disease categories (Neurological, Autoimmune, Metabolic, Genetic) to conduct a comparative computational analysis.

---

## Phase 1: The Anchor (BRCA Proof of Concept)

### Step 1: BRCA Multi-Omic Sourcing & Split
**Goal:** Acquire the most feature-dense dataset to stress-test every branch of the neural network.
* **Source:** TCGA (Level 3 Open Access).
* **Target Modalities:** Methylation (Beta-values), Transcriptomics (RNA-Seq), Genomics (Somatic Mutations), CNVs, and Clinical Demographics.
* **The Strict Boundary:** Immediately split the BRCA dataset into an **80% Training/Validation Set** and a locked **20% Holdout Test Set** before any preprocessing.

### Step 2: Infrastructure & Database Orchestration
**Goal:** Establish the remote environments required for distributed Optuna execution.
* **Central Hub:** Deploy a Dockerized PostgreSQL instance on your Hetzner Linux server to act as the permanent, centralized Optuna study hub.
* **CI/CD Pipeline:** Configure a GitHub Actions runner to orchestrate and deploy your PyTorch worker scripts natively from your repository to your university's Slurm compute clusters.

### Step 3: Engineering the Multi-Task Architecture
**Goal:** Write the PyTorch modules that handle multi-modal fusion and multi-task learning.
* **Input Branches:** Construct flexible ingestion layers for dense continuous data (1D-CNNs/Transformers for Methylation/RNA) and sparse data (Linear layers for Genomics).
* **MTL Output Heads:** Program the network to branch into three specific loss targets:
    * *Diagnostic (Cross-Entropy Loss):* Tumor vs. Normal matched tissue.
    * *Staging (Ordinal Loss):* Stage I, II, III, or IV.
    * *Prognostic (Cox-PH Loss):* Survival timeline (Days to Live) accounting for censored data.

### Step 4: Optuna NAS & Baseline Benchmarking
**Goal:** Execute the search space specifically for BRCA on the 80% Training Set using 5-Fold Cross Validation.
* **Neural Search (Optuna):** Tune the 5 deep learning topologies (MLP, 1D-CNN, Transformer, TabNet, Cross-Attention Fusion) to find the optimal BRCA network. Have Optuna dynamically weigh the multi-task loss functions.
* **Classical Baselines:** Train XGBoost, LightGBM, and ElasticNet strictly on the tabular/methylation data to establish a performance floor.
* **The PoC Validation:** Evaluate the single best Optuna-discovered model against the classical baselines using the locked 20% Holdout Test Set.

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
