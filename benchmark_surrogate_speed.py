from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import numpy as np


ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from data_loader import load_all
from local_search import solve_weights
from surrogate_ga import surrogate_fitness


DATASETS = ["port1", "port2", "port3", "port4", "port5"]
LAMBDAS = [0.1, 0.3, 0.5, 0.7, 0.9]
K = 10
N_SAMPLES = 30
OUTPUT_CSV = ROOT_DIR / "results" / "surrogate_speed.csv"
FIELDNAMES = [
    "dataset", "lambda", "n_samples", "surrogate_seconds",
    "slsqp_seconds", "speedup",
]


def main() -> None:
    datasets = load_all(ROOT_DIR / "data")
    rows = []
    for dataset_index, dataset_name in enumerate(DATASETS):
        data = datasets[dataset_name]
        rng = np.random.default_rng(10_000 + dataset_index)
        selections = [
            tuple(sorted(rng.choice(data.n_assets, K, replace=False).tolist()))
            for _ in range(N_SAMPLES)
        ]
        for lam in LAMBDAS:
            started = time.perf_counter()
            for selected in selections:
                surrogate_fitness(selected, data.mu, data.cov, lam)
            surrogate_seconds = time.perf_counter() - started

            started = time.perf_counter()
            for selected in selections:
                _, _, success = solve_weights(
                    data.cov, data.mu, np.asarray(selected), lam, 0.01, 0.15
                )
                if not success:
                    raise RuntimeError(
                        f"SLSQP nije uspeo za {dataset_name}, lambda={lam}"
                    )
            slsqp_seconds = time.perf_counter() - started
            rows.append({
                "dataset": dataset_name,
                "lambda": lam,
                "n_samples": N_SAMPLES,
                "surrogate_seconds": surrogate_seconds,
                "slsqp_seconds": slsqp_seconds,
                "speedup": slsqp_seconds / surrogate_seconds,
            })
            print(
                f"{dataset_name} lambda={lam:.1f}: "
                f"ubrzanje {slsqp_seconds / surrogate_seconds:.1f}x"
            )
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Sacuvano u {OUTPUT_CSV}.")


if __name__ == "__main__":
    main()
