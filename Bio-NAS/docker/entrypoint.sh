#!/usr/bin/env bash
set -euo pipefail

truthy() { case "${1:-}" in 1|true|TRUE|yes|YES|on|ON) return 0;; *) return 1;; esac; }
run() { echo "--- $1 ---"; shift; "$@"; }

DATA_ROOT="${DATA_ROOT:-/data}"
BRCA_DIR="${TCGA_SAMPLE_OUT:-$DATA_ROOT/tcga/BRCA}"
RA_DIR="${RA_SAMPLE_OUT:-$DATA_ROOT/ra}"
AGING_DIR="${EPIGENETIC_AGING_SAMPLE_OUT:-$DATA_ROOT/epigenetic_aging}"
export TORCH_NUM_THREADS="${TORCH_NUM_THREADS:-2}"
export TOY_NAS_NUM_WORKERS="${TOY_NAS_NUM_WORKERS:-0}"

echo "=== Bio-NAS Plan-1 CPU toy pipeline ==="
run "BRCA public GDC sample" python /app/scripts/download_tcga_brca_sample.py --out-dir "$BRCA_DIR"
if ! truthy "${SKIP_BRCA_NAS:-0}"; then run "BRCA toy NAS" python /app/scripts/train_toy_nas_cpu.py --disease "BRCA" --data-dir "$BRCA_DIR" --brca; fi

if truthy "${SKIP_ALZHEIMERS:-1}"; then
  mkdir -p "$DATA_ROOT/adni"; : > "$DATA_ROOT/adni/.skipped"
  echo "--- Alzheimer's skipped: ADNI/LONI requires approved controlled access ---"
else
  echo "Refusing ADNI run: this image never downloads controlled-access data." >&2; exit 2
fi

run "RA public GEO sample (GSE71841)" python /app/scripts/download_geo_series_sample.py --accession GSE71841 --out-dir "$RA_DIR"
if ! truthy "${SKIP_RA_NAS:-0}"; then run "RA toy NAS" python /app/scripts/train_toy_nas_cpu.py --disease "Rheumatoid Arthritis" --data-dir "$RA_DIR"; fi

if truthy "${SKIP_T2D:-1}"; then
  mkdir -p "$DATA_ROOT/t2d"; : > "$DATA_ROOT/t2d/.skipped"
  echo "--- Type 2 Diabetes skipped: KORA F4/FF4 requires a project agreement ---"
else
  echo "Refusing KORA run: configure a separate, explicitly open proxy before enabling T2D." >&2; exit 2
fi

for accession in GSE40279 GSE87571 GSE280465; do
  run "Epigenetic Aging public GEO sample ($accession)" python /app/scripts/download_geo_series_sample.py --accession "$accession" --out-dir "$AGING_DIR" --max-samples 8
done
if ! truthy "${SKIP_EPIGENETIC_AGING_NAS:-0}"; then run "Epigenetic Aging toy NAS" python /app/scripts/train_toy_nas_cpu.py --disease "Epigenetic Aging" --data-dir "$AGING_DIR"; fi

export DATA_ROOT
export DASHBOARD_OUT="${DASHBOARD_OUT:-$DATA_ROOT/dashboard/dashboard.html}"
run "Static HTML results dashboard" python /app/scripts/build_dashboard.py

if truthy "${GITHUB_DISPATCH_ENABLED:-0}"; then
  : "${GITHUB_REPOSITORY:?Set GITHUB_REPOSITORY=owner/repo}"
  : "${GITHUB_TOKEN:?Set GITHUB_TOKEN with repository dispatch permission}"
  run "GitHub Repository Dispatch" curl --fail --silent --show-error --request POST --header "Accept: application/vnd.github+json" --header "Authorization: Bearer ${GITHUB_TOKEN}" --header "X-GitHub-Api-Version: 2022-11-28" "https://api.github.com/repos/${GITHUB_REPOSITORY}/dispatches" --data "{\"event_type\":\"${GITHUB_DISPATCH_EVENT:-bio_nas_toy_pipeline_complete}\",\"client_payload\":{\"dashboard\":\"data/dashboard.html\",\"status\":\"complete\"}}"
else
  echo "--- GitHub dispatch disabled (GITHUB_DISPATCH_ENABLED=0) ---"
fi
echo "=== Pipeline complete: $DATA_ROOT/dashboard.html ==="
