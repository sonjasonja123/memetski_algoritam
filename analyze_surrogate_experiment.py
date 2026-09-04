from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon


ROOT_DIR = Path(__file__).parent
INPUT_CSV = ROOT_DIR / "results" / "surrogate_results.csv"
OUTPUT_CSV = ROOT_DIR / "results" / "surrogate_wilcoxon.csv"
FIELDNAMES = [
    "dataset", "lambda", "pop_size", "pm", "n_pairs", "ga_wins",
    "ties", "random_wins", "ga_median_fitness", "random_median_fitness",
    "median_difference", "p_value_one_sided", "p_value_holm",
    "significant_0_05_holm", "ga_mean_hit_rate", "random_mean_hit_rate",
    "ga_mean_seconds", "random_mean_seconds",
]


def _holm_adjust(p_values: list[float]) -> list[float]:
    count = len(p_values)
    order = np.argsort(p_values)
    adjusted = np.empty(count)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (count - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Najpre pokrenite eksperiment: {INPUT_CSV}")
    grouped = defaultdict(lambda: defaultdict(dict))
    with INPUT_CSV.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            group = (
                row["dataset"], float(row["lambda"]),
                int(row["pop_size"]), float(row["pm"]),
            )
            grouped[group][int(row["seed"])][row["method"]] = row

    results = []
    for group, seeds in sorted(grouped.items()):
        pairs = [methods for methods in seeds.values() if {"ga", "random"} <= methods.keys()]
        ga = np.array([float(pair["ga"]["best_fitness"]) for pair in pairs])
        random = np.array([float(pair["random"]["best_fitness"]) for pair in pairs])
        differences = ga - random
        p_value = (
            1.0 if np.all(differences == 0.0)
            else float(wilcoxon(ga, random, alternative="less").pvalue)
        )
        dataset, lam, pop_size, pm = group
        results.append({
            "dataset": dataset, "lambda": lam, "pop_size": pop_size, "pm": pm,
            "n_pairs": len(pairs), "ga_wins": int(np.sum(differences < 0)),
            "ties": int(np.sum(differences == 0)),
            "random_wins": int(np.sum(differences > 0)),
            "ga_median_fitness": float(np.median(ga)),
            "random_median_fitness": float(np.median(random)),
            "median_difference": float(np.median(differences)),
            "p_value_one_sided": p_value,
            "ga_mean_hit_rate": float(np.mean([float(pair["ga"]["cache_hit_rate"]) for pair in pairs])),
            "random_mean_hit_rate": float(np.mean([float(pair["random"]["cache_hit_rate"]) for pair in pairs])),
            "ga_mean_seconds": float(np.mean([float(pair["ga"]["elapsed_seconds"]) for pair in pairs])),
            "random_mean_seconds": float(np.mean([float(pair["random"]["elapsed_seconds"]) for pair in pairs])),
        })

    adjusted = _holm_adjust([row["p_value_one_sided"] for row in results])
    for row, value in zip(results, adjusted):
        row["p_value_holm"] = value
        row["significant_0_05_holm"] = value < 0.05
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)
    significant = sum(row["significant_0_05_holm"] for row in results)
    print(f"Sacuvano {len(results)} poredjenja u {OUTPUT_CSV}.")
    print(f"GA je znacajno bolji u {significant}/{len(results)} poredjenja (Holm, alpha=0.05).")


if __name__ == "__main__":
    main()
