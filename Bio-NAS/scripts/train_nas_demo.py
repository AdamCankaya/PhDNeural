#!/usr/bin/env python3
"""Minimal NAS / training smoke on the tiny TCGA-BRCA Docker sample.

Loads open-access **methylation beta** features + AJCC stage labels from
``/data/tcga/BRCA`` (or ``$TCGA_SAMPLE_OUT``), builds a small feature matrix,
and searches a handful of MLP architectures with sklearn.

RNA-seq may be present on disk (PoC-minimum download completeness) but is
**not** required for this smoke train path.

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
N_CPGS = 200
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


def _parse_methylation_betas(path: Path, max_rows: int = 5000) -> dict[str, float]:
    """Parse a GDC Methylation Beta Value TSV into probe_id -> beta."""
    values: dict[str, float] = {}
    with path.open(encoding="utf-8", errors="replace") as fh:
        header = None
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            header = line.rstrip("\n").split("\t")
            break
        if not header:
            return values

        col_names = [h.lower() for h in header]
        probe_col = 0
        for i, name in enumerate(col_names):
            if name in (
                "composite element ref",
                "composite_element_ref",
                "probe",
                "id",
                "illumina_id",
            ):
                probe_col = i
                break

        beta_col = 1 if len(header) > 1 else 0
        for name in ("beta_value", "beta", "value"):
            if name in col_names:
                beta_col = col_names.index(name)
                break

        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) <= max(probe_col, beta_col):
                continue
            probe = parts[probe_col]
            if not probe or probe.lower().startswith("composite"):
                continue
            try:
                beta = float(parts[beta_col])
            except ValueError:
                continue
            if not np.isfinite(beta):
                continue
            # Betas are [0, 1]; keep out-of-range as-is for smoke (clip later).
            values[probe] = beta
            if len(values) >= max_rows:
                break
    return values


def _resolve_meth_path(entry: dict[str, Any], files_dir: Path, manifest: dict) -> Path:
    fname = entry.get("methylation_file_name")
    if fname:
        path = files_dir / fname
        if path.exists():
            return path
    case_id = entry.get("case_id")
    for f in manifest.get("files") or []:
        if f.get("label") == "methylation" and f.get("case_id") == case_id:
            path = files_dir / f["file_name"]
            if path.exists():
                return path
    raise FileNotFoundError(
        f"Methylation file missing for case {case_id}; "
        "re-run download (delete .ready if schema changed)."
    )


def load_cohort(data_dir: Path, n_cpgs: int) -> tuple[np.ndarray, np.ndarray, list[str]]:
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

    meth_by_case: dict[str, dict[str, float]] = {}
    files_dir = data_dir / "files"
    for entry in cohort:
        case_id = entry["case_id"]
        path = _resolve_meth_path(entry, files_dir, manifest)
        meth_by_case[case_id] = _parse_methylation_betas(
            path, max_rows=max(5000, n_cpgs * 25)
        )

    probe_sets = [set(v.keys()) for v in meth_by_case.values()]
    common = set.intersection(*probe_sets) if probe_sets else set()
    if len(common) < 10:
        common = set()
        for vals in meth_by_case.values():
            common.update(list(vals.keys())[:n_cpgs])
    probes = sorted(common)
    mat = np.array(
        [[meth_by_case[c["case_id"]].get(p, np.nan) for p in probes] for c in cohort],
        dtype=np.float64,
    )
    # Mean-impute NaNs per column (smoke; Plan 07 will do train-only properly).
    col_means = np.nanmean(mat, axis=0)
    inds = np.where(np.isnan(mat))
    mat[inds] = np.take(col_means, inds[1])
    mat = np.clip(mat, 0.0, 1.0)

    if mat.shape[1] > n_cpgs:
        var = mat.var(axis=0)
        keep = np.argsort(var)[-n_cpgs:]
        probes = [probes[i] for i in keep]
        mat = mat[:, keep]

    labels: list[int] = []
    case_ids: list[str] = []
    for entry in cohort:
        case_id = entry["case_id"]
        demo: dict[str, Any] = demographics.get(case_id, {})
        labels.append(_stage_to_label(demo.get("ajcc_pathologic_stage")))
        case_ids.append(demo.get("submitter_id") or case_id)

    x = mat
    y = np.array(labels, dtype=np.int64)

    if len(np.unique(y)) < 2:
        _log("Note: stage labels are single-class; using median-split proxy label.")
        y = (x[:, 0] >= np.median(x[:, 0])).astype(np.int64)

    _log(
        f"Loaded {x.shape[0]} patients × {x.shape[1]} methylation features "
        f"({len(probes)} CpGs); label counts={np.bincount(y)}"
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
        "modality": "methylation_beta",
        "best_architecture": best,
        "all_results": results,
        "train_accuracy_refit": train_acc,
        "n_samples": int(x.shape[0]),
        "n_features": int(x.shape[1]),
        "note": "Smoke test only — methylation features + stage labels; not Intermediate Fusion NAS.",
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
        "--n-cpgs",
        type=int,
        default=N_CPGS,
        help=f"Top-variance CpG probes to keep (default: {N_CPGS})",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    data_dir = args.data_dir.resolve()
    _log(f"NAS demo data dir: {data_dir}")

    x, y, case_ids = load_cohort(data_dir, n_cpgs=args.n_cpgs)
    _log(f"Cases: {', '.join(case_ids)}")
    _log("Running tiny architecture search (MLP LOO-CV on methylation)...")
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
