# Architecture Decisions

Architecture Decision Records (ADRs) for the PhDNeural two-stage fusion framework.

![Two-Stage Stacked Late Fusion Architecture](https://raw.githubusercontent.com/AdamCankaya/PhDNeural/main/docs/architecture-stacked-fusion.png)

## ADR-001: Two-stage fusion evolution

**Status:** Accepted

**Context:** BRCA anchor must validate ingestion and MTL heads before algorithmic complexity.

**Decision:**

1. **Stage 1** — Early fusion via `torch.cat` through an MLP trunk (software baseline)
2. **Stage 2** — Stacked late fusion with 4 modality experts + ElasticNet on OOF predictions

**Consequences:** Stage 1 de-risks PyTorch/HDF5/Optuna; Stage 2 eliminates concatenation leakage and yields interpretable expert weights.

---

## ADR-002: Static MTL two-task baseline (Cox-PH deferred)

**Status:** Accepted

**Context:** Five-disease comparative NAS requires identical optimization objectives across cohorts.

**Decision:** Baseline = **phenotype (BCE) + severity (ordinal K)** only. Cox-PH prognostic head deferred to post-thesis optional extension.

**Consequences:**

- All Optuna studies comparable on two weighted losses
- Stage 2 stacking uses **8 meta-features** (4 × 2), not 12
- `src/models/extensions/cox_prognostic.py` remains a stub

See [Static MTL Baseline](Static-MTL-Baseline).

---

## ADR-003: Severity label isolation

**Status:** Accepted

**Context:** Prior designs risked tumor-stage leakage by including stage in both clinical inputs and severity targets.

**Decision:** Severity/stage source columns are **labels only** — excluded from clinical concatenation via `LABEL_SOURCE_COLUMNS` in `clinical_time.py`.

**Consequences:** Slightly reduced clinical feature set; correct causal separation for severity prediction.

---

## ADR-004: Eight meta-feature OOF stacking

**Status:** Accepted

**Context:** Stage 2 meta-classifier must consume expert outputs without training-set leakage.

**Decision:**

1. Hold out 20% test set before any preprocessing
2. On 80% pool: 5-fold stratified CV on phenotype labels
3. Each fold: train 4 experts on folds ≠ k; predict fold k only
4. Concatenate → $P_{\text{OOF}}$ with **8 columns** (4 experts × phenotype + severity preds)
5. Train ElasticNet `LogisticRegression(penalty='elasticnet', solver='saga')` on $P_{\text{OOF}}$
6. Retrain experts on full 80%; evaluate on locked 20% holdout

**Consequences:** No sample appears in both expert training and its own OOF prediction row.

---

## ADR-005: Semester-first roadmap sync

**Status:** Accepted

**Context:** 3-year academic calendar maps better to planning than legacy phase-only grouping.

**Decision:** GitHub issues titled `[Y1 Summer 2026] ...` with sync-ids like `year-1-summer-2026-phase-1-step-1-item-1-...`.

**Consequences:** Requires one-time `--prune-project` if stale phase-based issues remain on Project #2.

See [Roadmap and Tracking](Roadmap-and-Tracking).

---

## Related pages

- [Static MTL Baseline](Static-MTL-Baseline)
- [Code Map and Status](Code-Map-and-Status)
- [Glossary](Glossary)
