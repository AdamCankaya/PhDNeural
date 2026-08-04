#!/usr/bin/env python3
"""Create a tiny numeric sample from an open GEO series-matrix file.

The downloader reads only the first requested samples and probes from the public
NCBI FTP stream.  It never uses authenticated GEO resources.  The output is
deliberately sample-scale and exists only to exercise the CPU toy-NAS pipeline.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import urllib.request
from pathlib import Path


def matrix_url(accession: str) -> str:
    prefix = accession[:-3] + "nnn"
    return f"https://ftp.ncbi.nlm.nih.gov/geo/series/{prefix}/{accession}/matrix/{accession}_series_matrix.txt.gz"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--accession", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--max-samples", type=int, default=12)
    parser.add_argument("--max-features", type=int, default=200)
    args = parser.parse_args()
    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"{args.accession}_features.tsv"
    if output.exists():
        print(f"{args.accession}: existing sample retained: {output}")
        return 0

    request = urllib.request.Request(matrix_url(args.accession), headers={"User-Agent": "Bio-NAS-toy-sample/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response, gzip.GzipFile(fileobj=response) as archive:
        samples: list[str] | None = None
        rows: list[list[str]] = []
        in_table = False
        for raw in archive:
            line = raw.decode("utf-8", errors="replace").rstrip("\n\r")
            if line == "!series_matrix_table_begin":
                in_table = True
                continue
            if not in_table:
                continue
            if line == "!series_matrix_table_end":
                break
            fields = line.split("\t")
            if samples is None:
                samples = [x.strip('"') for x in fields[1: args.max_samples + 1]]
                continue
            if len(fields) < len(samples) + 1:
                continue
            values = [x.strip('"') for x in fields[1: len(samples) + 1]]
            try:
                [float(x) for x in values]
            except ValueError:
                continue
            rows.append(values)
            if len(rows) >= args.max_features:
                break
    if not samples or len(rows) < 2:
        raise RuntimeError(f"{args.accession}: no usable numeric matrix rows found")

    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, delimiter="\t")
        writer.writerow(["sample_id", *[f"feature_{i}" for i in range(len(rows))]])
        for sample_index, sample in enumerate(samples):
            writer.writerow([sample, *[row[sample_index] for row in rows]])
    (out_dir / f"{args.accession}_source.json").write_text(json.dumps({"accession": args.accession, "url": matrix_url(args.accession), "n_samples": len(samples), "n_features": len(rows)}, indent=2), encoding="utf-8")
    print(f"{args.accession}: wrote {len(samples)} samples x {len(rows)} features")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
