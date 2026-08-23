





from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from crossover import uniform_crossover
from local_search import solve_weights
from repair import random_repair


@dataclass
class GAConfig:
    k: int
    lam: float = 0.5
    pop_size: int = 50
    n_generations: int = 100
    pc: float = 0.8
    pm: float = 0.15
    elitism: int = 1
    tournament_size: int = 2
    eps: float = 0.01
    delta: float = 0.15
    seed: int | None = None


@dataclass
class GAResult:
    best_z: np.ndarray
    best_w: np.ndarray
    best_fitness: float
    history: list[float] = field(default_factory=list)
    n_evaluations: int = 0
    n_cache_hits: int = 0
    elapsed_seconds: float = 0.0


def _random_chromosome(n: int, k: int, rng: np.random.Generator) -> np.ndarray:
    z = np.zeros(n, dtype=int)
    z[rng.choice(n, size=k, replace=False)] = 1
    return z


def _tournament_select(
    population: list[np.ndarray], fitness: list[float], size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    idxs = rng.choice(len(population), size=size, replace=False)
    return population[min(idxs, key=lambda i: fitness[i])].copy()


def _swap_mutation(z: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    z = z.copy()
    selected = np.where(z == 1)[0]
    unselected = np.where(z == 0)[0]
    if len(selected) and len(unselected):
        z[rng.choice(selected)] = 0
        z[rng.choice(unselected)] = 1
    return z


def run_memetic_ga(
    cov: np.ndarray,
    mu: np.ndarray,
    corr: np.ndarray,
    config: GAConfig,
    verbose: bool = False,
) -> GAResult:

    del corr
    n = cov.shape[0]
    rng = np.random.default_rng(config.seed)
    t0 = time.time()
    n_evals = 0
    n_cache_hits = 0
    cache: dict[bytes, tuple[float, np.ndarray]] = {}

    def evaluate(z: np.ndarray) -> tuple[float, np.ndarray]:
        nonlocal n_evals, n_cache_hits
        key = z.tobytes()
        cached = cache.get(key)
        if cached is not None:
            n_cache_hits += 1
            return cached
        n_evals += 1
        selected = np.where(z == 1)[0]
        w, obj, _ = solve_weights(
            cov, mu, selected, config.lam, config.eps, config.delta
        )
        cache[key] = (obj, w)
        return obj, w

    population = [_random_chromosome(n, config.k, rng) for _ in range(config.pop_size)]
    evaluated = [evaluate(z) for z in population]
    fitness = [item[0] for item in evaluated]
    weights_cache = [item[1] for item in evaluated]
    history = [min(fitness)]

    for gen in range(config.n_generations):
        elite_idx = np.argsort(fitness)[:config.elitism]
        new_population = [population[i].copy() for i in elite_idx]
        new_fitness = [fitness[i] for i in elite_idx]
        new_weights = [weights_cache[i] for i in elite_idx]

        while len(new_population) < config.pop_size:
            parent1 = _tournament_select(population, fitness, config.tournament_size, rng)
            parent2 = _tournament_select(population, fitness, config.tournament_size, rng)
            child = (uniform_crossover(parent1, parent2, rng)
                     if rng.random() < config.pc else parent1.copy())
            if child.sum() != config.k:
                child = random_repair(child, config.k, rng)
            if rng.random() < config.pm:
                child = _swap_mutation(child, rng)

            f, w = evaluate(child)
            new_population.append(child)
            new_fitness.append(f)
            new_weights.append(w)

        population, fitness, weights_cache = new_population, new_fitness, new_weights
        history.append(min(fitness))
        if verbose and (gen + 1) % max(1, config.n_generations // 10) == 0:
            print(f"  gen {gen + 1:>4}/{config.n_generations}  best fitness = {min(fitness):.8f}")

    best_idx = int(np.argmin(fitness))
    return GAResult(
        best_z=population[best_idx], best_w=weights_cache[best_idx],
        best_fitness=fitness[best_idx], history=history,
        n_evaluations=n_evals, n_cache_hits=n_cache_hits,
        elapsed_seconds=time.time() - t0,
    )


if __name__ == "__main__":
    from data_loader import load_all

    data = load_all()["port1"]
    test_config = GAConfig(k=10, lam=0.5, seed=42)
    result = run_memetic_ga(data.cov, data.mu, data.corr, test_config, verbose=True)
    assert result.best_z.sum() == test_config.k
    assert abs(result.best_w.sum() - 1.0) < 1e-6
    assert result.history[-1] <= result.history[0]
    print("Sanity-check za memetski GA je prošao.")
