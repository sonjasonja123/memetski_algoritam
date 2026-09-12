from __future__ import annotations

import csv
import multiprocessing as mp
import os
import sys
import time
import traceback
from pathlib import Path

import numpy as np

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from data_loader import load_all
from memetic_ga import GAConfig, run_memetic_ga
from uef_benchmark import load_all_uef, percentage_deviation_error


DATASETS = ["port1", "port2", "port3", "port4", "port5"]
LAMBDAS = [0.1, 0.3, 0.5, 0.7, 0.9]
N_SEEDS = 30
NUM_WORKERS = None

K = 10
POP_SIZE = 50
N_GENERATIONS = 100
PC = 0.8
PM = 0.15
ELITISM = 1
TOURNAMENT_SIZE = 2
EPS = 0.01
DELTA = 0.15

DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
RAW_CSV = RESULTS_DIR / "ccef_results.csv"
BEST_CSV = RESULTS_DIR / "ccef_best.csv"
ERROR_LOG = RESULTS_DIR / "ccef_errors.log"
FIELDNAMES = [
    "dataset", "lambda", "seed", "best_fitness", "return", "std",
    "pe_percent", "n_evaluations", "n_cache_hits", "elapsed_seconds",
]

_g_cov = None
_g_mu = None
_g_corr = None
_g_uef = None
_g_dataset = None


def _init_worker(cov, mu, corr, uef, dataset):
    global _g_cov, _g_mu, _g_corr, _g_uef, _g_dataset
    _g_cov, _g_mu, _g_corr = cov, mu, corr
    _g_uef, _g_dataset = uef, dataset


def _run_task(task: tuple[float, int]) -> dict:
    lam, seed = task
    try:
        config = GAConfig(
            k=K, lam=lam, pop_size=POP_SIZE, n_generations=N_GENERATIONS,
            pc=PC, pm=PM, elitism=ELITISM,
            tournament_size=TOURNAMENT_SIZE, eps=EPS, delta=DELTA, seed=seed,
        )
        result = run_memetic_ga(_g_cov, _g_mu, _g_corr, config)
        ret = float(_g_mu @ result.best_w)
        variance = float(result.best_w @ _g_cov @ result.best_w)
        std = float(np.sqrt(max(variance, 0.0)))
        pe = percentage_deviation_error(_g_uef, std, ret) if _g_uef else None
        return {
            "ok": True, "dataset": _g_dataset, "lambda": lam, "seed": seed,
            "best_fitness": result.best_fitness, "return": ret, "std": std,
            "pe_percent": pe, "n_evaluations": result.n_evaluations,
            "n_cache_hits": result.n_cache_hits,
            "elapsed_seconds": round(result.elapsed_seconds, 3),
        }
    except Exception:
        return {
            "ok": False, "dataset": _g_dataset, "lambda": lam, "seed": seed,
            "error": traceback.format_exc(),
        }


def _selected_settings() -> tuple[list[str], list[float], int]:
    datasets = os.getenv("CCEF_DATASETS")
    lambdas = os.getenv("CCEF_LAMBDAS")
    n_seeds = int(os.getenv("CCEF_N_SEEDS", N_SEEDS))
    return (
        datasets.split(",") if datasets else DATASETS,
        [float(value) for value in lambdas.split(",")] if lambdas else LAMBDAS,
        n_seeds,
    )


def _load_completed_keys() -> set[tuple[str, float, int]]:
    if not RAW_CSV.exists():
        return set()
    with RAW_CSV.open(newline="", encoding="utf-8") as file:
        return {
            (row["dataset"], float(row["lambda"]), int(row["seed"]))
            for row in csv.DictReader(file)
        }


def _append_row(row: dict, write_header: bool) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with RAW_CSV.open("w" if write_header else "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow({name: row[name] for name in FIELDNAMES})
        file.flush()


def _log_error(result: dict) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with ERROR_LOG.open("a", encoding="utf-8") as file:
        file.write(
            f"\n--- {result['dataset']} lambda={result['lambda']} "
            f"seed={result['seed']} ---\n{result['error']}\n"
        )


def generate_best_csv() -> None:
    if not RAW_CSV.exists():
        return
    with RAW_CSV.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    best: dict[tuple[str, float], dict] = {}
    for row in rows:
        key = (row["dataset"], float(row["lambda"]))
        if key not in best or float(row["best_fitness"]) < float(best[key]["best_fitness"]):
            best[key] = row
    with BEST_CSV.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(best[key] for key in sorted(best))


def main() -> None:
    datasets_to_run, lambdas, n_seeds = _selected_settings()
    workers = NUM_WORKERS or os.cpu_count() or 1
    datasets = load_all(DATA_DIR)
    uef_curves = load_all_uef(DATA_DIR)
    completed = _load_completed_keys()
    write_header = not RAW_CSV.exists()
    successful = failed = 0
    started = time.time()

    print(f"CCEF eksperiment: {workers} procesa, {len(completed)} zavrsenih zadataka.")
    for dataset_name in datasets_to_run:
        if dataset_name not in datasets:
            print(f"[preskacem] {dataset_name} nije pronadjen u {DATA_DIR}")
            continue
        data = datasets[dataset_name]
        uef = uef_curves.get("portef" + dataset_name[4:])
        tasks = [
            (lam, seed) for lam in lambdas for seed in range(1, n_seeds + 1)
            if (dataset_name, lam, seed) not in completed
        ]
        if not tasks:
            print(f"{dataset_name}: svi zadaci su vec zavrseni.")
            continue
        print(f"{dataset_name}: {len(tasks)} zadataka")
        with mp.Pool(
            processes=workers, initializer=_init_worker,
            initargs=(data.cov, data.mu, data.corr, uef, dataset_name),
        ) as pool:
            for result in pool.imap_unordered(_run_task, tasks):
                if result["ok"]:
                    _append_row(result, write_header)
                    write_header = False
                    successful += 1
                else:
                    _log_error(result)
                    failed += 1
                    print(f"[GRESKA] {dataset_name}, lambda={result['lambda']}, seed={result['seed']}")

    generate_best_csv()
    print(
        f"Gotovo za {time.time() - started:.1f}s: {successful} uspesnih, "
        f"{failed} neuspesnih pokretanja."
    )


if __name__ == "__main__":
    mp.freeze_support()
    main()
