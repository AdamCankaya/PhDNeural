# Glossary

| Term | Definition |
|------|------------|
| **Track A — Standard NAS** | Control arm: unconstrained neural architecture / hyperparameter search (layers, nodes, dropout) optimizing for mathematical performance without pathway masks |
| **Track B — Bio-NAS** | Innovation arm: NAS constrained by biological blueprints (KEGG, Reactome) via binary adjacency masks (`MaskedLinear`) so searched synapses respect known pathways |
| **Dual track** | Parallel experimental design with two arms (Track A control and Track B Bio-NAS) trained and evaluated under matched data, splits, and metrics |
| **Dual-Track A/B Test** | Rigid comparison of Track A vs Track B on the same cohort, splits, and metrics to test whether biological priors help |
| **Scaling gate** | Decision point after BRCA Track A vs B holdout (Y2 Summer): positive Track B advantage justifies dual-track work on the Other 4 pathologies |
| **Bio-NAS** | Biologically-Informed Neural Architecture Search — the Track B method and the overall research program name |
| **MaskedLinear** | Linear layer whose weights are element-wise masked by a binary adjacency matrix derived from pathway graphs |
| **Adjacency matrix** | Binary matrix encoding allowed connections between features/genes (1 = biologically permitted synapse, 0 = blocked) |
| **KEGG** | Kyoto Encyclopedia of Genes and Genomes — pathway database used as a Track B biological blueprint source |
| **Reactome** | Curated pathway knowledgebase used alongside KEGG for Track B constraints |
| **Biological prior** | Domain knowledge (pathways, GRNs) injected into the model to bias architecture/search toward biologically plausible structure |
| **Gene Regulatory Network (GRN)** | Graph of regulatory relationships among genes; an example anatomical/biological constraint for Bio-NAS |
| **Sparsity** | Preferring models that use fewer active parameters or synapses (e.g., pathway masks zeroing disallowed weights); a Track B evaluation criterion alongside accuracy and interpretability |
| **Interpretability** | How well predictions can be traced to biological features or pathways (e.g., Captum/SHAP attribution over CpG sites and timepoints); a core Track A vs B comparison axis |
| **PyTorch** | Primary deep-learning framework for spatial/temporal modules, `MaskedLinear`, MTL heads, and training loops |
| **Optuna** | Hyperparameter / architecture search library used for distributed Track A and Track B studies (with Hyperband pruning and RDB storage) |
| **Multi-omic** | Joint use of multiple molecular modalities (e.g., methylation, transcriptomics, genomics, CNV) in one fusion model |
| **Multi-task (MTL)** | Shared backbone with multiple prediction heads; baseline solves phenotype and severity together (Static MTL) |
| **Spatial** | Axis over genomic/feature structure (e.g., CpG sites, gene indices, pathway neighborhoods) modeled by 1D-CNNs / Spatial Transformers |
| **Temporal** | Axis over longitudinal visits and irregular intervals (Δt); modeled by ConvLSTM/GRU / temporal attention for progression forecasting |
| **Vertical slice** | End-to-end BRCA pipeline (data → model → Optuna → evaluation) for both tracks before generalizing to other diseases |
| **Anchor cohort (BRCA)** | Breast Invasive Carcinoma — primary PoC disease used to validate dual-track NAS before the comparative matrix |
| **Other 4** | Alzheimer's, Rheumatoid Arthritis (RA), Type 2 Diabetes (T2D), and Epigenetic Aging cohorts in the comparative matrix |
| **Comparative matrix** | Cross-disease Track A vs Track B evaluation spanning five functional categories (oncological, neurological, autoimmune, metabolic, chromosomal/aging) |
| **All 5** | BRCA + Other 4 |
| **Shared (A+B)** | Work that serves both tracks (ETL, infra, classical baselines, OSS packaging) without preferring one search space |
| **Stage 1 (legacy)** | Early fusion: concatenate raw modalities through a single MLP trunk — **superseded for NAS** by Intermediate Fusion; keep only as a software baseline |
| **Stage 2** | Stacked late fusion: 4 modality experts + ElasticNet meta-classifier on OOF predictions (unchanged; separate from Intermediate Fusion) |
| **Intermediate Fusion** | Multi-branch fusion: modality-specific encoders (`MethEncoder`, `RNAEncoder`) → concat latents → `FusionDecoder` / post-fusion dense; Optuna tunes branches before post-fusion (plans 07/10/12) |
| **MethEncoder** | Standalone methylation branch `nn.Module`; NAS-tunable layers/dropout/latent dims; betas mean-imputed, no Z-score/log |
| **RNAEncoder** | Standalone transcriptome branch `nn.Module`; input `log2(TPM+1)` then Z-score; tuned independently to avoid modality dominance |
| **FusionDecoder** | Post-fusion dense network after `torch.cat` of branch latents; final Optuna phase tunes these layers only |
| **Static MTL** | Multi-task learning with fixed two heads (phenotype + severity); no temporal sequence modeling |
| **Phenotype** | Binary task: Healthy (`0`) vs. Diseased (`1`) |
| **Severity** | Ordinal task: ordered classes `0..K-1` (K varies by disease) |
| **OOF** | Out-of-Fold — predictions generated by models that did not train on those samples |
| **$P_{\text{OOF}}$** | Clean out-of-fold prediction matrix covering the full 80% train pool with zero leakage |
| **8 meta-features** | Stage 2 stacking input: 4 experts × 2 tasks (phenotype + severity predictions each) |
| **Spatio-temporal NAS** | Architecture search over spatial modules (1D-CNN / Spatial Transformer) and temporal modules (ConvLSTM/GRU / attention) |
| **Δt embedding** | Learned encoding of irregular inter-visit time gaps so temporal models handle uneven sampling |
| **`(B, T, S, C)` tensor** | Batch × Time × Spatial features × Channels multi-omic layout stored in HDF5 |
| **Causal CV** | Cross-validation that respects temporal order (no future-visit leakage into earlier steps) |
| **HyperbandPruner** | Optuna pruner that stops unpromising trials early during distributed search |
| **phd-sync-id** | Stable identifier in issue HTML comments for idempotent GitHub sync |
| **Additive sync** | Default sync mode: new plan items create issues; removed items stay open unless `--close-stale` |
| **Disease registry** | `src/config/disease_registry.yaml` — per-disease phenotype/severity column mappings and K |
| **Severity masking (`-1`)** | Missing severity labels use `-1` and mask the ordinal loss (e.g. normal tissue without stage) |
| **Quarter-first roadmap** | Tasks grouped by Year 1–3 quarters (Fall 2026 → Summer 2029); **24** checklist items each linked to a `phd-sync` issue |
| **Cox-PH** | Cox Proportional Hazards — optional post-thesis prognostic head; **not** in Static MTL baseline |

## Related pages

- [Static MTL Baseline](Static-MTL-Baseline)
- [Roadmap and Tracking](Roadmap-and-Tracking)
- [FAQ and Troubleshooting](FAQ-and-Troubleshooting)
- [Workflow](Workflow)
