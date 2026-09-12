from __future__ import annotations

import multiprocessing as mp
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import common

# --- Sta se sweep-uje ---
N_GENERATIONS_VALUES = [10, 15, 25, 50, 100]

# --- Fiksni parametri ---
DATASETS = ["port1", "port2", "port3", "port4", "port5"]
LAMBDAS = [0.1, 0.3, 0.5, 0.7, 0.9]
N_SEEDS = 30
NUM_WORKERS = None

K = 10
POP_SIZE = 50
PC = 0.8
PM = 0.15
ELITISM = 1
TOURNAMENT_SIZE = 2
EPS = 0.01
DELTA = 0.15

RESULTS_DIR = Path(__file__).resolve().parent
RAW_CSV = RESULTS_DIR / "results.csv"
ERROR_LOG = RESULTS_DIR / "errors.log"
FIELDNAMES = [
    "dataset", "lambda", "n_generations", "seed", "best_fitness", "return", "std",
    "pe_percent", "n_evaluations", "n_cache_hits", "elapsed_seconds",
]


def _run_task(task: tuple[float, int, int]) -> dict:
    lam, n_generations, seed = task
    try:
        metrics = common.score_ga(
            dict(k=K, lam=lam, pop_size=POP_SIZE, n_generations=n_generations,
                 pc=PC, pm=PM, elitism=ELITISM, tournament_size=TOURNAMENT_SIZE,
                 eps=EPS, delta=DELTA),
            seed,
        )
        return {
            "ok": True, "dataset": common.current_dataset(), "lambda": lam,
            "n_generations": n_generations, "seed": seed, **metrics,
        }
    except Exception:
        return {
            "ok": False, "dataset": common.current_dataset(), "lambda": lam,
            "n_generations": n_generations, "seed": seed, "error": traceback.format_exc(),
        }


def _key(row: dict) -> tuple[str, float, int, int]:
    return (row["dataset"], float(row["lambda"]), int(row["n_generations"]), int(row["seed"]))


def _format_error(result: dict) -> str:
    return (
        f"\n--- {result['dataset']} lambda={result['lambda']} "
        f"generations={result['n_generations']} seed={result['seed']} ---\n"
        f"{result['error']}\n"
    )


def main() -> None:
    datasets_to_run = common.env_list("GENSWEEP_DATASETS", DATASETS, str)
    lambdas = common.env_list("GENSWEEP_LAMBDAS", LAMBDAS, float)
    generations = common.env_list("GENSWEEP_GENERATIONS", N_GENERATIONS_VALUES, int)
    n_seeds = common.env_int("GENSWEEP_N_SEEDS", N_SEEDS)
    workers = common.env_int("GENSWEEP_WORKERS", NUM_WORKERS)

    def build_tasks(dataset_name, completed):
        return [
            (lam, n_gen, seed)
            for lam in lambdas for n_gen in generations for seed in range(1, n_seeds + 1)
            if (dataset_name, lam, n_gen, seed) not in completed
        ]

    common.run_experiment(
        datasets_to_run=datasets_to_run, data_dir=common.DATA_DIR,
        csv_path=RAW_CSV, fieldnames=FIELDNAMES, error_log_path=ERROR_LOG,
        build_tasks=build_tasks, run_task=_run_task, key_fn=_key,
        format_error=_format_error, workers=workers, label="Sweep generacija",
    )


if __name__ == "__main__":
    mp.freeze_support()
    main()
