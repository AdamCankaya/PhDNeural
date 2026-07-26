# Multi-disease cohort inventory (Plan 01 / issue #354)

Inventory of candidate cohorts with **repeated molecular measurements over time** for BRCA, Alzheimer's, Rheumatoid Arthritis, Type 2 Diabetes, and **Epigenetic Aging**.

| Field | Value |
|-------|-------|
| Plan | [`docs/plans/01-issue-354-multi-disease-dataset-inventory.md`](../plans/01-issue-354-multi-disease-dataset-inventory.md) |
| Issue | [#354](https://github.com/AdamCankaya/PhDNeural/issues/354) |
| Companion CSV | [`cohort_inventory.csv`](cohort_inventory.csv) |
| BRCA template | [`docs/wiki/Data-Acquisition-BRCA.md`](../wiki/Data-Acquisition-BRCA.md) |
| Draft date | 2026-07-24 |
| Last updated | 2026-07-24 — BRCA primary **locked** to TCGA-BRCA (GDC) |

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
| BRCA | **LOCKED** | **TCGA-BRCA** (GDC) | Year-1/2 multi-omic anchor. Open Level-3 is sufficient for PoC; dbGaP only if controlled BAM/raw needed. True serial molecular repeats are **weak** on TCGA — keep AURORA US as the longitudinal-molecular alternate for Plan 02 pairing work. |
| Alzheimer's | Recommended (unlocked) | ADNI (LONI) | Requires ADNI/LONI DUA before download. |
| Rheumatoid Arthritis | Recommended (unlocked) | GEO GSE138747 | Open multi-omic; optional NCBI login. |
| Type 2 Diabetes | Recommended (unlocked) | KORA F4/FF4 | Requires KORA.PASST + project agreement. |
| Epigenetic Aging | Recommended (unlocked) | LBC1936 | Requires Edinburgh / EGA DAC. Registry key still `down_syndrome` (naming mismatch). |

---

## Quick-pick summary

| Disease | Primary | Selection | Access | Multi-omic? | ≥2 molecular timepoints? |
|---------|---------|-----------|--------|-------------|--------------------------|
| BRCA | **TCGA-BRCA** (GDC) | **LOCKED** | Open Level-3; controlled BAM/raw optional | Yes | **Weak** on TCGA; use **AURORA US** when true molecular repeats matter |
| Alzheimer's | ADNI (LONI) | recommended | Controlled (DUA) | Methylation + genotype + clinical (± imaging) | **Yes** (~annual visits, up to ~4y) |
| RA | GSE138747 (GEO) | recommended | Open | RNA-seq + methylation | **Yes** (baseline + 3 mo) |
| T2D | KORA F4/FF4 | recommended | Controlled (project agreement) | Methylation (2 waves) + RNA-seq (FF4) | **Yes** (~7y between F4 and FF4) |
| Epigenetic Aging | LBC1936 | recommended | Controlled (request / EGA DAC) | Methylation multi-wave + genetics via cohort | **Yes** (waves ~age 70/73/76/79) |

---

## Full inventory

Columns match [`cohort_inventory.csv`](cohort_inventory.csv).

### BRCA (oncological anchor)

| cohort_name | source_portal | accession_or_id | access_method | license_ethics_notes | modalities | n_subjects_approx | n_samples_approx | timepoints_or_visits | longitudinal_notes | recommended_priority | selection_status | url | verification_status | needs_account_or_api_key |
|-------------|---------------|-----------------|---------------|----------------------|------------|-------------------|------------------|----------------------|--------------------|----------------------|------------------|-----|---------------------|--------------------------|
| TCGA-BRCA | GDC | TCGA-BRCA (dbGaP phs000178 for controlled) | open (Level-3 open); controlled (BAM/raw) | TCGA open clinical/molecular Level-3; controlled requires dbGaP | methylation, RNA-seq, miRNA, CNV, mutations, RPPA, clinical | ~1,098 cases | methylation/RNA ~1,097 cases; files tens of thousands | mostly 1 molecular visit; rare TM/NT co-samples | **SELECTED primary.** Year-1/2 multi-omic PoC anchor. True serial molecular repeats are sparse (~7 metastatic TM in older Firehose snapshots). Clinical follow-up ≠ repeated omics. | primary (locked) | locked | https://portal.gdc.cancer.gov/projects/TCGA-BRCA | unverified_public_metadata | yes — **GDC account recommended** for bulk download tooling; dbGaP only if controlled files needed (optional for Level-3 open) |
| AURORA US Metastatic Breast Multiomics | GEO + dbGaP (+ TCIA imaging) | GSE209998 / GSE212375; dbGaP phs002622 | open (processed GEO subsets); controlled (dbGaP raw/full) | Publication consortia DUAs for controlled; GEO processed often open | RNA-seq, WES/WGS, DNA methylation, clinical | ~55 patients (retrospective phase) | ~51 primaries + ~102 metastases | ≥2 tissue timepoints (primary + metastasis; some multi-met) | **Alternate** for true paired molecular timepoints (primary↔met). Prefer when Plan 02 needs genuine molecular repeats that TCGA lacks. Counts TBD — verify on GEO/dbGaP. | alternate (longitudinal molecular) | unlocked_alternate | https://www.cancerimagingarchive.net/collection/aurora-metastatic-breast-multiomics/ | unverified_public_metadata | yes — **dbGaP** for full multi-omic; NCBI/GEO optional for open matrices |
| AURORA BIG (EU) | Program / controlled repositories | BIG AURORA MBC (see Cancer Discovery 2022) | controlled / account+DUA | Consortia access; not a single open GEO dump | targeted DNA, RNA-seq subsets, clinical | ~381 profiled; paired RNA-seq ~152 | TBD — verify on program portal | primary + early metastasis pairs | Large paired primary–met resource; access path TBD. | exploratory | unlocked_exploratory | https://pubmed.ncbi.nlm.nih.gov/35850122/ | needs_dua | yes — program/DAC credentials (TBD) |
| I-SPY2 transcriptomic (+ serial MRI) | GEO + TCIA | GSE194040 (mRNA); TCIA ISPY2 | open (GEO expression; TCIA imaging CC-BY) | Trial data; check GEO/TCIA terms | gene expression (often pre-treatment); serial MRI | ~987 with pretreatment expression | ~987 expression; MRI multi-visit subset larger | imaging: multiple NAC visits; **molecular often single pre-treatment** | Strong imaging Δt; weak molecular repeats in public release. | exploratory | unlocked_exploratory | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE194040 | unverified_public_metadata | no for GEO matrices; TCIA optional |

### Alzheimer's Disease

| cohort_name | source_portal | accession_or_id | access_method | license_ethics_notes | modalities | n_subjects_approx | n_samples_approx | timepoints_or_visits | longitudinal_notes | recommended_priority | selection_status | url | verification_status | needs_account_or_api_key |
|-------------|---------------|-----------------|---------------|----------------------|------------|-------------------|------------------|----------------------|--------------------|----------------------|------------------|-----|---------------------|--------------------------|
| ADNI (blood EPIC methylation + genomics/clinical) | LONI IDA | ADNI (methylation studies ~n=650 subjects in published analyses) | controlled / account+DUA | ADNI Data Use Agreement required; IRB-aware use | DNA methylation (EPIC), GWAS, clinical/cognitive, imaging, CSF biomarkers | ~650 with methylation in published EWAS; ADNI overall larger | ~1,700+ methylation samples after QC in papers | baseline + follow-ups ~1y apart, up to ~4y | **Best AD fit for molecular Δt.** Multi-omic via methylation + genotype + clinical (± imaging). | primary (recommended) | recommended_unlocked | https://adni.loni.usc.edu/data-samples/adni-data/ | needs_dua | yes — **ADNI/LONI account + DUA required** |
| ROSMAP (AMP-AD) | Synapse AD Knowledge Portal | syn3219045 (study); metadata syn3157322 | controlled / account+DUA | Synapse + Data Use Certificate (DUC) | genotypes, WGS, methylation, RNA-seq, ChIP-seq, proteomics (generation ongoing), rich clinical | ROS+MAP >3,000 enrolled; omic subsets hundreds–thousands | RNA-seq ~638; methylation ~740 (first-gen atlas; growing) | **Clinical** longitudinal; **brain omics usually one postmortem sample** | Excellent multi-omic AD/aging biology; limited repeated *molecular* timepoints on same tissue. Use for phenotype severity later. | alternate | unlocked_alternate | https://adknowledgeportal.synapse.org/Explore/Studies/DetailsPage?Study=syn3219045 | needs_dua | yes — **Synapse account + ADKP DUC required** |
| Progressive MCI / AD blood RNA-seq | GEO | GSE282742 | open | GEO open; raw not provided | RNA-seq (WBC) | P-MCI ~28, S-MCI ~39, AD ~49 (+ serial draws) | ~100+ samples (serial subject IDs present) | ≥2 draws for many converters (ages differ across GSM rows) | Longitudinal *clinical progression* with repeated blood RNA. **Single-omic** → exploratory only under multi-omic preference. | exploratory | unlocked_exploratory | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE282742 | unverified_public_metadata | no (optional NCBI login) |
| AddNeuroMed / related blood methylation | GEO | GSE153712 (and related) | open | GEO open | methylation (EPIC) | TBD — verify on GEO | TBD — verify on GEO | often case/control; confirm visit labels on portal | Useful open methylation; confirm longitudinal vs cross-sectional before ETL. Single-omic. | exploratory | unlocked_exploratory | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE153712 | unverified_public_metadata | no (optional NCBI login) |

### Rheumatoid Arthritis

| cohort_name | source_portal | accession_or_id | access_method | license_ethics_notes | modalities | n_subjects_approx | n_samples_approx | timepoints_or_visits | longitudinal_notes | recommended_priority | selection_status | url | verification_status | needs_account_or_api_key |
|-------------|---------------|-----------------|---------------|----------------------|------------|-------------------|------------------|----------------------|--------------------|----------------------|------------------|-----|---------------------|--------------------------|
| Anti-TNF response multi-omics (Utrecht / CERTAIN-linked) | GEO | GSE138747 (SuperSeries); GSE138746 RNA; GSE138653 methylation | open | GEO open | RNA-seq + DNA methylation (+ related proteomics in paper) | ~40 biologic-naïve RA per described cohort arm (verify) | ~2× subjects (baseline + 3 mo) — TBD exact on GEO | baseline + ~3 months anti-TNF | **Open multi-omic + clear Δt.** Recommended RA primary under current constraints. | primary (recommended) | recommended_unlocked | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE138747 | unverified_public_metadata | no (optional NCBI login / E-utils key) |
| TNFi response longitudinal methylation (IMIDC Spain) | GEO | GSE176168 | open | GEO open | DNA methylation (EPIC) | discovery ~62 + validation ~60 | ~2× (baseline + wk12) | baseline + week 12 | Clear longitudinal methylation. **Single-omic** → alternate. | alternate | unlocked_alternate | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE176168 | unverified_public_metadata | no |
| Anti-TNF whole-blood RNA-seq | GEO | GSE129705 | open | GEO open; **raw withheld** (consent) | RNA-seq | TBD — verify on GEO | baseline + 3 mo pairs | baseline + 3 months | Processed counts available; raw blocked. Single-omic. | exploratory | unlocked_exploratory | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE129705 | unverified_public_metadata | no |

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
| Lothian Birth Cohort 1936 (LBC1936) | EGA + University of Edinburgh data access | EGAS00001000910; cohort request | controlled / account+DUA | Not fully public; DAC / Edinburgh collaboration terms | blood DNA methylation (450K) multi-wave; genetics available via cohort; rich phenotypes | Wave1 methyl ~920 QC'd historically; later waves hundreds | multi-wave samples (W1–W4 methyl subsets) | waves ~age 70, 73, 76, 79 (+) | **Recommended Epigenetic Aging primary** under multi-omic preference (methylation Δt + genetics/phenotypes). | primary (recommended) | recommended_unlocked | https://www.ed.ac.uk/lothian-birth-cohorts/data-access | needs_dua | yes — **Edinburgh request / EGA DAC**; no public API key |
| SATSA longitudinal methylation | ArrayExpress / BioStudies | E-MTAB-7309 | open | ArrayExpress open deposition | DNA methylation (450K) | ~385 twins after QC | ~1,011 samples across up to 5 waves | up to 5 waves (1992–2012); ~200 with ≥3 measures | Excellent open longitudinal methylation for clocks. **Single-omic** → alternate (upgrade if genotypes joined via Twin Registry). | alternate | unlocked_alternate | https://www.ebi.ac.uk/biostudies/arrayexpress/studies/E-MTAB-7309 | unverified_public_metadata | no |
| Normative Aging Study (NAS) methylation | dbGaP | phs000853 | controlled / account+DUA | dbGaP authorized-access | longitudinal blood methylation (+ study phenotypes) | TBD — verify on dbGaP | TBD — verify on dbGaP | repeated exams (multi-year) | Controlled longitudinal aging methylome; confirm multi-omic joins on dbGaP. | alternate | unlocked_alternate | https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs000853 | needs_login | yes — **dbGaP + eRA commons / institutional PI** |
| Framingham Heart Study methylation (Offspring etc.) | dbGaP | phs000974 (and related) | controlled / account+DUA | dbGaP; Framingham terms | methylation + genotypes + clinical longitudinal | TBD — verify on dbGaP | TBD — verify on dbGaP | exam cycles (multi-year) | Strong controlled multi-omic aging resource; heavier DUA. | exploratory | unlocked_exploratory | https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs000974 | needs_login | yes — **dbGaP** |
| Cross-sectional aging methylomes (clock training sets) | GEO | e.g. GSE40279, GSE87571 | open | GEO open | DNA methylation | hundreds each | hundreds–~700+ | typically **1 timepoint** (age span cross-sectional) | Useful for clock baselines / transfer learning; **do not** satisfy ≥2 timepoints alone. | exploratory | unlocked_exploratory | https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE40279 | unverified_public_metadata | no |

---

## Accounts, DUAs, and API keys (user has none yet)

Drafting this inventory **does not** require any credentials. With **BRCA primary locked to TCGA-BRCA (open Level-3)**, create accounts in this order:

| Priority | Account / agreement | Needed for | Needed vs optional |
|----------|---------------------|------------|--------------------|
| **1 (now)** | **GDC Portal account** (+ download token) | TCGA-BRCA open Level-3 bulk / API-friendly download | **Recommended first** — open data; no dbGaP required for Level-3 PoC |
| 2 | **ADNI / LONI IDA + DUA** | ADNI primary (if locked) | **Required** only after AD primary lock |
| 3 | **KORA.PASST + project agreement** | KORA F4/FF4 (if locked) | **Required** only after T2D primary lock |
| 4 | **Lothian Birth Cohorts / EGA DAC** | LBC1936 (if locked) | **Required** only after Epigenetic Aging primary lock |
| 5 | **Synapse + AD Knowledge Portal DUC** | ROSMAP (AD alternate) | **Required** only if ROSMAP chosen |
| 6 | **dbGaP authorized access** (eRA / institutional PI) | AURORA US full multi-omic; NAS/FHS aging; TCGA controlled BAMs | **Not needed** for TCGA Level-3 open; required later if AURORA controlled or TCGA BAM/raw |
| 7 | **NCBI account** | GEO / SRA convenience (RA GSE138747, open T2D/aging) | **Optional** for open GEO series |
| 8 | **NCBI E-utils API key** | Higher GEO/SRA query rate limits | **Optional** |

**TCGA-BRCA access split:** Open Level-3 (clinical + processed molecular) is the locked PoC path and does **not** need dbGaP. Controlled BAM/raw (phs000178) stays optional/out of scope until explicitly requested.

---

## Next concrete Plan 01 steps (BRCA locked)

1. **Create GDC account** and generate a download token (first account; enables TCGA-BRCA Level-3 bulk pulls per [`Data-Acquisition-BRCA.md`](../wiki/Data-Acquisition-BRCA.md)).
2. **Spot-verify TCGA-BRCA** on the GDC portal: case counts, available Level-3 modalities, and how many cases have >1 molecular aliquot / metastatic TM (document in verification_status).
3. **Lock or reject remaining primaries** (user decisions) — clarifying questions below.
4. After each lock, start only the matching account/DUA from the table above (do not apply for everything at once).
5. For open GEO primaries (likely RA): pull series metadata + confirm baseline/3-mo pairing counts without credentials.
6. Keep AURORA US in inventory as BRCA longitudinal alternate; defer dbGaP until Plan 02 needs true molecular repeats.
7. Resolve `down_syndrome` → Epigenetic Aging registry naming in a later PR after the fifth primary is locked (no invented severity maps).

### Clarifying questions (to lock Other-4)

1. **Alzheimer's:** Lock **ADNI** as primary, or prefer open GEO (e.g. GSE282742) first to avoid DUA delay?
2. **RA:** Lock **GSE138747** (open multi-omic), or keep shopping for a larger controlled cohort?
3. **T2D:** Lock **KORA F4/FF4** (best multi-omic Δt, controlled), or start with open **GSE184050** RNA-only for faster ETL rehearsal?
4. **Epigenetic Aging:** Lock **LBC1936** (controlled), or open **SATSA (E-MTAB-7309)** first?
5. **Registry naming:** When the fifth primary is locked, rename `down_syndrome` → `epigenetic_aging` (or keep key + alias)?

---

## Notes

1. **Multi-omic preference:** Primaries prioritized for ≥2 modalities (or methylation + genotype + rich clinical for AD/aging). Pure RNA or pure methylation series are alternate/exploratory.
2. **BRCA longitudinal gap:** TCGA-BRCA is the **locked** Year-1/2 multi-omic anchor, but a poor natural longitudinal molecular cohort. Use AURORA (or similar paired primary–met) when Plan 02 matching needs genuine molecular repeats.
3. **`down_syndrome` vs Epigenetic Aging:** Registry placeholder key is `down_syndrome`; this inventory covers **Epigenetic Aging** per Plan 01 / README. Severity maps intentionally untouched.
4. **Verification:** Rows marked `unverified_public_metadata` should be spot-checked on the portal after account creation; replace TBD counts before ETL freeze (Plan 02+).
5. **Out of scope here:** visit-pairing rules (Plan 02), feature axes / HDF5 (Plans 03–07), Other-4 full ETL (Year 3 gate).
