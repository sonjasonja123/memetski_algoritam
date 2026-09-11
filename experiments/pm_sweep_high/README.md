# Sweep verovatnoće mutacije (visok opseg)

## Šta se testira

Verovatnoća mutacije GA (`pm ∈ {0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40}`), na
`port5` (Nikkei) sa svih 5 vrednosti λ i 30 semena, i na ostala 4 skupa samo za
λ=0.5 sa 10 semena. Referentna vrednost za Wilcoxon poređenje je `pm=0.15`.

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

**Napomena:** pozadinska konfiguracija ovog sweep-a (pop=100, generacije=15) se
**ne** poklapa sa default vrednostima glavnog modela (pop=50, generacije=100).
Ovo nije greška — sweep je rađen sa pozadinom koja je u tom trenutku bila
aktuelna radi bržeg izvršavanja — ali znači da rezultat ovog eksperimenta sam
po sebi ne govori kako `pm` utiče na trenutnu konfiguraciju glavnog modela.
Videti `experiments/combined_verification/` za proveru na finalnoj pozadini.

## Kako pokrenuti

Jednim pozivom, iz korena projekta:

    python experiments/pm_sweep_high/run.py

Ovo pokreće ceo sweep (svi datasets x sve vrednosti swept parametra x svi
seed-ovi), paralelizovano, uz resume ako je vec delimicno zavrseno.
Rezultat: `experiments/pm_sweep_high/results.csv`

Za brzo testiranje na manjem opsegu, koriste se environment varijable
(`PM_DATASETS`, `PM_LAMBDAS`, `PM_VALUES`, `PM_N_SEEDS`, `PM_WORKERS`), npr.:

    PM_DATASETS=port5 PM_LAMBDAS=0.5 PM_VALUES=0.10,0.15 PM_N_SEEDS=2 python experiments/pm_sweep_high/run.py

Zatim, za statisticku analizu (Wilcoxon test) i tumacenje:

    python experiments/pm_sweep_high/analyze.py

Rezultat: `experiments/pm_sweep_high/wilcoxon.csv` i azuriran `FINDINGS.md`

## Vreme izvrsavanja

Puni obim je 1330 pokretanja GA (port5: 5λ×7pm×30 semena = 1050; ostala 4
skupa: 1λ×7pm×10 semena × 4 = 280). Medijalno vreme po pokretanju je ~8s, sto
je uz paralelizaciju (npr. 8 procesa) priblizno 20–25 minuta ukupno. (Sirovi
podaci sadrže jedan izolovan outlier od nekoliko sati — verovatno pauza/hibernacija
mašine tokom originalnog pokretanja, ne stvarno vreme GA — medijana je zato
pouzdanija procena od proseka.)
