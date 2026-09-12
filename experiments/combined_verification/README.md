# Kombinovana verifikacija

## Šta se testira

Pun **2³ faktorijalni dizajn** nad tri parametra koje su pojedinačni sweep-ovi
(`popsize_sweep/`, `pm_sweep_low/`) označili kao "bolje" u izolaciji — da bi
se proverilo da li se ta poboljšanja zaista isplate kada se primene
**zajedno**, i da bi se izračunali glavni efekti i efekti interakcije, na
`port5` (Nikkei — jedini skup gde je pojedinačni efekat pokazan), za svih 5
vrednosti λ i 30 semena:

| Faktor | Nivo "−" (original) | Nivo "+" (sweep pobednik) |
|---|---:|---:|
| POP (`pop_size`) | 50 | 100 |
| GEN (`n_generations`) | 100 | 50 |
| PM (`pm`) | 0.15 | 0.02 |

Svih 8 kombinacija (2³) su testirane, po jedna imenovana konfiguracija:

| Konfiguracija | pop_size | n_generations | pm | Ugao kocke |
|---|---:|---:|---:|:---:|
| `baseline` | 50 | 100 | 0.15 | − − − |
| `pop_gen100` | 100 | 100 | 0.15 | + − − |
| `gen_only` | 50 | 50 | 0.15 | − + − |
| `pm_only` | 50 | 100 | 0.02 | − − + |
| `pop_gen` | 100 | 50 | 0.15 | + + − |
| `pop_pm` | 100 | 100 | 0.02 | + − + |
| `gen_pm` | 50 | 50 | 0.02 | − + + |
| `combined_best` | 100 | 50 | 0.02 | + + + |

`baseline` je trenutna konfiguracija glavnog modela (GAConfig default).
`combined_best` kombinuje "pobednike" sva tri faktora, ali sa
`n_generations=50` (a ne 100) da bi ukupan računski budžet ostao uporediv sa
`baseline`-om.

**Napomena o `pop_only`:** eksperiment je ranije (pre uvođenja punog 2³
dizajna) sadržao i konfiguraciju `pop_only` = (100, **15**, 0.15) — sa
`n_generations=15`, što nije ni "−" (100) ni "+" (50) nivo GEN faktora u ovom
dizajnu. Ta konfiguracija je zadržana netaknuta u `results.csv` (već
verifikovan, ranije objavljen rezultat) i i dalje se poredi sa
`combined_best` u odeljku "Upareni Wilcoxon testovi", ali je **isključena** iz
faktorijalne analize ispod — `pop_gen100` (100, 100, 0.15) je prava POP+/GEN−/PM−
tačka kocke koju faktorijalna analiza koristi.

## Faktorijalna analiza

`analyze.py` računa svih 7 standardnih Yates efekata za 2³ dizajn (3 glavna
efekta + 3 dvostruke interakcije + 1 trostruka), po λ vrednosti i usrednjeno
preko svih λ, na `pe_percent` (efekat u procentnim poenima PE), sa
statističkom značajnošću preko uparenog Wilcoxon signed-rank testa na
kontrastu `best_fitness` po semenu i Holm korekcijom na 7 testova po grupi
(isti pristup kao u ostatku projekta). Rezultat: `factorial_effects.csv` i
nova sekcija u `FINDINGS.md`.

## Fiksni parametri

| Parametar | Vrednost |
|---|---:|
| `DATASETS` | port5 |
| `LAMBDAS` | 0.1, 0.3, 0.5, 0.7, 0.9 |
| `N_SEEDS` | 30 |
| `K` | 10 |
| `PC` | 0.8 |
| `ELITISM` | 1 |
| `TOURNAMENT_SIZE` | 2 |
| `EPS` | 0.01 |
| `DELTA` | 0.15 |

## Kako pokrenuti

Jednim pozivom, iz korena projekta:

    python experiments/combined_verification/run.py

Ovo pokreće svih 9 imenovanih konfiguracija (8 uglova kocke + istorijski
`pop_only`) x sve λ x svi seed-ovi, paralelizovano, uz resume ako je vec
delimicno zavrseno — vec zavrsene kombinacije (ukljucujuci originalne 4) se
preskacu i njihovi redovi u `results.csv` ostaju netaknuti.
Rezultat: `experiments/combined_verification/results.csv`

Za brzo testiranje na manjem opsegu, koriste se environment varijable
(`COMBVERIF_LAMBDAS`, `COMBVERIF_N_SEEDS`, `COMBVERIF_CONFIGS`), npr.:

    COMBVERIF_LAMBDAS=0.5 COMBVERIF_N_SEEDS=2 COMBVERIF_CONFIGS=baseline,combined_best python experiments/combined_verification/run.py

Zatim, za statisticku analizu (upareni Wilcoxon testovi + faktorijalna
analiza) i tumacenje:

    python experiments/combined_verification/analyze.py

Rezultat: `experiments/combined_verification/wilcoxon.csv`,
`experiments/combined_verification/factorial_effects.csv` i azuriran
`FINDINGS.md`

## Vreme izvrsavanja

Puni obim je 1200 pokretanja GA (8 uglova kocke + istorijski `pop_only` = 9
konfiguracija × 5 λ × 30 semena). Medijalno vreme po pokretanju je ~10s, sto
je uz paralelizaciju (npr. 8 procesa) priblizno 25 minuta ukupno.
