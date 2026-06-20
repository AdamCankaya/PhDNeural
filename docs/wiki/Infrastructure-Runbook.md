# Infrastructure Runbook

Operational guide for **Year 1 Fall Step 2**: distributed Optuna execution infrastructure.

Plan reference: [Y1 Fall 2026 — Infrastructure & Database Orchestration](https://github.com/AdamCankaya/PhDNeural/blob/main/phd_master_plan.md)

## Architecture overview

```mermaid
flowchart TB
  GH[GitHub Actions] -->|deploy workers| Slurm[University Slurm cluster]
  Workers[PyTorch Optuna workers] --> PG[(PostgreSQL on Hetzner)]
  PG --> Optuna[Optuna study storage]
  Repo[PhDNeural repo] --> GH
```

## Central hub — PostgreSQL (Hetzner)

| Item | Value |
|------|-------|
| Host | `[TBD]` — Hetzner Linux server |
| Port | `5432` (default) |
| Database | `[TBD]` — e.g. `optuna_phd` |
| Deployment | Dockerized PostgreSQL (persistent volume) |
| Purpose | Central Optuna study store for all NAS trials |

### Docker deployment checklist

- [ ] Provision Hetzner Linux VM
- [ ] Install Docker + docker-compose
- [ ] Deploy PostgreSQL with persistent volume mount
- [ ] Restrict firewall to Slurm subnet + admin IP
- [ ] Store credentials in local `.env` (see [`.env.example`](https://github.com/AdamCankaya/PhDNeural/blob/main/.env.example)) — **never commit secrets**

## CI/CD — GitHub Actions → Slurm

| Item | Value |
|------|-------|
| Workflow | `[TBD]` — worker deployment workflow |
| Runner | GitHub-hosted or self-hosted |
| Target cluster | `[TBD]` — university Slurm partition |
| Worker script | PyTorch training jobs reading HDF5 + logging to PostgreSQL |

### Slurm integration checklist

- [ ] Configure SSH or Slurm API credentials as GitHub Secrets
- [ ] Define partition/queue: `[TBD]`
- [ ] Test single-worker Optuna trial end-to-end
- [ ] Verify parallel workers share study namespace without collision

## Optuna connection string

Workers connect via environment variables (template in `.env.example`):

```
OPTUNA_STORAGE=postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

## Verification (Y1 Spring Stage 1)

After early fusion model exists, run a **small Optuna search** against the Hetzner PostgreSQL hub to confirm:

1. Workers can read HDF5 shards
2. Metrics log to the shared study
3. Parallel trials do not corrupt study state

## Monitoring

| Signal | Action |
|--------|--------|
| PostgreSQL disk usage | Alert at 80% volume |
| Failed Slurm jobs | Check GitHub Actions logs + Slurm `sacct` |
| Optuna trial failures | Query study trials table; link to [Experiment Log Template](Experiment-Log-Template) |

## Related pages

- [Workflow](Workflow) — CI sync workflow for plan updates
- [Data Acquisition BRCA](Data-Acquisition-BRCA) — HDF5 layout workers consume
- [FAQ and Troubleshooting](FAQ-and-Troubleshooting)
