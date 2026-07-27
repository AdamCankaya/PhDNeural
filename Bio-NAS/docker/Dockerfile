# Bio-NAS Plan-1 image: open GDC download + inventory verify + optional toy NAS.
# Data is downloaded at container start into /data/tcga (not during build).
# Open-access GDC only — no login / token required (token not needed for Plan 1/2).
# Chain: ~5–10 joint meth+RNA+clinical cases → inventory_verification/ → meth-only toy NAS.
FROM python:3.12-slim

LABEL org.opencontainers.image.title="Bio-NAS TCGA-BRCA Plan-1"
LABEL org.opencontainers.image.description="Open GDC BRCA sample + inventory verify + meth-only toy NAS"

WORKDIR /app

COPY docker/requirements.txt /app/docker/requirements.txt
RUN pip install --no-cache-dir -r /app/docker/requirements.txt

COPY scripts/download_tcga_brca_sample.py /app/scripts/download_tcga_brca_sample.py
COPY scripts/train_nas_demo.py /app/scripts/train_nas_demo.py
COPY scripts/verify_cohort_inventory_open.py /app/scripts/verify_cohort_inventory_open.py
COPY scripts/docker_entrypoint.py /app/scripts/docker_entrypoint.py
COPY docs/data/smoke_expected.json /app/docs/data/smoke_expected.json

ENV PYTHONUNBUFFERED=1 \
    TCGA_SAMPLE_OUT=/data/tcga/BRCA \
    TCGA_SAMPLE_N_CASES=8 \
    TCGA_SAMPLE_MAX_BYTES=1572864000 \
    INVENTORY_VERIFY_OUT=/data/tcga/inventory_verification \
    SMOKE_EXPECTED_JSON=/app/docs/data/smoke_expected.json

# Internal data paths only — host bind-mount overlays at runtime.
RUN mkdir -p /data/tcga/BRCA /data/tcga/inventory_verification

ENTRYPOINT ["python", "/app/scripts/docker_entrypoint.py"]
