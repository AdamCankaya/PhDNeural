#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def get_dir_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return total
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def format_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_mb = size_bytes / (1024 * 1024)
    if size_mb >= 1:
        return f"{size_mb:.2f} MB"
    size_kb = size_bytes / 1024
    return f"{size_kb:.2f} KB"


def load_pipeline_steps(step_log: Path) -> list[tuple[str, int]]:
    if not step_log.is_file():
        return []
    steps: list[tuple[str, int]] = []
    for line in step_log.read_text(encoding="utf-8").splitlines():
        if "|" not in line:
            continue
        title, code = line.rsplit("|", 1)
        try:
            steps.append((title, int(code)))
        except ValueError:
            continue
    return steps


def step_failures_for_disease(steps: list[tuple[str, int]], keywords: tuple[str, ...]) -> list[str]:
    failed: list[str] = []
    for title, code in steps:
        if code == 0:
            continue
        if any(keyword in title for keyword in keywords):
            failed.append(title)
    return failed


_SKIP_LABELS: dict[str, str] = {
    "plan1_deferred": "Skipped (not in Plan-1 demo; public GEO deferred)",
    "credentials_dua": "Skipped (credentials/DUA required)",
}


def skipped_status(path: Path) -> str | None:
    """Return dashboard status when ``.skipped`` exists, else None."""
    marker = path / ".skipped"
    if not marker.is_file():
        return None
    raw = marker.read_text(encoding="utf-8").strip()
    if raw in _SKIP_LABELS:
        return _SKIP_LABELS[raw]
    lowered = raw.lower()
    if raw and ("dua" in lowered or "credential" in lowered or "account" in lowered or "agreement" in lowered):
        return _SKIP_LABELS["credentials_dua"]
    if raw and ("plan-1" in lowered or "plan1" in lowered or "deferred" in lowered):
        return _SKIP_LABELS["plan1_deferred"]
    if not raw:
        if path.name == "epigenetic_aging":
            return _SKIP_LABELS["plan1_deferred"]
        if path.name in ("adni", "t2d"):
            return _SKIP_LABELS["credentials_dua"]
        return "Skipped"
    return f"Skipped ({raw.splitlines()[0][:120]})"


def disease_row(
    name: str,
    path: Path,
    source: str,
    steps: list[tuple[str, int]],
    step_keywords: tuple[str, ...],
) -> tuple[str, str, str, str, str, str]:
    size_str = format_size(get_dir_size(path))
    samples = "N/A"
    data_types = "N/A"
    nas_details = "N/A"
    feature_files = sorted(path.glob("*_features.tsv")) if path.is_dir() else []
    nas_path = path / "nas_demo_results.json"
    manifest_path = path / "manifest.json"
    failed_steps = step_failures_for_disease(steps, step_keywords)
    skip_status = skipped_status(path)

    if skip_status is not None:
        status = skip_status
    elif failed_steps and not (path / ".ready").is_file() and not nas_path.is_file() and not feature_files:
        status = f"Failed ({len(failed_steps)} step(s))"
    elif (path / ".ready").is_file() or manifest_path.is_file():
        status = "Ready"
        data_types = "Methylation, Clinical"
    elif nas_path.is_file() or feature_files:
        status = "Partial"
        data_types = "GEO feature matrices" if feature_files else "Toy sample"
        if failed_steps:
            status = f"Partial ({len(failed_steps)} step failure(s))"
    else:
        status = "Not Ready"
        if failed_steps:
            status = f"Failed ({len(failed_steps)} step(s))"

    if skip_status is None and manifest_path.is_file():
        try:
            with manifest_path.open(encoding="utf-8") as fh:
                manifest = json.load(fh)
                samples = str(manifest.get("n_cases", "Unknown"))
        except (json.JSONDecodeError, OSError):
            samples = "Unknown"

    if skip_status is None and nas_path.is_file():
        try:
            with nas_path.open(encoding="utf-8") as fh:
                nas = json.load(fh)
            if "n_samples" in nas:
                samples = str(nas["n_samples"])
            if "best_architecture" in nas:
                best = nas["best_architecture"]
                acc = best.get("validation_accuracy", best.get("loo_accuracy", 0))
                arch = best.get("hidden_width", best.get("hidden_layer_sizes", []))
                loss = best.get("validation_loss")
            else:
                acc = nas.get("best_cv_accuracy", 0)
                arch = nas.get("best_arch", [])
                loss = None
            nas_details = f"Accuracy: {acc:.2f}, Arch: {arch}"
            if loss is not None:
                nas_details += f", Val loss: {loss:.4f}"
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            nas_details = "Error parsing NAS"
    elif skip_status is None and feature_files:
        nas_details = f"{len(feature_files)} GEO matrix file(s); no NAS results yet"
    elif status.startswith("Failed"):
        nas_details = "; ".join(failed_steps[:3])
        if len(failed_steps) > 3:
            nas_details += f"; +{len(failed_steps) - 3} more"

    return name, source, status, size_str, samples, data_types, nas_details


def main() -> int:
    data_root = Path(os.environ.get("DATA_ROOT", "data"))
    out_html = Path(os.environ.get("DASHBOARD_OUT", str(data_root / "dashboard.html")))
    dashboard_dir = out_html.parent
    step_log = dashboard_dir / "pipeline_steps.log"
    steps = load_pipeline_steps(step_log)
    failed_steps = [title for title, code in steps if code != 0]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    diseases = [
        ("TCGA-BRCA", data_root / "tcga/BRCA", "TCGA (GDC)", ("BRCA",)),
        ("Alzheimer's (ADNI)", data_root / "adni", "ADNI (LONI)", ("ADNI", "Alzheimer")),
        ("Rheumatoid Arthritis", data_root / "ra", "GSE71841 & DAS28", ("RA", "GSE71841", "Rheumatoid")),
        (
            "Epigenetic Aging",
            data_root / "epigenetic_aging",
            "GSE40279, GSE87571, GSE280465",
            ("Epigenetic Aging", "GSE40279", "GSE87571", "GSE280465"),
        ),
        ("Type 2 Diabetes", data_root / "t2d", "KORA F4/FF4", ("T2D", "Type 2 Diabetes", "KORA")),
    ]

    summary = (
        f"Generated {generated_at}. "
        f"Pipeline steps: {len(steps)} total, {len(failed_steps)} failed."
        if steps
        else f"Generated {generated_at}. No pipeline step log found."
    )

    html = [
        "<html>",
        "<head><title>Bio-NAS Disease Dashboard</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; margin: 20px; }",
        "table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }",
        "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
        "th { background-color: #f2f2f2; }",
        ".warn { color: #8a1f11; }",
        "</style></head>",
        "<body>",
        "<h1>Bio-NAS Multi-Disease Dashboard</h1>",
        f"<p>{summary}</p>",
    ]

    if failed_steps:
        html.append('<h2 class="warn">Failed pipeline steps</h2><ul>')
        for title in failed_steps:
            html.append(f"<li>{title}</li>")
        html.append("</ul>")

    html.extend(
        [
            "<table>",
            "<tr><th>Disease</th><th>Data Source</th><th>Status</th><th>Size on Disk</th>"
            "<th>Samples</th><th>Types of Data</th><th>NAS Details</th></tr>",
        ]
    )

    for name, path, source, keywords in diseases:
        row = disease_row(name, path, source, steps, keywords)
        html.append(
            f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td>"
            f"<td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>"
        )

    html.extend(
        [
            "</table>",
            "<p><small>Toy NAS values validate the CPU Docker pipeline only. "
            "They are not clinical results.</small></p>",
            "</body>",
            "</html>",
        ]
    )

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text("\n".join(html), encoding="utf-8")
    print(f"Dashboard generated at {out_html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
