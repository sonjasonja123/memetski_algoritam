






















from __future__ import annotations

import numpy as np
from pathlib import Path
from dataclasses import dataclass

@dataclass
class UEFCurve:
    name: str                            
    returns: np.ndarray                                                 
    std_devs: np.ndarray                                                         


def load_portef_file(path: str | Path) -> UEFCurve:

    path = Path(path)
    tokens = path.read_text().split()
    vals = np.array([float(t) for t in tokens])

    returns = vals[0::2]
    variances = vals[1::2]
    std_devs = np.sqrt(variances)

    assert len(returns) == len(std_devs), "neparan broj tokena u fajlu"
                                                                               
    assert np.all(np.diff(returns) <= 1e-12), (
        f"{path.name}: ocekivano opadajuce sortiranje po prinosu"
    )

    return UEFCurve(name=path.stem, returns=returns, std_devs=std_devs)


def load_all_uef(data_dir: str | Path = "/home/claude/diplomski/data") -> dict[str, UEFCurve]:

    data_dir = Path(data_dir)
    result = {}
    for i in range(1, 6):
        fname = data_dir / f"portef{i}.txt"
        if fname.exists():
            result[f"portef{i}"] = load_portef_file(fname)
    return result


def percentage_deviation_error(uef: UEFCurve, std_dev: float, ret: float) -> float | None:









    returns = uef.returns                        
    stds = uef.std_devs

                                                                                   
                                                                                   
    pe_horizontal = None
                                                                                   
    idx_le = np.where(returns <= ret)[0]                                      
    idx_ge = np.where(returns >= ret)[0]                                       
    if len(idx_le) > 0 and len(idx_ge) > 0:
                                                                                            
        k = idx_le[np.argmax(returns[idx_le])]
        j = idx_ge[np.argmin(returns[idx_ge])]
        if returns[j] == returns[k]:
            x_interp = stds[j]
        else:
            x_interp = stds[k] + (stds[j] - stds[k]) * (ret - returns[k]) / (returns[j] - returns[k])
        if x_interp > 0:
            pe_horizontal = 100.0 * (std_dev - x_interp) / x_interp
    pe_vertical = None
    idx_le_x = np.where(stds <= std_dev)[0]
    idx_ge_x = np.where(stds >= std_dev)[0]
    if len(idx_le_x) > 0 and len(idx_ge_x) > 0:
        k = idx_le_x[np.argmax(stds[idx_le_x])]
        j = idx_ge_x[np.argmin(stds[idx_ge_x])]
        if stds[j] == stds[k]:
            y_interp = returns[j]
        else:
            y_interp = returns[k] + (returns[j] - returns[k]) * (std_dev - stds[k]) / (stds[j] - stds[k])
        if y_interp != 0:
            pe_vertical = 100.0 * (ret - y_interp) / y_interp

    candidates = [abs(v) for v in (pe_horizontal, pe_vertical) if v is not None]
    if not candidates:
        return None
    return min(candidates)


if __name__ == "__main__":
    uef_curves = load_all_uef()

    print(f"{'dataset':<10} {'n_tacaka':>8} {'max prinos':>12} {'min prinos':>12} "
          f"{'min std':>10} {'max std':>10}")
    for name, uef in uef_curves.items():
        print(f"{name:<10} {len(uef.returns):>8} {uef.returns.max():>12.6f} "
              f"{uef.returns.min():>12.6f} {uef.std_devs.min():>10.6f} {uef.std_devs.max():>10.6f}")

    print()
    print("--- Sanity test: tacka NA krivoj mora imati PE blizu 0 ---")
    uef = uef_curves["portef1"]
    test_ret = uef.returns[500]
    test_std = uef.std_devs[500]
    pe = percentage_deviation_error(uef, test_std, test_ret)
    print(f"Tacka #500 sa krive: ret={test_ret:.6f}, std={test_std:.6f} -> PE={pe:.6f}%")
    assert pe < 0.01, "PE tacke koja je TACNO na krivoj mora biti ~0"

    print()
    print("--- Test: tacka LOSIJA od UEF (vise rizika za isti prinos) ---")
    worse_std = test_std * 1.10                                  
    pe_worse = percentage_deviation_error(uef, worse_std, test_ret)
    print(f"Ista tacka sa 10% vecim std: PE (min od horiz/vert)={pe_worse:.6f}%")
    print("(napomena: PE moze biti manji od 10% jer se uzima MIN od horizontalnog")
    print(" i vertikalnog odstupanja - vertikalno zavisi od nagiba krive, videti")
    print(" objasnjenje u Chang et al. 2000, sekcija 5.2.2)")
    assert 0 < pe_worse <= 10.5, "PE treba da bude izmedju 0 i ~10% (min od dva pravca)"

    print("\nSvi testovi prošli.")
