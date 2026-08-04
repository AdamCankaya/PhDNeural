#!/usr/bin/env python3
import json
import os
from pathlib import Path

def get_dir_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return total
    for p in path.rglob('*'):
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

def main():
    data_root = Path(os.environ.get("DATA_ROOT", "data"))
    out_html = Path(os.environ.get("DASHBOARD_OUT", str(data_root / "dashboard.html")))

    diseases = [
        ("TCGA-BRCA", data_root / "tcga/BRCA", "TCGA (GDC)"),
        ("Alzheimer's (ADNI)", data_root / "adni", "ADNI (LONI)"),
        ("Rheumatoid Arthritis", data_root / "ra", "GSE71841 & DAS28"),
        ("Type 2 Diabetes", data_root / "t2d", "KORA F4/FF4"),
        ("Epigenetic Aging", data_root / "epigenetic_aging", "GSE40279, GSE87571, GSE280465"),
    ]

    html = [
        "<html>",
        "<head><title>Bio-NAS Disease Dashboard</title>",
        "<style>",
        "body { font-family: Arial, sans-serif; margin: 20px; }",
        "table { border-collapse: collapse; width: 100%; margin-bottom: 30px; }",
        "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
        "th { background-color: #f2f2f2; }",
        "</style></head>",
        "<body>",
        "<h1>Bio-NAS Multi-Disease Dashboard</h1>",
        "<table>",
        "<tr><th>Disease</th><th>Data Source</th><th>Status</th><th>Size on Disk</th><th>Samples</th><th>Types of Data</th><th>NAS Details</th></tr>"
    ]

    for name, path, source in diseases:
        size_str = format_size(get_dir_size(path))
        status = "Not Ready"
        samples = "N/A"
        data_types = "N/A"
        nas_details = "N/A"

        if (path / ".ready").exists():
            status = "Ready"
            data_types = "Methylation, Clinical"
            
            manifest_path = path / "manifest.json"
            if manifest_path.exists():
                try:
                    with manifest_path.open() as fh:
                        manifest = json.load(fh)
                        samples = str(manifest.get("n_cases", "Unknown"))
                except:
                    samples = "Unknown"
            
            nas_path = path / "nas_demo_results.json"
            if nas_path.exists():
                try:
                    with nas_path.open() as fh:
                        nas = json.load(fh)
                        if "best_architecture" in nas:
                            best = nas["best_architecture"]
                            acc = best.get("validation_accuracy", best.get("loo_accuracy", 0))
                            arch = best.get("hidden_width", best.get("hidden_layer_sizes", []))
                            loss = best.get("validation_loss")
                        else:
                            acc = nas.get("best_cv_accuracy", 0)
                            arch = nas.get("best_arch", [])
                        nas_details = f"Accuracy: {acc:.2f}, Arch: {arch}"
                        if loss is not None:
                            nas_details += f", Val loss: {loss:.4f}"
                except:
                    nas_details = "Error parsing NAS"
            else:
                nas_details = "No NAS results"
                
        elif (path / ".skipped").exists():
            status = "Skipped (Credentials/DUA required)"
            
        html.append(f"<tr><td>{name}</td><td>{source}</td><td>{status}</td><td>{size_str}</td><td>{samples}</td><td>{data_types}</td><td>{nas_details}</td></tr>")

    html.extend(["</table>", "<p><small>Toy NAS values validate the CPU Docker pipeline only. They are not clinical results.</small></p>", "</body>", "</html>"])

    out_html.parent.mkdir(parents=True, exist_ok=True)
    with out_html.open("w") as fh:
        fh.write("\n".join(html))

    print(f"Dashboard generated at {out_html}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
