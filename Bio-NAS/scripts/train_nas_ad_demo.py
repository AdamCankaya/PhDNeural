#!/usr/bin/env python3
"""Methylation-focused toy NAS smoke for Alzheimer's (ADNI sample layout).

Runs only when a real sample is present under ``$ADNI_SAMPLE_OUT``
(default ``/data/adni``): requires ``.ready`` and methylation files under
``files/``. Otherwise skips with exit 0 (account/DUA pending or scaffold).

Mirrors the BRCA meth-only smoke spirit; not Intermediate Fusion NAS.
Severity/phenotype maps stay placeholders in ``disease_registry.yaml``.
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

DEFAULT_DATA = Path("data/adni")
N_CPGS = 200
RANDOM_STATE = 42
READY_MARKER = ".ready"
ARCH_SPACE: list[tuple[int, ...]] = [
    (32,),
    (64,),
    (32, 16),
    (64, 32),
]


def _log(msg: str) -> None:
    print(msg, flush=True)


def _parse_methylation_betas(path: Path, max_rows: int = 5000) -> dict[str, float]:
    """Parse a methylation beta TSV/CSV into probe_id -> beta (GDC-like or simple)."""
    values: dict[str, float] = {}
    with path.open(encoding="utf-8", errors="replace") as fh:
        header = None
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            header = line.rstrip("\n").replace(",", "\t").split("\t")
            break
        if not header:
            return values

        col_names = [h.lower() for h in header]
        probe_col = 0
        beta_col = 1 if len(header) > 1 else 0
        for i, name in enumerate(col_names):
            if name in (
                "composite element ref",
                "composite_element_ref",
                "probe",
                "id",
                "illumina_id",
                "cg",
                "cpg",
            ):
                probe_col = i
            if name in ("beta_value", "beta", "value", "avg_beta"):
                beta_col = i

        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").replace(",", "\t").split("\t")
            if len(parts) <= max(probe_col, beta_col):
                continue
            try:
                beta = float(parts[beta_col])
            except ValueError:
                continue
            if not (0.0 <= beta <= 1.0) and not np.isfinite(beta):
                continue
            values[parts[probe_col]] = beta
            if len(values) >= max_rows:
                break
    return values


def sample_ready(data_dir: Path) -> bool:
    if not (data_dir / READY_MARKER).is_file():
        return False
    files_dir = data_dir / "files"
    if not files_dir.is_dir():
        return False
    meth = list(files_dir.rglob("*"))
    return any(
        p.is_file()
        and p.suffix.lower() in {".txt", ".tsv", ".csv", ".beta"}
        for p in meth
    )


def load_ad_cohort(
    data_dir: Path, *, n_cpgs: int
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Load methylation matrix + binary labels from ADNI sample layout.

    Labels: prefer ``labels.json`` mapping case_id -> 0/1; else alternate 0/1
    by case order (smoke only).
    """
    files_dir = data_dir / "files"
    label_path = data_dir / "labels.json"
    labels: dict[str, int] = {}
    if label_path.is_file():
        raw = json.loads(label_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            labels = {str(k): int(v) for k, v in raw.items()}

    case_dirs = sorted(
        [p for p in files_dir.iterdir() if p.is_dir()],
        key=lambda p: p.name,
    )
    if not case_dirs:
        # Flat files: treat each meth file as a case.
        meth_files = sorted(
            p
            for p in files_dir.rglob("*")
            if p.is_file()
            and p.suffix.lower() in {".txt", ".tsv", ".csv", ".beta"}
        )
        case_files = [(p.stem, p) for p in meth_files]
    else:
        case_files = []
        for case_dir in case_dirs:
            candidates = [
                p
                for p in case_dir.rglob("*")
                if p.is_file()
                and p.suffix.lower() in {".txt", ".tsv", ".csv", ".beta"}
            ]
            if candidates:
                case_files.append((case_dir.name, candidates[0]))

    if len(case_files) < 2:
        raise RuntimeError(
            f"Need ≥2 methylation files under {files_dir} for AD NAS smoke"
        )

    probe_sets: list[dict[str, float]] = []
    case_ids: list[str] = []
    y_list: list[int] = []
    for i, (cid, path) in enumerate(case_files):
        betas = _parse_methylation_betas(path)
        if not betas:
            continue
        probe_sets.append(betas)
        case_ids.append(cid)
        if cid in labels:
            y_list.append(labels[cid])
        else:
            y_list.append(i % 2)

    if len(probe_sets) < 2:
        raise RuntimeError("Parsed fewer than 2 usable methylation matrices")

    common = set(probe_sets[0])
    for s in probe_sets[1:]:
        common &= set(s)
    if not common:
        raise RuntimeError("No shared CpG probes across AD sample files")

    # Variance filter on shared probes.
    probes = sorted(common)
    mat = np.array(
        [[ps[p] for p in probes] for ps in probe_sets], dtype=np.float64
    )
    variances = mat.var(axis=0)
    order = np.argsort(-variances)[: min(n_cpgs, len(probes))]
    x = mat[:, order]
    y = np.array(y_list, dtype=np.int64)
    return x, y, case_ids


def run_nas(x: np.ndarray, y: np.ndarray) -> dict[str, Any]:
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
    return {
        "disease": "alzheimers",
        "cohort": "ADNI",
        "modality": "methylation_beta",
        "best_architecture": best,
        "all_results": results,
        "n_samples": int(x.shape[0]),
        "n_features": int(x.shape[1]),
        "note": (
            "Smoke test only — ADNI methylation features; "
            "not Intermediate Fusion NAS. Labels may be placeholder."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--data-dir",
        type=Path,
        default=Path(os.environ.get("ADNI_SAMPLE_OUT", str(DEFAULT_DATA))),
        help=f"ADNI sample directory (default: {DEFAULT_DATA} or $ADNI_SAMPLE_OUT)",
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
    _log(f"AD NAS demo data dir: {data_dir}")

    if not sample_ready(data_dir):
        _log(
            "SKIP: ADNI sample not ready (no .ready + methylation under files/). "
            "Account + DUA in progress — toy AD NAS not run."
        )
        return 0

    x, y, case_ids = load_ad_cohort(data_dir, n_cpgs=args.n_cpgs)
    _log(f"Cases: {', '.join(case_ids)}")
    _log("Running tiny AD architecture search (MLP LOO-CV on methylation)...")
    summary = run_nas(x, y)
    out_path = data_dir / "nas_demo_results.json"
    out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    best = summary["best_architecture"]
    _log(
        f"Best arch={best['hidden_layer_sizes']} "
        f"LOO={best['loo_accuracy']:.3f}"
    )
    _log(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 — top-level CLI
        _log(f"ERROR: {exc}")
        raise SystemExit(1) from exc
