# Surogat fitnes

## Šta se testira

Doprinos samog GA (selekcija, ukrštanje, mutacija) portfolio optimizaciji, bez
SLSQP lokalne pretrage — GA sa jeftinim surogat fitnesom (jednake težine po
izabranoj aktivi) poredi se sa random search-om koji koristi isti surogat
fitnes, na svih 5 skupova podataka, svih 5 vrednosti λ, dve veličine populacije
(10, 15), pet vrednosti `pm` (0.10–0.30) i 30 semena po kombinaciji.

Ovo je odvojen eksperiment od glavnog CCEF-a (koji uvek koristi SLSQP) — cilj
mu je da proveri da li GA operatori sami po sebi doprinose kvalitetu rešenja,
nezavisno od lokalne pretrage.

## Fiksni parametri

| Parametar | Vrednost |
|---|---:|
| `DATASETS` | port1, port2, port3, port4, port5 |
| `LAMBDAS` | 0.1, 0.3, 0.5, 0.7, 0.9 |
| `POP_SIZES` (swept) | 10, 15 |
| `MUTATION_RATES` (swept) | 0.10, 0.15, 0.20, 0.25, 0.30 |
| `N_SEEDS` | 30 |
| `N_GENERATIONS` | 100 |
| `K` | 10 |
| `PC` | 0.8 |
| `ELITISM` | 1 |
| `TOURNAMENT_SIZE` | 2 |

## Kako pokrenuti

Jednim pozivom, iz korena projekta:

    python experiments/surrogate_fitness/run.py

Ovo pokreće ceo grid (svi datasets x pop_size x pm x seed-ovi), paralelizovano
u uparenim (GA, random) zadacima, uz resume ako je vec delimicno zavrseno.
Rezultat: `experiments/surrogate_fitness/results.csv`

Za brzo testiranje na manjem opsegu, koriste se environment varijable
(`SURROGATE_DATASETS`, `SURROGATE_LAMBDAS`, `SURROGATE_POP_SIZES`,
`SURROGATE_PM`, `SURROGATE_N_SEEDS`), npr.:

    SURROGATE_DATASETS=port1 SURROGATE_LAMBDAS=0.5 SURROGATE_N_SEEDS=2 python experiments/surrogate_fitness/run.py

Zatim, za statisticku analizu (jednostrani Wilcoxon test, GA naspram random
search-a) i tumacenje:

    python experiments/surrogate_fitness/analyze.py

Rezultat: `experiments/surrogate_fitness/wilcoxon.csv` (tumačenje je ručno
pisano u `FINDINGS.md`, jer sadrži prozu koju `analyze.py` ne generiše).

Dva dodatna, opciona koraka specifična za ovaj eksperiment:

    python experiments/surrogate_fitness/benchmark_speed.py

meri ubrzanje surogat evaluacije naspram SLSQP-a → `experiments/surrogate_fitness/speed.csv`.

    python experiments/surrogate_fitness/plot.py

crta GA i random search naspram PORTEF granice → `experiments/surrogate_fitness/surrogate_vs_portef.png`.

## Vreme izvrsavanja

Puni obim je 7500 uparenih (GA, random) pokretanja = 15000 redova (5 skupova ×
5 λ × 2 popsize × 5 pm × 30 semena). Surogat fitnes je znatno jeftiniji od
SLSQP-a, pa je medijalno vreme po uparenom pokretanju ~0.2s — ceo grid traje
svega nekoliko minuta.
