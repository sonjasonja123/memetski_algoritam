# Sweep niske verovatnoće mutacije

## Šta se testira

Verovatnoća mutacije GA (`pm ∈ {0.00, 0.02, 0.04, 0.06, 0.08, 0.10}`), na
`port5` (Nikkei) sa svih 5 vrednosti λ i 30 semena, i na ostala 4 skupa samo za
λ=0.5 sa 10 semena. Referentna vrednost za Wilcoxon poređenje je `pm=0.10`
(nastavak `pm_sweep_high/` opsega naniže).

## Fiksni parametri

| Parametar | Vrednost |
|---|---:|
| `DATASETS` | port1, port2, port3, port4, port5 |
| `LAMBDAS` (port5) | 0.1, 0.3, 0.5, 0.7, 0.9 |
| `OTHER_DATASET_LAMBDAS` (port1–4) | 0.5 |
| `PORT5_N_SEEDS` | 30 |
| `OTHER_DATASETS_N_SEEDS` | 10 |
| `K` | 10 |
| `POP_SIZE` | 100 |
| `N_GENERATIONS` | 15 |
| `PC` | 0.8 |
| `ELITISM` | 1 |
| `TOURNAMENT_SIZE` | 2 |
| `EPS` | 0.01 |
| `DELTA` | 0.15 |

**Napomena:** ista pozadinska konfiguracija (pop=100, generacije=15) kao
`pm_sweep_high/`, koja se ne poklapa sa default vrednostima glavnog modela.
Videti `experiments/combined_verification/` za proveru na finalnoj pozadini.

## Kako pokrenuti

Jednim pozivom, iz korena projekta:

    python experiments/pm_sweep_low/run.py

Ovo pokreće ceo sweep (svi datasets x sve vrednosti swept parametra x svi
seed-ovi), paralelizovano, uz resume ako je vec delimicno zavrseno.
Rezultat: `experiments/pm_sweep_low/results.csv`

Za brzo testiranje na manjem opsegu, koriste se environment varijable
(`PMLOW_DATASETS`, `PMLOW_LAMBDAS`, `PMLOW_VALUES`, `PMLOW_N_SEEDS`,
`PMLOW_WORKERS`), npr.:

    PMLOW_DATASETS=port5 PMLOW_LAMBDAS=0.5 PMLOW_VALUES=0.00,0.10 PMLOW_N_SEEDS=2 python experiments/pm_sweep_low/run.py

Zatim, za statisticku analizu (Wilcoxon test) i tumacenje:

    python experiments/pm_sweep_low/analyze.py

Rezultat: `experiments/pm_sweep_low/wilcoxon.csv` i azuriran `FINDINGS.md`

## Vreme izvrsavanja

Puni obim je 1140 pokretanja GA (port5: 5λ×6pm×30 semena = 900; ostala 4
skupa: 1λ×6pm×10 semena × 4 = 240). Medijalno vreme po pokretanju je ~6.5s,
sto je uz paralelizaciju (npr. 8 procesa) priblizno 15 minuta ukupno.
