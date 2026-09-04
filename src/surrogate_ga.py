from __future__ import annotations

import time
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from crossover import uniform_crossover
from repair import random_repair


@dataclass(frozen=True)
class SurrogateGAConfig:
    k: int = 10
    lam: float = 0.5
    pop_size: int = 10
    n_generations: int = 100
    pc: float = 0.8
    pm: float = 0.15
    elitism: int = 1
    tournament_size: int = 2
    seed: int | None = None


@dataclass
class SearchResult:
    best_selected: tuple[int, ...]
    best_fitness: float
    n_requests: int
    n_evaluations: int
    n_cache_hits: int
    elapsed_seconds: float

    @property
    def cache_hit_rate(self) -> float:
        return self.n_cache_hits / self.n_requests if self.n_requests else 0.0


def surrogate_fitness(
    selected_assets: tuple[int, ...],
    mu: np.ndarray,
    cov: np.ndarray,
    lam: float,
) -> float:
    """Original objective evaluated with equal (1/k) selected-asset weights."""
    selected = np.asarray(selected_assets, dtype=int)
    if selected.size == 0:
        raise ValueError("selected_assets ne sme biti prazan")
    weight = 1.0 / selected.size
    variance = weight * weight * float(cov[np.ix_(selected, selected)].sum())
    expected_return = weight * float(mu[selected].sum())
    return lam * variance - (1.0 - lam) * expected_return


class SurrogateEvaluator:
    """Per-run LRU cache and counters for the deterministic surrogate."""

    def __init__(self, mu: np.ndarray, cov: np.ndarray, lam: float):
        self.mu = mu
        self.cov = cov
        self.lam = float(lam)
        self.n_requests = 0

        @lru_cache(maxsize=None)
        def cached(selected_assets: tuple[int, ...], lam_key: float) -> float:
            return surrogate_fitness(selected_assets, self.mu, self.cov, lam_key)

        self._cached = cached

    def evaluate(self, chromosome: np.ndarray) -> float:
        self.n_requests += 1
        selected = tuple(np.flatnonzero(chromosome).tolist())
        return self._cached(selected, self.lam)

    @property
    def n_evaluations(self) -> int:
        return self._cached.cache_info().misses

    @property
    def n_cache_hits(self) -> int:
        return self._cached.cache_info().hits


def _validate(n_assets: int, config: SurrogateGAConfig) -> None:
    if not 1 <= config.k <= n_assets:
        raise ValueError("k mora biti između 1 i broja asseta")
    if config.pop_size < 2:
        raise ValueError("pop_size mora biti najmanje 2")
    if config.n_generations < 0:
        raise ValueError("n_generations ne sme biti negativan")
    if not 0 <= config.lam <= 1 or not 0 <= config.pc <= 1 or not 0 <= config.pm <= 1:
        raise ValueError("lam, pc i pm moraju biti u opsegu [0, 1]")
    if not 0 <= config.elitism < config.pop_size:
        raise ValueError("elitism mora biti u opsegu [0, pop_size)")
    if not 1 <= config.tournament_size <= config.pop_size:
        raise ValueError("tournament_size mora biti u opsegu [1, pop_size]")


def _random_chromosome(n: int, k: int, rng: np.random.Generator) -> np.ndarray:
    chromosome = np.zeros(n, dtype=np.int8)
    chromosome[rng.choice(n, size=k, replace=False)] = 1
    return chromosome


def _tournament(
    population: list[np.ndarray],
    fitness: list[float],
    size: int,
    rng: np.random.Generator,
) -> np.ndarray:
    candidates = rng.choice(len(population), size=size, replace=False)
    return population[min(candidates, key=lambda index: fitness[index])].copy()


def _swap_mutation(chromosome: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    child = chromosome.copy()
    selected = np.flatnonzero(child)
    unselected = np.flatnonzero(child == 0)
    child[rng.choice(selected)] = 0
    child[rng.choice(unselected)] = 1
    return child


def _result(
    best: np.ndarray,
    best_fitness: float,
    evaluator: SurrogateEvaluator,
    started: float,
) -> SearchResult:
    return SearchResult(
        best_selected=tuple(np.flatnonzero(best).tolist()),
        best_fitness=float(best_fitness),
        n_requests=evaluator.n_requests,
        n_evaluations=evaluator.n_evaluations,
        n_cache_hits=evaluator.n_cache_hits,
        elapsed_seconds=time.perf_counter() - started,
    )


def run_surrogate_ga(
    cov: np.ndarray, mu: np.ndarray, config: SurrogateGAConfig
) -> SearchResult:
    _validate(len(mu), config)
    started = time.perf_counter()
    rng = np.random.default_rng(config.seed)
    evaluator = SurrogateEvaluator(mu, cov, config.lam)
    population = [
        _random_chromosome(len(mu), config.k, rng) for _ in range(config.pop_size)
    ]
    fitness = [evaluator.evaluate(chromosome) for chromosome in population]

    for _ in range(config.n_generations):
        elite_indices = np.argsort(fitness)[: config.elitism]
        next_population = [population[index].copy() for index in elite_indices]
        next_fitness = [fitness[index] for index in elite_indices]
        while len(next_population) < config.pop_size:
            parent1 = _tournament(
                population, fitness, config.tournament_size, rng
            )
            parent2 = _tournament(
                population, fitness, config.tournament_size, rng
            )
            child = (
                uniform_crossover(parent1, parent2, rng)
                if rng.random() < config.pc
                else parent1.copy()
            )
            if int(child.sum()) != config.k:
                child = random_repair(child, config.k, rng)
            if rng.random() < config.pm:
                child = _swap_mutation(child, rng)
            next_population.append(child)
            next_fitness.append(evaluator.evaluate(child))
        population, fitness = next_population, next_fitness

    best_index = int(np.argmin(fitness))
    return _result(population[best_index], fitness[best_index], evaluator, started)


def run_random_search(
    cov: np.ndarray, mu: np.ndarray, config: SurrogateGAConfig
) -> SearchResult:
    """Random control with exactly the same number of candidate requests as GA."""
    _validate(len(mu), config)
    started = time.perf_counter()
    rng = np.random.default_rng(config.seed)
    evaluator = SurrogateEvaluator(mu, cov, config.lam)
    budget = config.pop_size + config.n_generations * (
        config.pop_size - config.elitism
    )
    best = None
    best_fitness = np.inf
    for _ in range(budget):
        candidate = _random_chromosome(len(mu), config.k, rng)
        fitness = evaluator.evaluate(candidate)
        if fitness < best_fitness:
            best, best_fitness = candidate, fitness
    assert best is not None
    return _result(best, best_fitness, evaluator, started)


if __name__ == "__main__":
    from data_loader import load_all

    data = load_all()["port1"]
    test_config = SurrogateGAConfig(pop_size=10, n_generations=5, seed=42)
    ga = run_surrogate_ga(data.cov, data.mu, test_config)
    random = run_random_search(data.cov, data.mu, test_config)
    expected_budget = 10 + 5 * 9
    assert ga.n_requests == random.n_requests == expected_budget
    assert len(ga.best_selected) == len(random.best_selected) == test_config.k
    direct = surrogate_fitness(ga.best_selected, data.mu, data.cov, test_config.lam)
    assert np.isclose(direct, ga.best_fitness)
    print("Sanity-check za surogat GA i random search je prosao.")
