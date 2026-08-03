# Multi-disease cohort inventory (Plan 01 / issue #354)

Inventory of candidate cohorts with **repeated molecular measurements over time** for BRCA, Alzheimer's, Rheumatoid Arthritis, Type 2 Diabetes, and **Epigenetic Aging**.

| Field | Value |
|-------|-------|
| Plan | [`docs/plans/01-issue-354-multi-disease-dataset-inventory.md`](../plans/01-issue-354-multi-disease-dataset-inventory.md) |
| Issue | [#354](https://github.com/AdamCankaya/PhDNeural/issues/354) |
| Companion CSV | [`cohort_inventory.csv`](cohort_inventory.csv) |
| BRCA template | [`docs/wiki/Data-Acquisition-BRCA.md`](../wiki/Data-Acquisition-BRCA.md) |
| Draft date | 2026-07-24 |
| Last updated | 2026-08-02 — RA and Epigenetic Aging primaries **LOCKED**; All 5 diseases now locked |

## How to read this table

- **Primary (locked)** = user-selected cohort for that disease (source of truth for next Plan 01 / ETL steps).
- **Primary (recommended)** = preferred next step; not yet user-locked.
- **Alternate** = strong backup (may be single-omic or harder access).
- **Exploratory** = useful for prototyping ETL / Δt logic; not the Year-3 scaling pick by default.
- Sample counts are **approx / ranges** from public metadata or papers. Prefer portal verification before locking ETL.
- **Controlled-access** candidates are included and **flagged** explicitly.
- Single-omic series are marked **alternate/exploratory only** when multi-omic options exist.

### Acceptance (≥2 timepoints)

| Disease | ≥1 candidate with ≥2 molecular timepoints documented? |
|---------|--------------------------------------------------------|
| BRCA | **Yes** — primary **TCGA-BRCA** (sparse true molecular repeats); alternate **AURORA US** for genuine primary↔metastasis pairs |
| Alzheimer's | **Yes** (ADNI longitudinal blood methylation ± genomics; clinical waves) |
| Rheumatoid Arthritis | **Yes** (GSE138747 baseline + ~3 months, RNA + methylation) |
| Type 2 Diabetes | **Yes** (KORA F4→FF4 methylation; GSE184050 two RNA timepoints) |
| Epigenetic Aging | **Yes** (LBC1936 / SATSA multi-wave blood methylation) |

---

## Selections locked

User decisions recorded here. Unlock/change only by explicit decision (do not silently swap primaries).

| Disease | Status | Selected / recommended primary | Notes |
|---------|--------|--------------------------------|-------|
| BRCA | **LOCKED** | **TCGA-BRCA** (GDC) | Year-1/2 multi-omic anchor. Open Level-3 **PoC minimum** = meth betas + RNA + clinical/labels; controlled/dbGaP **deferred**. GDC token **not required** for open Plan 1/2 API smoke/metadata. True serial molecular repeats are **weak** on TCGA — keep AURORA US as the longitudinal-molecular alternate for Plan 02 pairing work. |
| Alzheimer's | **LOCKED** | **ADNI** (LONI IDA) | Primary locked 2026-07-27. Blood EPIC methylation + genotype + clinical (± imaging). **ADNI/LONI account + DUA in progress** (user applying) — no controlled bulk/sample download can succeed yet. Docker scaffold skips without credentials (`scripts/download_adni_sample.py`). ROSMAP stays unlocked alternate. |
| Rheumatoid Arthritis | **LOCKED** | **GSE71841 & DAS28 Cohorts** | GSE71841 as Phenotype Anchor; DAS28 cohorts as Severity Anchor. Unpaired multi-omic architecture with zero-imputation. All RA data sources are public and immediately available. |
| Type 2 Diabetes | **LOCKED** | **KORA F4/FF4** | Primary source for T2D. Will apply for data access (12 week processing). GSE184050 may be used as well. |
| Epigenetic Aging | **LOCKED** | **GSE40279, GSE87571, GSE280465** | Fused datasets to build an epigenetic clock with an Elastic Net regression baseline to compute EAA. K=4 discretized severity output. |

---

## Quick-pick summary

| Disease | Primary | Selection | Access | Multi-omic? | ≥2 molecular timepoints? |
|---------|---------|-----------|--------|-------------|--------------------------|
| BRCA | **TCGA-BRCA** (GDC) | **LOCKED** | Open Level-3 PoC (meth+RNA+clinical); controlled deferred; token not required for Plan 1/2 | Yes | **Weak** on TCGA; use **AURORA US** when true molecular repeats matter |
| Alzheimer's | **ADNI** (LONI) | **LOCKED** | Controlled (DUA **in progress**) | Methylation + genotype + clinical (± imaging) | **Yes** (~annual visits, up to ~4y) |
| RA | **GSE71841 & DAS28** | **LOCKED** | Open | Phenotype: 450K methylation (GSE71841); Severity: RNA-seq, WES, metabolites (DAS28) | **Yes** (DAS28 cohorts) |
| T2D | **KORA F4/FF4** | **LOCKED** | Controlled (project agreement) | Methylation (2 waves) + RNA-seq (FF4) | **Yes** (~7y between F4 and FF4) |
| Epigenetic Aging | **GSE40279, GSE87571, GSE280465** | **LOCKED** | Open | DNA methylation (Illumina 450K and EPIC arrays) | **Yes** (fused chronologically) |

---

## Full inventory

Columns match [`cohort_inventory.csv`](cohort_inventory.csv).

### BRCA (oncological anchor)

| cohort_name | source_portal | accession_or_id | access_method | license_ethics_notes | modalities | n_subjects_approx | n_samples_approx | timepoints_or_visits | longitudinal_notes | recommended_priority | selection_status | url | verification_status | needs_account_or_api_key |
|-------------|---------------|-----------------|---------------|----------------------|------------|-------------------|------------------|----------------------|--------------------|----------------------|------------------|-----|---------------------|--------------------------|
| TCGA-BRCA | GDC | TCGA-BRCA (dbGaP phs000178 for controlled — **deferred**) | open (Level-3 open); controlled (BAM/raw) deferred | TCGA open clinical/molecular Level-3; controlled requires dbGaP (not Plan 1/2) | **PoC minimum:** methylation, RNA-seq, clinical (+ inventory lists miRNA/CNV/mutations/RPPA) | **1,098** cases (GDC summary 2026-07-27) | open meth beta cases **1,097**; STAR RNA cases **1,095**; project files **70,774** | mostly 1 molecular visit; rare TM/NT co-samples | **SELECTED primary.** Year-1/2 multi-omic PoC anchor. True serial molecular repeats are sparse (~7 metastatic TM in older Firehose snapshots). Clinical follow-up ≠ repeated omics. Regenerable verify: `scripts/verify_cohort_inventory_open.py` → `/data/tcga/inventory_verification/`. | primary (locked) | locked | https://portal.gdc.cancer.gov/projects/TCGA-BRCA | **verified_gdc_api** (2026-07-27; live counts may drift) | **no for Plan 1/2 open API smoke** — GDC token optional (portal bulk UX later); dbGaP only if controlled files needed later |
| AURORA US Metastatic Breast Multiomics | GEO + dbGaP (+ TCIA imaging) | GSE209998 / GSE212375; dbGaP phs002622 | open (processed GEO subsets); controlled (dbGaP raw/full) | Publication consortia DUAs for controlled; GEO processed often open | RNA-seq, WES/WGS, DNA methylation, clinical | ~55 patients (retrospective phase) | ~51 primaries + ~102 metastases | ≥2 tissue timepoints (primary + metastasis; some multi-met) | **Alternate** for true paired molecular timepoints (primary↔met). Prefer when Plan 02 needs genuine molecular repeats that TCGA lacks. Counts TBD — verify on GEO/dbGaP. | alternate (longitudinal molecular) | unlocked_alternate | https://www.cancerimagingarchive.net/collection/aurora-metastatic-breast-multiomics/ | unverified_public_metadata | yes — **dbGaP** for full multi-omic; NCBI/GEO optional for open matrices |
| AURORA BIG (EU) | Program / controlled repositories | BIG AURORA MBC (see Cancer Discovery 2022) | controlled / account+DUA | Consortia access; not a single open GEO dump | targeted DNA, RNA-seq subsets, clinical | ~381 profiled; paired RNA-seq ~152 | TBD — verify on program portal | primary + early metastasis pairs | Large paired primary–met resource; access path TBD. | exploratory | unlocked_exploratory | https://pubmed.ncbi.nlm.nih.gov/35850122/ | needs_dua | yes — program/DAC credentials (TBD) |
| I-SPY2 transcriptomic (+ serial MRI) | GEO + TCIA | GSE194040 (mRNA); TCIA ISPY2 | open (GEO expression; TCIA imaging CC-BY) | Trial data; check GEO/TCIA terms | gene expression (often pre-treatment); serial MRI | ~987 with pretreatment expression | ~987 expression; MRI multi-visit subset larger | imaging: multiple NAC visits; **molecular often single pre-treatment** | Strong imaging Δt; weak molecular repeats in public release. | exploratory | unlocked_exploratory | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE194040 | unverified_public_metadata | no for GEO matrices; TCIA optional |

### Alzheimer's Disease

| cohort_name | source_portal | accession_or_id | access_method | license_ethics_notes | modalities | n_subjects_approx | n_samples_approx | timepoints_or_visits | longitudinal_notes | recommended_priority | selection_status | url | verification_status | needs_account_or_api_key |
|-------------|---------------|-----------------|---------------|----------------------|------------|-------------------|------------------|----------------------|--------------------|----------------------|------------------|-----|---------------------|--------------------------|
| ADNI (blood EPIC methylation + genomics/clinical) | LONI IDA | ADNI (methylation studies ~n=650 subjects in published analyses) | controlled / account+DUA | ADNI Data Use Agreement required; IRB-aware use. **Account + DUA in progress** (user applying 2026-07-27). | DNA methylation (EPIC), GWAS, clinical/cognitive, imaging, CSF biomarkers | ~650 with methylation in published EWAS; ADNI overall larger | ~1,700+ methylation samples after QC in papers | baseline + follow-ups ~1y apart, up to ~4y | **SELECTED primary.** Best AD fit for molecular Δt. Multi-omic via methylation + genotype + clinical (± imaging). Docker scaffold: `scripts/download_adni_sample.py` → `/data/adni` (skip until credentials). Verify **post-DUA** (no public LONI API without login). | primary (locked) | locked | https://adni.loni.usc.edu/data-samples/adni-data/ | needs_dua (account **in progress**) | yes — **ADNI/LONI account + DUA required** (in progress) |
| ROSMAP (AMP-AD) | Synapse AD Knowledge Portal | syn3219045 (study); metadata syn3157322 | controlled / account+DUA | Synapse + Data Use Certificate (DUC) | genotypes, WGS, methylation, RNA-seq, ChIP-seq, proteomics (generation ongoing), rich clinical | ROS+MAP >3,000 enrolled; omic subsets hundreds–thousands | RNA-seq ~638; methylation ~740 (first-gen atlas; growing) | **Clinical** longitudinal; **brain omics usually one postmortem sample** | Excellent multi-omic AD/aging biology; limited repeated *molecular* timepoints on same tissue. Use for phenotype severity later. | alternate | unlocked_alternate | https://adknowledgeportal.synapse.org/Explore/Studies/DetailsPage?Study=syn3219045 | needs_dua | yes — **Synapse account + ADKP DUC required** |
| Progressive MCI / AD blood RNA-seq | GEO | GSE282742 | open | GEO open; raw not provided | RNA-seq (WBC) | P-MCI ~28, S-MCI ~39, AD ~49 (+ serial draws) | ~100+ samples (serial subject IDs present) | ≥2 draws for many converters (ages differ across GSM rows) | Longitudinal *clinical progression* with repeated blood RNA. **Single-omic** → exploratory only under multi-omic preference. | exploratory | unlocked_exploratory | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE282742 | unverified_public_metadata | no (optional NCBI login) |
| AddNeuroMed / related blood methylation | GEO | GSE153712 (and related) | open | GEO open | methylation (EPIC) | TBD — verify on GEO | TBD — verify on GEO | often case/control; confirm visit labels on portal | Useful open methylation; confirm longitudinal vs cross-sectional before ETL. Single-omic. | exploratory | unlocked_exploratory | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE153712 | unverified_public_metadata | no (optional NCBI login) |

### Rheumatoid Arthritis

| cohort_name | source_portal | accession_or_id | access_method | license_ethics_notes | modalities | n_subjects_approx | n_samples_approx | timepoints_or_visits | longitudinal_notes | recommended_priority | selection_status | url | verification_status | needs_account_or_api_key |
|-------------|---------------|-----------------|---------------|----------------------|------------|-------------------|------------------|----------------------|--------------------|----------------------|------------------|-----|---------------------|--------------------------|
| RA Phenotype Anchor | GEO | GSE71841 | open | GEO open | DNA methylation (450K) | 24 (12 RA, 12 healthy) | 24 | baseline | Provides the healthy baseline for the binary Phenotype prediction. | primary (locked) | locked | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE71841 | unverified_public_metadata | no |
| RA Severity Anchor | Various | DAS28 cohorts | open | Open access | RNA-seq, WES, plasma metabolites | TBD | TBD | baseline + follow-ups | Provides the severity groups (DAS28L, DAS28M, DAS28H) for the ordinal Severity prediction. | primary (locked) | locked | N/A | unverified_public_metadata | no |

**Unpaired Multi-Omic Architecture Strategy:**
- **Datasets:** The Phenotype and Severity anchors feature completely different patients and distinct biological modalities. All data sources are public and immediately available.
- **Encoders:** Independent PyTorch `nn.Module` encoders for each modality (Methylation, RNA-seq, Metabolomics).
- **Zero-Imputation Strategy:** Implemented in the `Dataset` class. Missing modalities are filled with zero tensors, and a boolean mask vector (e.g., `[1, 0, 0]`) indicates which specific modalities are present.
- **Unified Latent Fusion Strategy:** Concatenate the outputs of the available encoders alongside the boolean mask vector. The mask is passed explicitly into the fully connected layers so the network learns to ignore the zeroed-out nodes and make predictions based purely on the available latent space.
- **Routing the MTL Losses:**
  - *GSE71841 Healthy Patient:* Phenotype Target = 0, Severity Target = -1 (Severity loss is bypassed/masked).
  - *GSE71841 RA Patient:* Phenotype Target = 1, Severity Target = -1 (Masked to prevent confusing the CORAL loss with arbitrary staging).
  - *DAS28 Cohort Patient:* Phenotype Target = 1, Severity Target = 0, 1, 2, or 3 (Depending on mapped DAS28 clinical tier).

### Type 2 Diabetes

| cohort_name | source_portal | accession_or_id | access_method | license_ethics_notes | modalities | n_subjects_approx | n_samples_approx | timepoints_or_visits | longitudinal_notes | recommended_priority | selection_status | url | verification_status | needs_account_or_api_key |
|-------------|---------------|-----------------|---------------|----------------------|------------|-------------------|------------------|----------------------|--------------------|----------------------|------------------|-----|---------------------|--------------------------|
| KORA F4 / FF4 | Helmholtz Munich KORA.PASST | KORA F4→FF4 (no single public GEO dump for full longitudinal set) | controlled / account+DUA (project agreement) | Board-approved project agreement; European cohort ethics | DNA methylation (450K F4; EPIC FF4); RNA-seq (FF4 ~1,543); clinical/metabolic | papers use ~1,800+ with paired traits; exact dual-wave methylation n TBD on application | F4 and FF4 arrays separately; overlap TBD | **2 survey waves ~7 years apart** | **Best T2D multi-omic longitudinal candidate.** RNA-seq denser at FF4; methylation spans both waves. | primary (recommended) | recommended_unlocked | https://www.helmholtz-munich.de/en/epi/cohort/kora | needs_dua | yes — **KORA.PASST account + project proposal/agreement required** |
| CCHC T2D transition RNA-seq | GEO | GSE184050 | open | GEO open | RNA-seq | cases ~50 + controls ~66 (2 timepoints each in design) | 116 listed GSM rows | 2 RNA timepoints per subject (nested case–control transition) | Strong open longitudinal RNA for incidence transition. **Single-omic** → alternate. | alternate | unlocked_alternate | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE184050 | unverified_public_metadata | no |
| Metformin response drug-naïve T2D RNA-seq | GEO | GSE153315 | open | GEO open | RNA-seq | ~20 T2D + ~10 controls | pre/post therapy subset TBD | ~3 months metformin follow-up | Small n; drug-response Δt. Single-omic. | exploratory | unlocked_exploratory | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE153315 | unverified_public_metadata | no |
| recount3 / GTEx-style reprocessed RNA (T2D-tagged projects) | Bioconductor recount3 | project-dependent (select T2D GEO/SRA studies) | open (reprocessed counts) | inherits source study licenses | RNA-seq (harmonized) | study-dependent | study-dependent | only if underlying study is longitudinal | Useful **ETL rehearsal** layer after picking a longitudinal accession; not a cohort by itself. | exploratory | unlocked_exploratory | https://bioconductor.org/packages/recount3/ | unverified_public_metadata | no |

### Epigenetic Aging

> **Registry note:** `src/config/disease_registry.yaml` still has placeholder disease key `down_syndrome` (chromosomal). Plan 01 / README inventory the fifth category as **Epigenetic Aging**. Do **not** invent severity maps here; resolve naming in a later registry PR after cohort lock.

| cohort_name | source_portal | accession_or_id | access_method | license_ethics_notes | modalities | n_subjects_approx | n_samples_approx | timepoints_or_visits | longitudinal_notes | recommended_priority | selection_status | url | verification_status | needs_account_or_api_key |
|-------------|---------------|-----------------|---------------|----------------------|------------|-------------------|------------------|----------------------|--------------------|----------------------|------------------|-----|---------------------|--------------------------|
| Hannum blood methylation | GEO | GSE40279 | open | GEO open | DNA methylation (450K) | 656 | 656 | 1 timepoint | Spans ages 19-101. Provides massive anchor for adult/geriatric aging. | primary (locked) | locked | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE40279 | unverified_public_metadata | no |
| Johansson blood methylation | GEO | GSE87571 | open | GEO open | DNA methylation (450K) | 729 | 729 | 1 timepoint | Spans ages 14-94. | primary (locked) | locked | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE87571 | unverified_public_metadata | no |
| Multi-tissue methylation | GEO | GSE280465 | open | GEO open | DNA methylation (arrays) | TBD | TBD | 1 timepoint | Covers diverse cell types (buccal epithelial, saliva, dry blood spots). | primary (locked) | locked | N/A | unverified_public_metadata | no |

**Epigenetic Aging Pipeline & MTL Strategy:**
- **Data Harmonization:** Combine GSE40279, GSE87571, and GSE280465 by extracting the intersection of overlapping CpG probes between Illumina 450K and EPIC arrays.
- **Bias Mitigation:**
  - *Tissue-Specific Bias:* Stratify multi-tissue arrays evenly in training batches.
  - *Age Distribution Gaps:* Fuse diverse cohorts to ensure continuous support across the non-linear chronological axis.
- **MTL Baseline (EAA):** A scikit-learn Elastic Net model trained on healthy controls predicts epigenetic age from methylation beta values. `EAA = Predicted Age - Chronological Age`.
- **Ordinal Target Discretization:** EAA is binned into 4 classes: 0 (Normal, $\le$ 0y), 1 (Mild, 0 to +3y), 2 (Moderate, +3 to +7y), 3 (Severe, > +7y).
- **Loss Routing:** Phenotype = 1 (Diseased) or 0 (Healthy). Severity = EAA Class (0-3), or -1 if chronological age is missing.

---

## Accounts, DUAs, and API keys

Inventory drafting does not require credentials. **BRCA** (open Level-3) and **Alzheimer's** (ADNI locked) account status:

| Priority | Account / agreement | Needed for | Status / needed vs optional |
|----------|---------------------|------------|------------------------------|
| **1** | **GDC Portal account** (+ download token) | Optional portal bulk UX later; **not** required for Plan 1/2 open API smoke / metadata | **Optional for Plan 1/2** — open Level-3 needs no token; no dbGaP for PoC |
| **2** | **ADNI / LONI IDA + DUA** | **ADNI primary (LOCKED)** | **In progress** — user applying (2026-07-27). Required before any controlled download. Host `.env` (`ADNI_USER` / `ADNI_PASSWORD`) only — never bake into Docker. |
| 3 | **KORA.PASST + project agreement** | KORA F4/FF4 (if locked) | **Required** only after T2D primary lock |
| 4 | **Lothian Birth Cohorts / EGA DAC** | LBC1936 (if locked) | **Required** only after Epigenetic Aging primary lock |
| 5 | **Synapse + AD Knowledge Portal DUC** | ROSMAP (AD alternate) | **Required** only if ROSMAP chosen |
| 6 | **dbGaP authorized access** (eRA / institutional PI) | AURORA US full multi-omic; NAS/FHS aging; TCGA controlled BAMs | **Deferred** — not needed for TCGA Level-3 open Plan 1/2 |
| 7 | **NCBI account** | GEO / SRA convenience (RA GSE138747, open T2D/aging) | **Optional** for open GEO series |
| 8 | **NCBI E-utils API key** | Higher GEO/SRA query rate limits | **Optional** |

**TCGA-BRCA access split:** Open Level-3 (clinical + processed molecular; PoC minimum meth+RNA+clinical) is the locked Plan 1/2 path and does **not** need a GDC token or dbGaP. Controlled BAM/raw (phs000178) stays deferred until explicitly requested.

---

## Plan 01 status split (BRCA / AD vs remaining Other-3)

| Slice | Status | Notes |
|-------|--------|-------|
| **BRCA Plan-1** | **Complete** for open path | Primary locked; GDC API verified; Docker chain = download → inventory verify → optional toy NAS; expected pins in `docs/data/smoke_expected.json`. Controlled/dbGaP still deferred. |
| **Alzheimer's Plan-1** | **Primary locked; Docker scaffold done; DUA open** | ADNI (LONI) locked. Account + DUA **in progress**. Compose adds ADNI scaffold (skip without creds) + optional AD meth NAS when sample present. Inventory verify for ADNI is **post-DUA** (no public login-free API). |
| **Remaining Other-3** | **Open** | RA / T2D / Epigenetic Aging primaries still recommended-unlocked. |

## Next concrete Plan 01 steps (BRCA + AD lock done; DUA + Other-3 remaining)

1. ~~Spot-verify TCGA-BRCA~~ — done via `scripts/verify_cohort_inventory_open.py` (`verified_gdc_api`, 2026-07-27). Re-run anytime inside Compose.
2. ~~Lock Alzheimer's primary → ADNI~~ — done 2026-07-27; ROSMAP alternate.
3. **Complete ADNI/LONI account + DUA** (outside Docker) → then stage sample under `data/adni/` or extend download script; AD inventory verify post-DUA.
4. **Lock or reject remaining primaries** (RA / T2D / Epigenetic Aging) — clarifying questions below.
5. After each lock, start only the matching account/DUA from the table above (do not apply for everything at once).
6. For open GEO primaries (likely RA): pull series metadata + confirm baseline/3-mo pairing counts without credentials (optional extend verify script).
7. Keep AURORA US in inventory as BRCA longitudinal alternate; defer dbGaP until Plan 02 needs true molecular repeats beyond open metadata.
8. Resolve `down_syndrome` → Epigenetic Aging registry naming in a later PR after the fifth primary is locked (no invented severity maps).

### Clarifying questions (to lock remaining Other-3)

1. ~~**Alzheimer's:** Lock **ADNI** as primary?~~ — **LOCKED** ADNI (LONI); DUA in progress.
2. **RA:** Lock **GSE138747** (open multi-omic), or keep shopping for a larger controlled cohort?
3. **T2D:** Lock **KORA F4/FF4** (best multi-omic Δt, controlled), or start with open **GSE184050** RNA-only for faster ETL rehearsal?
4. **Epigenetic Aging:** Lock **LBC1936** (controlled), or open **SATSA (E-MTAB-7309)** first?
5. **Registry naming:** When the fifth primary is locked, rename `down_syndrome` → `epigenetic_aging` (or keep key + alias)?

---

## Notes

1. **Multi-omic preference:** Primaries prioritized for ≥2 modalities (or methylation + genotype + rich clinical for AD/aging). Pure RNA or pure methylation series are alternate/exploratory.
2. **BRCA longitudinal gap:** TCGA-BRCA is the **locked** Year-1/2 multi-omic anchor, but a poor natural longitudinal molecular cohort. Use AURORA (or similar paired primary–met) when Plan 02 matching needs genuine molecular repeats.
3. **`down_syndrome` vs Epigenetic Aging:** Registry placeholder key is `down_syndrome`; this inventory covers **Epigenetic Aging** per Plan 01 / README. Severity maps intentionally untouched.
4. **Verification:** TCGA-BRCA is `verified_gdc_api`. Other rows marked `unverified_public_metadata` / `needs_dua` should be spot-checked after account creation; replace TBD counts before ETL freeze (Plan 02+).
5. **Out of scope here:** visit-pairing rules (Plan 02), feature axes / HDF5 (Plans 03–07), Other-4 full ETL (Year 3 gate).
