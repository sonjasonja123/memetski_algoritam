from __future__ import annotations

import multiprocessing as mp
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import common

# --- Sta se sweep-uje (visi opseg verovatnoce mutacije) ---
MUTATION_RATES = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]

# --- Fiksni parametri ---
DATASETS = ["port1", "port2", "port3", "port4", "port5"]
LAMBDAS = [0.1, 0.3, 0.5, 0.7, 0.9]
OTHER_DATASET_LAMBDAS = [0.5]
PORT5_N_SEEDS = 30
OTHER_DATASETS_N_SEEDS = 10
NUM_WORKERS = None

K = 10
POP_SIZE = 100
N_GENERATIONS = 15
PC = 0.8
ELITISM = 1
TOURNAMENT_SIZE = 2
EPS = 0.01
DELTA = 0.15

RESULTS_DIR = Path(__file__).resolve().parent
RAW_CSV = RESULTS_DIR / "results.csv"
ERROR_LOG = RESULTS_DIR / "errors.log"
FIELDNAMES = [
    "dataset", "lambda", "pm", "seed", "best_fitness", "return", "std",
    "pe_percent", "n_evaluations", "n_cache_hits", "elapsed_seconds",
]


def _run_task(task: tuple[float, float, int]) -> dict:
    lam, pm, seed = task
    try:
        metrics = common.score_ga(
            dict(k=K, lam=lam, pop_size=POP_SIZE, n_generations=N_GENERATIONS,
                 pc=PC, pm=pm, elitism=ELITISM, tournament_size=TOURNAMENT_SIZE,
                 eps=EPS, delta=DELTA),
            seed,
        )
        return {
            "ok": True, "dataset": common.current_dataset(), "lambda": lam,
            "pm": pm, "seed": seed, **metrics,
        }
    except Exception:
        return {
            "ok": False, "dataset": common.current_dataset(), "lambda": lam,
            "pm": pm, "seed": seed, "error": traceback.format_exc(),
        }


def _key(row: dict) -> tuple[str, float, float, int]:
    return (row["dataset"], float(row["lambda"]), float(row["pm"]), int(row["seed"]))


def _format_error(result: dict) -> str:
    return (
        f"\n--- {result['dataset']} lambda={result['lambda']} pm={result['pm']} "
        f"seed={result['seed']} ---\n{result['error']}\n"
    )


def main() -> None:
    datasets_to_run = common.env_list("PM_DATASETS", DATASETS, str)
    mutation_rates = common.env_list("PM_VALUES", MUTATION_RATES, float)
    n_seeds_override = common.env_int("PM_N_SEEDS", None)
    workers = common.env_int("PM_WORKERS", NUM_WORKERS)

    def build_tasks(dataset_name, completed):
        lambdas = common.env_list(
            "PM_LAMBDAS", LAMBDAS if dataset_name == "port5" else OTHER_DATASET_LAMBDAS, float,
        )
        n_seeds = n_seeds_override if n_seeds_override is not None else (
            PORT5_N_SEEDS if dataset_name == "port5" else OTHER_DATASETS_N_SEEDS
        )
        return [
            (lam, pm, seed)
            for lam in lambdas for pm in mutation_rates for seed in range(1, n_seeds + 1)
            if (dataset_name, lam, pm, seed) not in completed
        ]

    common.run_experiment(
        datasets_to_run=datasets_to_run, data_dir=common.DATA_DIR,
        csv_path=RAW_CSV, fieldnames=FIELDNAMES, error_log_path=ERROR_LOG,
        build_tasks=build_tasks, run_task=_run_task, key_fn=_key,
        format_error=_format_error, workers=workers, label="Sweep pm (visok opseg)",
    )


if __name__ == "__main__":
    mp.freeze_support()
    main()
