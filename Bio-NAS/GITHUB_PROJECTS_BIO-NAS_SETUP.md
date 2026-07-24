# GitHub Projects Setup

> **This guide has moved to the project wiki.**

For the full GitHub Projects v2 setup, sync workflow, quarter roadmap tracking, and troubleshooting:

- **Wiki (published):** [Workflow](https://github.com/AdamCankaya/PhDNeural/wiki/Workflow)
- **Repo source (edit here):** [`docs/wiki/Workflow.md`](docs/wiki/Workflow.md)

Related wiki pages:

- [Roadmap and Tracking](https://github.com/AdamCankaya/PhDNeural/wiki/Roadmap-and-Tracking) — **24-task** quarter calendar, issue format, labels
- [FAQ and Troubleshooting](https://github.com/AdamCankaya/PhDNeural/wiki/FAQ-and-Troubleshooting)

Quick start:

```powershell
Copy-Item bio-nas_github_sync.config.json.example bio-nas_github_sync.config.json
gh auth login
python -m unittest discover -s tests -v
python scripts/sync_phd_to_github.py --parse-only   # expect 24 tasks
python scripts/sync_phd_to_github.py --update-existing --close-stale --prune-project
python scripts/embed_dashboard_plan.py              # dashboard + master_plan.html
```

Live surfaces:

- [Timeline dashboard](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html)
- [Master plan HTML](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html)
- [Pages landing](https://adamcankaya.github.io/PhDNeural/Bio-NAS/)

Project board: [PhD Master Plan (Project #2)](https://github.com/AdamCankaya/PhDNeural/projects/2)
