#!/usr/bin/env bash
# Pipeline steps may fail individually; the static dashboard is always built last.
set -uo pipefail

truthy() { case "${1:-}" in 1|true|TRUE|yes|YES|on|ON) return 0;; *) return 1;; esac; }

DATA_ROOT="${DATA_ROOT:-/data}"
BRCA_DIR="${TCGA_SAMPLE_OUT:-$DATA_ROOT/tcga/BRCA}"
RA_DIR="${RA_SAMPLE_OUT:-$DATA_ROOT/ra}"
AGING_DIR="${EPIGENETIC_AGING_SAMPLE_OUT:-$DATA_ROOT/epigenetic_aging}"
DASHBOARD_DIR="${DATA_ROOT}/dashboard"
STEP_LOG="${DASHBOARD_DIR}/pipeline_steps.log"
PIPELINE_FAILURES=0

export TORCH_NUM_THREADS="${TORCH_NUM_THREADS:-2}"
export TOY_NAS_NUM_WORKERS="${TOY_NAS_NUM_WORKERS:-0}"

mkdir -p "$DASHBOARD_DIR"
: > "$STEP_LOG"

run_step() {
  local title="$1"
  shift
  echo "--- $title ---"
  if "$@"; then
    printf '%s|%s\n' "$title" "0" >> "$STEP_LOG"
    return 0
  fi
  local rc=$?
  echo "WARNING: step failed (exit ${rc}): ${title}" >&2
  printf '%s|%s\n' "$title" "$rc" >> "$STEP_LOG"
  PIPELINE_FAILURES=$((PIPELINE_FAILURES + 1))
  return 0
}

echo "=== Bio-NAS Plan-1 CPU toy pipeline ==="
run_step "BRCA public GDC sample" python /app/scripts/download_tcga_brca_sample.py --out-dir "$BRCA_DIR"
if ! truthy "${SKIP_BRCA_NAS:-0}"; then
  run_step "BRCA toy NAS" python /app/scripts/train_toy_nas_cpu.py --disease "BRCA" --data-dir "$BRCA_DIR" --brca
fi

if truthy "${SKIP_ALZHEIMERS:-1}"; then
  mkdir -p "$DATA_ROOT/adni"
  : > "$DATA_ROOT/adni/.skipped"
  echo "--- Alzheimer's skipped: ADNI/LONI requires approved controlled access ---"
else
  echo "Refusing ADNI run: this image never downloads controlled-access data." >&2
  exit 2
fi

run_step "RA public GEO sample (GSE71841)" python /app/scripts/download_geo_series_sample.py --accession GSE71841 --out-dir "$RA_DIR"
if ! truthy "${SKIP_RA_NAS:-0}"; then
  run_step "RA toy NAS" python /app/scripts/train_toy_nas_cpu.py --disease "Rheumatoid Arthritis" --data-dir "$RA_DIR"
fi

if truthy "${SKIP_T2D:-1}"; then
  mkdir -p "$DATA_ROOT/t2d"
  : > "$DATA_ROOT/t2d/.skipped"
  echo "--- Type 2 Diabetes skipped: KORA F4/FF4 requires a project agreement ---"
else
  echo "Refusing KORA run: configure a separate, explicitly open proxy before enabling T2D." >&2
  exit 2
fi

for accession in GSE40279 GSE87571 GSE280465; do
  run_step "Epigenetic Aging public GEO sample (${accession})" \
    python /app/scripts/download_geo_series_sample.py --accession "$accession" --out-dir "$AGING_DIR" --max-samples 8
done
if ! truthy "${SKIP_EPIGENETIC_AGING_NAS:-0}"; then
  run_step "Epigenetic Aging toy NAS" python /app/scripts/train_toy_nas_cpu.py --disease "Epigenetic Aging" --data-dir "$AGING_DIR"
fi

export DATA_ROOT
export DASHBOARD_OUT="${DASHBOARD_OUT:-$DATA_ROOT/dashboard/dashboard.html}"
echo "--- Static HTML results dashboard ---"
if ! python /app/scripts/build_dashboard.py; then
  echo "ERROR: dashboard generation failed." >&2
  exit 1
fi

if truthy "${GITHUB_DISPATCH_ENABLED:-0}"; then
  : "${GITHUB_REPOSITORY:?Set GITHUB_REPOSITORY=owner/repo}"
  : "${GITHUB_TOKEN:?Set GITHUB_TOKEN with repository dispatch permission}"
  run_step "GitHub Repository Dispatch" curl --fail --silent --show-error --request POST \
    --header "Accept: application/vnd.github+json" \
    --header "Authorization: Bearer ${GITHUB_TOKEN}" \
    --header "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/${GITHUB_REPOSITORY}/dispatches" \
    --data "{\"event_type\":\"${GITHUB_DISPATCH_EVENT:-bio_nas_toy_pipeline_complete}\",\"client_payload\":{\"dashboard\":\"data/dashboard/dashboard.html\",\"status\":\"complete\"}}"
else
  echo "--- GitHub dispatch disabled (GITHUB_DISPATCH_ENABLED=0) ---"
fi

if [[ "$PIPELINE_FAILURES" -gt 0 ]]; then
  echo "=== Pipeline finished with ${PIPELINE_FAILURES} failed step(s); dashboard: ${DASHBOARD_OUT} ==="
  echo "=== See ${STEP_LOG} and the dashboard for details ==="
  exit 1
fi
echo "=== Pipeline complete: ${DASHBOARD_OUT} ==="
exit 0
