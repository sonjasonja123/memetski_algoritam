
















from __future__ import annotations

import numpy as np
from scipy.optimize import minimize


def solve_weights(
    cov: np.ndarray,
    mu: np.ndarray,
    selected: np.ndarray,
    lam: float,
    eps: float | np.ndarray = 0.0,
    delta: float | np.ndarray = 1.0,
    w0: np.ndarray | None = None,
) -> tuple[np.ndarray, float, bool]:



















    n = cov.shape[0]
    k = len(selected)

    sub_cov = cov[np.ix_(selected, selected)]
    sub_mu = mu[selected]

    eps_arr = np.full(k, eps, dtype=float) if np.isscalar(eps) else np.asarray(eps, dtype=float)
    delta_arr = np.full(k, delta, dtype=float) if np.isscalar(delta) else np.asarray(delta, dtype=float)

    if eps_arr.sum() > 1.0 + 1e-9 or delta_arr.sum() < 1.0 - 1e-9:

        w_full = np.zeros(n)
        return w_full, np.inf, False

    def objective(w):
        risk = w @ sub_cov @ w
        ret = sub_mu @ w
        return lam * risk - (1.0 - lam) * ret

    def objective_grad(w):
        return 2.0 * lam * (sub_cov @ w) - (1.0 - lam) * sub_mu

    constraints = [{"type": "eq", "fun": lambda w: w.sum() - 1.0, "jac": lambda w: np.ones(k)}]
    bounds = list(zip(eps_arr, delta_arr))

    if w0 is None:
                                                                      
        free = 1.0 - eps_arr.sum()
        w0 = eps_arr + free / k

    result = minimize(
        objective,
        w0,
        jac=objective_grad,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 200, "ftol": 1e-12},
    )

    w_full = np.zeros(n)
    w_full[selected] = np.clip(result.x, eps_arr, delta_arr)
                                                                        
    s = w_full[selected].sum()
    if s > 0:
        w_full[selected] = w_full[selected] / s

    obj_value = objective(w_full[selected])
    return w_full, obj_value, result.success


if __name__ == "__main__":
    datasets = load_all()
    d = datasets["port1"]

    rng = np.random.default_rng(42)
    k = 10
    selected = rng.choice(d.n_assets, size=k, replace=False)
    selected.sort()

    print(f"Dataset: {d.label} (N={d.n_assets}), K={k}")
    print(f"Izabrani asseti (0-indeksirano): {selected}")
    print()
    print(f"{'lambda':>8} {'risk (var)':>12} {'return':>10} {'objective':>12} {'success':>8}")

    for lam in [0.0, 0.25, 0.5, 0.75, 1.0]:
        w, obj, ok = solve_weights(d.cov, d.mu, selected, lam)
        risk = w @ d.cov @ w
        ret = d.mu @ w
        print(f"{lam:>8.2f} {risk:>12.6f} {ret:>10.6f} {obj:>12.6f} {str(ok):>8}")
        assert abs(w.sum() - 1.0) < 1e-6, "sum(w) mora biti 1"
        assert (w[selected] >= -1e-9).all(), "w_i mora biti >= 0"
        assert (w[~np.isin(np.arange(d.n_assets), selected)] == 0).all(), "neizabrani w_i moraju biti 0"

    print("\nSvi testovi prošli (sum=1, w>=0, w=0 van izabranog skupa).")
