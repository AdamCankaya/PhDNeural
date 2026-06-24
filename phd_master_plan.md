# PhD Master Roadmap: Comparative Spatio-Temporal Neural Architecture Search for Multi-Omic Disease Prediction

## Executive Summary
This three-year Ph.D. project investigates whether Biologically-Informed Neural Architecture Search (Bio-NAS)—where neural pathways are constrained by known human anatomy (e.g., Gene Regulatory Networks)—outperforms unconstrained, mathematical optimization in multi-omic disease prediction. The thesis will establish Breast Invasive Carcinoma (BRCA) as the anchor dataset before conducting a comparative A/B test across four additional, distinct pathologies, now utilizing a Spatio-Temporal framework.

## Core Objective
Develop a high-performance, distributed Neural Architecture Search (NAS) framework utilizing Optuna to discover optimal Spatio-Temporal Deep Learning networks across 5 distinct disease categories to model, predict, and forecast disease progression trajectories.

---

## Year 1: Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure

### Q1 Quarter: Longitudinal Multi-Omic Cohort Sourcing
**Phases:** 1 | **Goal:** Identify and secure multi-disease datasets.
#### Step 1: Data Acquisition
* Identify and secure multi-disease datasets containing repeated molecular measurements over time (BRCA, Alzheimer’s, Rheumatoid Arthritis, T2D, Epigenetic Aging).
* Source longitudinal tracking options focusing on primary vs. recurrent match points.

### Q2 Quarter: Spatio-Temporal Data Modalities
**Phases:** 1 | **Goal:** Map spatial/temporal dimensions.
#### Step 1: Feature Mapping
* Map spatial dimension (sequence coordinates, CpG sites) and temporal dimension (longitudinal intervals).
* Define genomic structural spacing.

### Q3 Quarter: 4D Tensor Construction & Irregular Time-Step Normalization
**Phases:** 2 | **Goal:** Construct a robust ETL pipeline.
#### Step 1: ETL Pipeline
* Partition data by Patient ID (80/20 train/holdout split, strict temporal isolation).
* Implement Time-Delta Embedding Layer ($\Delta t$) for irregular intervals.
* Construct 4D tensors: (Batch, Time_Steps, Spatial_Features, Channels).

### Q4 Quarter: Spatio-Temporal Software Integration & Central Hub
**Phases:** 2 | **Goal:** Provision compute servers.
#### Step 1: Infrastructure
* Provision compute servers with `torch`, `tsai`/`sktime`, `optuna`.
* Set up Dockerized PostgreSQL engine for orchestration.

---

## Year 2: Spatio-Temporal NAS Execution & Multi-Task Forecasting

### Q1 Quarter: Engineering the Spatio-Temporal Search Space
**Phases:** 3 | **Goal:** Code the modular PyTorch components.
#### Step 1: Spatial Modules
* Develop 1D-CNNs for local clusters of CpG sites and Spatial Transformers for long-range dependencies.

### Q2 Quarter: Temporal Progression Modules
**Phases:** 3 | **Goal:** Implement progression modules.
#### Step 1: Temporal Modules
* Implement ConvLSTM/GRU blocks and Temporal Attention layers for longitudinal progression.

### Q3 Quarter: Parallel Search Optimization
**Phases:** 3 | **Goal:** Execute large-scale search.
#### Step 1: Large Scale Search
* Execute large-scale spatio-temporal architecture search with Causal Cross-Validation.
* Use Horizontally Scaled Workers via Slurm and HyperbandPruner.

### Q4 Quarter: Structural Taxonomy & Baseline Benchmarking
**Phases:** 3 | **Goal:** Mine the optimization database.
#### Step 1: Benchmarking
* Evaluate architectures on 20% holdout trajectories.
* Ablation study: Spatial vs. Spatio-Temporal predictive gain.
* Compare with longitudinal Random Forests/XGBoost.

---

## Year 3: Spatio-Temporal Interpretability and Clinical Interface

### Q1 Quarter: Spatio-Temporal Interpretability
**Phases:** 4 | **Goal:** Unpack model tracking changes.
#### Step 1: Multi-dimensional Attribution
* Implement `captum` or `shap` for multi-dimensional attribution.
* Extract maps identifying CpG sites and timestamps driving disease progression predictions.

### Q2 Quarter: The Trajectory Dashboard Application
**Phases:** 4 | **Goal:** Build interactive dashboard.
#### Step 1: Streamlit Dashboard
* Build interactive `streamlit` interface.
* Render health trajectories and risk forecasting curves.

### Q3 Quarter: Thesis Synthesis and Framework Release
**Phases:** 4 | **Goal:** Document discovery and release.
#### Step 1: Synthesis
* Document structural taxonomy discovered.
* Compare slow-progressing vs. fast-acting condition architectures.

### Q4 Quarter: Thesis Defense
**Phases:** 4 | **Goal:** Finalize and release.
#### Step 1: Defense
* Finalize dissertation. 
* Release the complete open-source Python framework.
