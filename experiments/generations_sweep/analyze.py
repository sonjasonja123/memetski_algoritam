from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import common

RESULTS_DIR = Path(__file__).resolve().parent
INPUT_CSV = RESULTS_DIR / "results.csv"
OUTPUT_CSV = RESULTS_DIR / "wilcoxon.csv"
FINDINGS_MD = RESULTS_DIR / "FINDINGS.md"
BASELINE_GENERATIONS = 100
FIELDNAMES = [
    "dataset", "lambda", "n_generations", "baseline_generations", "n_pairs",
    "mean_pe_percent", "median_pe_percent", "baseline_mean_pe_percent", "baseline_median_pe_percent",
    "mean_elapsed_seconds", "baseline_mean_elapsed_seconds", "mean_n_evaluations", "baseline_mean_n_evaluations",
    "median_fitness_difference", "p_value_two_sided", "p_value_holm", "significant_0_05_holm",
]


def _mean(rows: list[dict], name: str) -> float:
    return float(np.mean([float(row[name]) for row in rows]))


def _median(rows: list[dict], name: str) -> float:
    return float(np.median([float(row[name]) for row in rows]))


def _write_findings(rows: list[dict]) -> None:
    lines = [
        "# Sweep broja generacija", "",
        "Poređenja su uparena po istom semenu. Wilcoxon test je dvostrani; Holm korekcija se primenjuje na četiri poređenja sa 100 generacija unutar svakog para skupa i λ.", "",
    ]
    by_pair = defaultdict(list)
    for row in rows:
        by_pair[(row["dataset"], row["lambda"])].append(row)
    for (dataset, lam), comparisons in sorted(by_pair.items()):
        lines.extend([
            f"## {dataset}, λ={lam}", "",
            "| Generacije | PE prosečno | PE medijana | Vreme prosečno (s) | Evaluacije prosečno | Δ medijan fitnessa prema 100 | p (Holm) | Značajno |",
            "|---:|---:|---:|---:|---:|---:|---:|:---:|",
        ])
        for row in sorted(comparisons, key=lambda value: int(value["n_generations"])):
            speedup = 100 * (1 - float(row["mean_elapsed_seconds"]) / float(row["baseline_mean_elapsed_seconds"])) if float(row["baseline_mean_elapsed_seconds"]) else 0.0
            lines.append(
                f"| {row['n_generations']} | {float(row['mean_pe_percent']):.4f} | {float(row['median_pe_percent']):.4f} | "
                f"{float(row['mean_elapsed_seconds']):.3f} ({speedup:.1f}% brže) | {float(row['mean_n_evaluations']):.1f} | "
                f"{float(row['median_fitness_difference']):.8f} | {float(row['p_value_holm']):.4g} | "
                f"{'da' if row['significant_0_05_holm'] else 'ne'} |"
            )
        lines.append("")
    FINDINGS_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Najpre pokrenite eksperiment: {INPUT_CSV}")
    grouped = defaultdict(lambda: defaultdict(dict))
    with INPUT_CSV.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            grouped[(row["dataset"], float(row["lambda"]))][int(row["n_generations"])][int(row["seed"])] = row

    results = []
    for (dataset, lam), by_generations in sorted(grouped.items()):
        baseline_by_seed = by_generations.get(BASELINE_GENERATIONS)
        if not baseline_by_seed:
            print(f"[preskacem] {dataset}, lambda={lam}: nedostaje kontrola od {BASELINE_GENERATIONS} generacija")
            continue
        baseline_rows = list(baseline_by_seed.values())
        family = []
        for n_generations, values_by_seed in sorted(by_generations.items()):
            if n_generations >= BASELINE_GENERATIONS:
                continue
            paired_seeds = sorted(set(values_by_seed) & set(baseline_by_seed))
            current_rows = [values_by_seed[seed] for seed in paired_seeds]
            paired_baseline = [baseline_by_seed[seed] for seed in paired_seeds]
            current_fitness = np.array([float(row["best_fitness"]) for row in current_rows])
            baseline_fitness = np.array([float(row["best_fitness"]) for row in paired_baseline])
            differences = current_fitness - baseline_fitness
            p_value = 1.0 if len(differences) == 0 or np.all(differences == 0.0) else float(wilcoxon(current_fitness, baseline_fitness, alternative="two-sided").pvalue)
            family.append({
                "dataset": dataset, "lambda": lam, "n_generations": n_generations,
                "baseline_generations": BASELINE_GENERATIONS, "n_pairs": len(paired_seeds),
                "mean_pe_percent": _mean(current_rows, "pe_percent"), "median_pe_percent": _median(current_rows, "pe_percent"),
                "baseline_mean_pe_percent": _mean(baseline_rows, "pe_percent"), "baseline_median_pe_percent": _median(baseline_rows, "pe_percent"),
                "mean_elapsed_seconds": _mean(current_rows, "elapsed_seconds"), "baseline_mean_elapsed_seconds": _mean(baseline_rows, "elapsed_seconds"),
                "mean_n_evaluations": _mean(current_rows, "n_evaluations"), "baseline_mean_n_evaluations": _mean(baseline_rows, "n_evaluations"),
                "median_fitness_difference": float(np.median(differences)), "p_value_two_sided": p_value,
            })
        adjusted = common.holm_adjust([row["p_value_two_sided"] for row in family])
        for row, p_value in zip(family, adjusted):
            row["p_value_holm"] = p_value
            row["significant_0_05_holm"] = p_value < 0.05
        results.extend(family)

    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)
    _write_findings(results)
    print(f"Sacuvano {len(results)} poredjenja u {OUTPUT_CSV} i {FINDINGS_MD}.")


if __name__ == "__main__":
    main()
