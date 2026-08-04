# Bio-NAS Plan-1 CPU image: public samples + independent toy NAS + dashboard.
# Data is downloaded at container start into /data/tcga (not during build).
# Open-access GDC only for BRCA — no login / token required.
# ADNI: credentials from host .env only — never baked into this image.
# Chain: BRCA smoke → inventory_verification/ → meth-only toy NAS →
#        ADNI scaffold → optional AD meth NAS when sample present.
FROM python:3.12-slim

LABEL org.opencontainers.image.title="Bio-NAS Plan-1"
LABEL org.opencontainers.image.description="CPU-only public multi-disease toy NAS with static dashboard"

WORKDIR /app

COPY docker/requirements.txt /app/docker/requirements.txt
RUN pip install --no-cache-dir -r /app/docker/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends bash curl && rm -rf /var/lib/apt/lists/*

COPY scripts/download_tcga_brca_sample.py /app/scripts/download_tcga_brca_sample.py
COPY scripts/train_nas_demo.py /app/scripts/train_nas_demo.py
COPY scripts/verify_cohort_inventory_open.py /app/scripts/verify_cohort_inventory_open.py
COPY scripts/download_adni_sample.py /app/scripts/download_adni_sample.py
COPY scripts/train_nas_ad_demo.py /app/scripts/train_nas_ad_demo.py
COPY scripts/download_geo_series_sample.py /app/scripts/download_geo_series_sample.py
COPY scripts/train_toy_nas_cpu.py /app/scripts/train_toy_nas_cpu.py
COPY scripts/build_dashboard.py /app/scripts/build_dashboard.py
COPY docker/entrypoint.sh /app/entrypoint.sh
COPY docs/data/smoke_expected.json /app/docs/data/smoke_expected.json

ENV PYTHONUNBUFFERED=1 \
    TCGA_SAMPLE_OUT=/data/tcga/BRCA \
    TCGA_SAMPLE_N_CASES=8 \
    TCGA_SAMPLE_MAX_BYTES=1572864000 \
    INVENTORY_VERIFY_OUT=/data/tcga/inventory_verification \
    SMOKE_EXPECTED_JSON=/app/docs/data/smoke_expected.json \
    ADNI_SAMPLE_OUT=/data/adni \
    RA_SAMPLE_OUT=/data/ra \
    T2D_SAMPLE_OUT=/data/t2d \
    EPIGENETIC_AGING_SAMPLE_OUT=/data/epigenetic_aging \
    SKIP_ALZHEIMERS=1 \
    SKIP_T2D=1 \
    TORCH_NUM_THREADS=2 \
    TOY_NAS_NUM_WORKERS=0

# Internal data paths only — host bind-mount overlays at runtime.
RUN mkdir -p /data/tcga/BRCA /data/adni /data/ra /data/t2d /data/epigenetic_aging && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
