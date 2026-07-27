# Code Map and Status

Implementation status for `src/` modules (Y2 Summer 2027 Step 5 targets and related code). README has the full module table — this page tracks **done vs. TODO**.

Repository: [`src/`](https://github.com/AdamCankaya/PhDNeural/tree/main/src)

## Implementation status

| Module | Status | Notes |
|--------|--------|-------|
| [`src/config/disease_registry.yaml`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/config/disease_registry.yaml) | **Implemented** | BRCA phenotype/severity mappings complete; 4 other diseases are placeholders |
| [`src/data/clinical_time.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/data/clinical_time.py) | **Implemented** | Canonical time features, TCGA column map, Z-score helpers, `LABEL_SOURCE_COLUMNS` exclusion |
| [`src/data/base_multiomic_dataset.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/data/base_multiomic_dataset.py) | **Implemented** | Abstract contract: uniform `{features, labels{phenotype, severity}}` dict; `FusionMode.EARLY` is **legacy** — plan 07 adds Intermediate Fusion `(meth, rna, labels)` |
| [`src/data/brca_dataset.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/data/brca_dataset.py) | **Partial** | Clinical time + label guardrails wired; **HDF5 loading + Intermediate Fusion scalings TODO** (plan 07) |
| [`src/models/static_mtl_model.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/models/static_mtl_model.py) | **Implemented** | Shared trunk + phenotype/severity heads |
| [`src/models/brca_early_fusion.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/models/brca_early_fusion.py) | **Legacy / partial** | Early raw-concat baseline — **superseded for NAS** by Intermediate Fusion modules (plan 10) + phased Optuna (plan 12) |
| [`src/models/losses.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/models/losses.py) | **Implemented** | `PhenotypeBCELoss`, `OrdinalSeverityLoss`, `StaticMtlLoss` |
| [`src/models/extensions/cox_prognostic.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/models/extensions/cox_prognostic.py) | **Stub** | Post-thesis only; not in baseline |
| [`src/pipelines/train_stacking.py`](https://github.com/AdamCankaya/PhDNeural/blob/main/src/pipelines/train_stacking.py) | **Partial** | 8 meta-feature constants + OOF loop scaffold; expert training **TODO** |

## Module responsibilities

| Module | Path | Responsibility |
|--------|------|----------------|
| Disease registry | `src/config/disease_registry.yaml` | Per-disease phenotype/severity mappings and `n_severity_classes` |
| Clinical time features | `src/data/clinical_time.py` | Canonical time tabular extraction and train-only Z-scoring |
| Base dataset | `src/data/base_multiomic_dataset.py` | Abstract multi-omic `Dataset` with uniform label dict |
| BRCA dataset | `src/data/brca_dataset.py` | Legacy Stage 1/2 modes; plan 07 → Intermediate Fusion `(meth, rna, labels)` + scalings |
| Static MTL model | `src/models/static_mtl_model.py` | Shared trunk + phenotype/severity heads |
| Early fusion model | `src/models/brca_early_fusion.py` | Legacy Stage 1 `torch.cat` baseline (not NAS default) |
| Intermediate Fusion (planned) | `src/models/` (`MethEncoder`, `RNAEncoder`, `FusionDecoder`) | Multi-branch NAS path — plan 10 |
| Losses | `src/models/losses.py` | `PhenotypeBCELoss`, `OrdinalSeverityLoss`, `StaticMtlLoss` |
| Cox-PH extension | `src/models/extensions/cox_prognostic.py` | Post-thesis prognostic stub (not in baseline) |
| Stacking pipeline | `src/pipelines/train_stacking.py` | Stage 2 5-fold OOF loop + ElasticNet meta-classifier (8 meta-features) |

## Next implementation priorities

1. **HDF5 loader + Intermediate Fusion batch** in `brca_dataset.py` — `(meth, rna, labels)` + Step 1/2 scalings (plan 07)
2. **`MethEncoder` / `RNAEncoder` / `FusionDecoder`** — multi-branch modules (plan 10); do not grow NAS around early fusion
3. **Phased Optuna** — branch HPs then post-fusion dense; Postgres via plan 09/12
4. **Expert training** in `train_stacking.py` — complete Stage 2 OOF matrix generation (separate path)

## Related pages

- [Static MTL Baseline](Static-MTL-Baseline) — two-task contract
- [Data Acquisition BRCA](Data-Acquisition-BRCA) — HDF5 layout spec
- [Architecture Decisions](Architecture-Decisions) — design rationale
