#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import random

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--disease", required=True)
    p.add_argument("--out-dir", required=True, type=Path)
    args = p.parse_args()

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    files_dir = out_dir / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    if (out_dir / ".ready").is_file():
        return 0

    # Generate dummy data
    n_samples = 10
    n_features = 200

    labels = {}
    for i in range(n_samples):
        case_id = f"CASE_{i}"
        labels[case_id] = random.choice([0, 1])
        
        # Write dummy TSV for methylation
        tsv_path = files_dir / f"{case_id}_methylation.tsv"
        with tsv_path.open("w") as fh:
            fh.write("probe\tbeta_value\n")
            for j in range(n_features):
                fh.write(f"cg{j:08d}\t{random.random()}\n")

    with (out_dir / "labels.json").open("w") as fh:
        json.dump(labels, fh)

    # Write some demographics
    demographics = []
    for i in range(n_samples):
        demographics.append({"case_id": f"CASE_{i}", "age": random.randint(30, 80)})
    with (out_dir / "demographics.json").open("w") as fh:
        json.dump(demographics, fh)

    with (out_dir / "manifest.json").open("w") as fh:
        json.dump({"schema_version": 2, "n_cases": n_samples}, fh)

    (out_dir / ".ready").write_text("ok")
    print(f"Downloaded mock data for {args.disease} to {out_dir}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
