# GitHub Projects Setup

> **This guide has moved to the project wiki.**

For the full GitHub Projects v2 setup, sync workflow, quarter roadmap tracking, and troubleshooting:

- **Wiki (published):** [Workflow](https://github.com/AdamCankaya/PhDNeural/wiki/Workflow)
- **Repo source (edit here):** [`docs/wiki/Workflow.md`](docs/wiki/Workflow.md)

Related wiki pages:

- [Roadmap and Tracking](https://github.com/AdamCankaya/PhDNeural/wiki/Roadmap-and-Tracking) — 43-task quarter calendar, issue format, labels
- [FAQ and Troubleshooting](https://github.com/AdamCankaya/PhDNeural/wiki/FAQ-and-Troubleshooting)

Quick start:

```powershell
Copy-Item github_sync.config.json.example github_sync.config.json
gh auth login
python scripts/sync_phd_to_github.py --parse-only   # expect 43 tasks
python scripts/sync_phd_to_github.py
```

Project board: [PhD Master Plan (Project #2)](https://github.com/AdamCankaya/PhDNeural/projects/2)
