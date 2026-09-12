from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent
INPUT_CSV = RESULTS_DIR / "results.csv"
OUTPUT_PNG = RESULTS_DIR / "ga_vs_random.png"

DATASET_LABELS = {
    "port1": "Hang Seng",
    "port2": "DAX 100",
    "port3": "FTSE 100",
    "port4": "S&P 100",
    "port5": "Nikkei 225",
}

REQUIRED_COLUMNS = {"dataset", "method", "best_fitness"}
GA_COLOR = "#1f77b4"
RANDOM_COLOR = "#7f7f7f"


def main() -> None:
    if not INPUT_CSV.exists():
        print(f"Nema fajla {INPUT_CSV} - prvo pokreni run.py.")
        sys.exit(1)

    df = pd.read_csv(INPUT_CSV)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        print(f"Nedostaju ocekivane kolone u {INPUT_CSV}: {sorted(missing)}. Stvarne kolone: {list(df.columns)}")
        sys.exit(1)

    datasets = sorted(df["dataset"].unique())
    print(f"Dataset-i: {datasets}, ukupno redova: {len(df)} (po dataset x metod: "
          f"{df.groupby(['dataset', 'method']).size().to_dict()})")

    plt.rcParams["font.size"] = 10
    fig, ax = plt.subplots(figsize=(9, 5.5))

    positions = range(1, len(datasets) + 1)
    for pos, dataset in zip(positions, datasets):
        ga_vals = df[(df["dataset"] == dataset) & (df["method"] == "ga")]["best_fitness"]
        random_vals = df[(df["dataset"] == dataset) & (df["method"] == "random")]["best_fitness"]

        ga_box = ax.boxplot(
            [ga_vals], positions=[pos - 0.2], widths=0.35, patch_artist=True, showfliers=False,
        )
        random_box = ax.boxplot(
            [random_vals], positions=[pos + 0.2], widths=0.35, patch_artist=True, showfliers=False,
        )
        for patch in ga_box["boxes"]:
            patch.set_facecolor(GA_COLOR)
        for patch in random_box["boxes"]:
            patch.set_facecolor(RANDOM_COLOR)

    ax.set_xticks(list(positions))
    ax.set_xticklabels([DATASET_LABELS.get(d, d) for d in datasets])
    ax.set_xlabel("Skup podataka")
    ax.set_ylabel("Surrogate fitness (manje je bolje)")
    ax.set_title("GA naspram random search — surrogate fitness (250 konfiguracija)")
    ax.grid(alpha=0.3, axis="y")

    legend_handles = [
        mpatches.Patch(facecolor=GA_COLOR, label="GA"),
        mpatches.Patch(facecolor=RANDOM_COLOR, label="Random search"),
    ]
    ax.legend(handles=legend_handles, fontsize=8)

    fig.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Sacuvano: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
