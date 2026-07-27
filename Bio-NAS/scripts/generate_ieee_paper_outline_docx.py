"""Generate IEEE-style outline DOCX for BRCA TCGA NAS vs Bio-NAS paper."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


def set_run_font(run, name="Times New Roman", size=10, bold=False, italic=False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def style_paragraph(p, space_before=0, space_after=6, line_spacing=1.08, align=None):
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    if align is not None:
        p.alignment = align


def add_centered(doc, text, size=10, bold=False, italic=False, space_before=0, space_after=6):
    p = doc.add_paragraph()
    style_paragraph(
        p, space_before=space_before, space_after=space_after, align=WD_ALIGN_PARAGRAPH.CENTER
    )
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_body(doc, text, size=10, italic=False, space_before=0, space_after=6, indent=False):
    p = doc.add_paragraph()
    style_paragraph(p, space_before=space_before, space_after=space_after)
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.2)
    run = p.add_run(text)
    set_run_font(run, size=size, italic=italic)
    return p


def add_heading_ieee(doc, text, level=1):
    p = doc.add_paragraph()
    if level == 1:
        style_paragraph(p, space_before=12, space_after=6, align=WD_ALIGN_PARAGRAPH.CENTER)
        run = p.add_run(text.upper())
        set_run_font(run, size=10, bold=True)
    elif level == 2:
        style_paragraph(p, space_before=10, space_after=4)
        run = p.add_run(text)
        set_run_font(run, size=10, bold=True)
    elif level == 3:
        style_paragraph(p, space_before=8, space_after=3)
        run = p.add_run(text)
        set_run_font(run, size=10, bold=True, italic=True)
    else:
        style_paragraph(p, space_before=6, space_after=3)
        run = p.add_run(text)
        set_run_font(run, size=10, italic=True)
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.clear()
    style_paragraph(p, space_before=0, space_after=2)
    p.paragraph_format.left_indent = Inches(0.25 + 0.2 * level)
    run = p.add_run(text)
    set_run_font(run, size=10)
    return p


def add_note(doc, text):
    return add_body(doc, text, size=9, italic=True, space_after=8)


def build_document(out_path: Path) -> None:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(1.0)

    # Front matter
    add_centered(
        doc,
        "Comparative Neural Architecture Search versus Biologically-Informed NAS "
        "for Multi-Omic Breast Cancer Prediction on TCGA-BRCA",
        size=14,
        bold=True,
        space_after=10,
    )
    add_centered(doc, "[Author Name(s)]", size=11, space_after=2)
    add_centered(doc, "[Affiliation(s), Department, Institution]", size=10, italic=True, space_after=2)
    add_centered(doc, "[City, Country]  ·  [email@institution.edu]", size=9, space_after=8)
    add_centered(
        doc,
        "IEEE Manuscript Outline — Structure Only (Draft Scaffold)",
        size=9,
        italic=True,
        space_after=4,
    )
    add_note(
        doc,
        "Document status: outline for peer-reviewed CS / computational biology journal submission. "
        "Placeholder summary lines (italic) indicate intended content; replace with full prose, "
        "equations, tables, and figures prior to submission. Formatting approximates IEEE journal "
        "manuscript prep (Times New Roman; numbered sections).",
    )

    add_heading_ieee(doc, "Index Terms", level=2)
    add_body(
        doc,
        "Neural architecture search, biologically-informed deep learning, multi-omics, "
        "intermediate fusion, Optuna, TCGA-BRCA, breast invasive carcinoma, gene regulatory "
        "networks, pathway constraints, hyperparameter optimization.",
        space_after=10,
    )

    # Abstract
    add_heading_ieee(doc, "Abstract", level=1)
    add_note(
        doc,
        "[~150–250 words when written.] State the problem (unconstrained NAS vs biologically "
        "constrained search for multi-omic BRCA prediction), the dual-track design (Track A: "
        "standard NAS; Track B: Bio-NAS with KEGG/Reactome pathway constraints), the data "
        "(TCGA-BRCA methylation + RNA-seq via GDC), the method (Intermediate Fusion encoders, "
        "phased Optuna), key evaluation protocol (patient-level holdout, CV), and the intended "
        "contribution (whether biological priors improve accuracy, sparsity, and/or interpretability).",
    )
    add_body(
        doc,
        "Placeholder abstract: This paper presents a structured comparison of unconstrained "
        "Neural Architecture Search (NAS) and Biologically-Informed NAS (Bio-NAS) on The Cancer "
        "Genome Atlas Breast Invasive Carcinoma (TCGA-BRCA) cohort. … [complete after results.]",
        indent=True,
    )

    # I. Introduction
    add_heading_ieee(doc, "I. Introduction", level=1)
    add_note(
        doc,
        "Motivate multi-omic prediction in BRCA; limitations of hand-designed nets and early "
        "raw-concat fusion; introduce NAS and the Bio-NAS hypothesis; state contributions and "
        "paper organization.",
    )

    add_heading_ieee(doc, "A. Motivation and Clinical / Computational Context", level=2)
    add_bullet(doc, "Why BRCA is an appropriate anchor cohort for multi-omic NAS.")
    add_bullet(doc, "Curse of dimensionality and modality dominance under early fusion.")
    add_bullet(doc, "Need for reproducible, leakage-safe patient-level evaluation.")

    add_heading_ieee(doc, "B. Neural Architecture Search (NAS) in Biomedical ML", level=2)
    add_bullet(doc, "Brief survey of NAS for tabular / omic settings (citations TBD).")
    add_bullet(doc, "Role of hyperparameter and architecture search with Optuna / Hyperband.")

    add_heading_ieee(doc, "C. Biologically-Informed Learning and Pathway Priors", level=2)
    add_bullet(doc, "Gene regulatory / pathway graphs (KEGG, Reactome) as structural constraints.")
    add_bullet(
        doc,
        "Hypothesis: Track B (Bio-NAS) improves generalization and interpretability vs Track A.",
    )

    add_heading_ieee(doc, "D. Contributions", level=2)
    add_bullet(doc, "Formal dual-track A/B comparison protocol on TCGA-BRCA (shared data splits).")
    add_bullet(
        doc,
        "Intermediate Fusion multi-branch architecture search space "
        "(MethEncoder, RNAEncoder, FusionDecoder).",
    )
    add_bullet(
        doc,
        "Phased Optuna search (branch HPs → post-fusion dense) with distributed study storage.",
    )
    add_bullet(
        doc,
        "Empirical evaluation design: holdout metrics, sparsity/interpretability proxies, ablations.",
    )

    add_heading_ieee(doc, "E. Paper Organization", level=2)
    add_note(doc, "One short paragraph mapping Sections II–X.")

    # II. Related Work
    add_heading_ieee(doc, "II. Related Work", level=1)
    add_note(doc, "Position against prior multi-omic fusion, NAS, and biology-informed DL papers.")

    add_heading_ieee(doc, "A. Multi-Omic Integration and Fusion Strategies", level=2)
    add_bullet(doc, "Early, intermediate, and late fusion taxonomies.")
    add_bullet(doc, "Prior BRCA / TCGA multi-omic models (citations TBD).")

    add_heading_ieee(doc, "B. Neural Architecture Search for Healthcare and Genomics", level=2)
    add_bullet(doc, "AutoML/NAS applied to clinical and molecular data.")
    add_bullet(doc, "Search algorithms: Bayesian optimization, Hyperband, evolutionary NAS.")

    add_heading_ieee(doc, "C. Biologically Constrained Neural Networks", level=2)
    add_bullet(doc, "Pathway-masked layers, GRN-informed connectivity, sparse biological priors.")
    add_bullet(
        doc,
        "Gap: controlled A/B of unconstrained vs pathway-constrained NAS under identical fusion and data.",
    )

    # III. Background
    add_heading_ieee(doc, "III. Background: NAS versus Bio-NAS", level=1)
    add_note(
        doc,
        "Define terms precisely so reviewers can distinguish Track A (control) from Track B "
        "(innovation) without conflating fusion strategy with biological constraints.",
    )

    add_heading_ieee(doc, "A. Unconstrained Neural Architecture Search (Track A)", level=2)
    add_bullet(
        doc,
        "Search space over encoder widths/depths, activations, regularization, fusion head HPs.",
    )
    add_bullet(doc, "No pathway adjacency mask; connectivity learned freely within module families.")
    add_note(
        doc,
        "Summary: Track A optimizes predictive performance under Intermediate Fusion without "
        "biological graph constraints.",
    )

    add_heading_ieee(doc, "B. Biologically-Informed NAS (Track B / Bio-NAS)", level=2)
    add_bullet(
        doc,
        "Same fusion scaffold as Track A; additional KEGG/Reactome-derived adjacency / pathway masks.",
    )
    add_bullet(
        doc,
        "Constraints applied to spatial / branch modules (frozen mask construction; dual-track Optuna).",
    )
    add_note(
        doc,
        "Summary: Bio-NAS restricts or biases architecture choices using prior molecular network knowledge.",
    )

    add_heading_ieee(doc, "C. Comparative Framing and Fairness Criteria", level=2)
    add_bullet(
        doc,
        "Shared cohort, preprocessing, Intermediate Fusion topology family, CV folds, and compute budget.",
    )
    add_bullet(doc, "Differ only in biological constraint track (A vs B).")
    add_bullet(
        doc,
        "Primary and secondary endpoints (accuracy/AUROC/AUPRC; sparsity; attribution stability).",
    )

    # IV. Data
    add_heading_ieee(doc, "IV. Data Sources and Cohort Construction", level=1)

    add_heading_ieee(doc, "A. TCGA-BRCA and GDC Access", level=2)
    add_bullet(doc, "Project: TCGA Breast Invasive Carcinoma (TCGA-BRCA).")
    add_bullet(doc, "Access path: NCI GDC Portal / API; Level-3 open-access matrices preferred.")
    add_bullet(doc, "Controlled-access BAM/raw noted as out of scope unless required.")
    add_note(
        doc,
        "Summary: Describe download provenance, versioning, and open vs controlled data boundaries.",
    )

    add_heading_ieee(doc, "B. Multi-Omic Modalities", level=2)
    add_bullet(
        doc,
        "DNA methylation (beta values; mean-impute NaNs; no Z-score/log for meth branch).",
    )
    add_bullet(doc, "RNA-seq transcriptomics (log2(TPM+1) then Z-score for RNA branch).")
    add_bullet(
        doc,
        "Optional clinical covariates / phenotype and severity labels from disease registry.",
    )
    add_note(doc, "Summary: Specify feature spaces, units, and modality-specific scaling rules.")

    add_heading_ieee(doc, "C. Cohort Filtering, Matching, and Longitudinal Considerations", level=2)
    add_bullet(doc, "Case inclusion/exclusion; primary vs recurrent matching if used.")
    add_bullet(doc, "Irregular time steps and Δt embedding (if in scope for this paper).")
    add_note(
        doc,
        "Summary: State whether this manuscript is static multi-omic, longitudinal, or both.",
    )

    add_heading_ieee(doc, "D. Train / Validation / Holdout Splits", level=2)
    add_bullet(doc, "Patient-level 80/20 train–holdout; no patient leakage across folds.")
    add_bullet(doc, "Variance masks and scalers fit on training pool only.")
    add_bullet(doc, "5-fold CV within train pool for Optuna objectives.")
    add_note(doc, "Summary: Leakage-safe split protocol shared by Track A and Track B.")

    add_heading_ieee(doc, "E. Storage Layout and Reproducibility Artifacts", level=2)
    add_bullet(
        doc,
        "HDF5 / tensor serialization for Intermediate Fusion batches (meth_tensor, rna_tensor, labels).",
    )
    add_bullet(doc, "Manifests, demographics, experiment logs, Optuna study identifiers.")
    add_bullet(
        doc,
        "Containerized reproduction path (Docker Compose) for open-access sample workflows.",
    )

    # V. Methods
    add_heading_ieee(doc, "V. Methods", level=1)
    add_note(doc, "Core technical section: architecture families, fusion, search, training, evaluation.")

    add_heading_ieee(doc, "A. Problem Formulation", level=2)
    add_bullet(doc, "Input: multi-omic patient sample (x_meth, x_rna[, covariates]).")
    add_bullet(doc, "Output: phenotype / severity / survival or MTL heads (specify final task).")
    add_bullet(doc, "Objective: maximize validation metric under Track A or Track B constraints.")

    add_heading_ieee(doc, "B. Network Structure and Module Families", level=2)
    add_heading_ieee(doc, "1) Methylation Encoder (MethEncoder)", level=3)
    add_bullet(doc, "Candidate blocks: MLP / spatial CNN / transformer variants (as implemented).")
    add_bullet(doc, "Searchable HPs: depth, width, dropout, normalization, etc.")

    add_heading_ieee(doc, "2) RNA Encoder (RNAEncoder)", level=3)
    add_bullet(doc, "Parallel branch with modality-appropriate input scaling.")
    add_bullet(doc, "Searchable HPs analogous to methylation branch.")

    add_heading_ieee(doc, "3) Fusion Decoder (FusionDecoder)", level=3)
    add_bullet(doc, "Post-concatenation dense tower → task head(s).")
    add_bullet(doc, "MTL loss design if multi-task (cite losses module).")

    add_heading_ieee(doc, "4) Track B Pathway / Adjacency Constraints", level=3)
    add_bullet(doc, "Construction and freeze of biological masks from pathway databases.")
    add_bullet(doc, "How masks alter searchable connectivity vs Track A.")

    add_heading_ieee(doc, "C. Intermediate Fusion of Multi-Omic Data", level=2)
    add_bullet(doc, "Branch-specific encoding → latent concatenation → post-fusion dense.")
    add_bullet(
        doc,
        "Rationale vs early raw-concat (legacy baseline) and late stacked fusion (ADR path).",
    )
    add_bullet(doc, "Diagram placeholder: Fig. 1 — Intermediate Fusion NAS scaffold.")
    add_note(
        doc,
        "Summary: Intermediate Fusion is the default NAS architecture; early fusion retained only "
        "as a legacy software baseline, not as the primary search target.",
    )

    add_heading_ieee(doc, "D. Optuna-Based Architecture and Hyperparameter Search", level=2)
    add_heading_ieee(doc, "1) Search Space Definition", level=3)
    add_bullet(doc, "Categorical and continuous parameters for branches and decoder.")
    add_bullet(doc, "Track A vs Track B parameter differences (mask on/off or mask-related choices).")

    add_heading_ieee(doc, "2) Phased Search Protocol", level=3)
    add_bullet(doc, "Phase A: optimize branch HPs (encoders) independently / with frozen decoder policy.")
    add_bullet(doc, "Phase B: freeze selected branch configs; optimize post-fusion dense only.")
    add_note(
        doc,
        "Summary: Phasing reduces joint search dimensionality and modality interference.",
    )

    add_heading_ieee(doc, "3) Pruners, Samplers, and Distributed Storage", level=3)
    add_bullet(doc, "TPE / Hyperband (or configured sampler/pruner); PostgreSQL Optuna RDB storage.")
    add_bullet(doc, "Parallel workers (Slurm / Docker) and study naming conventions.")

    add_heading_ieee(doc, "4) Trial Objective and Early Stopping", level=3)
    add_bullet(doc, "CV metric (e.g., mean AUROC / loss); pruner feedback.")
    add_bullet(doc, "Compute budget: trials × epochs × folds (state planned budget).")

    add_heading_ieee(doc, "E. Training Procedure", level=2)
    add_bullet(doc, "Optimizer, learning-rate schedule, batch size, regularization.")
    add_bullet(doc, "Losses for classification / regression / Cox / MTL (as applicable).")
    add_bullet(doc, "Hardware and software stack (PyTorch, CUDA, container image pins).")

    add_heading_ieee(doc, "F. Baselines and Ablations", level=2)
    add_bullet(doc, "Legacy early-fusion model (raw concat) as non-NAS or fixed-architecture reference.")
    add_bullet(doc, "Classical ML baselines (e.g., ElasticNet / stacking late fusion) if in scope.")
    add_bullet(doc, "Ablations: spatial-only vs spatio-temporal; Track A vs B; fusion variants.")

    add_heading_ieee(doc, "G. Evaluation Protocol", level=2)
    add_bullet(doc, "Locked patient holdout; report point estimates + uncertainty.")
    add_bullet(doc, "Calibration, confusion matrices, survival metrics if applicable.")
    add_bullet(doc, "Interpretability: attribution / pathway enrichment for Track B.")
    add_bullet(doc, "Statistical comparison of Track A vs Track B (paired tests / bootstrap).")

    # VI. Experimental Setup
    add_heading_ieee(doc, "VI. Experimental Setup", level=1)
    add_note(
        doc,
        "Concrete settings reviewers need to reproduce: tables of HPs, budgets, seeds.",
    )

    add_heading_ieee(doc, "A. Implementation and Reproducibility", level=2)
    add_bullet(doc, "Code repository, container image, dependency pins.")
    add_bullet(doc, "Random seeds; deterministic flags where feasible.")

    add_heading_ieee(doc, "B. Compute Infrastructure", level=2)
    add_bullet(doc, "Worker nodes, GPUs, Optuna hub (PostgreSQL), job orchestration.")

    add_heading_ieee(doc, "C. Hyperparameter Ranges and Search Budgets", level=2)
    add_bullet(doc, "Table II (placeholder): search space ranges for Track A and Track B.")
    add_bullet(doc, "Table III (placeholder): trials, wall-clock, GPU-hours.")

    add_heading_ieee(doc, "D. Metrics and Reporting Conventions", level=2)
    add_bullet(doc, "Primary metric; secondary metrics; significance thresholds.")

    # VII. Results
    add_heading_ieee(doc, "VII. Results", level=1)
    add_note(doc, "[To be filled after experiments.] Structure reserved for peer-review completeness.")

    add_heading_ieee(doc, "A. Cohort and Feature Statistics", level=2)
    add_bullet(doc, "Table/figure: sample counts, modality coverage, class balance.")

    add_heading_ieee(doc, "B. Search Dynamics and Selected Architectures", level=2)
    add_bullet(doc, "Optuna optimization curves; best trial architectures for Tracks A and B.")
    add_bullet(doc, "Fig. 2 (placeholder): trial objective vs trial number.")

    add_heading_ieee(doc, "C. Predictive Performance: Track A (NAS) vs Track B (Bio-NAS)", level=2)
    add_bullet(doc, "CV and holdout tables; confidence intervals.")
    add_bullet(doc, "Head-to-head comparison under matched budgets.")

    add_heading_ieee(doc, "D. Ablation Studies", level=2)
    add_bullet(doc, "Fusion strategy ablations; module family ablations; constraint strength.")

    add_heading_ieee(doc, "E. Efficiency, Sparsity, and Resource Trade-offs", level=2)
    add_bullet(doc, "Parameters, FLOPs, training time, effective sparsity under Bio-NAS masks.")

    add_heading_ieee(doc, "F. Interpretability and Biological Plausibility", level=2)
    add_bullet(
        doc,
        "Pathway-level attributions; overlap with known BRCA biology (qualitative + quantitative).",
    )

    # VIII. Discussion
    add_heading_ieee(doc, "VIII. Discussion", level=1)

    add_heading_ieee(doc, "A. Interpretation of NAS vs Bio-NAS Findings", level=2)
    add_note(
        doc,
        "Discuss whether biological priors helped, hurt, or traded accuracy for interpretability.",
    )

    add_heading_ieee(doc, "B. Intermediate Fusion Design Choices", level=2)
    add_note(doc, "Reflect on modality imbalance, latent sizes, and phased Optuna effectiveness.")

    add_heading_ieee(doc, "C. Limitations", level=2)
    add_bullet(doc, "Cohort biases (TCGA clinical demographics); open-access Level-3 limits.")
    add_bullet(doc, "Incomplete pathway coverage; mask construction assumptions.")
    add_bullet(doc, "Search budget and stochasticity of NAS.")
    add_bullet(
        doc,
        "Generalization beyond BRCA not claimed in this manuscript (unless included).",
    )

    add_heading_ieee(doc, "D. Threats to Validity", level=2)
    add_bullet(doc, "Internal: leakage controls, multiple-testing, hyperparameter overfitting to CV.")
    add_bullet(doc, "External: other cancers / non-TCGA cohorts.")
    add_bullet(doc, "Construct: whether chosen metrics capture clinical utility.")

    add_heading_ieee(doc, "E. Implications for Practice and Future Multi-Disease Extension", level=2)
    add_note(
        doc,
        "Bridge to broader Bio-NAS thesis agenda (additional pathologies) without overclaiming.",
    )

    # IX. Conclusion
    add_heading_ieee(doc, "IX. Conclusion", level=1)
    add_note(
        doc,
        "Restate problem, dual-track method, main empirical takeaway (TBD), and contribution to "
        "CS/AutoML + computational oncology. Avoid introducing new results.",
    )
    add_body(
        doc,
        "Placeholder conclusion: We outlined and will report a controlled comparison of unconstrained "
        "NAS and Bio-NAS for Intermediate Fusion multi-omic learning on TCGA-BRCA. …",
        indent=True,
    )

    # X. Summary
    add_heading_ieee(doc, "X. Summary", level=1)
    add_note(
        doc,
        "Optional short executive wrap-up for readers skimming after the conclusion: 5–8 sentences "
        "recapping data, Intermediate Fusion, Optuna phasing, Track A vs B, and take-home message. "
        "If the target journal disallows a separate Summary, merge into Conclusion or Abstract.",
    )
    add_bullet(doc, "Data: TCGA-BRCA multi-omics (methylation + RNA) from GDC.")
    add_bullet(doc, "Method: Intermediate Fusion encoders + FusionDecoder; phased Optuna.")
    add_bullet(doc, "Comparison: Track A (NAS) vs Track B (Bio-NAS pathway constraints).")
    add_bullet(doc, "Evaluation: patient-level holdout + CV; performance and interpretability.")
    add_bullet(doc, "Take-home: [fill after results].")

    add_heading_ieee(doc, "Acknowledgment", level=1)
    add_note(doc, "Funding, compute sponsors, data acknowledgments (TCGA/GDC), and colleagues.")

    add_heading_ieee(doc, "References", level=1)
    add_note(
        doc,
        "IEEE numbered citation list. Seed topics: NAS surveys; Optuna; multi-omic fusion; "
        "TCGA-BRCA; KEGG/Reactome; Hyperband; related Bio-NAS / pathway-informed DL.",
    )
    add_body(doc, "[1]  …", space_after=2)
    add_body(doc, "[2]  …", space_after=2)
    add_body(doc, "[3]  …", space_after=8)

    add_heading_ieee(doc, "Appendix A — Extended Search Space Tables", level=1)
    add_note(doc, "Full Optuna parameter catalogs for Track A and Track B.")

    add_heading_ieee(doc, "Appendix B — Additional Cohort and Preprocessing Details", level=1)
    add_note(doc, "GDC query filters, QC plots, missingness handling.")

    add_heading_ieee(doc, "Appendix C — Supplementary Results", level=1)
    add_note(doc, "Per-fold metrics, failed trials, sensitivity analyses.")

    add_heading_ieee(doc, "Figure and Table Checklist (for manuscript completion)", level=1)
    add_bullet(doc, "Fig. 1: Intermediate Fusion architecture (Track A vs Track B overlay).")
    add_bullet(doc, "Fig. 2: Optuna search dynamics.")
    add_bullet(doc, "Fig. 3: Holdout performance comparison (NAS vs Bio-NAS).")
    add_bullet(doc, "Fig. 4: Ablation / sparsity / pathway attribution panel.")
    add_bullet(doc, "Table I: Cohort and modality statistics.")
    add_bullet(doc, "Table II: Search space summary.")
    add_bullet(doc, "Table III: Compute budget and selected hyperparameters.")
    add_bullet(doc, "Table IV: Main results (CV + holdout).")
    add_bullet(doc, "Table V: Ablations and baselines.")

    add_heading_ieee(doc, "Author Notes — Clarifying Questions for Outline Refinement", level=1)
    add_note(
        doc,
        "These questions are for the author (not for the journal). Resolve before drafting full prose.",
    )
    questions = [
        "Primary prediction task: subtype classification, severity/stage, survival (Cox), multi-task, or other?",
        "Scope of this paper: BRCA-only vertical slice, or include any non-BRCA cohorts?",
        "Temporal scope: static multi-omic only, or include longitudinal / Δt modules in this manuscript?",
        "Must early-fusion and late-stacking baselines appear as first-class comparisons, or appendix-only?",
        "Target venue (IEEE TCBB, JBHI, TNNLS, NeurIPS workshop, etc.) — affects Summary section and page limits?",
        "Author list, affiliations, and corresponding author?",
        "Working title preferences (shorter conference-style vs longer journal-style)?",
        "Which pathway databases are authoritative for Track B in this paper (KEGG, Reactome, both)?",
        "Will Docker/reproducibility be a Methods subsection or a short Availability statement only?",
        "Any results embargo or committee constraints on what may appear in a preprint?",
    ]
    for i, q in enumerate(questions, 1):
        add_body(doc, f"{i}. {q}", space_after=3)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)


def main() -> None:
    out_path = Path(__file__).resolve().parents[1] / "papers" / (
        "BRCA_TCGA_NAS_vs_Bio-NAS_IEEE_Outline.docx"
    )
    build_document(out_path)
    print(out_path)


if __name__ == "__main__":
    main()
