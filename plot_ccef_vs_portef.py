from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT_DIR = Path(__file__).resolve().parent
DATASET_LABELS = {
    "port1": "Hang Seng",
    "port2": "DAX 100",
    "port3": "FTSE 100",
    "port4": "S&P 100",
    "port5": "Nikkei 225",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Poredi CCEF rezultate sa PORTEF efikasnom granicom."
    )
    parser.add_argument(
        "--ccef",
        type=Path,
        default=ROOT_DIR / "results" / "ccef_results.csv",
        help="CCEF CSV (podrazumevano: results/ccef_results.csv)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT_DIR / "data",
        help="Direktorijum sa portef1.txt ... portef5.txt",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT_DIR / "results" / "ccef_vs_portef.png",
        help="Putanja izlazne slike",
    )
    parser.add_argument("--dpi", type=int, default=200, help="Rezolucija izlazne slike")
    parser.add_argument("--show", action="store_true", help="Prikazi grafikon u prozoru")
    return parser.parse_args()


def load_ccef(path: Path) -> dict[str, list[dict[str, float]]]:
    required = {"dataset", "lambda", "best_fitness", "return", "std"}
    grouped: dict[str, list[dict[str, float]]] = defaultdict(list)
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} nema kolone: {', '.join(sorted(missing))}")
        for row in reader:
            grouped[row["dataset"]].append(
                {
                    "lambda": float(row["lambda"]),
                    "fitness": float(row["best_fitness"]),
                    "return": float(row["return"]),
                    "std": float(row["std"]),
                }
            )
    if not grouped:
        raise ValueError(f"Nema CCEF rezultata u {path}")
    return dict(grouped)


def load_portef(path: Path) -> tuple[np.ndarray, np.ndarray]:
    values = np.fromstring(path.read_text(encoding="utf-8"), sep=" ")
    if values.size == 0 or values.size % 2:
        raise ValueError(f"Neispravan PORTEF format: {path}")
    returns = values[0::2]
    variances = values[1::2]
    if np.any(variances < 0):
        raise ValueError(f"Negativna varijansa u {path}")
    return np.sqrt(variances), returns


def best_per_lambda(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    best: dict[float, dict[str, float]] = {}
    for row in rows:
        lam = row["lambda"]
        if lam not in best or row["fitness"] < best[lam]["fitness"]:
            best[lam] = row
    return [best[lam] for lam in sorted(best)]


def main() -> None:
    args = parse_args()
    ccef = load_ccef(args.ccef)
    datasets = sorted(ccef, key=lambda name: int(name.removeprefix("port")))

    ncols = min(3, len(datasets))
    nrows = (len(datasets) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 4.8 * nrows), squeeze=False)
    axes_flat = axes.ravel()
    color_norm = plt.Normalize(
        min(row["lambda"] for rows in ccef.values() for row in rows),
        max(row["lambda"] for rows in ccef.values() for row in rows),
    )
    scatter = None

    for ax, dataset in zip(axes_flat, datasets):
        portef_path = args.data_dir / f"portef{dataset.removeprefix('port')}.txt"
        if not portef_path.exists():
            raise FileNotFoundError(f"Nedostaje {portef_path}")
        frontier_std, frontier_return = load_portef(portef_path)
        rows = ccef[dataset]
        best = sorted(best_per_lambda(rows), key=lambda row: row["std"])

        ax.plot(frontier_std, frontier_return, color="black", linewidth=1.8, label="PORTEF (UEF)")
        scatter = ax.scatter(
            [row["std"] for row in rows],
            [row["return"] for row in rows],
            c=[row["lambda"] for row in rows],
            cmap="viridis",
            norm=color_norm,
            s=24,
            alpha=0.35,
            linewidths=0,
            label="Sva CCEF pokretanja",
        )
        ax.plot(
            [row["std"] for row in best],
            [row["return"] for row in best],
            color="#d62728",
            linewidth=2.4,
            linestyle="--",
            label="CCEF linija (najbolji po lambda)",
            zorder=2,
        )
        ax.scatter(
            [row["std"] for row in best],
            [row["return"] for row in best],
            c=[row["lambda"] for row in best],
            cmap="viridis",
            norm=color_norm,
            s=75,
            marker="X",
            edgecolors="white",
            linewidths=0.8,
            label="CCEF tacke po lambda",
            zorder=3,
        )
        ax.set_title(f"{dataset} - {DATASET_LABELS.get(dataset, dataset)}")
        ax.set_xlabel("Rizik (standardna devijacija)")
        ax.set_ylabel("Ocekivani prinos")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)

    for ax in axes_flat[len(datasets):]:
        ax.remove()

    if scatter is not None:
        colorbar = fig.colorbar(scatter, ax=list(axes_flat[: len(datasets)]), shrink=0.82, pad=0.02)
        colorbar.set_label("lambda")
    fig.suptitle("CCEF rezultati u odnosu na PORTEF efikasnu granicu", fontsize=15)
    fig.subplots_adjust(top=0.90, right=0.93, hspace=0.34, wspace=0.28)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=args.dpi, bbox_inches="tight")
    print(f"Grafikon sacuvan: {args.output.resolve()}")
    if args.show:
        plt.show()
    else:
        plt.close(fig)


if __name__ == "__main__":
    main()
