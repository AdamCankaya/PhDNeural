# Responsible Multi-Omic Neural Architecture Search: Ethical, Social, and Public-Health Considerations in the Spatio-Temporal Bio-NAS Program

*Breast cancer anchor cohort, controlled-access neurodegenerative data, and open reproducibility via Docker*

## Authoring note

This white paper was drafted and edited with assistance from **Cursor Composer 2.5** (AI). The human author reviewed all content, verified project-specific facts against the Bio-NAS repository and master plan, and remains responsible for the arguments and citations.

## Introduction and Objectives

### Motivation and intellectual merit

The Spatio-Temporal Dual-Track **Bio-NAS** program asks whether biologically informed neural architecture search—where connectivity is constrained by curated pathway knowledge (KEGG, Reactome) via masked linear layers—outperforms unconstrained neural architecture search on multi-omic disease trajectory prediction. The thesis design runs a rigorous **Track A (control)** versus **Track B (Bio-NAS)** comparison on a breast invasive carcinoma (BRCA) anchor cohort before scaling, under a documented **scaling gate**, to Alzheimer's disease, rheumatoid arthritis, type 2 diabetes, and epigenetic aging cohorts. Intellectual merit lies in coupling spatio-temporal deep learning (genomic “spatial” axes and longitudinal Δt embeddings) with reproducible experiment orchestration (Optuna, patient-level holdout, causal cross-validation).

### Broader impacts and objectives

Multi-omic machine learning touches sensitive human data, uneven cohort representation, and pathways toward clinical decision support. Even when the immediate goal is research software, stakeholders may misread pipeline smoke metrics as diagnostic evidence, re-identify participants from rich omics tables, or deploy models trained on convenience cohorts (for example TCGA) as if they were population-representative. This white paper maps **concrete Bio-NAS design choices** to ethical, social, environmental, and economic implications, and pairs each risk with mitigations already planned or implemented in the repository.

Objectives of this document are to: (1) explain why Bio-NAS raises distinct governance challenges compared with tabular clinical models; (2) analyze three project-native examples—mislabeled “toy” metrics, controlled-access data handling, and equity in cohort composition; and (3) align the three-year technical roadmap with responsible outcomes. In the same spirit of transparency applied to model outputs, we note that **Composer 2.5 assisted in drafting this paper**, while factual claims about Bio-NAS were checked against project documentation (for example `docker/README.md`, `docs/data/cohort_inventory.md`, and `phd_bio_nas_master_plan.md`).

### Non-goals

Plan-1 Docker demonstrations download small **open-access** public slices (for example TCGA-BRCA Level-3 methylation and RNA) and run CPU toy architecture search. Project documentation states explicitly that these runs **validate engineering workflows only** and are **not clinical evidence**. Full holdout benchmarks and attribution interfaces are Year 2–3 deliverables; until then, AUROC-style numbers from smoke demos must not inform patient care.

### Issue 1: Toy metrics mistaken for clinical truth

The epigenetic aging Docker smoke uses chronological age thresholds (for example age ≥ 50 as a binary label) solely to exercise the training pipeline; wiki text labels this a **pipeline validation label**, not clinical aging acceleration or disease status. Similarly, the static HTML dashboard and `train_toy_nas_cpu.py` distinguish clinical proxies (such as AJCC staging on BRCA smoke) from **synthetic** targets on other diseases. **Implication:** Without persistent labeling discipline, funders or collaborators may over-trust metrics from five to ten joint cases. **Mitigation:** Frozen nomenclature (“smoke” versus “holdout”), dashboard disclaimers, and planned OSS release notes (Summer 2029) that separate demo artifacts from frozen experiment IDs cited in the dissertation.

### Issue 2: Data governance, privacy, and reproducibility

Alzheimer's work locks **ADNI (LONI)** as the primary cohort, which requires an approved Data Use Agreement; the Docker entrypoint **scaffolds and skips** controlled download when credentials are absent—no automated LONI scrape—and stores skip status under `data/adni/`. Credentials belong in a gitignored host `.env`, never in the image. Type 2 diabetes primary **KORA** and dbGaP-controlled alternates (for example AURORA metastatic breast resources) remain **outside Docker** until project agreements complete, while the open reproducibility path documents honest limits in `cohort_inventory.md`. **Implication:** Open science and privacy pull in opposite directions if reproducibility is misread as “all cohorts ship in Compose.” **Mitigation:** Inventory verification lists controlled sources under `skipped_controlled`; human-in-the-loop DUA steps are documented exceptions to Docker-first implementation; post-DUA verification only after approval.

### Issue 3: Equity, representation, and multi-cohort fusion

TCGA-BRCA (~1,098 cases in inventory verification) is a practical anchor but **not demographically representative** of all patients with breast cancer; true repeated molecular timepoints are **sparse** on TCGA, with AURORA US documented as an alternate when paired primary–metastasis omics matter. Epigenetic aging harmonization (GSE40279, GSE87571, GSE280465) must address **tissue-specific and age distribution biases** per master-plan acceptance criteria. Rheumatoid arthritis integrates **unpaired** cohorts (GSE71841 methylation versus DAS28 severity anchors) with multi-task loss masking so severity is not falsely trained on the small healthy/RA methylation set (n≈24). **Implication:** Models may absorb ancestry, sex, or batch effects as apparent biology. **Mitigation:** Patient-level 80/20 holdout with automated leakage tests; subgroup sensitivity analyses in thesis synthesis; **scaling gate** limiting multi-disease Track B claims unless BRCA holdout shows advantage on accuracy, interpretability, and/or sparsity.

### Environmental and economic factors

Year 2 distributed Optuna search on Slurm carries non-trivial energy and cloud cost. Track B explicitly targets **computational sparsity** via pathway constraints; if sparsity improves without sacrificing holdout performance, that outcome supports both interpretability and greener large-scale search—a secondary economic and environmental benefit worth reporting alongside accuracy deltas.

## Project Plan

### Technical plan

The technical plan follows the three-year Bio-NAS master roadmap, with ethics and welfare coupling at each phase.

**Year 1 (Spring 2026 – Spring 2027) — sourcing, tensors, infrastructure.** Spring 2026 completes the five-disease **cohort inventory** with license and ethics columns (`docs/data/cohort_inventory.md`). Winter 2026–Spring 2027 builds leakage-safe four-dimensional tensors `(batch, time, spatial features, channels)`, Δt embeddings for irregular visits, and Dockerized PostgreSQL for Optuna metadata. Ethics coupling: document DUAs and IRB-aware ADNI use; defer controlled dbGaP files; enforce patient-level holdout before preprocessing to reduce optimistic bias that could later harm translation efforts.

**Year 2 (Summer 2027 – Spring 2028) — dual-track NAS and benchmarking.** Modular spatial (1D-CNN, spatial transformer) and temporal (ConvLSTM/GRU, attention) blocks feed separate Track A and Track B Optuna studies on BRCA. Winter 2027 runs large-scale search with causal cross-validation; Spring 2028 evaluates frozen **20% holdout** trajectories, ablations, and classical baselines—the **scaling gate** evidence base. Ethics coupling: report Track A versus Track B deltas with uncertainty; if Track B does not improve interpretability or sparsity, narrow claims before Other 4 scaling.

**Year 3 (Summer 2028 – Summer 2029) — interpretability, interface, release.** Summer 2028 implements Captum/SHAP attribution over CpG sites and timestamps, with Track B maps checked against pathway priors. Fall 2028 delivers a Streamlit trajectory dashboard; master-plan acceptance requires **auth and PII constraints documented** before any demo resembling clinical workflow. Winter 2028–Summer 2029 synthesizes cross-disease taxonomy (post–scaling gate) and releases tagged open-source Python with install docs and smoke boundaries.

### Anticipated outcomes

**Scientific outcomes:** Quantitative evidence on whether KEGG/Reactome-constrained `MaskedLinear` Bio-NAS beats unconstrained NAS on BRCA holdout for prediction, interpretability (pathway-plausible attributions), and sparsity. **Societal outcomes:** A reproducible Docker path for **public** data only; transparent status files for controlled cohorts; attribution exports intended for **expert human review**, not autonomous triage. **Risk monitoring:** Over-interpretation of SHAP/Captum maps as causal mechanisms; performance disparities across subgroups; accidental credential commits in OSS forks—each tracked via inventory honesty, holdout discipline, and planned `DATA_USE.md` at release.

### Schedule

| Period | Technical focus | Ethics and governance milestones |
|--------|-----------------|----------------------------------|
| Y1 Spring 2026 | All-5 inventory; BRCA PoC readiness | License/ethics table; ADNI DUA application (in progress) |
| Y1 Summer 2026 – Spring 2027 | Feature maps; 4D ETL; Optuna hub | Leakage tests; controlled cohorts marked outside Docker |
| Y2 Summer 2027 – Spring 2028 | Track A/B NAS; holdout benchmarks | Scaling gate decision; causal CV documented |
| Y3 Summer – Fall 2028 | Attribution; Streamlit dashboard | PII/auth review; demo ≠ clinical product |
| Y3 Winter 2028 – Summer 2029 | Taxonomy; thesis; OSS tag | Release notes; smoke vs holdout nomenclature frozen |

Calendar authority: Bio-NAS README and `phd_bio_nas_master_plan.md` (Spring 2026 through Summer 2029).

## References

[1] National Cancer Institute, “Genomic Data Commons (GDC) Data Access Policies and Data Use Certification,” GDC Portal, accessed 2026. [Online]. Available: https://portal.gdc.cancer.gov/

[2] Alzheimer's Disease Neuroimaging Initiative, “ADNI Data Use Agreement,” LONI IDA, accessed 2026. [Online]. Available: https://adni.loni.usc.edu/

[3] NIH National Human Genome Research Institute, “dbGaP Controlled-Access Data,” accessed 2026. [Online]. Available: https://www.ncbi.nlm.nih.gov/gap/

[4] NCBI, “Gene Expression Omnibus (GEO) Data Sharing and Access,” accessed 2026. [Online]. Available: https://www.ncbi.nlm.nih.gov/geo/info/faq.html

[5] S. Rajkomar, M. Hardt, M. D. Howell, G. Corrado, and M. H. Chin, “Ensuring Fairness in Machine Learning to Advance Health Equity,” *Annals of Internal Medicine*, vol. 169, no. 12, pp. 866–872, 2018.

[6] B. S. Obermeyer et al., “Dissecting racial bias in an algorithm used to manage the health of populations,” *Science*, vol. 366, no. 6464, pp. 447–453, 2019.

[7] S. Horvath, “DNA methylation age of human tissues and cell types,” *Genome Biology*, vol. 14, no. 10, p. R115, 2013.

[8] R. L. Wallace et al., “Ethical considerations for epigenetic clocks and biological age estimation,” *Frontiers in Genetics*, vol. 13, 2022, Art. no. 875722.

[9] U.S. Food and Drug Administration, “Artificial Intelligence/Machine Learning (AI/ML)-Based Software as a Medical Device (SaMD) Action Plan,” FDA, Jan. 2021.

[10] International Medical Device Regulators Forum, “Software as a Medical Device: Clinical Evaluation,” IMDRF, 2017.

[11] M. T. Ribeiro, S. Singh, and C. Guestrin, “"Why Should I Trust You?": Explaining the Predictions of Any Classifier,” in *Proc. ACM SIGKDD*, 2016, pp. 1135–1144.

[12] P. H. Chuang et al., “Interpretability and explainability in machine learning for genomics and epigenomics,” *Briefings in Bioinformatics*, vol. 24, no. 1, 2023.

[13] A. Cankaya, “PhDNeural Bio-NAS: Spatio-Temporal Dual-Track Multi-Omic Fusion,” GitHub repository, 2026. [Online]. Available: https://github.com/AdamCankaya/PhDNeural

[14] A. Cankaya, “Bio-NAS cohort inventory and Docker reproducibility documentation,” *PhDNeural/Bio-NAS*, paths `docs/data/cohort_inventory.md`, `docker/README.md`, 2026.

[15] A. Cankaya, “PhD Master Roadmap: Comparative Spatio-Temporal NAS for Multi-Omic Disease Prediction,” *phd_bio-nas_master_plan.md*, Bio-NAS, 2026.

[16] S. L. Wickler et al., “Environmental impacts of machine learning on biomedicine: a scoping review,” *Patterns*, vol. 4, no. 4, 2023.

[17] E. J. Topol, “High-performance medicine: the convergence of human and artificial intelligence,” *Nature Medicine*, vol. 25, pp. 44–56, 2019.

[18] Cursor, “Composer 2.5 (AI assistant),” used as a writing tool for this document—not listed as a scientific co-author, 2026.
