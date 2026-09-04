from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent / "src"))
DATA_DIR = Path(__file__).parent / "data"

from data_loader import load_all
from memetic_ga import GAConfig, run_memetic_ga


DATASETS = ["port1", "port2", "port3", "port4", "port5"]
K = 10                 
LAMBDA = 0.5            
POP_SIZE = 50
N_GENERATIONS = 100
N_SEEDS = 5            

OUTPUT_CSV = Path(__file__).parent / "results" / "core_experiment.csv"

def main():
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    datasets = load_all(DATA_DIR)

    rows = []
    t_start = time.time()

    print("=" * 70)
    print("CORE memetski algoritam (tacno memetic.md, bez ekstenzija)")
    print(f"K={K}, lambda={LAMBDA}, pop_size={POP_SIZE}, "
          f"n_generations={N_GENERATIONS}, n_seeds={N_SEEDS}")
    print("=" * 70)
    print()

    for ds_name in DATASETS:
        if ds_name not in datasets:
            print(f"[preskačem] {ds_name} nije pronađen u {DATA_DIR}")
            continue
        d = datasets[ds_name]

        finals = []
        best_result = None

        for seed in range(1, N_SEEDS + 1):
            config = GAConfig(
                k=K,
                lam=LAMBDA,
                pop_size=POP_SIZE,
                n_generations=N_GENERATIONS,
                seed=seed,
                pc=0.8,
                pm=0.15,
                elitism=1,
                tournament_size=2,
                eps=0.01,
                delta=0.15,
            )
            t0 = time.time()
            result = run_memetic_ga(d.cov, d.mu, d.corr, config)
            elapsed = time.time() - t0

            finals.append(result.best_fitness)
            if best_result is None or result.best_fitness < best_result.best_fitness:
                best_result = result

            rows.append({
                "dataset": ds_name,
                "label": d.label,
                "n_assets": d.n_assets,
                "seed": seed,
                "best_fitness": result.best_fitness,
                "n_evaluations": result.n_evaluations,
                "elapsed_seconds": round(elapsed, 3),
            })

        finals = np.array(finals)
        selected_assets = np.where(best_result.best_z == 1)[0]

        print(f"--- {ds_name} ({d.label}, N={d.n_assets}) ---")
        print(f"  fitness preko {N_SEEDS} pokretanja: mean={finals.mean():.8f}  "
              f"std={finals.std():.8f}  best={finals.min():.8f}")
        print(f"  najbolji portfolio (asseti, 0-indeksirano): {selected_assets}")
        print(f"  tezine (samo nenulte):")
        for i in selected_assets:
            if best_result.best_w[i] > 1e-6:
                print(f"    asset {i:>3}: w = {best_result.best_w[i]:.4f}")
        print()

    print(f"Ukupno vreme: {time.time() - t_start:.1f}s")

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Rezultati sačuvani u: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
