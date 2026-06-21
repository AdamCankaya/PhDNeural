# PhDNeural Wiki

Welcome to the **PhDNeural** project wiki — a published mirror of documentation under [`docs/wiki/`](https://github.com/AdamCankaya/PhDNeural/tree/main/docs/wiki) in the repository.

> **Planning phase:** All roadmap tasks are tracked as open GitHub issues; none are marked done yet. Roadmap updates are **additive** — new bullets create new issues; existing issues stay open unless you explicitly pass `--close-stale` to the sync script.

## Quick links

| Resource | Link |
|----------|------|
| Repository | [github.com/AdamCankaya/PhDNeural](https://github.com/AdamCankaya/PhDNeural) |
| Project board | [PhD Master Plan (Project #2)](https://github.com/AdamCankaya/PhDNeural/projects/2) |
| Live dashboard | [phd_timeline_dashboard.html](https://adamcankaya.github.io/PhDNeural/phd_timeline_dashboard.html) |
| Master plan | [phd_master_plan.md](https://github.com/AdamCankaya/PhDNeural/blob/main/phd_master_plan.md) |
| README | [README.md](https://github.com/AdamCankaya/PhDNeural/blob/main/README.md) |

## Research overview

**Dual-Track Multi-Omic Fusion & Bio-NAS** starting with Breast Invasive Carcinoma (BRCA) as the anchor, scaling to five disease categories over a **3-year academic calendar** (Summer 2026 → Spring 2029).

| Track | Approach | Purpose |
|-------|----------|---------|
| **Track A — Standard NAS (Control)** | Unconstrained hyperparameter search (layers, nodes) | Establish standard Late Fusion meta-classifier baseline |
| **Track B — Bio-NAS (Innovation)** | `MaskedLinear` layers constrained by KEGG/Reactome matrices | Force Optuna to select and optimize true biological pathways |

## Wiki navigation

| Page | Description |
|------|-------------|
| [Workflow](Workflow) | Master plan → dashboard → GitHub sync loop |
| [Roadmap and Tracking](Roadmap-and-Tracking) | 3-year semester calendar, issue format, labels |
| [Static MTL Baseline](Static-MTL-Baseline) | Multi-task prediction contract |
| [Code Map and Status](Code-Map-and-Status) | `src/` implementation status |
| [Glossary](Glossary) | Key terms |
| [Infrastructure Runbook](Infrastructure-Runbook) | Hetzner PostgreSQL, Docker, Slurm CI/CD |
| [Data Acquisition BRCA](Data-Acquisition-BRCA) | TCGA sourcing, HDF5, disease registry |
| [Architecture Decisions](Architecture-Decisions) | ADRs for Bio-NAS and MTL design |
| [Experiment Log Template](Experiment-Log-Template) | Reproducible experiment records |
| [FAQ and Troubleshooting](FAQ-and-Troubleshooting) | Sync, dashboard, and wiki FAQs |
