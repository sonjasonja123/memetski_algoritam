from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from data_loader import load_all


DATASET_LABELS = {
    "port1": "Hang Seng",
    "port2": "DAX 100",
    "port3": "FTSE 100",
    "port4": "S&P 100",
    "port5": "Nikkei 225",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Poredi surogat GA i random search sa PORTEF granicom."
    )
    parser.add_argument(
        "--results", type=Path,
        default=ROOT_DIR / "results" / "surrogate_results.csv",
    )
    parser.add_argument("--data-dir", type=Path, default=ROOT_DIR / "data")
    parser.add_argument(
        "--output", type=Path,
        default=ROOT_DIR / "results" / "surrogate_vs_portef.png",
    )
    parser.add_argument("--pop-size", type=int, default=10)
    parser.add_argument("--pm", type=float, default=0.25)
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--show", action="store_true")
    return parser.parse_args()


def load_portef(path: Path) -> tuple[np.ndarray, np.ndarray]:
    values = np.fromstring(path.read_text(encoding="utf-8"), sep=" ")
    if values.size == 0 or values.size % 2:
        raise ValueError(f"Neispravan PORTEF format: {path}")
    return np.sqrt(values[1::2]), values[0::2]


def load_results(
    path: Path, pop_size: int, pm: float, datasets
) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    with path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        required = {
            "dataset", "lambda", "pop_size", "pm", "method",
            "best_fitness", "selected_assets",
        }
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} nema kolone: {', '.join(sorted(missing))}")
        for row in reader:
            if int(row["pop_size"]) != pop_size or not np.isclose(float(row["pm"]), pm):
                continue
            dataset = row["dataset"]
            selected = np.fromstring(row["selected_assets"], sep=" ", dtype=int)
            data = datasets[dataset]
            weights = np.full(len(selected), 1.0 / len(selected))
            variance = float(weights @ data.cov[np.ix_(selected, selected)] @ weights)
            grouped[dataset].append({
                "lambda": float(row["lambda"]),
                "method": row["method"],
                "fitness": float(row["best_fitness"]),
                "std": float(np.sqrt(max(variance, 0.0))),
                "return": float(weights @ data.mu[selected]),
            })
    if not grouped:
        raise ValueError(f"Nema rezultata za pop_size={pop_size}, pm={pm}")
    return dict(grouped)


def best_per_lambda(rows: list[dict], method: str) -> list[dict]:
    best = {}
    for row in rows:
        if row["method"] != method:
            continue
        lam = row["lambda"]
        if lam not in best or row["fitness"] < best[lam]["fitness"]:
            best[lam] = row
    return [best[lam] for lam in sorted(best)]


def main() -> None:
    args = parse_args()
    datasets = load_all(args.data_dir)
    results = load_results(args.results, args.pop_size, args.pm, datasets)
    dataset_names = sorted(results, key=lambda name: int(name.removeprefix("port")))
    lambdas = [row["lambda"] for rows in results.values() for row in rows]
    color_norm = plt.Normalize(min(lambdas), max(lambdas))

    ncols = min(3, len(dataset_names))
    nrows = (len(dataset_names) + ncols - 1) // ncols
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(6 * ncols, 4.8 * nrows), squeeze=False
    )
    axes_flat = axes.ravel()
    color_source = None
    for ax, dataset_name in zip(axes_flat, dataset_names):
        frontier_std, frontier_return = load_portef(
            args.data_dir / f"portef{dataset_name.removeprefix('port')}.txt"
        )
        rows = results[dataset_name]
        ga_rows = [row for row in rows if row["method"] == "ga"]
        random_rows = [row for row in rows if row["method"] == "random"]
        ga_best = sorted(best_per_lambda(rows, "ga"), key=lambda row: row["std"])
        random_best = sorted(
            best_per_lambda(rows, "random"), key=lambda row: row["std"]
        )

        ax.plot(frontier_std, frontier_return, color="black", lw=1.8, label="PORTEF (UEF)")
        ax.scatter(
            [row["std"] for row in random_rows],
            [row["return"] for row in random_rows],
            c=[row["lambda"] for row in random_rows], cmap="viridis",
            norm=color_norm, marker="^", s=24, alpha=0.20, linewidths=0,
            label="Random search",
        )
        color_source = ax.scatter(
            [row["std"] for row in ga_rows],
            [row["return"] for row in ga_rows],
            c=[row["lambda"] for row in ga_rows], cmap="viridis",
            norm=color_norm, marker="o", s=27, alpha=0.42, linewidths=0,
            label="Surogat GA",
        )
        ax.plot(
            [row["std"] for row in random_best],
            [row["return"] for row in random_best],
            color="#ff7f0e", lw=1.5, ls=":", label="Najbolji random po lambda",
        )
        ax.plot(
            [row["std"] for row in ga_best],
            [row["return"] for row in ga_best],
            color="#d62728", lw=2.3, ls="--", label="Najbolji GA po lambda",
        )
        ax.scatter(
            [row["std"] for row in ga_best],
            [row["return"] for row in ga_best],
            c=[row["lambda"] for row in ga_best], cmap="viridis",
            norm=color_norm, marker="X", s=75, edgecolors="white",
            linewidths=0.8, zorder=3,
        )
        ax.set_title(f"{dataset_name} - {DATASET_LABELS.get(dataset_name, dataset_name)}")
        ax.set_xlabel("Rizik (standardna devijacija)")
        ax.set_ylabel("Ocekivani prinos")
        ax.grid(alpha=0.25)
        ax.legend(fontsize=7.5)

    if color_source is not None:
        unused_axes = list(axes_flat[len(dataset_names):])
        if unused_axes:
            color_axis = unused_axes[0]
            color_axis.set_box_aspect(1.8)
            colorbar = fig.colorbar(color_source, cax=color_axis)
            for ax in unused_axes[1:]:
                ax.remove()
        else:
            colorbar = fig.colorbar(
                color_source, ax=list(axes_flat[: len(dataset_names)]),
                shrink=0.82, pad=0.02,
            )
        colorbar.set_label("lambda")
    fig.suptitle(
        f"Surogat GA i random search prema PORTEF granici "
        f"(pop={args.pop_size}, pm={args.pm:g}, K=10)",
        fontsize=15,
    )
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
