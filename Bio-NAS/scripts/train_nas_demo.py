#!/usr/bin/env python3
"""Minimal NAS / training demo on the tiny TCGA-BRCA Docker sample.

Loads open-access demographics + RNA-seq gene expression from
``/data/tcga/BRCA`` (or ``$TCGA_SAMPLE_OUT``), builds a small feature matrix,
and searches a handful of MLP architectures with sklearn.

Designed for 5–10 patients only — a smoke test, not a research result.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

DEFAULT_DATA = Path("data/tcga/BRCA")
N_GENES = 200
RANDOM_STATE = 42

# Tiny architecture search space (hidden-layer configs).
ARCH_SPACE: list[tuple[int, ...]] = [
    (32,),
    (64,),
    (32, 16),
    (64, 32),
]


def _log(msg: str) -> None:
    print(msg, flush=True)


def _stage_to_label(stage: str | None) -> int:
    """Map AJCC stage string to a coarse binary label (early vs late)."""
    if not stage:
        return 0
    s = stage.upper().replace("STAGE", "").strip()
    if s.startswith("III") or s.startswith("IV"):
        return 1
    return 0


def _parse_star_counts(path: Path, n_genes: int) -> dict[str, float]:
    """Parse a GDC STAR gene-counts TSV into gene_id -> tpm (or unstranded)."""
    values: dict[str, float] = {}
    with path.open(encoding="utf-8", errors="replace") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        # Prefer TPM if present; else unstranded / counts column.
        col_names = [h.lower() for h in header]
        prefer = ("tpm_unstranded", "fpkm_unstranded", "unstranded", "tpm", "fpkm")
        value_col = 1
        for name in prefer:
            if name in col_names:
                value_col = col_names.index(name)
                break
        gene_col = 0
        for i, name in enumerate(col_names):
            if name in ("gene_id", "geneid", "ensembl_gene_id"):
                gene_col = i
                break

        for line in fh:
            if not line.strip() or line.startswith("N_"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= max(gene_col, value_col):
                continue
            gene = parts[gene_col]
            # Skip PAR_Y / non-gene rows if present.
            if gene.startswith("_") or gene in {"N_unmapped", "N_multimapping"}:
                continue
            try:
                values[gene] = float(parts[value_col])
            except ValueError:
                continue
            if len(values) >= n_genes * 20:
                # Read enough rows to pick high-variance genes later.
                # Keep going until we have a large pool; cap for speed.
                if len(values) >= 5000:
                    break
    return values


def load_cohort(data_dir: Path, n_genes: int) -> tuple[np.ndarray, np.ndarray, list[str]]:
    manifest_path = data_dir / "manifest.json"
    demo_path = data_dir / "demographics.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing {manifest_path}; run download first.")
    if not demo_path.exists():
        raise FileNotFoundError(f"Missing {demo_path}; run download first.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    demographics = {
        row["case_id"]: row
        for row in json.loads(demo_path.read_text(encoding="utf-8"))
    }
    cohort = manifest.get("cohort") or []
    if len(cohort) < 5:
        raise RuntimeError(f"Expected >=5 cases in manifest, found {len(cohort)}")

    expr_by_case: dict[str, dict[str, float]] = {}
    files_dir = data_dir / "files"
    for entry in cohort:
        case_id = entry["case_id"]
        fname = entry["expression_file_name"]
        path = files_dir / fname
        if not path.exists():
            raise FileNotFoundError(f"Expression file missing: {path}")
        expr_by_case[case_id] = _parse_star_counts(path, n_genes=n_genes)

    # Gene universe: intersection, then top-variance genes.
    gene_sets = [set(v.keys()) for v in expr_by_case.values()]
    common = set.intersection(*gene_sets) if gene_sets else set()
    if len(common) < 10:
        # Fallback: union of first n_genes keys per file.
        common = set()
        for vals in expr_by_case.values():
            common.update(list(vals.keys())[:n_genes])
    genes = sorted(common)
    mat = np.array(
        [[expr_by_case[c["case_id"]].get(g, 0.0) for g in genes] for c in cohort],
        dtype=np.float64,
    )
    if mat.shape[1] > n_genes:
        var = mat.var(axis=0)
        keep = np.argsort(var)[-n_genes:]
        genes = [genes[i] for i in keep]
        mat = mat[:, keep]

    # Demographic features: age + gender one-hot.
    ages: list[float] = []
    gender_codes: list[float] = []
    labels: list[int] = []
    case_ids: list[str] = []
    for entry in cohort:
        case_id = entry["case_id"]
        demo: dict[str, Any] = demographics.get(case_id, {})
        age = demo.get("age_at_diagnosis")
        ages.append(float(age) if age is not None else float(np.nan))
        gender = (demo.get("gender") or "").lower()
        gender_codes.append(1.0 if gender == "female" else 0.0)
        labels.append(_stage_to_label(demo.get("ajcc_pathologic_stage")))
        case_ids.append(demo.get("submitter_id") or case_id)

    age_arr = np.array(ages, dtype=np.float64)
    if np.isnan(age_arr).all():
        age_arr = np.zeros_like(age_arr)
    else:
        med = float(np.nanmedian(age_arr))
        age_arr = np.where(np.isnan(age_arr), med, age_arr)

    demo_mat = np.column_stack(
        [age_arr, np.array(gender_codes, dtype=np.float64)]
    )
    x = np.hstack([mat, demo_mat])
    y = np.array(labels, dtype=np.int64)

    # With tiny n, ensure both classes exist for CV.
    if len(np.unique(y)) < 2:
        # Synthetic split by median expression of first gene (demo only).
        _log("Note: stage labels are single-class; using median-split proxy label.")
        y = (x[:, 0] >= np.median(x[:, 0])).astype(np.int64)

    _log(
        f"Loaded {x.shape[0]} patients × {x.shape[1]} features "
        f"({len(genes)} genes + demographics); label counts={np.bincount(y)}"
    )
    return x, y, case_ids


def run_nas(x: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    """Leave-one-out CV over a small MLP architecture grid."""
    loo = LeaveOneOut()
    results: list[dict[str, Any]] = []

    for arch in ARCH_SPACE:
        clf = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "mlp",
                    MLPClassifier(
                        hidden_layer_sizes=arch,
                        max_iter=300,
                        random_state=RANDOM_STATE,
                        early_stopping=False,
                    ),
                ),
            ]
        )
        scores = cross_val_score(clf, x, y, cv=loo, scoring="accuracy")
        mean_acc = float(scores.mean())
        results.append(
            {
                "hidden_layer_sizes": list(arch),
                "loo_accuracy": mean_acc,
                "n_splits": int(len(scores)),
            }
        )
        _log(f"  arch={arch}: LOO accuracy={mean_acc:.3f}")

    best = max(results, key=lambda r: r["loo_accuracy"])
    # Refit best on all samples (demo artifact).
    best_arch = tuple(best["hidden_layer_sizes"])
    final = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "mlp",
                MLPClassifier(
                    hidden_layer_sizes=best_arch,
                    max_iter=300,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )
    final.fit(x, y)
    train_acc = float(final.score(x, y))
    return {
        "best_architecture": best,
        "all_results": results,
        "train_accuracy_refit": train_acc,
        "n_samples": int(x.shape[0]),
        "n_features": int(x.shape[1]),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--data-dir",
        type=Path,
        default=Path(os.environ.get("TCGA_SAMPLE_OUT", str(DEFAULT_DATA))),
        help=f"Sample directory (default: {DEFAULT_DATA} or $TCGA_SAMPLE_OUT)",
    )
    p.add_argument(
        "--n-genes",
        type=int,
        default=N_GENES,
        help=f"Top-variance genes to keep (default: {N_GENES})",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    data_dir = args.data_dir.resolve()
    _log(f"NAS demo data dir: {data_dir}")

    x, y, case_ids = load_cohort(data_dir, n_genes=args.n_genes)
    _log(f"Cases: {', '.join(case_ids)}")
    _log("Running tiny architecture search (MLP LOO-CV)...")
    summary = run_nas(x, y)

    out_path = data_dir / "nas_demo_results.json"
    out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    best = summary["best_architecture"]
    _log(
        f"Best arch={best['hidden_layer_sizes']} "
        f"LOO={best['loo_accuracy']:.3f}; "
        f"refit train acc={summary['train_accuracy_refit']:.3f}"
    )
    _log(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 — top-level CLI
        _log(f"ERROR: {exc}")
        raise SystemExit(1) from exc
