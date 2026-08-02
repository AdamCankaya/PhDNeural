# Plan 25: Integrate TensorBoard Logging into Training Loop

## Issue reference

| Field | Value |
|-------|-------|
| Number | [378](https://github.com/AdamCankaya/PhDNeural/issues/378) |
| Title | [Y2 Fall-Spring] Integrate TensorBoard into existing Static MTL training loop |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/378 |
| Labels | `phd-sync, year-2, phase-3, logging, step-1` |
| Year / Quarter | 2 - Spatio-Temporal NAS Execution & Multi-Task Forecasting |
| Phase | 3 - Scaling to the Comparative Matrix |
| Master-plan goal | Enable continuous trajectory monitoring and logging for multi-task model evaluation. |

## Goals / requirements checklist

- [ ] **Dynamic Writer Initialization**: The PyTorch training loop will initialize `torch.utils.tensorboard.SummaryWriter` with the directory `runs/mtl_experiment_{disease_name}`.
- [ ] **Training Metrics Logging**: `Loss/Train_Phenotype` and `Loss/Train_Severity` must be tracked as separate scalars.
- [ ] **Evaluation Metrics Logging**: `Eval/Pheno_AUROC` and `Eval/Severity_QWK` must be tracked separately.
- [ ] **Safety Condition**: Skip logging `Eval/Severity_QWK` if the custom `evaluate_mtl_metrics` function returns `np.nan` (which happens when healthy patients do not have a severity stage).
- [ ] **Resource Cleanup**: Ensure `writer.close()` is reliably called at the end of training.

## Technical Context
The models are trained across 5 different disease pipelines, outputting two tasks simultaneously: a binary Phenotype prediction and an ordinal Severity prediction. Metrics are evaluated using the custom `evaluate_mtl_metrics` function. A crucial detail is that we use a `missing_policy: mask` for severity. Healthy patients do not have a severity stage. Therefore, if a validation batch only contains healthy patients, the `sev_qwk` metric will return `np.nan`.

## Implementation Approach
1. **Initialize `SummaryWriter`**: Modify the training entrypoint to initialize a TensorBoard writer. Ensure the log path includes the dynamic `disease_name`.
2. **Train Step Changes**: In the training loop, after backpropagation, add `writer.add_scalar()` calls for `Loss/Train_Phenotype` and `Loss/Train_Severity`.
3. **Validation Step Changes**: During the validation pass, capture the output from `evaluate_mtl_metrics`. Log `Eval/Pheno_AUROC` normally. Use an `if not np.isnan(sev_qwk)` or `math.isnan` block to conditionalize logging for `Eval/Severity_QWK`.
4. **Cleanup**: Wrap training or use `try/finally` block to guarantee `writer.close()` is executed when the training completes or throws an exception.
