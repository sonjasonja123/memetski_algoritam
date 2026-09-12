# Sweep broja generacija

## Šta se testira

Broj generacija GA (`n_generations ∈ {10, 15, 25, 50, 100}`), na svih 5 skupova
podataka (port1–port5), svih 5 vrednosti λ i 30 semena po kombinaciji.
Referentna vrednost za Wilcoxon poređenje je 100 generacija.

## Fiksni parametri

| Parametar | Vrednost |
|---|---:|
| `DATASETS` | port1, port2, port3, port4, port5 |
| `LAMBDAS` | 0.1, 0.3, 0.5, 0.7, 0.9 |
| `N_SEEDS` | 30 |
| `K` | 10 |
| `POP_SIZE` | 50 |
| `PC` | 0.8 |
| `PM` | 0.15 |
| `ELITISM` | 1 |
| `TOURNAMENT_SIZE` | 2 |
| `EPS` | 0.01 |
| `DELTA` | 0.15 |

Ova pozadinska konfiguracija (pop=50, pm=0.15) se poklapa sa default vrednostima
u `GAConfig` i sa glavnim CCEF eksperimentom.

## Kako pokrenuti

Jednim pozivom, iz korena projekta:

    python experiments/generations_sweep/run.py

Ovo pokreće ceo sweep (svi datasets x sve vrednosti swept parametra x svi
seed-ovi), paralelizovano, uz resume ako je vec delimicno zavrseno.
Rezultat: `experiments/generations_sweep/results.csv`

Za brzo testiranje na manjem opsegu, koriste se environment varijable
(`GENSWEEP_DATASETS`, `GENSWEEP_LAMBDAS`, `GENSWEEP_GENERATIONS`,
`GENSWEEP_N_SEEDS`, `GENSWEEP_WORKERS`), npr.:

    GENSWEEP_DATASETS=port1 GENSWEEP_LAMBDAS=0.5 GENSWEEP_GENERATIONS=10,100 GENSWEEP_N_SEEDS=2 python experiments/generations_sweep/run.py

Zatim, za statisticku analizu (Wilcoxon test) i tumacenje:

    python experiments/generations_sweep/analyze.py

Rezultat: `experiments/generations_sweep/wilcoxon.csv` i azuriran `FINDINGS.md`

## Vreme izvrsavanja

Puni obim je 5 skupova × 5 λ × 30 semena × 5 vrednosti generacija = 3750
pokretanja GA. Medijalno vreme po pokretanju je ~9s, sto je uz paralelizaciju
(npr. 8 procesa) priblizno 60–70 minuta ukupno.
