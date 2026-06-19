# PhD Master Roadmap: Comparative Neural Architecture Search for Multi-Task, Multi-Omic Disease Prediction

## Core Objective
Develop a high-performance, distributed Neural Architecture Search (NAS) framework utilizing Optuna to discover the optimal computational networks across 5 fundamental disease categories. The system will ingest multi-omic data (Methylation, Transcriptomics, Genomics, CNVs) and patient demographics via 5 independent ETL pipelines. Final architectures will use Multi-Task Learning (MTL) to simultaneously predict disease presence, staging, and prognostic survival timelines.

---

## Year 1: The 5-Category Sourcing & Multi-Omic ETL

### Fall Semester: 5-Category Disease Selection & Sourcing
**Goal:** Secure high-quality datasets representing the 5 major disease topologies to prove how biological etiology dictates neural network structure.

* **1. The 5 Disease Targets:**
    * **Oncological:** Breast Invasive Carcinoma (BRCA) via TCGA. (Localized, high mutational burden).
    * **Neurological:** Alzheimer's Disease via NCBI GEO. (Systemic, progressive structural degradation).
    * **Autoimmune:** Rheumatoid Arthritis via NCBI GEO. (Systemic, immune-driven inflammation).
    * **Metabolic:** Type 2 Diabetes via GEO or `recountmethylation`. (Lifestyle, lipid/insulin driven).
    * **Genetic/Developmental:** Down Syndrome via GEO. (Innate chromosomal variation).
* **2. The Multi-Omic Data Modalities:**
    * **Epigenomic (The Anchor):** DNA Methylation arrays (Beta-values ranging from 0.0 to 1.0 at CpG sites).
    * **Transcriptomic:** RNA-Seq Gene Expression (Continuous FPKM or TPM values).
    * **Genomic:** Somatic Mutations and SNPs (Sparse binary matrices from VCF files).
    * **Structural:** Copy Number Variations (Continuous Log2 copy ratios).
    * **Demographic/Clinical:** Age, Sex, Ethnicity, plus disease-specific targets (e.g., Tumor Stage for BRCA, Cognitive Score for Alzheimer's, Days to Live).

### Spring Semester: 5 Independent Pipelines & Normalization
**Goal:** Construct the ETL pipelines without flattening the data. Because each disease has unique clinical variables and available omics, you must build 5 distinct pipelines.

* **1. The Universal Split (Train vs. Test):**
    * Extract a strict **20% Holdout Test Set** for each of the 5 diseases before any preprocessing occurs.
* **2. The 5 Independent PyTorch `Dataset` Classes:**
    * Write 5 separate data ingestion scripts (e.g., `BRCADataset`, `AlzheimersDataset`). 
    * This ensures disease-specific clinical variables are perfectly preserved. If a dataset lacks a specific omic layer (e.g., no RNA-Seq for Rheumatoid Arthritis), that specific pipeline simply omits the RNA-Seq tensor without breaking the universal code.
* **3. Dynamic Normalization (Applied to the 80% Training Set):**
    * *Demographics:* Z-score standardization for continuous arrays; One-Hot Encoding for categorical.
    * *Methylation/Transcriptomics:* Variance-based dimensionality reduction to isolate the top 10,000 highly variable features, preventing GPU memory exhaustion.
* **4. Unified Storage:**
    * Serialize the processed, multi-modal tensors into 5 distinct, partitioned `HDF5` databases.

### Summer Semester: Software Stack & Hub Setup
**Goal:** Provision the remote execution servers and establish the Python ecosystem.

* **1. The Core Stack:**
    * `torch`, `optuna`, `scikit-learn`, `xgboost`, `h5py`, `pandas`, `numpy`.
* **2. The Central Database Hub:**
    * Deploy a Dockerized PostgreSQL database (`psycopg2-binary`) on a dedicated Linux server to track the distributed Optuna trials for all 5 independent disease pipelines concurrently.

---

## Year 2: Distributed NAS & Multi-Task Execution

### Fall Semester: Defining the Multi-Omic Architecture Toolkit
**Goal:** Code the PyTorch algorithmic blueprints that Optuna will dynamically assemble.

* **1. The Multi-Branched Network Body:**
    * *Tabular Branch (Demographics):* MLPs or TabNet.
    * *Epigenomic/Transcriptomic Branch:* 1D-CNNs or Transformer Encoders for dense continuous sequences.
    * *Genomic/CNV Branch:* Sparse linear layers.
    * *Fusion Layers:* Code Early (Concatenation) and Intermediate (Cross-Attention) fusion modules. Optuna will dynamically skip omic branches if a specific pipeline (like Alzheimer's) does not provide that data.
* **2. The Multi-Task Learning (MTL) Heads:**
    * Design the network to split into three output heads:
        * **Diagnostic Head:** Binary/Multi-class Softmax layer predicting disease presence.
        * **Staging Head:** Ordinal classification layer predicting severity/progression.
        * **Prognostic Head:** Linear regression layer predicting timelines (Days to Live).

### Spring Semester: Execution & K-Fold Cross-Validation
**Goal:** Execute the NAS engines across university compute clusters.

* **1. Optuna Objective Function:**
    * Train architectures using **5-Fold Cross-Validation** exclusively on the 80% Training Set.
    * Program Optuna to automatically tune the weights of the combined MTL loss function.
* **2. Parallel Execution:**
    * Deploy execution scripts to Slurm clusters, pointed at the PostgreSQL database (`load_if_exists=True`). Use `HyperbandPruner` to terminate unpromising architectures.

### Summer Semester: Holdout Evaluation & Benchmarking
**Goal:** Evaluate the discovered architectures against classical models.

* **1. The 20% Holdout Evaluation:**
    * Extract the single optimal multi-task architecture for each of the 5 diseases.
    * Train from scratch on the full 80% dataset, then evaluate against the untouched 20% Test Set to generate final ROC-AUC and Mean Squared Error metrics.
* **2. Classical Benchmarking:**
    * Train baseline XGBoost and ElasticNet models on the tabular/methylation data to prove whether the deep multi-omic neural networks statistically outperformed standard tree-based methods.

---

## Year 3: Synthesis & Final Deliverables

### Fall Semester: Interpretability & The Patient Portal
**Goal:** Build the end-to-end inference software.

* **1. Interpretability (SHAP):**
    * Map feature importance. Determine which specific omic layer or demographic variable drove the predictions for each distinct disease category.
* **2. The Universal Inference Application:**
    * Build a `streamlit` web interface.
    * A user selects the disease category, uploads the available patient demographics and raw omic `.CSV` files.
    * The software passes the data through the specific optimized PyTorch model and outputs the Disease Probability, Predicted Stage, and Prognostic Timeline.

### Spring & Summer Semesters: Thesis Defense & Publication
**Goal:** Synthesize the meta-methodology.

* **1. The CS Focus:** Document the structural taxonomy. Did systemic diseases inherently favor self-attention (Transformers) while localized cancers favored spatial architectures (CNNs)?
* **2. Publication:** Open-source the multi-pipeline PyTorch NAS framework and submit findings to computational biology conferences (e.g., ISMB, NeurIPS).
