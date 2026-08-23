from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from pathlib import Path


DATASET_NAMES = {
    "port1": "Hang Seng",
    "port2": "DAX 100",
    "port3": "FTSE 100",
    "port4": "S&P 100",
    "port5": "Nikkei 225",
}


@dataclass
class PortfolioData:


    name: str                        
    label: str                           
    n_assets: int         
    mu: np.ndarray                             
    sigma_i: np.ndarray                                                       
    corr: np.ndarray                                            
    cov: np.ndarray                                                                

    def __repr__(self) -> str:
        return (
            f"PortfolioData(name={self.name!r}, label={self.label!r}, "
            f"n_assets={self.n_assets})"
        )


def load_port_file(path: str | Path) -> PortfolioData:

    path = Path(path)
                                                                      
                                                                        
    tokens = path.read_text().split()

    idx = 0
    n = int(tokens[idx]); idx += 1

    mu = np.empty(n, dtype=float)
    sigma_i = np.empty(n, dtype=float)
    for i in range(n):
        mu[i] = float(tokens[idx]); idx += 1
        sigma_i[i] = float(tokens[idx]); idx += 1

    corr = np.eye(n, dtype=float)
    n_pairs = n * (n + 1) // 2
    for _ in range(n_pairs):
        i = int(tokens[idx]) - 1; idx += 1                         
        j = int(tokens[idx]) - 1; idx += 1
        c = float(tokens[idx]); idx += 1
        corr[i, j] = c
        corr[j, i] = c

    assert idx == len(tokens), (
        f"{path.name}: očekivano {idx} tokena, fajl ima {len(tokens)} "
        "(proveriti format fajla)"
    )

                                                                        
    cov = corr * np.outer(sigma_i, sigma_i)

    name = path.stem                         
    label = DATASET_NAMES.get(name, name)

    return PortfolioData(
        name=name,
        label=label,
        n_assets=n,
        mu=mu,
        sigma_i=sigma_i,
        corr=corr,
        cov=cov,
    )


def load_all(data_dir: str | Path = "/home/claude/diplomski/data") -> dict[str, PortfolioData]:

    data_dir = Path(data_dir)
    result = {}
    for i in range(1, 6):
        fname = data_dir / f"port{i}.txt"
        if fname.exists():
            result[f"port{i}"] = load_port_file(fname)
    return result


if __name__ == "__main__":
    datasets = load_all()
    print(f"{'dataset':<8} {'label':<12} {'N':>4} {'min corr':>10} {'max corr':>10} "
          f"{'PSD (cov)':>10}")
    for name, d in datasets.items():
                                                                   
        eigvals = np.linalg.eigvalsh(d.cov)
        is_psd = eigvals.min() > -1e-8
        off_diag = d.corr[~np.eye(d.n_assets, dtype=bool)]
        print(f"{d.name:<8} {d.label:<12} {d.n_assets:>4} "
              f"{off_diag.min():>10.4f} {off_diag.max():>10.4f} {str(is_psd):>10}")
