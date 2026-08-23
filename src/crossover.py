

from __future__ import annotations

import numpy as np


def uniform_crossover(
    p1: np.ndarray, p2: np.ndarray, rng: np.random.Generator
) -> np.ndarray:

    mask = rng.integers(0, 2, size=len(p1)).astype(bool)
    return np.where(mask, p1, p2)


if __name__ == "__main__":
    test_rng = np.random.default_rng(0)
    parent1 = np.zeros(12, dtype=int)
    parent2 = np.ones(12, dtype=int)
    child = uniform_crossover(parent1, parent2, test_rng)
    assert len(child) == len(parent1)
    assert np.all((child == 0) | (child == 1))
    print("Sanity-check za uniform_crossover je prošao.")
