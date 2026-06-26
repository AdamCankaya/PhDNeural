# 3-Year Execution Roadmap: Epigenetic Deconvolution SaaS (β-VAE)

## Executive Summary
This document outlines a 12-quarter (3-year) timeline to build, validate, and commercialize a machine learning platform capable of mathematically unmixing bulk epigenetic data into single-cell resolution. The project serves dual purposes: fulfilling the requirements of a Computer Science Ph.D. dissertation and functioning as the Minimum Viable Product (MVP) for a B2B clinical diagnostics software company.

---

## Year 1: The Anchor Model & Infrastructure

### Q1 Quarter: Infrastructure & Data Sourcing
**Phases:** 1 | **Goal:** Build the automated data pipeline.
#### Step 1: Data Pipelines
* Write Python Bio.Entrez scripts to scrape the Human Cell Atlas (HCA) for pure single-cell PBMC reference data, and NCBI GEO for bulk PBMC holdout datasets.
#### Step 2: Infrastructure
* Configure the local WSL 2/Docker development environment in Cursor.
* Provision the remote Hetzner compute cluster and establish the GitHub Actions CI/CD pipeline for automated training deployments.

### Q2 Quarter: The Pseudobulk Engine
**Phases:** 1 | **Goal:** Construct the explicit ground-truth dataset.
#### Step 1: Engine Design
* Engineer the Python "digital blender" script.
#### Step 2: Simulation Loop
* Randomly sample and aggregate pure single-cell vectors to create 50,000+ simulated bulk tissue samples with known, perfect cellular ratios.

### Q3 Quarter: Core Architecture & Optuna NAS
**Phases:** 1 | **Goal:** Finalize network topology.
#### Step 1: PyTorch Engineering
* Draft the dynamic hourglass β-VAE architecture with parameterized encoder/decoder depths and latent dimensions.
#### Step 2: Hyperparameter Optimization
* Deploy Optuna to the Hetzner cluster. Execute massive search sweeps focusing on the latent dimension size (z) and the disentanglement penalty (β).

### Q4 Quarter: Clinical Validation & First Publication
**Phases:** 1 | **Goal:** Validate and publish results.
#### Step 1: Real-World Testing
* Run the completely untrained, real-world clinical bulk samples (from Q1) through the optimized β-VAE pipeline.
#### Step 2: Publication
* Draft and submit Chapter 1 of the dissertation / Paper 1: Optimizing β-VAE Architectures for High-Fidelity Epigenetic Deconvolution in Whole Blood.

---

## Year 2: Multi-Tissue Generalization & Academic Defense

### Q1 Quarter: Architecture Generalization
**Phases:** 2 | **Goal:** Generalize the pipeline.
#### Step 1: Data Sourcing II
* Scrape single-cell and paired bulk datasets for a completely different biological topology (e.g., Breast Cancer / BRCA microenvironments).
#### Step 2: Pipeline Refinement
* Abstract the pseudobulking Python script to dynamically handle varying tissue structures without requiring hardcoded logic changes.

### Q2 Quarter: Parallel Optuna Studies
**Phases:** 2 | **Goal:** Optimize for multiple tissues.
#### Step 1: Transfer Learning
* Spin up new Optuna studies for the solid tumor datasets, seeding the optimizer with the best spatial hyperparameter dictionaries discovered in Year 1.
#### Step 2: Scaling
* Monitor the Hetzner server load as multiple disease-specific networks train simultaneously.

### Q3 Quarter: The Comparative Analysis
**Phases:** 2 | **Goal:** Map the latent spaces.
#### Step 1: Aggregation
* Aggregate the validation metrics across the distinct tissue models. 
#### Step 2: Mechanistic Discovery
* Map the latent spaces of the different models to mathematically prove why a β-VAE must be uniquely tuned per tissue type, highlighting the algorithm's adaptability.

### Q4 Quarter: The Ph.D. Capstone
**Phases:** 2 | **Goal:** Finalize dissertation.
#### Step 1: Synthesis
* Bind the data engineering, network architecture search, and multi-tissue comparative analyses into the final dissertation format.
#### Step 2: Defense
* Finalize the presentation focusing strictly on the high-performance computing constraints, the Optuna optimization strategy, and the novel loss function metrics.

---

## Year 3: SaaS Transformation & Commercial Handoff

### Q1 Quarter: The API Routing Engine
**Phases:** 3 | **Goal:** Build the API gateway.
#### Step 1: Backend Engineering
* Wrap the specialized PyTorch inference models in a high-performance Python framework (like FastAPI).
#### Step 2: Smart Routing
* Build the metadata parser that reads incoming clinical CSVs and instantly routes them to the correct, tissue-specific Hetzner inference container.

### Q2 Quarter: Security & LLC Infrastructure
**Phases:** 3 | **Goal:** Secure inference.
#### Step 1: Access Control
* Implement API key generation, rate limiting, and OAuth2 security protocols for client verification.
#### Step 2: Data Privacy
* Ensure the pipeline is completely stateless—clinical data is unmixed in memory and instantly wiped from the Hetzner servers post-inference.

### Q3 Quarter: The Clinical Beta Test
**Phases:** 3 | **Goal:** Partner testing.
#### Step 1: Onboarding
* Partner with a single, mid-sized bioinformatics lab or university research team. Provide them with free/discounted API tokens.
#### Step 2: Stress Testing
* Allow the partner to run massive batches of cheap bulk sequencing data through the pipeline. Monitor Hetzner compute costs versus API response times.

### Q4 Quarter: Commercial Launch & Scale
**Phases:** 3 | **Goal:** Public launch.
#### Step 1: Productization
* Finalize the API documentation and developer portal.
#### Step 2: Launch
* Establish the SaaS tiers and public launch of the \\Virtual Centrifuge\\ platform.
