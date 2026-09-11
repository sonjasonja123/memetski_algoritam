"""Zajednička infrastruktura za sweep eksperimente nad memetskim GA.

Ovaj modul objedinjuje kod koji se, pre refaktorisanja, ponavljao skoro
identično u svih šest `run_*_experiment.py` skripti (CCEF, generations_sweep,
pm_sweep_high, pm_sweep_low, popsize_sweep, combined_verification):

- čitanje environment varijabli za ograničavanje opsega (obrazac
  `CCEF_DATASETS` iz `run_ccef_experiment.py`);
- multiprocessing.Pool orkestracija sa resume mehanizmom (incremental CSV
  upis, preskakanje već završenih kombinacija);
- standardni poziv GAConfig + run_memetic_ga + računanje PE metrike.

`run_surrogate_experiment.py` namerno NIJE prebačen na ovaj modul: koristi
drugačiju konfiguraciju (`SurrogateGAConfig`), drugačiji worker init (bez
uef/lambda) i vraća par (ga, random) redova po zadatku umesto jednog reda —
deljenje samo GAConfig+PE pomoćne funkcije mu ne odgovara. I dalje deli
matematiku Holm korekcije iz ovog modula.

Ne menja se logika GA/SLSQP poziva niti redosled random operacija u odnosu na
kod pre refaktorisanja — samo je premešten na jedno mesto.
"""

from __future__ import annotations

import csv
import multiprocessing as mp
import os
import sys
import time
import traceback
from pathlib import Path

import numpy as np

EXPERIMENTS_DIR = Path(__file__).resolve().parent
ROOT_DIR = EXPERIMENTS_DIR.parent
DATA_DIR = ROOT_DIR / "data"
RESULTS_ROOT = ROOT_DIR / "results"

sys.path.insert(0, str(ROOT_DIR / "src"))

from data_loader import load_all  # noqa: E402
from memetic_ga import GAConfig, run_memetic_ga  # noqa: E402
from uef_benchmark import load_all_uef, percentage_deviation_error  # noqa: E402

__all__ = [
    "DATA_DIR",
    "env_list",
    "env_int",
    "env_float",
    "load_all",
    "load_all_uef",
    "load_completed_keys",
    "append_row",
    "log_error",
    "run_experiment",
    "score_ga",
    "current_dataset",
    "holm_adjust",
]


# --- environment varijable za ograničavanje opsega (npr. za brzo testiranje) ---


def env_list(name: str, default: list, converter):
    value = os.getenv(name)
    return [converter(item.strip()) for item in value.split(",")] if value else default


def env_int(name: str, default: int | None) -> int | None:
    value = os.getenv(name)
    return int(value) if value else default


def env_float(name: str, default: float | None) -> float | None:
    value = os.getenv(name)
    return float(value) if value else default


# --- worker-lokalno stanje (po procesu, postavljeno kroz mp.Pool initializer) ---

_g_cov = None
_g_mu = None
_g_corr = None
_g_uef = None
_g_dataset = None


def init_worker(cov, mu, corr, uef, dataset) -> None:
    global _g_cov, _g_mu, _g_corr, _g_uef, _g_dataset
    _g_cov, _g_mu, _g_corr, _g_uef, _g_dataset = cov, mu, corr, uef, dataset


def current_dataset() -> str:
    return _g_dataset


def score_ga(ga_kwargs: dict, seed: int) -> dict:
    """Pokreće run_memetic_ga nad podacima trenutnog worker-a i vraća metrike.

    `ga_kwargs` su svi GAConfig parametri OSIM `seed` (koji sweep skripta
    prosleđuje po zadatku). Vraćeni rečnik ima tačno one kolone koje su bile
    zajedničke svim run_*_experiment.py skriptama pre refaktorisanja.
    """
    config = GAConfig(seed=seed, **ga_kwargs)
    result = run_memetic_ga(_g_cov, _g_mu, _g_corr, config)
    ret = float(_g_mu @ result.best_w)
    variance = float(result.best_w @ _g_cov @ result.best_w)
    std = float(np.sqrt(max(variance, 0.0)))
    pe = percentage_deviation_error(_g_uef, std, ret) if _g_uef else None
    return {
        "best_fitness": result.best_fitness,
        "return": ret,
        "std": std,
        "pe_percent": pe,
        "n_evaluations": result.n_evaluations,
        "n_cache_hits": result.n_cache_hits,
        "elapsed_seconds": round(result.elapsed_seconds, 3),
    }


# --- incremental CSV upis sa resume mehanizmom ---


def load_completed_keys(csv_path: Path, key_fn) -> set[tuple]:
    if not csv_path.exists():
        return set()
    with csv_path.open(newline="", encoding="utf-8") as file:
        return {key_fn(row) for row in csv.DictReader(file)}


def append_row(csv_path: Path, fieldnames: list[str], row: dict, write_header: bool) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w" if write_header else "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({name: row[name] for name in fieldnames})
        file.flush()


def log_error(error_log_path: Path, message: str) -> None:
    error_log_path.parent.mkdir(parents=True, exist_ok=True)
    with error_log_path.open("a", encoding="utf-8") as file:
        file.write(message)


# --- multiprocessing.Pool orkestracija preko liste (dataset, ...) zadataka ---


def run_experiment(
    *,
    datasets_to_run: list[str],
    data_dir: Path,
    csv_path: Path,
    fieldnames: list[str],
    error_log_path: Path,
    build_tasks,
    run_task,
    key_fn,
    format_error,
    workers: int | None = None,
    label: str = "Eksperiment",
) -> None:
    """Generički pokretač sweep eksperimenta.

    `build_tasks(dataset_name, completed) -> list[task]` pravi listu zadataka
    za jedan dataset, preskačući kombinacije već u `completed`.
    `run_task(task) -> dict` se izvršava u worker procesu (mora biti
    picklable, tj. definisana na nivou modula u run.py skripti) i vraća
    rečnik sa `"ok"` i ili poljima iz `fieldnames` ili `"error"`.
    `key_fn(row) -> tuple` i `format_error(result) -> str` su specifični za
    svaku skriptu (koje kolone čine jedinstven ključ kombinacije).
    """
    workers = workers or os.cpu_count() or 1
    datasets = load_all(data_dir)
    uef_curves = load_all_uef(data_dir)
    completed = load_completed_keys(csv_path, key_fn)
    write_header = not csv_path.exists()
    successful = failed = 0
    started = time.time()

    print(f"{label}: {workers} procesa, {len(completed)} zavrsenih zadataka.")
    for dataset_name in datasets_to_run:
        if dataset_name not in datasets:
            print(f"[preskacem] {dataset_name} nije pronadjen u {data_dir}")
            continue
        data = datasets[dataset_name]
        uef = uef_curves.get("portef" + dataset_name[4:])
        tasks = build_tasks(dataset_name, completed)
        if not tasks:
            print(f"{dataset_name}: svi zadaci su vec zavrseni.")
            continue
        print(f"{dataset_name}: {len(tasks)} zadataka")
        with mp.Pool(
            processes=workers, initializer=init_worker,
            initargs=(data.cov, data.mu, data.corr, uef, dataset_name),
        ) as pool:
            for result in pool.imap_unordered(run_task, tasks):
                if result["ok"]:
                    append_row(csv_path, fieldnames, result, write_header)
                    write_header = False
                    successful += 1
                else:
                    log_error(error_log_path, format_error(result))
                    failed += 1
                    print(f"[GRESKA] {format_error(result)}".splitlines()[0])

    print(
        f"Gotovo za {time.time() - started:.1f}s: {successful} uspesnih, "
        f"{failed} neuspesnih pokretanja."
    )


# --- Holm korekcija (deljena i sa analyze_surrogate_experiment.py) ---


def holm_adjust(p_values: list[float]) -> list[float]:
    count = len(p_values)
    order = np.argsort(p_values)
    adjusted = np.empty(count)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (count - rank) * p_values[index])
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


if __name__ == "__main__":
    # Sanity-check da modul ima ispravne putanje i da se `src` moduli uvoze.
    datasets = load_all(DATA_DIR)
    uef_curves = load_all_uef(DATA_DIR)
    assert "port1" in datasets and "portef1" in uef_curves
    print("experiments/common.py: osnovne putanje i uvozi rade.")
