# PhD Projects Repository

This repository contains the PhD research project.

## Projects

### [Bio-NAS](./Bio-NAS)
**Path:** `Bio-NAS/`

A Spatio-Temporal Bio-NAS framework investigating whether Biologically-Informed Neural Architecture Search (where neural pathways are constrained by known human anatomy, e.g., Gene Regulatory Networks) outperforms unconstrained, mathematical optimization in multi-omic disease prediction.

- **24 roadmap items** — each linked 1:1 to a GitHub issue (`label:phd-sync`) with implementation requirements
- Live [timeline dashboard](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_timeline_dashboard.html) and [master plan](https://adamcankaya.github.io/PhDNeural/Bio-NAS/phd_bio-nas_master_plan.html)
- Dual-track framing (standard NAS vs biologically constrained architectures) with a BRCA-first comparative matrix

For detailed documentation, tracking, and the codebase, see the [Bio-NAS README](./Bio-NAS/README.md) or the [Pages landing](https://adamcankaya.github.io/PhDNeural/Bio-NAS/).

## Running Bio-NAS (Docker)

Bio-NAS is **Docker-first**. On Windows:

1. Install and start [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/).
2. `cd Bio-NAS`
3. Build from [`Bio-NAS/docker/Dockerfile`](./Bio-NAS/docker/Dockerfile) and run:

```powershell
docker compose up --build
```

That loads the Dockerfile, builds `bio-nas-demo:local`, downloads a tiny open-access TCGA-BRCA sample on first run, and executes the smoke NAS demo. Full Windows steps: [Bio-NAS README § Deploy with Docker](./Bio-NAS/README.md#5-deploy-with-docker-windows) and [Bio-NAS/docker/README.md](./Bio-NAS/docker/README.md).
