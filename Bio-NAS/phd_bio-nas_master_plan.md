# PhD Master Roadmap: Comparative Spatio-Temporal Neural Architecture Search for Multi-Omic Disease Prediction

## Executive Summary
This three-year Ph.D. project investigates whether Biologically-Informed Neural Architecture Search (Bio-NAS)—where neural pathways are constrained by known human anatomy (e.g., Gene Regulatory Networks)—outperforms unconstrained, mathematical optimization in multi-omic disease prediction. The thesis will establish Breast Invasive Carcinoma (BRCA) as the anchor dataset before conducting a comparative A/B test across four additional, distinct pathologies, now utilizing a Spatio-Temporal framework.

## Core Objective
Develop a high-performance, distributed Neural Architecture Search (NAS) framework utilizing Optuna to discover optimal Spatio-Temporal Deep Learning networks across 5 distinct disease categories to model, predict, and forecast disease progression trajectories.

---

## Year 1: Spatio-Temporal Sourcing, Irregular Time-Step ETL, and Infrastructure

### Q3 Fall 2026: Longitudinal Multi-Omic Cohort Sourcing
**Phases:** 1 | **Goal:** Identify and secure multi-disease datasets with repeated molecular measurements over time.
#### Step 1: Data Acquisition
* Identify and secure multi-disease datasets containing repeated molecular measurements over time (BRCA, Alzheimer’s, Rheumatoid Arthritis, T2D, Epigenetic Aging).
  * Deliverables: dataset inventory table (source, access method, license/ethics, sample counts by timepoint) for all five disease categories.
  * Acceptance: every disease has at least one candidate cohort with ≥2 timepoints documented.
  * Dependencies: GDC/GEO/recount3 accounts; disease registry entries in `src/config/disease_registry.yaml`.
* Source longitudinal tracking options focusing on primary vs. recurrent match points.
  * Deliverables: matching strategy note (patient ID schemes, primary/recurrent or visit pairing rules) per disease.
  * Acceptance: documented join keys and exclusion rules that preserve temporal order.
  * Dependencies: cohort-specific clinical/metadata dictionaries.

### Q4 Winter 2026: Spatio-Temporal Data Modalities
**Phases:** 1 | **Goal:** Map spatial and temporal feature dimensions for multi-omic tensors.
#### Step 1: Feature Mapping
* Map spatial dimension (sequence coordinates, CpG sites) and temporal dimension (longitudinal intervals).
  * Deliverables: feature map spec covering spatial axes (genomic coordinates / CpG / gene indices) and temporal axes (visit index, calendar time, Δt).
  * Acceptance: written mapping covering methylation, transcriptomics, and at least one additional omic modality.
  * Dependencies: Level-3 matrices or equivalent processed tables from Fall 2026 sourcing.
* Define genomic structural spacing.
  * Deliverables: spacing/binning rules (bp windows, CpG neighborhood, chromosome boundaries) used by spatial modules.
  * Acceptance: reproducible spacing config checked into repo with unit tests for edge cases (chromosome ends, missing coords).
  * Dependencies: reference genome build documented (e.g., GRCh38).

### Q1 Spring 2027: 4D Tensor Construction & Irregular Time-Step Normalization
**Phases:** 2 | **Goal:** Construct a leakage-safe ETL pipeline producing irregular-time 4D tensors.
#### Step 1: ETL Pipeline
* Partition data by Patient ID (80/20 train/holdout split, strict temporal isolation).
  * Deliverables: patient-level split files + loader that never peeks at holdout during fit.
  * Acceptance: automated leakage tests (no patient ID overlap; no future-visit leakage into earlier steps).
  * Dependencies: finalized cohort tables from Year 1 Fall/Winter.
* Implement Time-Delta Embedding Layer ($\Delta t$) for irregular intervals.
  * Deliverables: PyTorch module embedding inter-visit Δt; documented units (days/weeks) and missing-interval policy.
  * Acceptance: unit tests for zero, irregular, and missing Δt; shapes match tensor contract.
  * Dependencies: visit timestamps aligned to patient IDs.
* Construct 4D tensors: (Batch, Time_Steps, Spatial_Features, Channels).
  * Deliverables: HDF5 (or equivalent) writer/reader for `(B, T, S, C)` tensors plus metadata sidecars.
  * Acceptance: round-trip equality tests; documented channel layout per omic.
  * Dependencies: feature map + Δt embedding from prior items.

### Q2 Summer 2027: Spatio-Temporal Software Integration & Central Hub
**Phases:** 2 | **Goal:** Provision reproducible compute and experiment orchestration.
#### Step 1: Infrastructure
* Provision compute servers with `torch`, `tsai`/`sktime`, `optuna`.
  * Deliverables: environment lockfile / Docker image pin list; smoke-test script importing stack packages.
  * Acceptance: clean install on target host(s); GPU detection logged when available.
  * Dependencies: cloud/HPC access; Slurm or equivalent job runner path identified.
* Set up Dockerized PostgreSQL engine for orchestration.
  * Deliverables: `docker-compose` (or k8s) Postgres for Optuna/study metadata; backup/restore notes.
  * Acceptance: Optuna RDB storage connects; one trial write/read verified.
  * Dependencies: host networking/firewall rules; credentials in `.env` (not committed).

---

## Year 2: Spatio-Temporal NAS Execution & Multi-Task Forecasting

### Q3 Fall 2027: Engineering the Spatio-Temporal Search Space
**Phases:** 3 | **Goal:** Code modular spatial PyTorch blocks for the NAS search space.
#### Step 1: Spatial Modules
* Develop 1D-CNNs for local clusters of CpG sites and Spatial Transformers for long-range dependencies.
  * Deliverables: reusable `nn.Module`s with configurable depth/width; registered in Optuna search space.
  * Acceptance: forward-pass tests on synthetic `(B,T,S,C)` batches; parameter counts logged.
  * Dependencies: genomic spacing config; Year 1 tensors.

### Q4 Winter 2027: Temporal Progression Modules
**Phases:** 3 | **Goal:** Implement temporal progression blocks for longitudinal forecasting.
#### Step 1: Temporal Modules
* Implement ConvLSTM/GRU blocks and Temporal Attention layers for longitudinal progression.
  * Deliverables: temporal stack modules that consume Δt embeddings; optional attention over time.
  * Acceptance: causal masking verified (no future visit leakage); gradient flow smoke test.
  * Dependencies: spatial module outputs; Δt embedding layer.

### Q1 Spring 2028: Parallel Search Optimization
**Phases:** 3 | **Goal:** Execute large-scale distributed spatio-temporal architecture search.
#### Step 1: Large Scale Search
* Execute large-scale spatio-temporal architecture search with Causal Cross-Validation.
  * Deliverables: Optuna study configs, causal CV splitter, trial metrics schema (loss, AUROC/C-index as applicable).
  * Acceptance: ≥1 full study completes on BRCA (or primary cohort) with reproducible seed and stored best trial.
  * Dependencies: Postgres Optuna storage; Slurm workers; train tensors.
* Use Horizontally Scaled Workers via Slurm and HyperbandPruner.
  * Deliverables: Slurm job templates; HyperbandPruner wired; worker scale-out runbook.
  * Acceptance: ≥2 concurrent workers report trials to the same study without corruption.
  * Dependencies: cluster account; shared storage for artifacts.

### Q2 Summer 2028: Structural Taxonomy & Baseline Benchmarking
**Phases:** 3 | **Goal:** Benchmark searched architectures against baselines and ablations.
#### Step 1: Benchmarking
* Evaluate architectures on 20% holdout trajectories.
  * Deliverables: holdout evaluation script + metrics table for best NAS architectures.
  * Acceptance: metrics published for frozen holdout only; confidence intervals or bootstrap noted.
  * Dependencies: completed Optuna studies; locked holdout split.
* Ablation study: Spatial vs. Spatio-Temporal predictive gain.
  * Deliverables: controlled ablation comparing spatial-only vs full spatio-temporal models.
  * Acceptance: same data splits/seeds; delta metrics documented with interpretation.
  * Dependencies: spatial and temporal modules; evaluation harness.
* Compare with longitudinal Random Forests/XGBoost.
  * Deliverables: classical baseline pipelines on comparable flattened/windowed features.
  * Acceptance: baseline metrics on identical holdout; fair feature budget documented.
  * Dependencies: tabular feature export from tensors/metadata.

---

## Year 3: Spatio-Temporal Interpretability and Clinical Interface

### Q3 Fall 2028: Spatio-Temporal Interpretability
**Phases:** 4 | **Goal:** Attribute predictions to spatial sites and timepoints.
#### Step 1: Multi-dimensional Attribution
* Implement `captum` or `shap` for multi-dimensional attribution.
  * Deliverables: attribution pipeline producing per-sample spatial×temporal importance tensors.
  * Acceptance: attributions run on holdout subset without OOM; API documented.
  * Dependencies: trained best models; captum/shap in environment.
* Extract maps identifying CpG sites and timestamps driving disease progression predictions.
  * Deliverables: ranked site/time maps + export (CSV/Parquet) and summary figures.
  * Acceptance: top-k drivers reviewable per disease trajectory example.
  * Dependencies: attribution pipeline; genomic annotations.

### Q4 Winter 2028: The Trajectory Dashboard Application
**Phases:** 4 | **Goal:** Build an interactive clinical trajectory interface.
#### Step 1: Streamlit Dashboard
* Build interactive `streamlit` interface.
  * Deliverables: Streamlit app loading model outputs and patient trajectories.
  * Acceptance: local demo runbook; auth/PII constraints documented.
  * Dependencies: inference artifacts; holdout demo cohort.
* Render health trajectories and risk forecasting curves.
  * Deliverables: plots for observed vs predicted risk over time with uncertainty bands if available.
  * Acceptance: at least one end-to-end patient view from load → forecast → attribution snippet.
  * Dependencies: Streamlit shell; attribution exports.

### Q1 Spring 2029: Thesis Synthesis and Framework Release
**Phases:** 4 | **Goal:** Document discovery and prepare framework release notes.
#### Step 1: Synthesis
* Document structural taxonomy discovered.
  * Deliverables: taxonomy chapter/section mapping architectures to disease categories and motifs.
  * Acceptance: peer-readable draft checked into docs with figure list.
  * Dependencies: Year 2–3 experiment logs and benchmarks.
* Compare slow-progressing vs. fast-acting condition architectures.
  * Deliverables: comparative analysis contrasting architecture preferences across disease tempos.
  * Acceptance: quantitative table + qualitative discussion ready for thesis inclusion.
  * Dependencies: multi-disease study results (Phases 3–4).

### Q2 Summer 2029: Thesis Defense
**Phases:** 4 | **Goal:** Finalize dissertation and release the open-source framework.
#### Step 1: Defense
* Finalize dissertation.
  * Deliverables: defense draft, slides, and response-to-committee checklist.
  * Acceptance: committee-ready PDF; all chapters cite frozen experiment IDs.
  * Dependencies: synthesis documents; completed experiments.
* Release the complete open-source Python framework.
  * Deliverables: tagged release, install docs, example notebooks, license/citation.
  * Acceptance: clean clone → install → smoke demo on public sample data.
  * Dependencies: stable `src/` APIs; CI green on main.
