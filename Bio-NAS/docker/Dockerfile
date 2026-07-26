# Bio-NAS smoke image: Python + first-run GDC download + toy NAS.
# Data is downloaded at container start into /data/tcga/BRCA (not during build).
# Open-access GDC only — no login / token required.
FROM python:3.12-slim

LABEL org.opencontainers.image.title="Bio-NAS TCGA-BRCA demo"
LABEL org.opencontainers.image.description="First-run open GDC BRCA sample + toy NAS"

WORKDIR /app

COPY docker/requirements.txt /app/docker/requirements.txt
RUN pip install --no-cache-dir -r /app/docker/requirements.txt

COPY scripts/download_tcga_brca_sample.py /app/scripts/download_tcga_brca_sample.py
COPY scripts/train_nas_demo.py /app/scripts/train_nas_demo.py
COPY scripts/docker_entrypoint.py /app/scripts/docker_entrypoint.py

ENV PYTHONUNBUFFERED=1 \
    TCGA_SAMPLE_OUT=/data/tcga/BRCA \
    TCGA_SAMPLE_N_CASES=8 \
    TCGA_SAMPLE_MAX_BYTES=83886080

# Internal data path only — no host volume required.
RUN mkdir -p /data/tcga/BRCA

ENTRYPOINT ["python", "/app/scripts/docker_entrypoint.py"]
