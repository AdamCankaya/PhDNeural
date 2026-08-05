#!/usr/bin/env python3
"""Small CPU-only PyTorch architecture search for public toy samples."""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


class ToyNet(nn.Module):
    def __init__(self, features: int, width: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(features, width), nn.ReLU(), nn.Linear(width, 2))

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        return self.layers(values)


def load_tsvs(data_dir: Path) -> np.ndarray:
    arrays = []
    for path in sorted(data_dir.glob("*_features.tsv")):
        with path.open(encoding="utf-8") as fh:
            rows = list(csv.reader(fh, delimiter="\t"))[1:]
        if rows:
            arrays.append(np.asarray([[float(v) for v in row[1:]] for row in rows], dtype=np.float32))
    if not arrays:
        raise RuntimeError(f"No GEO feature samples found in {data_dir}")
    width = min(array.shape[1] for array in arrays)
    return np.concatenate([array[:, :width] for array in arrays], axis=0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--disease", required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--brca", action="store_true", help="Load BRCA methylation and stage labels")
    args = parser.parse_args()
    torch.set_num_threads(int(os.environ.get("TORCH_NUM_THREADS", "2")))
    torch.manual_seed(42)
    np.random.seed(42)
    if args.brca:
        from train_nas_demo import N_CPGS, load_cohort

        values, labels, _ = load_cohort(args.data_dir, n_cpgs=N_CPGS)
        target_note = "clinical AJCC stage proxy"
    else:
        values = load_tsvs(args.data_dir)
        target_note = "data-derived synthetic proxy (not clinical)"
    values = np.nan_to_num(values).astype(np.float32, copy=False)
    values = ((values - values.mean(axis=0)) / (values.std(axis=0) + 1e-6)).astype(
        np.float32, copy=False
    )
    # A deterministic, data-derived proxy target. This validates orchestration only;
    # it is not a clinical phenotype or severity label.
    if not args.brca:
        labels = (values[:, 0] > np.median(values[:, 0])).astype(np.int64)
        if len(np.unique(labels)) < 2:
            labels = np.arange(len(values), dtype=np.int64) % 2
    split = max(2, int(len(values) * 0.75))
    split = min(split, len(values) - 1)
    train = TensorDataset(torch.tensor(values[:split]), torch.tensor(labels[:split]))
    validation_x = torch.tensor(values[split:])
    validation_y = torch.tensor(labels[split:])
    loader = DataLoader(train, batch_size=min(8, len(train)), shuffle=True, num_workers=int(os.environ.get("TOY_NAS_NUM_WORKERS", "0")))
    candidates = [8, 16, 32]
    best: dict[str, object] | None = None
    for width in candidates:
        model = ToyNet(values.shape[1], width).cpu()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        loss_fn = nn.CrossEntropyLoss()
        model.train()
        for _ in range(12):
            for batch_x, batch_y in loader:
                optimizer.zero_grad()
                loss = loss_fn(model(batch_x.cpu()), batch_y.cpu())
                loss.backward()
                optimizer.step()
        model.eval()
        with torch.no_grad():
            logits = model(validation_x.cpu())
            validation_loss = float(loss_fn(logits, validation_y.cpu()).item())
            accuracy = float((logits.argmax(dim=1) == validation_y.cpu()).float().mean().item())
        candidate = {"hidden_width": width, "validation_loss": validation_loss, "validation_accuracy": accuracy}
        if best is None or validation_loss < float(best["validation_loss"]):
            best = candidate
    result = {"disease": args.disease, "runner": "pytorch_cpu", "device": "cpu", "target": target_note, "n_samples": int(len(values)), "n_features": int(values.shape[1]), "candidates": candidates, "best_architecture": best, "coral_severity_loss": None}
    (args.data_dir / "nas_demo_results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"{args.disease}: CPU toy NAS complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
