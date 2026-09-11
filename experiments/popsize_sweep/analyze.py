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
BASELINE_POP_SIZE = 50
FIELDNAMES = [
    "dataset", "lambda", "pop_size", "baseline_pop_size", "n_pairs",
    "mean_pe_percent", "median_pe_percent", "baseline_mean_pe_percent", "baseline_median_pe_percent",
    "mean_elapsed_seconds", "baseline_mean_elapsed_seconds", "mean_n_evaluations", "baseline_mean_n_evaluations",
    "median_fitness_difference", "p_value_two_sided", "p_value_holm", "significant_0_05_holm",
]


def _metric(rows: list[dict], name: str, function) -> float:
    return float(function([float(row[name]) for row in rows]))


def _write_findings(rows: list[dict]) -> None:
    lines = [
        "# Sweep veličine populacije", "",
        "Poređenja su uparena po istom semenu. Wilcoxon test je dvostrani; Holm korekcija je primenjena na tri poređenja sa populacijom 50 unutar svakog para skupa i λ.", "",
    ]
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["dataset"], row["lambda"])].append(row)
    for (dataset, lam), comparisons in sorted(grouped.items()):
        lines.extend([f"## {dataset}, λ={lam}", "", "| Populacija | PE prosečno | PE medijana | Vreme prosečno (s) | Δ medijan fitnessa prema 50 | p (Holm) | Značajno |", "|---:|---:|---:|---:|---:|---:|:---:|"])
        for row in sorted(comparisons, key=lambda value: int(value["pop_size"])):
            lines.append(f"| {row['pop_size']} | {float(row['mean_pe_percent']):.4f} | {float(row['median_pe_percent']):.4f} | {float(row['mean_elapsed_seconds']):.3f} | {float(row['median_fitness_difference']):.8f} | {float(row['p_value_holm']):.4g} | {'da' if row['significant_0_05_holm'] else 'ne'} |")
        lines.append("")
    FINDINGS_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Najpre pokrenite eksperiment: {INPUT_CSV}")
    grouped = defaultdict(lambda: defaultdict(dict))
    with INPUT_CSV.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            grouped[(row["dataset"], float(row["lambda"]))][int(row["pop_size"])][int(row["seed"])] = row
    results = []
    for (dataset, lam), by_pop_size in sorted(grouped.items()):
        baseline_by_seed = by_pop_size.get(BASELINE_POP_SIZE)
        if not baseline_by_seed:
            print(f"[preskacem] {dataset}, lambda={lam}: nedostaje kontrola sa populacijom {BASELINE_POP_SIZE}")
            continue
        baseline_rows = list(baseline_by_seed.values())
        family = []
        for pop_size, values_by_seed in sorted(by_pop_size.items()):
            if pop_size <= BASELINE_POP_SIZE:
                continue
            paired_seeds = sorted(set(values_by_seed) & set(baseline_by_seed))
            current = [values_by_seed[seed] for seed in paired_seeds]
            baseline = [baseline_by_seed[seed] for seed in paired_seeds]
            current_fitness = np.array([float(row["best_fitness"]) for row in current])
            baseline_fitness = np.array([float(row["best_fitness"]) for row in baseline])
            differences = current_fitness - baseline_fitness
            p_value = 1.0 if not len(differences) or np.all(differences == 0.0) else float(wilcoxon(current_fitness, baseline_fitness, alternative="two-sided").pvalue)
            family.append({
                "dataset": dataset, "lambda": lam, "pop_size": pop_size, "baseline_pop_size": BASELINE_POP_SIZE, "n_pairs": len(paired_seeds),
                "mean_pe_percent": _metric(current, "pe_percent", np.mean), "median_pe_percent": _metric(current, "pe_percent", np.median),
                "baseline_mean_pe_percent": _metric(baseline_rows, "pe_percent", np.mean), "baseline_median_pe_percent": _metric(baseline_rows, "pe_percent", np.median),
                "mean_elapsed_seconds": _metric(current, "elapsed_seconds", np.mean), "baseline_mean_elapsed_seconds": _metric(baseline_rows, "elapsed_seconds", np.mean),
                "mean_n_evaluations": _metric(current, "n_evaluations", np.mean), "baseline_mean_n_evaluations": _metric(baseline_rows, "n_evaluations", np.mean),
                "median_fitness_difference": float(np.median(differences)), "p_value_two_sided": p_value,
            })
        adjusted = common.holm_adjust([row["p_value_two_sided"] for row in family])
        for row, value in zip(family, adjusted):
            row["p_value_holm"] = value
            row["significant_0_05_holm"] = value < 0.05
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
