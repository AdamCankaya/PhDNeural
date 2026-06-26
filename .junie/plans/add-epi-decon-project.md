---
sessionId: session-260624-203957-16le
---

# Requirements

### Overview & Goals
Create a new PhD research project entitled "Epigenetic Deconvolution SaaS ($\beta$-VAE)" within a new folder `epi-decon` and integrate it into the existing multi-project repository. The project will follow a 3-year execution roadmap as outlined in the provided documentation.

### Scope
In Scope:
- Create `epi-decon/` project folder and structure.
- Create project-specific documentation (`phd_epi-decon_master_plan.md`, `README.md`, `epi-decon_github_sync.config.json.example`).
- Update repository root `index.html` and `README.md` to reference the new project.
- Use `scripts/sync_phd_to_github.py` to create GitHub issues based on the roadmap.
- Publish the roadmap as a GitHub Page.
- Commit all changes and push to the existing PR.

Out of Scope:
- Implementation of actual machine learning model or data pipeline code.

# Technical Design

### Current Implementation
The repository uses a multi-project structure with projects in dedicated subfolders (e.g., `Bio-NAS/`). The root `index.html` and `README.md` manage the portfolio. Existing GitHub workflows synchronize projects with issues and pages.

### Proposed Changes
- Create `epi-decon/` folder structure mimicking `Bio-NAS/`.
- Populate `epi-decon/` with `phd_epi-decon_master_plan.md` (roadmap), `README.md`, and `epi-decon_github_sync.config.json.example`.
- Modify root `index.html` to add `epi-decon` with a summary, objectives, and planned outputs, matching the `Bio-NAS` card style.
- Modify root `README.md` to list `epi-decon`.
- Execute `sync_phd_to_github.py` to create issues from the new master plan.

### File Structure
- `epi-decon/`
    - `phd_epi-decon_master_plan.md`
    - `README.md`
    - `epi-decon_github_sync.config.json.example`
- `index.html` (updated)
- `README.md` (updated)

# Roadmap (Epigenetic Deconvolution SaaS ($\beta$-VAE))

- **Year 1:** Anchor Model & Infrastructure (Data pipelines, Pseudobulk engine, Optuna NAS, Clinical validation).
- **Year 2:** Multi-Tissue Generalization & Academic Defense (Generalization, Parallel studies, Comparative analysis, Ph.D. defense).
- **Year 3:** SaaS Transformation & Commercial Handoff (API routing, Security, Clinical Beta, Commercial launch).

# Testing

### Validation Approach
- Verify the `epi-decon/` directory exists with all expected files.
- Verify the root `index.html` and `README.md` correctly link to `epi-decon` and display the summary accurately.
- Verify GitHub issues are created for the roadmap tasks via repository sync.
- Ensure all changes are committed and pushed.