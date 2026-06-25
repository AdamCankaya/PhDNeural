# Static MTL Baseline

All five disease pipelines share a **Static Multi-Task Learning (MTL) baseline**: time-related variables are tabular clinical inputs, and every cohort solves **two prediction tasks** — **phenotype** and **severity**. Cox-PH prognostic modeling is **deferred** to a post-thesis optional extension.

Full spec: [`phd_master_plan.md` § Static MTL Baseline](https://github.com/AdamCankaya/PhDNeural/blob/main/phd_master_plan.md)

![Two-Stage Stacked Late Fusion Architecture](https://raw.githubusercontent.com/AdamCankaya/PhDNeural/main/docs/architecture-stacked-fusion.png)

## Time as tabular clinical inputs

Time fields are **continuous tabular features** in the clinical modality — Z-scored on the training partition only. No RNN/Transformer sequences in the baseline.

| Feature | Description | BRCA example |
|---------|-------------|--------------|
| `age_at_sample` | Patient age at collection | TCGA `age_at_index` |
| `years_since_diagnosis` | Duration since first diagnosis | Derived from diagnosis date |
| `days_since_sample_collection` | Timeline offset within study | Study day / collection offset |
| `survival_days` | Observed follow-up duration | TCGA `days_to_death` / last follow-up |
| `time_since_last_visit` | Gap between visits | Derived (longitudinal cohorts) |

Censoring indicators (e.g. `event_observed`) may be tabular inputs when survival duration is present — but are **not** a baseline prediction target.

## Two standardized tasks

| Task | Head | Loss | Target |
|------|------|------|--------|
| **Phenotype** | `phenotype_head` (1 logit) | Binary cross-entropy | `0=Healthy`, `1=Diseased` |
| **Severity** | `severity_head` (K logits) | Ordinal log-loss | `0..K-1` ordered (missing → mask) |

Per-disease mappings and `n_severity_classes` (variable K): [`src/config/disease_registry.yaml`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/config/disease_registry.yaml)

## Input / label separation (no severity leakage)

**Severity and stage source columns are labels only** — they must not appear in the clinical input concatenation branch. Implementation: [`src/data/clinical_time.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/data/clinical_time.py) defines `LABEL_SOURCE_COLUMNS` excluded from clinical features.

## Stacking meta-features (Stage 2)

Stage 2 OOF stacking: **4 modality experts × 2 tasks = 8 meta-features** per sample in $P_{\text{OOF}}$:

| Expert | Phenotype pred | Severity pred |
|--------|----------------|---------------|
| Methylation (1D-CNN) | ✓ | ✓ |
| Transcriptomics (MLP) | ✓ | ✓ |
| Genomics (sparse linear) | ✓ | ✓ |
| CNV (sparse linear) | ✓ | ✓ |

ElasticNet meta-classifier(s) train on this 8-column matrix with true labels — see [Architecture Decisions](Architecture-Decisions).

## Optional extension: Cox-PH (deferred)

A third **prognostic head** using Cox Proportional Hazards can be added **after** the Static MTL baseline is validated. This would enable:

- Prognostic timeline outputs in Streamlit
- 4 experts × 3 tasks = **12** meta-feature stacking variant

**Not in baseline scope** — keeps all Optuna studies comparable on the shared two-task contract. Stub: [`src/models/extensions/cox_prognostic.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/models/extensions/cox_prognostic.py)

## Related pages

- [Data Acquisition BRCA](Data-Acquisition-BRCA) — BRCA label mappings
- [Architecture Decisions](Architecture-Decisions) — ADR for 2-task vs Cox-PH
- [Code Map and Status](Code-Map-and-Status) — losses, heads, dataset guardrails
