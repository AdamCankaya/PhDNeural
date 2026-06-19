# PhD Master Roadmap: Automated Neural Architecture Search for Epigenomic Phenotype Prediction

## Core Objective

Develop a high-performance Neural Architecture Search (NAS) framework utilizing Optuna to autonomously discover the optimal multi-modal fusion network. This network will predict a specific disease phenotype by integrating DNA methylation arrays, genetic variants, and tabular clinical data. The final deliverable is an end-to-end software application for patient-specific inference.

---

## Year 1: Foundation, Data Engineering & Central Infrastructure

### Fall Semester: Phenotype Selection & Data Sourcing

**Goal:** Define the biological scope and secure the raw datasets.

#### 1. Disease Phenotype Selection

- **Criteria:** Focus on a disease with a highly documented epigenetic footprint and massive amounts of open-access data. Avoid rare diseases to ensure statistical significance.
- **Action:** Target Breast Invasive Carcinoma (BRCA) or Lung Adenocarcinoma (LUAD).
- **Phenotype Target:** Define the prediction goal as a binary classification (Disease vs. Healthy Tissue) or a multi-class prediction (Tumor Stage I, II, III, IV).

#### 2. Data Sourcing (The Cancer Genome Atlas - TCGA)

- **Repository:** Navigate to the NCI Genomic Data Commons (GDC) Portal.
- **Access Level:** Filter strictly for "Level 3 Open Access" data, which requires no institutional IRB approval and contains pre-processed, de-identified patient data.
- **Data Types to Download:**
  - **Methylation:** Illumina HumanMethylation450 or EPIC array data (beta-values).
  - **Clinical:** XML or TSV files containing age, biological sex, tumor stage, and survival metrics.
  - **Genomic:** Masked Somatic Mutation files (VCFs) representing single nucleotide polymorphisms (SNPs).

### Spring Semester: Data Preparation & Normalization

**Goal:** Construct the ETL (Extract, Transform, Load) pipeline to format the disparate data modalities for neural network ingestion.

#### 1. Clinical Data Normalization

- Apply one-hot encoding for categorical variables (e.g., gender, race).
- Apply standard Z-score normalization for continuous variables (e.g., age, BMI).

#### 2. Methylation Data Dimensionality Reduction

- Implement variance-based feature selection to isolate the top 10,000 most highly variable CpG sites across the dataset to prevent memory exhaustion.

#### 3. Unified Storage Architecture

- Align all modalities using the universal `Patient_ID`.
- Serialize the aligned tensors into high-performance `HDF5` or `Zarr` files to ensure memory-mapped, zero-copy reading from disk to GPU during fast-paced Optuna trials.

### Summer Semester: Model Building Blocks & "The Hub" Setup

**Goal:** Code the modular PyTorch network architectures and spin up the centralized database for parallelization.

#### 1. Defining the Sub-Networks & Fusion Layers

- **Tabular/Clinical Branch:** Multi-Layer Perceptrons (MLPs).
- **Methylation Branch:** 1D-Convolutional Neural Networks (1D-CNNs) or lightweight Transformer Encoders.
- **Fusion Layers:** Code Early Fusion (concatenation), Intermediate Fusion (cross-attention), and Late Fusion (ensemble) modules.

#### 2. The Hub (Centralized Database Configuration)

- Deploy a lightweight Docker container running PostgreSQL on your dedicated Hetzner Linux server.
- This database acts as the centralized "brain" that will track the distributed trial history and prevent remote workers from evaluating duplicate architectures.
- Configure network firewalls to securely accept connections from external university IP addresses.

---

## Year 2: Distributed NAS Execution & Optimization

### Fall Semester: Distributed Optuna Integration (The Workers)

**Goal:** Write the "Define-by-Run" NAS engine and deploy the execution script across university compute clusters.

#### 1. Building the Search Space

- Use Optuna's conditional logic to dynamically build models inside the objective function.
- **Structural Choices:** Number of hidden layers (`trial.suggest_int`), layer widths (`trial.suggest_categorical`), and activation functions.

#### 2. Worker Configuration & Parallelization

- Code the Optuna initialization to strictly use `storage="postgresql://..."` and `load_if_exists=True`.
- **Execution Strategy:** Parallelize the *trials*, not the individual training loops. Worker 1 handles Trial A while Worker 2 handles Trial B independently.

#### 3. Deployment to University Clusters

- Utilize GitHub Actions as your CI/CD runner to package your PyTorch/Optuna code.
- Deploy the scripts to your university's remote compute servers (via Slurm job scheduler or direct SSH). Scale horizontally by spinning up as many worker nodes as your access permits.

### Spring Semester: Model Training & Validation Strategy

**Goal:** Execute the search and rigorously validate the discovered architectures.

#### 1. The Holdout Set

- Strictly partition 20% of the unified dataset into a "blind" Test Set before the search begins.

#### 2. K-Fold Cross-Validation (The Search Phase)

- For the remaining 80% of the data, implement 5-Fold Cross-Validation within the Optuna objective function running on the university nodes.

#### 3. Pruning Mechanisms

- Implement Optuna's `HyperbandPruner` to monitor the training loss of unpromising neural architectures and terminate them early, saving massive amounts of university GPU compute time.

### Summer Semester: Architecture Refinement & Analysis

**Goal:** Lock in the final model and evaluate its performance against biological reality.

#### 1. Final Evaluation

- Extract the single highest-performing multi-modal architecture discovered in the PostgreSQL database.
- Train this final model from scratch on the entire 80% training set and evaluate it against the 20% blind Test Set to generate final accuracy, precision, and AUC-ROC metrics.

#### 2. Interpretability

- Implement SHAP (SHapley Additive exPlanations) or Integrated Gradients to trace the model's predictions back to specific biological features.

---

## Year 3: Final Deliverable & Thesis

### Fall Semester: Software Application Development

**Goal:** Build the patient-facing inference application.

#### 1. The Inference Engine

- Export the PyTorch model weights via TorchScript or ONNX for optimized, low-latency execution.

#### 2. The User Interface

- Build a lightweight frontend (e.g., Streamlit, React, or Vue) where a user can securely upload their raw `.CSV` or `.TXT` methylation and clinical data.
- Implement a parser that instantly formats the user's data to match the pipeline developed in Year 1.

#### 3. Deployment

- Containerize the entire application using Docker. Push the image via CI/CD to a production-ready web environment. The software will output the phenotypic prediction alongside a statistical confidence score.

### Spring Semester: Thesis Writing & Defense

**Goal:** Synthesize the computational novelty of the project.

#### 1. The CS Focus

- Emphasize the efficiency of the search space design, the horizontal scalability of the distributed workers, and the computational overhead reduced through pruning.

#### 2. Visualization

- Generate Pareto front charts demonstrating how the automated NAS discovered highly accurate models faster than manual hyperparameter tuning.

### Summer Semester: Open Source Release & Publication

**Goal:** Finalize the academic output.

#### 1. Code Release

- Clean and document the GitHub repository, providing instructions for how other researchers can connect to their own databases to utilize your distributed NAS framework.

#### 2. Publication

- Submit the methodology to a computational biology or applied machine learning conference (e.g., ISMB, NeurIPS ML4H).
