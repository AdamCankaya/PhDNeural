# PhD Master Roadmap: Dual-Track Multi-Omic Fusion & Bio-NAS

## Core Objective
This three-year Ph.D. project investigates whether Biologically-Informed Neural Architecture Search (Bio-NAS)—where neural pathways are constrained by known human anatomy (e.g., Gene Regulatory Networks)—outperforms unconstrained, mathematical optimization in multi-omic disease prediction. The thesis will establish Breast Invasive Carcinoma (BRCA) as the anchor dataset before conducting a comparative A/B test across four additional, distinct pathologies.

---

## Year 1: The Anchor & Algorithmic Innovation (BRCA)
> Phases: 1

### Summer 2026 Semester: Mass Data Import & ETL Pipeline
**Phase:** 1 | **Goal:** Build the infrastructure, invent the Bio-NAS algorithm, and prove it works on the most feature-dense cancer dataset.

#### Step 1: Mass Data Import & ETL Pipeline
**Goal:** Source multi-omic data and build the ETL pipeline.
* Source multi-omic data (Methylation, RNA-Seq, Clinical) for Breast Invasive Carcinoma (BRCA) from TCGA.
* Build the automated PyTorch ETL pipeline that aligns patient IDs and compiles the data into an HDF5 database.
* *Crucial Step:* Enforce the strict 80/20 train/holdout split immediately to prevent data leakage.

### Fall 2026 Semester: Track A and Track B Innovation
**Phase:** 1 | **Goal:** Build standard NAS and invent Bio-NAS framework.

#### Step 2: Track A (The Control) - Standard NAS
**Goal:** Build the standard Late Fusion meta-classifier and optimize.
* Build the standard Late Fusion meta-classifier.
* Deploy Optuna to optimize standard hyperparameters (layers, nodes, dropout) for BRCA prediction purely based on mathematical efficiency.

#### Step 3: Track B (The Innovation) - Bio-NAS Framework
**Goal:** Convert blueprints to matrices and shift Optuna.
* Download biological blueprints (KEGG, Reactome) and convert them into binary Adjacency Matrices.
* Write the custom PyTorch `MaskedLinear` layers that sever non-biological artificial synapses.
* Shift the Optuna search space to select optimal biological pathways rather than hidden nodes.

### Spring 2027 Semester: The First Validation
**Phase:** 1 | **Goal:** Validate Track A vs Track B on BRCA.

#### Step 4: The First Validation
**Goal:** Prove Bio-NAS works on the BRCA holdout test set.
* Compare Track A vs. Track B for BRCA on the 20% holdout test set. If Bio-NAS achieves comparable accuracy with greater sparsity and interpretability, the core algorithm is successfully invented.

---

## Year 2: Scaling the A/B Test Across Modalities
> Phases: 2, 3

### Summer 2027 Semester: Neurological & Autoimmune Ingestion
**Phase:** 2 | **Goal:** Source new datasets and execute tracks.

#### Step 1: Neurological & Autoimmune Ingestion
**Goal:** Source AD and RA data and run ETL.
* Source Alzheimer's Disease data (NCBI GEO: brain tissue methylation/expression).
* Source Rheumatoid Arthritis data (NCBI GEO: synovial tissue/blood profiles).
* Run both datasets through the automated ETL HDF5 pipeline.

#### Step 2: Dual-Track Execution (Brain & Inflammation)
**Goal:** Execute standard and Bio-NAS for brain and inflammation.
* Execute Optuna Track A (Standard) and Track B (Bio-NAS) for Alzheimer's and Rheumatoid Arthritis.

### Fall 2027 Semester: Metabolic & Genetic Ingestion
**Phase:** 3 | **Goal:** Source metabolic and genetic data.

#### Step 3: Metabolic & Genetic Ingestion
**Goal:** Source T2D and Down Syndrome data and run ETL.
* Source Type 2 Diabetes data (NCBI GEO / recount3).
* Source Down Syndrome data (NCBI GEO: Trisomy 21 multi-omic profiles).
* Run through the ETL pipeline.

### Spring 2028 Semester: Metabolic & Chromosomal Execution
**Phase:** 3 | **Goal:** Complete dual-track execution for all 5 diseases.

#### Step 4: Dual-Track Execution (Metabolic & Chromosomal)
**Goal:** Complete the remaining Optuna studies.
* Execute Optuna Track A and Track B for Type 2 Diabetes and Down Syndrome.
* *Milestone:* By the end of Year 2, the database will contain 10 completed optimization studies (5 diseases × 2 tracks).

---

## Year 3: Comparative Analysis & Thesis Synthesis
> Phases: 4

### Summer 2028 Semester: Audits & Interpretability
**Phase:** 4 | **Goal:** Audit performance and extract pathways.

#### Step 1: Performance & Efficiency Audits
**Goal:** Quantify predictive metrics and compute reduction.
* Chart the predictive metrics (F1-Score, ROC-AUC, C-Index) comparing standard NAS to Bio-NAS across all five diseases.
* Quantify the computational efficiency: calculate the exact reduction in GPU memory and model parameters achieved by severing non-biological connections.

#### Step 2: LLM-Driven Biological Interpretability
**Goal:** Summarize mechanistic pathways via LLM.
* Extract the highest-weighted biological pathways from the 5 Bio-NAS models.
* Run these pathways through an LLM (e.g., Gemini Pro) to generate mechanistic summaries. Answer the question: *Why did the neural network select these specific pathways to predict each disease?*

### Fall 2028 Semester: Taxonomy Mapping
**Phase:** 4 | **Goal:** Map the architectures side-by-side.

#### Step 3: Multi-Disease Taxonomy Mapping
**Goal:** Identify overlapping biological networks across diseases.
* Lay the five optimal biological architectures side-by-side.
* Map the overlapping biological networks (e.g., Did the optimizer use the exact same inflammatory sub-network to predict both Alzheimer's and Rheumatoid Arthritis?).

### Spring 2029 Semester: Thesis Synthesis
**Phase:** 4 | **Goal:** Finalize the written dissertation and defense.

#### Step 4: Thesis Defense
**Goal:** Finalize and present the thesis.
* Finalize the written dissertation.
* Present the project not as five separate disease models, but as the invention and universal validation of the Bio-NAS framework.

---

## Timeline Mapping

| Year | Semester | Phase(s) | Focus | Tasks |
|------|----------|----------|-------|-------|
| **Year 1** | Summer 2026 | 1 | Mass Data Import & ETL Pipeline | 3 |
| **Year 1** | Fall 2026 | 1 | Track A and Track B | 5 |
| **Year 1** | Spring 2027 | 1 | The First Validation | 1 |
| **Year 2** | Summer 2027 | 2 | Neurological & Autoimmune | 4 |
| **Year 2** | Fall 2027 | 3 | Metabolic & Genetic Ingestion | 3 |
| **Year 2** | Spring 2028 | 3 | Metabolic & Chromosomal Execution | 2 |
| **Year 3** | Summer 2028 | 4 | Audits & Interpretability | 4 |
| **Year 3** | Fall 2028 | 4 | Taxonomy Mapping | 2 |
| **Year 3** | Spring 2029 | 4 | Thesis Synthesis | 2 |
