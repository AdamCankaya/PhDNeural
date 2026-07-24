# PhDNeural Wiki

Welcome to the **PhDNeural** project wiki — a published mirror of documentation under [`docs/wiki/`](https://github.com/AdamCankaya/PhDNeural/tree/main/Bio-NAS/docs/wiki) in the repository.

> **Planning phase:** **24** roadmap checklist items, each with a 1:1 open GitHub issue (`label:phd-sync`) containing implementation requirements. Sync with `--update-existing`; prune orphans with `--close-stale --prune-project`.

## Quick links

| Resource | Link |
|----------|------|
| Repository | [github.com/AdamCankaya/PhDNeural](https://github.com/AdamCankaya/PhDNeural) |
| Project board | [PhD Master Plan (Project #2)](https://github.com/AdamCankaya/PhDNeural/projects/2) |
| Issues (`phd-sync`) | [Open roadmap issues](https://github.com/AdamCankaya/PhDNeural/issues?q=label%3Aphd-sync+is%3Aopen) |
| Pages landing | [adamcankaya.github.io/PhDNeural/Bio-NAS/](https://adamcankaya.github.io/PhDNeural/Bio-NAS/) |
| Live dashboard | [phd_bio-nas_timeline_dashboard.html](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html) |
| Master plan (HTML) | [phd_bio-nas_master_plan.html](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html) |
| Master plan (source) | [phd_bio-nas_master_plan.md](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/phd_bio-nas_master_plan.md) |
| README | [Bio-NAS/README.md](https://github.com/AdamCankaya/PhDNeural/blob/main/Bio-NAS/README.md) |

## Research overview

**Spatio-Temporal Dual-Track Multi-Omic Fusion & Bio-NAS** — BRCA as the anchor cohort, scaling toward five disease categories over a **3-year academic calendar** (Fall 2026 → Summer 2029).

| Track | Approach | Purpose |
|-------|----------|---------|
| **Track A — Standard NAS (Control)** | Unconstrained hyperparameter / architecture search | Mathematical efficiency baseline |
| **Track B — Bio-NAS (Innovation)** | Pathway-constrained layers (KEGG/Reactome) | Biological priors for accuracy, interpretability, sparsity |

Every timeline item on the dashboard and master-plan HTML links to its GitHub issue.

## Wiki navigation

| Page | Description |
|------|-------------|
| [Workflow](Workflow) | Master plan → dashboard / HTML → GitHub sync loop |
| [Roadmap and Tracking](Roadmap-and-Tracking) | 3-year quarter calendar, 24 tasks, issue format, labels |
| [Static MTL Baseline](Static-MTL-Baseline) | Multi-task prediction contract |
| [Code Map and Status](Code-Map-and-Status) | `src/` implementation status |
| [Glossary](Glossary) | Key terms |
| [Infrastructure Runbook](Infrastructure-Runbook) | Hetzner PostgreSQL, Docker, Slurm CI/CD |
| [Data Acquisition BRCA](Data-Acquisition-BRCA) | TCGA sourcing, HDF5, disease registry |
| [Architecture Decisions](Architecture-Decisions) | ADRs for Bio-NAS and MTL design |
| [Experiment Log Template](Experiment-Log-Template) | Reproducible experiment records |
| [FAQ and Troubleshooting](FAQ-and-Troubleshooting) | Sync, dashboard, and wiki FAQs |
