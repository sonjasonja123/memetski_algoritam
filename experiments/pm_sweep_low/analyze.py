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
BASELINE_PM = 0.10
FIELDNAMES = ["dataset", "lambda", "pm", "baseline_pm", "n_pairs", "mean_pe_percent", "median_pe_percent", "baseline_mean_pe_percent", "baseline_median_pe_percent", "mean_elapsed_seconds", "baseline_mean_elapsed_seconds", "median_fitness_difference", "p_value_two_sided", "p_value_holm", "significant_0_05_holm"]


def _metric(rows: list[dict], field: str, aggregate) -> float:
    return float(aggregate([float(row[field]) for row in rows]))


def _write_findings(rows: list[dict]) -> None:
    lines = ["# Sweep niske verovatnoće mutacije", "", "Poređenja su uparena po istom semenu sa referencom `pm=0.10`. Holm korekcija je primenjena unutar svakog para skupa i λ.", ""]
    grouped = defaultdict(list)
    for row in rows:
        grouped[(row["dataset"], row["lambda"])].append(row)
    for (dataset, lam), comparisons in sorted(grouped.items()):
        lines.extend([f"## {dataset}, λ={lam}", "", "| pm | PE prosečno | PE medijana | Vreme prosečno (s) | Δ medijan fitnessa prema 0.10 | p (Holm) | Značajno |", "|---:|---:|---:|---:|---:|---:|:---:|"])
        for row in sorted(comparisons, key=lambda value: float(value["pm"])):
            lines.append(f"| {float(row['pm']):.2f} | {float(row['mean_pe_percent']):.4f} | {float(row['median_pe_percent']):.4f} | {float(row['mean_elapsed_seconds']):.3f} | {float(row['median_fitness_difference']):.8f} | {float(row['p_value_holm']):.4g} | {'da' if row['significant_0_05_holm'] else 'ne'} |")
        lines.append("")
    if rows:
        global_pe = defaultdict(list)
        for row in rows:
            global_pe[float(row["pm"])].append(float(row["mean_pe_percent"]))
            global_pe[BASELINE_PM].append(float(row["baseline_mean_pe_percent"]))
        means = {pm: float(np.mean(values)) for pm, values in global_pe.items()}
        best_pm = min(means, key=means.get)
        lines.extend(["## Zbirni nalaz", "", "Prosečan PE preko svih dostupnih parova `(skup, λ)`:", "", "| pm | Prosečan PE (%) |", "|---:|---:|"])
        lines.extend(f"| {pm:.2f} | {value:.4f} |" for pm, value in sorted(means.items()))
        lines.extend(["", f"Najniži prosečan PE u ovom opsegu ima `pm={best_pm:.2f}` ({means[best_pm]:.4f}%)."])
    FINDINGS_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Najpre pokrenite eksperiment: {INPUT_CSV}")
    grouped = defaultdict(lambda: defaultdict(dict))
    with INPUT_CSV.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            grouped[(row["dataset"], float(row["lambda"]))][float(row["pm"])][int(row["seed"])] = row
    results = []
    for (dataset, lam), by_pm in sorted(grouped.items()):
        baseline_by_seed = by_pm.get(BASELINE_PM)
        if not baseline_by_seed:
            print(f"[preskacem] {dataset}, lambda={lam}: nedostaje pm={BASELINE_PM}")
            continue
        baseline_rows, family = list(baseline_by_seed.values()), []
        for pm, by_seed in sorted(by_pm.items()):
            if pm == BASELINE_PM:
                continue
            paired = sorted(set(by_seed) & set(baseline_by_seed))
            current, baseline = [by_seed[seed] for seed in paired], [baseline_by_seed[seed] for seed in paired]
            current_fitness = np.array([float(row["best_fitness"]) for row in current])
            baseline_fitness = np.array([float(row["best_fitness"]) for row in baseline])
            diff = current_fitness - baseline_fitness
            p_value = 1.0 if not len(diff) or np.all(diff == 0.0) else float(wilcoxon(current_fitness, baseline_fitness, alternative="two-sided").pvalue)
            family.append({"dataset": dataset, "lambda": lam, "pm": pm, "baseline_pm": BASELINE_PM, "n_pairs": len(paired), "mean_pe_percent": _metric(current, "pe_percent", np.mean), "median_pe_percent": _metric(current, "pe_percent", np.median), "baseline_mean_pe_percent": _metric(baseline_rows, "pe_percent", np.mean), "baseline_median_pe_percent": _metric(baseline_rows, "pe_percent", np.median), "mean_elapsed_seconds": _metric(current, "elapsed_seconds", np.mean), "baseline_mean_elapsed_seconds": _metric(baseline_rows, "elapsed_seconds", np.mean), "median_fitness_difference": float(np.median(diff)), "p_value_two_sided": p_value})
        for row, value in zip(family, common.holm_adjust([row["p_value_two_sided"] for row in family])):
            row["p_value_holm"], row["significant_0_05_holm"] = value, value < 0.05
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
