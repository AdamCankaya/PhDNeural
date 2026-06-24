# 3-Year Ph.D. Roadmap: Dual-Track Multi-Omic Fusion & Bio-NAS

## Executive Summary
This three-year Ph.D. project investigates whether Biologically-Informed Neural Architecture Search (Bio-NAS)—where neural pathways are constrained by known human anatomy (e.g., Gene Regulatory Networks)—outperforms unconstrained, mathematical optimization in multi-omic disease prediction. The thesis will establish Breast Invasive Carcinoma (BRCA) as the anchor dataset before conducting a comparative A/B test across four additional, distinct pathologies.

---

## Year 1: The Anchor & Algorithmic Innovation (BRCA)
**Focus:** Build the infrastructure, invent the Bio-NAS algorithm, and prove it works on the most feature-dense cancer dataset.

* **Q1: Mass Data Import & ETL Pipeline**
  * Source multi-omic data (Methylation, RNA-Seq, Clinical) for Breast Invasive Carcinoma (BRCA) from TCGA.
  * Build the automated PyTorch ETL pipeline that aligns patient IDs and compiles the data into an HDF5 database.
  * *Crucial Step:* Enforce the strict 80/20 train/holdout split immediately to prevent data leakage.
* **Q2: Track A (The Control) - Standard NAS**
  * Build the standard Late Fusion meta-classifier.
  * Deploy Optuna to optimize standard hyperparameters (layers, nodes, dropout) for BRCA prediction purely based on mathematical efficiency.
* **Q3: Track B (The Innovation) - Bio-NAS Framework**
  * Download biological blueprints (KEGG, Reactome) and convert them into binary Adjacency Matrices.
  * Write the custom PyTorch `MaskedLinear` layers that sever non-biological artificial synapses.
  * Shift the Optuna search space to select optimal biological pathways rather than hidden nodes.
* **Q4: The First Validation**
  * Compare Track A vs. Track B for BRCA on the 20% holdout test set. If Bio-NAS achieves comparable accuracy with greater sparsity and interpretability, the core algorithm is successfully invented.

---

## Year 2: Scaling the A/B Test Across Modalities
**Focus:** Prove the Bio-NAS framework is a universal, generalizable algorithm by deploying the Year 1 dual-track system across four entirely different diseases.

* **Q1: Neurological & Autoimmune Ingestion**
  * Source Alzheimer's Disease data (NCBI GEO: brain tissue methylation/expression).
  * Source Rheumatoid Arthritis data (NCBI GEO: synovial tissue/blood profiles).
  * Run both datasets through the automated ETL HDF5 pipeline.
* **Q2: Dual-Track Execution (Brain & Inflammation)**
  * Execute Optuna Track A (Standard) and Track B (Bio-NAS) for Alzheimer's and Rheumatoid Arthritis.
* **Q3: Metabolic & Genetic Ingestion**
  * Source Type 2 Diabetes data (NCBI GEO / recount3).
  * Source Down Syndrome data (NCBI GEO: Trisomy 21 multi-omic profiles).
  * Run through the ETL pipeline.
* **Q4: Dual-Track Execution (Metabolic & Chromosomal)**
  * Execute Optuna Track A and Track B for Type 2 Diabetes and Down Syndrome.
  * *Milestone:* By the end of Year 2, the database will contain 10 completed optimization studies (5 diseases × 2 tracks).

---

## Year 3: Comparative Analysis & Thesis Synthesis
**Focus:** Stop running code and start writing. Synthesize the results into a cohesive dissertation proving the value of biological constraints in deep learning.

* **Q1: Performance & Efficiency Audits**
  * Chart the predictive metrics (F1-Score, ROC-AUC, C-Index) comparing standard NAS to Bio-NAS across all five diseases.
  * Quantify the computational efficiency: calculate the exact reduction in GPU memory and model parameters achieved by severing non-biological connections.
* **Q2: LLM-Driven Biological Interpretability**
  * Extract the highest-weighted biological pathways from the 5 Bio-NAS models.
  * Run these pathways through an LLM (e.g., Gemini Pro) to generate mechanistic summaries. Answer the question: *Why did the neural network select these specific pathways to predict each disease?*
* **Q3: Multi-Disease Taxonomy Mapping**
  * Lay the five optimal biological architectures side-by-side. 
  * Map the overlapping biological networks (e.g., Did the optimizer use the exact same inflammatory sub-network to predict both Alzheimer's and Rheumatoid Arthritis?).
* **Q4: Thesis Defense**
  * Finalize the written dissertation. 
  * Present the project not as five separate disease models, but as the invention and universal validation of the Bio-NAS framework.