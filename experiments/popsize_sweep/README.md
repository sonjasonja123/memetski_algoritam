# Sweep veličine populacije

## Šta se testira

Veličina populacije GA (`pop_size ∈ {50, 75, 100, 150}`), na `port5` (Nikkei)
sa svih 5 vrednosti λ i 30 semena, i na ostala 4 skupa samo za λ=0.5 sa 10
semena. Referentna vrednost za Wilcoxon poređenje je `pop_size=50`.

## Fiksni parametri

| Parametar | Vrednost |
|---|---:|
| `DATASETS` | port1, port2, port3, port4, port5 |
| `LAMBDAS` (port5) | 0.1, 0.3, 0.5, 0.7, 0.9 |
| `OTHER_DATASET_LAMBDAS` (port1–4) | 0.5 |
| `PORT5_N_SEEDS` | 30 |
| `OTHER_DATASETS_N_SEEDS` | 10 |
| `K` | 10 |
| `N_GENERATIONS` | 15 |
| `PC` | 0.8 |
| `PM` | 0.15 |
| `ELITISM` | 1 |
| `TOURNAMENT_SIZE` | 2 |
| `EPS` | 0.01 |
| `DELTA` | 0.15 |

**Napomena:** pozadinska konfiguracija ovog sweep-a koristi `generacije=15`,
što se ne poklapa sa glavnim modelom (100 generacija) — rađeno tako radi bržeg
izvršavanja. `PM=0.15` se poklapa sa glavnim modelom. Videti
`experiments/combined_verification/` za proveru na finalnoj pozadini.

## Kako pokrenuti

Jednim pozivom, iz korena projekta:

    python experiments/popsize_sweep/run.py

Ovo pokreće ceo sweep (svi datasets x sve vrednosti swept parametra x svi
seed-ovi), paralelizovano, uz resume ako je vec delimicno zavrseno.
Rezultat: `experiments/popsize_sweep/results.csv`

Za brzo testiranje na manjem opsegu, koriste se environment varijable
(`POPSIZE_DATASETS`, `POPSIZE_LAMBDAS`, `POPSIZE_VALUES`, `POPSIZE_N_SEEDS`,
`POPSIZE_WORKERS`), npr.:

    POPSIZE_DATASETS=port5 POPSIZE_LAMBDAS=0.5 POPSIZE_VALUES=50,100 POPSIZE_N_SEEDS=2 python experiments/popsize_sweep/run.py

Zatim, za statisticku analizu (Wilcoxon test) i tumacenje:

    python experiments/popsize_sweep/analyze.py

Rezultat: `experiments/popsize_sweep/wilcoxon.csv` i azuriran `FINDINGS.md`

## Vreme izvrsavanja

Puni obim je 760 pokretanja GA (port5: 5λ×4 popsize×30 semena = 600; ostala 4
skupa: 1λ×4 popsize×10 semena × 4 = 160). Medijalno vreme po pokretanju je
~10s, sto je uz paralelizaciju (npr. 8 procesa) priblizno 15–20 minuta ukupno.
