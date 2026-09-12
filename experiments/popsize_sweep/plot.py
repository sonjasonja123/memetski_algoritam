from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent
INPUT_CSV = RESULTS_DIR / "results.csv"
OUTPUT_PNG = RESULTS_DIR / "popsize_sweep.png"

DATASET_LABELS = {
    "port1": "Hang Seng",
    "port2": "DAX 100",
    "port3": "FTSE 100",
    "port4": "S&P 100",
    "port5": "Nikkei 225",
}

REQUIRED_COLUMNS = {"dataset", "pop_size", "pe_percent"}


def main() -> None:
    if not INPUT_CSV.exists():
        print(f"Nema fajla {INPUT_CSV} - prvo pokreni run.py i analyze.py.")
        sys.exit(1)

    df = pd.read_csv(INPUT_CSV)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        print(f"Nedostaju ocekivane kolone u {INPUT_CSV}: {sorted(missing)}. Stvarne kolone: {list(df.columns)}")
        sys.exit(1)

    print(f"Dataset-i prisutni u {INPUT_CSV.name}: {sorted(df['dataset'].unique())}")

    plt.rcParams["font.size"] = 10
    fig, ax = plt.subplots(figsize=(8, 5.5))

    for dataset in sorted(df["dataset"].unique()):
        subset = df[df["dataset"] == dataset]
        grouped = subset.groupby("pop_size")["pe_percent"].agg(["mean", "std"]).sort_index()
        ax.errorbar(
            grouped.index, grouped["mean"], yerr=grouped["std"],
            marker="o", capsize=3, label=DATASET_LABELS.get(dataset, dataset),
        )

    ax.set_title("Uticaj velicine populacije na PE, po skupu podataka")
    ax.set_xlabel("Velicina populacije")
    ax.set_ylabel("PE (%)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    fig.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Sacuvano: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
