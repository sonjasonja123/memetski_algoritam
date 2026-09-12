from __future__ import annotations

import multiprocessing as mp
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import common

# --- Sta se testira: pun 2^3 faktorijalni dizajn (POP x GEN x PM), ---
# --- svaki faktor na 2 nivoa: "-" (original) naspram "+" (sweep pobednik) ---
# (naziv, pop_size, n_generations, pm)
#
# POP: "-"=50, "+"=100 | GEN: "-"=100, "+"=50 | PM: "-"=0.15, "+"=0.02
#
# `pop_only` (100, 15, 0.15) je istorijska konfiguracija iz ranije verzije
# ovog eksperimenta - koristi n_generations=15, sto NIJE ni "-" (100) ni "+"
# (50) nivo GEN faktora u ovom dizajnu. Namerno je NIJE diran (vec
# verifikovan rezultat), ali NIJE deo 2^3 kocke ispod - `pop_gen100` je
# prava POP+/GEN-/PM- konfiguracija koju faktorijalna analiza koristi.
CONFIGS = [
    ("baseline",       50, 100, 0.15),   # - - -
    ("pop_gen100",    100, 100, 0.15),   # + - -   (NOVO: pravi POP+ ugao kocke)
    ("gen_only",       50,  50, 0.15),   # - + -
    ("pm_only",        50, 100, 0.02),   # - - +   (NOVO)
    ("pop_gen",       100,  50, 0.15),   # + + -   (NOVO)
    ("pop_pm",        100, 100, 0.02),   # + - +   (NOVO)
    ("gen_pm",         50,  50, 0.02),   # - + +   (NOVO)
    ("combined_best", 100,  50, 0.02),   # + + +
    ("pop_only",      100,  15, 0.15),   # istorijsko, VAN kocke - videti napomenu gore
]

# --- Fiksni parametri ---
DATASETS = ["port5"]           # samo Nikkei - jedini skup gde je efekat pokazan
LAMBDAS = [0.1, 0.3, 0.5, 0.7, 0.9]
N_SEEDS = 30
NUM_WORKERS = None

K = 10
PC = 0.8
ELITISM = 1
TOURNAMENT_SIZE = 2
EPS = 0.01
DELTA = 0.15

RESULTS_DIR = Path(__file__).resolve().parent
RAW_CSV = RESULTS_DIR / "results.csv"
ERROR_LOG = RESULTS_DIR / "errors.log"
FIELDNAMES = [
    "config_name", "dataset", "lambda", "pop_size", "n_generations", "pm",
    "seed", "best_fitness", "return", "std", "pe_percent",
    "n_evaluations", "n_cache_hits", "elapsed_seconds",
]


def _run_task(task: tuple[str, float, int, int, float, int]) -> dict:
    config_name, lam, pop_size, n_gen, pm, seed = task
    try:
        metrics = common.score_ga(
            dict(k=K, lam=lam, pop_size=pop_size, n_generations=n_gen,
                 pc=PC, pm=pm, elitism=ELITISM, tournament_size=TOURNAMENT_SIZE,
                 eps=EPS, delta=DELTA),
            seed,
        )
        return {
            "ok": True, "config_name": config_name, "dataset": common.current_dataset(),
            "lambda": lam, "pop_size": pop_size, "n_generations": n_gen, "pm": pm,
            "seed": seed, **metrics,
        }
    except Exception:
        return {
            "ok": False, "config_name": config_name, "dataset": common.current_dataset(),
            "lambda": lam, "pop_size": pop_size, "n_generations": n_gen, "pm": pm,
            "seed": seed, "error": traceback.format_exc(),
        }


def _key(row: dict) -> tuple[str, str, float, int]:
    return (row["config_name"], row["dataset"], float(row["lambda"]), int(row["seed"]))


def _format_error(result: dict) -> str:
    return (
        f"\n--- {result['config_name']} {result['dataset']} lambda={result['lambda']} "
        f"seed={result['seed']} ---\n{result['error']}\n"
    )


def main() -> None:
    # Za brzi test pre punog obima: postavi promenljive okruzenja, npr.
    #   COMBVERIF_N_SEEDS=2 COMBVERIF_LAMBDAS=0.5 python experiments/combined_verification/run.py
    lambdas = common.env_list("COMBVERIF_LAMBDAS", LAMBDAS, float)
    n_seeds = common.env_int("COMBVERIF_N_SEEDS", N_SEEDS)
    configs_filter = common.env_list("COMBVERIF_CONFIGS", None, str)
    configs = [c for c in CONFIGS if c[0] in set(configs_filter)] if configs_filter else CONFIGS

    def build_tasks(dataset_name, completed):
        return [
            (config_name, lam, pop_size, n_gen, pm, seed)
            for config_name, pop_size, n_gen, pm in configs
            for lam in lambdas
            for seed in range(1, n_seeds + 1)
            if (config_name, dataset_name, lam, seed) not in completed
        ]

    print(f"Konfiguracije: {[c[0] for c in configs]}")
    common.run_experiment(
        datasets_to_run=DATASETS, data_dir=common.DATA_DIR,
        csv_path=RAW_CSV, fieldnames=FIELDNAMES, error_log_path=ERROR_LOG,
        build_tasks=build_tasks, run_task=_run_task, key_fn=_key,
        format_error=_format_error, workers=None, label="Kombinovana verifikacija",
    )


if __name__ == "__main__":
    mp.freeze_support()
    main()
