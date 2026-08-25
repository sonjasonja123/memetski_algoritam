from __future__ import annotations

import numpy as np


def _selected_indices(z: np.ndarray) -> np.ndarray:
    return np.where(z == 1)[0]


def random_repair(z: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:

    z = z.copy()
    selected = _selected_indices(z)
    if len(selected) > k:
        z[rng.choice(selected, size=len(selected) - k, replace=False)] = 0
    elif len(selected) < k:
        unselected = np.where(z == 0)[0]
        z[rng.choice(unselected, size=k - len(selected), replace=False)] = 1
    return z


if __name__ == "__main__":
    test_rng = np.random.default_rng(0)
    for selected_count in (3, 5, 8):
        chromosome = np.zeros(12, dtype=int)
        chromosome[:selected_count] = 1
        assert random_repair(chromosome, 5, test_rng).sum() == 5
    print("Sanity-check za random_repair je prošao.")
