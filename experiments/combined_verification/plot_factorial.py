from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

RESULTS_DIR = Path(__file__).resolve().parent
INPUT_CSV = RESULTS_DIR / "factorial_effects.csv"
OUTPUT_PNG = RESULTS_DIR / "factorial_effects.png"

REQUIRED_COLUMNS = {"lambda", "factor", "effect_size_pe_pp", "significant_0_05_holm"}


def main() -> None:
    if not INPUT_CSV.exists():
        print(f"Nema fajla {INPUT_CSV} - prvo pokreni analyze.py.")
        sys.exit(1)

    df = pd.read_csv(INPUT_CSV)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        print(f"Nedostaju ocekivane kolone u {INPUT_CSV}: {sorted(missing)}. Stvarne kolone: {list(df.columns)}")
        sys.exit(1)

    avg = df[df["lambda"] == "average"].copy()
    if avg.empty:
        print(f"Nema reda sa lambda='average' u {INPUT_CSV} - proveri strukturu fajla.")
        sys.exit(1)

    avg["abs_effect"] = avg["effect_size_pe_pp"].abs()
    avg = avg.sort_values("abs_effect", ascending=True).reset_index(drop=True)

    plt.rcParams["font.size"] = 10
    fig, ax = plt.subplots(figsize=(8, 5))

    colors = ["#d62728" if v > 0 else "#1f77b4" for v in avg["effect_size_pe_pp"]]
    alphas = [1.0 if sig else 0.4 for sig in avg["significant_0_05_holm"]]
    bars = ax.barh(range(len(avg)), avg["effect_size_pe_pp"], color=colors)
    for bar, alpha in zip(bars, alphas):
        bar.set_alpha(alpha)

    labels = [
        f"{factor} *" if sig else factor
        for factor, sig in zip(avg["factor"], avg["significant_0_05_holm"])
    ]
    ax.set_yticks(range(len(avg)))
    ax.set_yticklabels(labels)
    ax.axvline(0, color="black", lw=0.8)

    ax.set_title("2³ faktorijalni dizajn — glavni efekti i interakcije")
    ax.set_xlabel("Efekat na PE (procentni poeni)")
    ax.grid(alpha=0.3, axis="x")

    legend_handles = [
        mpatches.Patch(color="#1f77b4", label="Poboljsava PE"),
        mpatches.Patch(color="#d62728", label="Pogorsava PE"),
    ]
    ax.legend(handles=legend_handles, fontsize=8, loc="lower right")
    fig.text(
        0.01, 0.01, "* = statisticki znacajno (Holm, alpha=0.05); providniji bar = nije znacajno",
        fontsize=7, ha="left",
    )

    fig.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Sacuvano: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
