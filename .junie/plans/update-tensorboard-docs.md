---
sessionId: session-260802-145604-ibbz
---

# Requirements

### Overview & Goals
The goal of this task is to prepare the project's documentation, roadmaps, and issue trackers for the future implementation of TensorBoard logging. The actual PyTorch implementation is intentionally deferred; the current scope is strictly updating the planning documents to ensure the implementation is properly scheduled and specified.

### Scope
**In Scope**:
- Creating a new detailed plan issue for TensorBoard integration.
- Updating the `ROADMAP.md` to track this new issue.
- Updating the `phd_bio-nas_master_plan.md` and `Static-MTL-Baseline.md` wiki pages with the metric logging behavior and requirements.

**Out of Scope**:
- Writing or modifying any actual PyTorch `.py` code. The user has explicitly stated to only update the documentation for now.

### Functional Requirements for Future Implementation
- **Dynamic Writer Initialization**: The PyTorch training loop will initialize `torch.utils.tensorboard.SummaryWriter` with the directory `runs/mtl_experiment_{disease_name}`.
- **Training Metrics**: `Loss/Train_Phenotype` and `Loss/Train_Severity` tracked as separate scalars.
- **Evaluation Metrics**: `Eval/Pheno_AUROC` and `Eval/Severity_QWK` tracked separately.
- **Safety Condition**: Skip logging `Eval/Severity_QWK` if the custom `evaluate_mtl_metrics` function returns `np.nan` (which happens when healthy patients do not have a severity stage).
- **Resource Cleanup**: Ensure `writer.close()` is reliably called at the end of training.

# Technical Design

### Current Implementation Context
The project currently manages its implementation roadmap across a series of Markdown documents inside `Bio-NAS/docs/plans/`, coordinated by `ROADMAP.md` and `phd_bio-nas_master_plan.md`. There are currently 24 sequenced issues.

### Proposed Changes
We will create a 25th planning document specifically for the TensorBoard integration and link it across the tracker.

#### File Structure
- **Add**: `Bio-NAS/docs/plans/25-issue-378-tensorboard-integration.md`
- **Modify**: `Bio-NAS/docs/plans/ROADMAP.md`
- **Modify**: `Bio-NAS/phd_bio-nas_master_plan.md`
- **Modify**: `Bio-NAS/docs/wiki/Static-MTL-Baseline.md`

### Components
1. **Plan 25 Issue**: Will serve as the authoritative spec for the developer writing the TensorBoard integration, including the `np.nan` checking logic.
2. **ROADMAP.md**: Needs an updated mermaid flowchart and an expanded table to include issue 25 (e.g. sequentially following the modules/infrastructure setup, depending on Plan 12 search logic).
3. **Static MTL Baseline Wiki**: Needs an updated section documenting that the severity metric can output `np.nan` during validation, meaning downstream logging consumers must conditionally check it.

# Delivery Steps

### ✓ Step 1: create-tensorboard-plan-issue
The project's documentation will contain a new tracking issue detailing the TensorBoard setup.

- Create `Bio-NAS/docs/plans/25-issue-378-tensorboard-integration.md`.
- Detail the requirement for `torch.utils.tensorboard.SummaryWriter` and the dynamic path `runs/mtl_experiment_{disease_name}`.
- Detail the scalar tracking for training (`Loss/Train_Phenotype`, `Loss/Train_Severity`) and validation (`Eval/Pheno_AUROC`, `Eval/Severity_QWK`).
- Detail the requirement to conditionally skip logging `sev_qwk` when it evaluates to `np.nan` (due to missing healthy patient stages).
- Detail the requirement for `writer.close()`.

### ✓ Step 2: update-roadmap-tracker
The project roadmaps will properly reference and sequence the new TensorBoard integration plan.

- Update `Bio-NAS/docs/plans/ROADMAP.md` to increment the issue count to 25.
- Add `25-issue-378-tensorboard-integration.md` to the Implementation Order table.
- Add the new issue to the Phase/Year grouping table under "Year 2 Fall–Spring" (training loop execution).
- Update the Mermaid flowchart in `ROADMAP.md` to visually include the new plan issue as a dependency of the execution phases.

### ✓ Step 3: update-master-plan-and-wiki
The master plan and baseline wiki will include the TensorBoard logging specifications.

- Update `Bio-NAS/phd_bio-nas_master_plan.md` to include a checklist item for setting up TensorBoard tracking inside the Year 2 Q1 (or Q2) execution steps.
- Update `Bio-NAS/docs/wiki/Static-MTL-Baseline.md` to explicitly note that `sev_qwk` metrics will return `np.nan` on healthy batches and must be conditionally skipped by logging consumers.