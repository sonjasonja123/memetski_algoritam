from __future__ import annotations

import csv
import multiprocessing as mp
import os
import sys
import time
import traceback
from pathlib import Path


ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from data_loader import load_all
from surrogate_ga import SurrogateGAConfig, run_random_search, run_surrogate_ga


DATASETS = ["port1", "port2", "port3", "port4", "port5"]
LAMBDAS = [0.1, 0.3, 0.5, 0.7, 0.9]
POP_SIZES = [10, 15]
MUTATION_RATES = [0.10, 0.15, 0.20, 0.25, 0.30]
N_SEEDS = 30
N_GENERATIONS = 100
K = 10
PC = 0.8
ELITISM = 1
TOURNAMENT_SIZE = 2
NUM_WORKERS = None

RESULTS_DIR = ROOT_DIR / "results"
OUTPUT_CSV = RESULTS_DIR / "surrogate_results.csv"
ERROR_LOG = RESULTS_DIR / "surrogate_errors.log"
FIELDNAMES = [
    "dataset", "lambda", "pop_size", "pm", "seed", "method",
    "best_fitness", "selected_assets", "n_requests", "n_evaluations",
    "n_cache_hits", "cache_hit_rate", "elapsed_seconds",
]

_worker_data = None
_worker_dataset = None


def _init_worker(data, dataset: str) -> None:
    global _worker_data, _worker_dataset
    _worker_data, _worker_dataset = data, dataset


def _run_pair(task: tuple[float, int, float, int]) -> dict:
    lam, pop_size, pm, seed = task
    try:
        config = SurrogateGAConfig(
            k=K, lam=lam, pop_size=pop_size,
            n_generations=N_GENERATIONS, pc=PC, pm=pm,
            elitism=ELITISM, tournament_size=TOURNAMENT_SIZE, seed=seed,
        )
        ga = run_surrogate_ga(_worker_data.cov, _worker_data.mu, config)
        random = run_random_search(_worker_data.cov, _worker_data.mu, config)
        rows = []
        for method, result in (("ga", ga), ("random", random)):
            rows.append({
                "dataset": _worker_dataset,
                "lambda": lam,
                "pop_size": pop_size,
                "pm": pm,
                "seed": seed,
                "method": method,
                "best_fitness": result.best_fitness,
                "selected_assets": " ".join(map(str, result.best_selected)),
                "n_requests": result.n_requests,
                "n_evaluations": result.n_evaluations,
                "n_cache_hits": result.n_cache_hits,
                "cache_hit_rate": result.cache_hit_rate,
                "elapsed_seconds": result.elapsed_seconds,
            })
        return {"ok": True, "rows": rows}
    except Exception:
        return {
            "ok": False, "dataset": _worker_dataset, "lambda": lam,
            "pop_size": pop_size, "pm": pm, "seed": seed,
            "error": traceback.format_exc(),
        }


def _env_list(name: str, default: list, converter):
    value = os.getenv(name)
    return [converter(item.strip()) for item in value.split(",")] if value else default


def _settings():
    return (
        _env_list("SURROGATE_DATASETS", DATASETS, str),
        _env_list("SURROGATE_LAMBDAS", LAMBDAS, float),
        _env_list("SURROGATE_POP_SIZES", POP_SIZES, int),
        _env_list("SURROGATE_PM", MUTATION_RATES, float),
        int(os.getenv("SURROGATE_N_SEEDS", N_SEEDS)),
    )


def _key(row: dict) -> tuple[str, float, int, float, int, str]:
    return (
        row["dataset"], float(row["lambda"]), int(row["pop_size"]),
        float(row["pm"]), int(row["seed"]), row["method"],
    )


def _completed() -> set[tuple[str, float, int, float, int, str]]:
    if not OUTPUT_CSV.exists():
        return set()
    with OUTPUT_CSV.open(newline="", encoding="utf-8") as file:
        return {_key(row) for row in csv.DictReader(file)}


def _append_rows(rows: list[dict], write_header: bool) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with OUTPUT_CSV.open(
        "w" if write_header else "a", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
        file.flush()


def main() -> None:
    dataset_names, lambdas, pop_sizes, mutation_rates, n_seeds = _settings()
    data_by_name = load_all(ROOT_DIR / "data")
    completed = _completed()
    write_header = not OUTPUT_CSV.exists()
    workers = NUM_WORKERS or os.cpu_count() or 1
    successful = failed = 0
    started = time.perf_counter()

    print(f"Surogat eksperiment: {workers} procesa, {len(completed)} redova postoji.")
    for dataset_name in dataset_names:
        if dataset_name not in data_by_name:
            print(f"[preskacem] Nepoznat dataset: {dataset_name}")
            continue
        tasks = []
        for lam in lambdas:
            for pop_size in pop_sizes:
                for pm in mutation_rates:
                    for seed in range(1, n_seeds + 1):
                        keys = {
                            (dataset_name, lam, pop_size, pm, seed, "ga"),
                            (dataset_name, lam, pop_size, pm, seed, "random"),
                        }
                        if not keys.issubset(completed):
                            tasks.append((lam, pop_size, pm, seed))
        if not tasks:
            print(f"{dataset_name}: sve je vec zavrseno.")
            continue
        print(f"{dataset_name}: {len(tasks)} uparenih zadataka")
        with mp.Pool(
            workers, initializer=_init_worker,
            initargs=(data_by_name[dataset_name], dataset_name),
        ) as pool:
            for result in pool.imap_unordered(_run_pair, tasks, chunksize=4):
                if result["ok"]:
                    new_rows = [row for row in result["rows"] if _key(row) not in completed]
                    if new_rows:
                        _append_rows(new_rows, write_header)
                        write_header = False
                        completed.update(_key(row) for row in new_rows)
                    successful += 1
                else:
                    RESULTS_DIR.mkdir(exist_ok=True)
                    with ERROR_LOG.open("a", encoding="utf-8") as file:
                        file.write(str(result) + "\n")
                    failed += 1
    print(
        f"Gotovo za {time.perf_counter() - started:.1f}s: "
        f"{successful} uspesnih parova, {failed} neuspesnih."
    )


if __name__ == "__main__":
    mp.freeze_support()
    main()
