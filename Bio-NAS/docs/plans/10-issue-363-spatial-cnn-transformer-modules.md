# Plan 10: Develop 1D-CNNs for local clusters of CpG sites and Spatial Transformers for long-range dependencies.

## Issue reference

| Field | Value |
|-------|-------|
| Number | [363](https://github.com/AdamCankaya/PhDNeural/issues/363) |
| Title | [Y2 Q3 Fall 2027] Develop 1D-CNNs for local clusters of CpG sites and Spatial Transformers for long-range dependencies. |
| URL | https://github.com/AdamCankaya/PhDNeural/issues/363 |
| Labels | `phd-sync, year-2, phase-3, scaling, step-1, q3-2027` |
| Year / Quarter | 2 - Spatio-Temporal NAS Execution & Multi-Task Forecasting / Q3 Fall 2027 - Engineering the Spatio-Temporal Search Space |
| Phase | 3 - Scaling to the Comparative Matrix |
| Master-plan goal | Code modular spatial PyTorch blocks for the NAS search space. |

## Goals / requirements checklist

Maps 1:1 to the issue **Implementation requirements**, plus Track B adjacency ownership (this plan is the earliest consumer; see [`ROADMAP.md`](ROADMAP.md) non-duplication rule):

- [ ] **Deliverables:** reusable `nn.Module`s with configurable depth/width; registered in Optuna search space.
- [ ] **Deliverables (Track B):** versioned frozen binary adjacency artifact + `MaskedLinear` (or equivalent) that applies it; load adapters for KEGG/Reactome blueprints.
- [ ] **Acceptance:** forward-pass tests on synthetic `(B,T,S,C)` batches; parameter counts logged.
- [ ] **Acceptance (Track B):** masked forward pass zeros disallowed synapses; frozen mask hash/version recorded in config.
- [ ] **Upstream deps satisfied:** genomic spacing config; Year 1 tensors.


## Approach

Build reusable spatial `nn.Module`s: 1D-CNN for local CpG clusters and Spatial Transformers for
long-range dependencies. Track A = unconstrained; Track B adds pathway-masked / adjacency-constrained
variants (`MaskedLinear`) using KEGG/Reactome matrices. Register searchable depth/width hyperparameters
for Optuna. Forward-pass tests on synthetic `(B,T,S,C)` batches; log parameter counts. Place under
`src/models/spatial/`. Depend on spacing config from plan 04.

**Ownership:** this plan **builds and freezes** the Track B adjacency pipeline. Plan 12 **consumes** the
frozen mask in dual-track Optuna search and does not re-derive graph construction.

### Track B adjacency pipeline (build & freeze)

Terminology matches [`docs/wiki/Glossary.md`](../wiki/Glossary.md): Track B constraints via binary
**adjacency matrix** applied in **`MaskedLinear`**; blueprints from **KEGG** / **Reactome**.

#### 1. Biological blueprint sources

| Source | Role | Notes |
|--------|------|-------|
| **KEGG** | Pathway graphs / gene membership | Primary blueprint API or dump; pin release/date in freeze config |
| **Reactome** | Curated pathway networks | Secondary (or joint) source; pin release/date |

Load adapters may stub remote APIs behind local cached pathway tables under `data/` or `artifacts/` until
final dumps are pinned.

#### 2. Build gene–gene graph

Construct an undirected (default) gene–gene graph \(G=(V,E)\) over HGNC / Ensembl gene IDs present in the
BRCA feature map (plan 03).

| Edge rule | Definition | When to use |
|-----------|------------|-------------|
| **Pathway edges (default)** | Edge \((u,v)\) if KEGG/Reactome records a directed or undirected interaction between \(u\) and \(v\) within a selected pathway set | Prefer when interaction edges are available; denser biological specificity |
| **Co-membership (alternative)** | Edge \((u,v)\) if \(u\) and \(v\) share at least one selected pathway | Simpler fallback when only membership tables exist; typically denser |
| **Union** | Pathway edges ∪ co-membership | Optional sensitivity run; document if used |

**Default for BRCA vertical slice:** pathway edges from the union of pinned KEGG + Reactome releases;
fall back to co-membership if interaction edges are missing for a source. Record the chosen rule and
pathway ID allow-list in the freeze config.

#### 3. Map model features → genes

Feature indices in the spatial axis \(S\) must map to gene vertices before adjacency is placed over
model dimensions:

| Modality | Mapping rule |
|----------|--------------|
| **RNA / gene expression** | Feature ID → gene ID (identity or symbol→Ensembl lookup) |
| **CpG methylation** | CpG → gene via annotation (e.g. promoter/TSS window or Illumina manifest gene field); document many-to-one / unmapped handling |
| **Mutations / CNV** | Variant or segment → locus → overlapping gene(s); document multi-gene collapse (OR into gene node) |

Unmapped features: **no off-diagonal edges** to other features (self-loop optional for bias/residual path —
default: allow self-connection so diagonal of \(A\) is 1). Log unmapped count in freeze metadata.

#### 4. Construct binary adjacency matrix \(A\)

1. Order features by the locked spatial index from tensors / feature map (plans 03, 07).
2. For each feature pair \((i,j)\), set \(A_{ij}=1\) iff their mapped gene(s) are adjacent in \(G\)
   (or \(i=j\) for self-loops).
3. Store \(A\) as a binary matrix aligned to feature indices (sparse format acceptable on disk;
   dense boolean ok for BRCA-scale prototypes).
4. Sanity checks: shape `(S,S)` or `(F,F)` matching searchable linear fan-in/fan-out; sparsity %;
   connected-component summary.

#### 5. `MaskedLinear` (or equivalent) application

Implement a linear (or projection) layer whose weight \(W\) is element-wise masked:

\[
y = (W \odot A)\,x + b
\]

(or the transpose convention required by fan-in layout — document once in code + this plan). Track A
modules omit the mask. Track B spatial blocks that expose fully connected projections use
`MaskedLinear` with the **frozen** \(A\) loaded at module init (not re-sampled per trial).

#### 6. Freeze procedure (versioned artifact)

Produce an immutable adjacency package before any Track B Optuna study (plan 12):

| Item | Suggested location / content |
|------|------------------------------|
| Matrix artifact | e.g. `artifacts/adjacency/brca_track_b_A_v{VERSION}.npz` (or `.pt` / `.parquet` sparse COO) |
| Sidecar metadata | same stem + `.json` / `.yaml`: source releases, pathway allow-list, edge rule, feature→gene map path, seed, git commit, content hash (SHA-256 of matrix bytes) |
| Builder config | e.g. `src/config/adjacency_track_b.yaml` recording sources, mapping rules, self-loop policy |
| Seed | deterministic shuffle/tie-break seed if any sampling used during graph build (default: no sampling) |

**Freeze means:** plan 12 and later plans reference `VERSION` + hash only; rebuilding requires a new
version string. Do not silently overwrite `v1` after Track B search starts.

#### Deliverables / acceptance (adjacency pipeline)

- [ ] Builder script/module documented under Key files; runnable for BRCA feature index.
- [ ] Frozen artifact + metadata written under `artifacts/adjacency/` (or `data/adjacency/` if preferred — pick one and keep consistent).
- [ ] SHA-256 (or equivalent) of \(A\) recorded; reload round-trip test passes.
- [ ] `MaskedLinear` unit test: disallowed positions remain zero after backward (or are non-trainable / re-masked each forward).
- [ ] Unmapped-feature policy documented; counts logged.
- [ ] Plan 12 can cite `adjacency_version` + hash in Optuna study user attrs.

## Key files / areas to touch

- `src/models/spatial/` (new packages — CNN / Spatial Transformer)
- `src/models/spatial/masked_linear.py` (or `src/models/layers/masked_linear.py`)
- `src/pipelines/adjacency/` or `src/data/adjacency/` (graph build, feature→gene map, freeze writer)
- `src/config/adjacency_track_b.yaml` (sources, edge rule, pathway allow-list, paths)
- `src/config/genomic_spacing.yaml`
- `artifacts/adjacency/` (versioned \(A\) + metadata; git-lfs or local-only large binaries as appropriate)
- `src/models/static_mtl_model.py` (head attachment patterns)
- `tests/` forward-pass tests; mask sparsity / freeze round-trip tests (new)

## Dependencies on other plans

- `03-issue-356-spatial-temporal-feature-map.md` (#356) — feature IDs for gene mapping
- `04-issue-357-genomic-structural-spacing.md` (#357)
- `07-issue-360-four-d-tensor-hdf5.md` (#360)
- `08-issue-361-compute-stack-provisioning.md` (#361)

## Out of scope / owned by other plans

- Genomic spacing config → plan 04 (#357)
- Temporal modules → plan 11 (#364); may *consume* pathway-selected features but does not own adjacency freeze
- **Optuna dual-track search under the frozen mask** → plan 12 (#365)
- Holdout Track A vs B metrics → plan 14 (#367)
- Attribution vs pathway priors → plan 17–18 (#370–#371)

## Acceptance criteria

Satisfied when the issue acceptance text is met:

> forward-pass tests on synthetic `(B,T,S,C)` batches; parameter counts logged.

Plus Track B adjacency:

> frozen adjacency artifact version + hash exist; `MaskedLinear` respects \(A\); builder config records KEGG/Reactome releases, edge rule, and feature→gene mapping rules.

Plus: linked PR(s) reference this plan path and issue #363; experiments (if any) record IDs per `docs/wiki/Experiment-Log-Template.md`.

## Rough sequencing notes

Start of Year 2 search space; needs tensors + spacing + torch env. Build Track A spatial modules and the
adjacency freeze in parallel where possible; **freeze \(A\) before** any Track B study in plan 12.

Recommended roadmap position: **10 / 24** (see [`ROADMAP.md`](ROADMAP.md)).

## Dual-track / cohort notes

Follow Track scope and cohort focus declared for this quarter in [`phd_bio-nas_master_plan.md`](../../phd_bio-nas_master_plan.md). BRCA remains the vertical-slice anchor through Year 2; Other 4 work after the Year 2 Summer scaling gate unless this plan explicitly inventories or templates them.

- **Track A:** spatial CNN / Transformer blocks without pathway masks.
- **Track B:** same block families with `MaskedLinear` (or equivalent) wired to the **frozen** BRCA adjacency from this plan.
- Glossary: [Track A](../wiki/Glossary.md), [Track B](../wiki/Glossary.md), [MaskedLinear](../wiki/Glossary.md), [Adjacency matrix](../wiki/Glossary.md).
