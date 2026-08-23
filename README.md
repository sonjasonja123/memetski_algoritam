# Memetski algoritam za portfolio optimizaciju

Ovaj projekat implementira memetski genetski algoritam za portfolio optimizaciju sa ograničenom kardinalnošću. Diskretni deo algoritma bira tačno `K` hartija od vrednosti, dok lokalna pretraga za taj izbor određuje njihove optimalne težine. Rezultati se porede sa efikasnom granicom bez ograničenja kardinalnosti iz OR-Library skupa podataka.

## Model optimizacije

Portfolio je opisan binarnim vektorom `z` i vektorom težina `w`. Vrednost `z[i] = 1` znači da je hartija `i` uključena u portfolio. Model minimizuje:

```text
f(w) = λ · wᵀΣw − (1 − λ) · μᵀw
```

gde je `Σ` kovarijaciona matrica, `μ` vektor očekivanih prinosa, a `λ` odnos između rizika i prinosa. Veće `λ` daje veći značaj smanjenju rizika, dok manje `λ` daje veći značaj prinosu.

Ograničenja su:

- izabrano je tačno `K` hartija;
- zbir svih težina je 1;
- neizabrane hartije imaju težinu 0;
- težina izabrane hartije je između `eps` i `delta`.

Sa podrazumevanim vrednostima `K=10`, `eps=0.01` i `delta=0.15`, svaki portfolio sadrži deset hartija, svaka sa udelom između 1% i 15%.

## Kako algoritam radi

1. Početna populacija se formira slučajnim izborom tačno `K` hartija.
2. Svaki hromozom se ocenjuje lokalnom pretragom. Za fiksan izbor hartija SLSQP rešava kontinualni problem određivanja težina.
3. Roditelji se biraju turnirskom selekcijom.
4. Uniformni crossover za svaki bit bira vrednost jednog od dva roditelja sa jednakom verovatnoćom.
5. Ako potomak nema tačno `K` jedinica, nasumična popravka dodaje ili uklanja hartije.
6. Swap mutacija uklanja jednu izabranu i dodaje jednu neizabranu hartiju, pa čuva kardinalnost.
7. Elitizam prenosi najbolje jedinke u sledeću generaciju.
8. Keš sprečava ponovno rešavanje lokalnog problema za već ocenjen hromozom.

Manja vrednost fitness funkcije označava bolje rešenje.

## Struktura projekta

```text
diplomski_kod/
├── data/                       OR-Library ulazni podaci i UEF krive
├── results/                    CSV rezultati, grafici i eventualni log grešaka
├── src/
│   ├── data_loader.py          učitavanje port1–port5 skupova
│   ├── crossover.py            uniformni crossover
│   ├── repair.py               popravka kardinalnosti
│   ├── local_search.py         SLSQP optimizacija težina
│   ├── memetic_ga.py           glavni memetski algoritam
│   └── uef_benchmark.py        UEF učitavanje i PE metrika
├── run_core_experiment.py      manji osnovni eksperiment
├── run_ccef_experiment.py      kompletan paralelni CCEF eksperiment
├── plot_ccef_vs_portef.py      vizuelno poređenje CCEF i UEF rezultata
└── archive/                    raniji operatori, eksperimenti i njihovi rezultati
```

Datoteke `port1.txt`–`port5.txt` sadrže broj hartija, očekivani prinos i standardnu devijaciju svake hartije, a zatim gornji trougao korelacione matrice. Pri učitavanju se izračunava kovarijaciona matrica `cov[i,j] = corr[i,j] · sigma[i] · sigma[j]`.

Datoteke `portef1.txt`–`portef5.txt` sadrže po 2.000 tačaka nekonstruisane efikasne granice kao parove očekivani prinos–varijansa. Varijansa se pri učitavanju pretvara u standardnu devijaciju.

## Zahtevi i instalacija

Potreban je Python 3.10 ili noviji. Iz korena projekta preporučuje se pravljenje virtuelnog okruženja.

PowerShell, Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy scipy matplotlib
```

Linux ili macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy scipy matplotlib
```

Skripte treba pokretati iz korena projekta, jer se relativne putanje do `data/`, `src/` i `results/` određuju u odnosu na njihovu lokaciju.

## Brzo pokretanje

Za osnovni eksperiment nad svih pet skupova pokrenuti:

```powershell
python run_core_experiment.py
```

Podrazumevana konfiguracija koristi `λ=0.5`, pet semena, populaciju od 50 jedinki i 100 generacija. Za svaki skup se ispisuju srednja vrednost, standardna devijacija i najbolji fitness, kao i izabrane hartije i njihove težine. Rezultati se upisuju u `results/core_experiment.csv`.

Parametri ovog eksperimenta nalaze se na početku `run_core_experiment.py`: `DATASETS`, `K`, `LAMBDA`, `POP_SIZE`, `N_GENERATIONS` i `N_SEEDS`.

## Menjanje parametara algoritma

Parametri nisu zadati preko komandne linije, već se menjaju direktno u skripti eksperimenta pre pokretanja. Za osnovni eksperiment otvoriti `run_core_experiment.py`. Na početku fajla nalaze se:

```python
DATASETS = ["port1", "port2", "port3", "port4", "port5"]
K = 10
LAMBDA = 0.5
POP_SIZE = 50
N_GENERATIONS = 100
N_SEEDS = 5
```

U istoj skripti, unutar poziva `GAConfig(...)`, mogu se promeniti i ostali parametri:

```python
config = GAConfig(
    k=K,
    lam=LAMBDA,
    pop_size=POP_SIZE,
    n_generations=N_GENERATIONS,
    seed=seed,
    pc=0.8,
    pm=0.15,
    elitism=1,
    tournament_size=2,
    eps=0.01,
    delta=0.15,
)
```

Za kompletan eksperiment iste vrednosti se nalaze na početku `run_ccef_experiment.py`. U toj skripti su svi parametri izdvojeni kao konstante:

```python
K = 10
POP_SIZE = 50
N_GENERATIONS = 100
PC = 0.8
PM = 0.15
ELITISM = 1
TOURNAMENT_SIZE = 2
EPS = 0.01
DELTA = 0.15
```

Značenje parametara:

| Parametar | Podrazumevano | Značenje |
|---|---:|---|
| `K` / `k` | 10 | tačan broj hartija u portfoliju |
| `LAMBDA` / `LAMBDAS` / `lam` | 0.5 ili lista | odnos rizika i prinosa; dozvoljeni opseg je od 0 do 1 |
| `POP_SIZE` / `pop_size` | 50 | broj jedinki u populaciji |
| `N_GENERATIONS` / `n_generations` | 100 | broj generacija genetskog algoritma |
| `N_SEEDS` | 5 ili 30 | broj nezavisnih ponavljanja eksperimenta |
| `PC` / `pc` | 0.8 | verovatnoća crossovera |
| `PM` / `pm` | 0.15 | verovatnoća swap mutacije |
| `ELITISM` / `elitism` | 1 | broj najboljih jedinki prenetih u sledeću generaciju |
| `TOURNAMENT_SIZE` / `tournament_size` | 2 | broj kandidata u turnirskoj selekciji |
| `EPS` / `eps` | 0.01 | najmanja dozvoljena težina izabrane hartije |
| `DELTA` / `delta` | 0.15 | najveća dozvoljena težina izabrane hartije |
| `NUM_WORKERS` | `None` | broj paralelnih procesa; `None` koristi sva dostupna jezgra |

Vrednosti moraju zadovoljiti uslov izvodljivosti:

```text
K · eps ≤ 1 ≤ K · delta
```

Na primer, za `K=20` nije moguće zadržati `delta=0.04`, jer bi najveći mogući zbir težina bio samo `20 · 0.04 = 0.8`. U tom slučaju `delta` mora biti najmanje `0.05`. Takođe, `K` ne sme biti veće od broja hartija u izabranom skupu podataka, `elitism` ne sme biti veći od populacije, a `tournament_size` ne sme biti veći od `POP_SIZE`.

Povećanje `POP_SIZE`, `N_GENERATIONS`, broja skupova, lambda vrednosti ili semena povećava vreme izvršavanja. Približan broj GA pokretanja kompletnog eksperimenta jednak je:

```text
broj skupova · broj lambda vrednosti · broj semena
```

Posle promene parametara kompletnog eksperimenta treba premestiti ili preimenovati postojeći `results/ccef_results.csv`. U suprotnom resume mehanizam može preskočiti kombinacije koje su već zabeležene sa starom konfiguracijom, jer CSV ključ sadrži samo skup, lambda vrednost i seme, a ne sadrži `K`, `eps`, `delta`, veličinu populacije i ostale GA parametre.

## Kompletan CCEF eksperiment

```powershell
python run_ccef_experiment.py
```

Podrazumevano se obrađuje pet skupova, vrednosti `λ = 0.1, 0.3, 0.5, 0.7, 0.9` i 30 nezavisnih semena. Poslovi se izvršavaju paralelno na svim dostupnim procesorskim jezgrima. To je ukupno 750 pokretanja i može trajati znatno duže od osnovnog eksperimenta.

Za brzu proveru u PowerShell-u opseg se može ograničiti promenljivama okruženja:

```powershell
$env:CCEF_DATASETS = "port1,port2"
$env:CCEF_LAMBDAS = "0.3,0.5"
$env:CCEF_N_SEEDS = "3"
python run_ccef_experiment.py
```

U Linux/macOS okruženju ekvivalent je:

```bash
CCEF_DATASETS=port1,port2 CCEF_LAMBDAS=0.3,0.5 CCEF_N_SEEDS=3 python run_ccef_experiment.py
```

Izlazi su:

- `results/ccef_results.csv` — svako uspešno pokretanje;
- `results/ccef_best.csv` — najbolje pokretanje za svaki par skupa i `λ`;
- `results/ccef_errors.log` — traceback neuspešnih poslova, ako ih bude.

Eksperiment podržava nastavak rada. Pre pokretanja čita postojeći `ccef_results.csv` i preskače već završene kombinacije skupa, `λ` i semena. Ako je potreban potpuno nov eksperiment, prethodni CSV treba sačuvati pod drugim imenom ili premestiti iz `results/`.

Kolone rezultata znače:

| Kolona | Značenje |
|---|---|
| `dataset` | oznaka OR-Library skupa |
| `lambda` | odnos rizika i prinosa |
| `seed` | seme generatora slučajnih brojeva |
| `best_fitness` | najmanja pronađena vrednost ciljne funkcije |
| `return` | očekivani prinos najboljeg portfolija |
| `std` | rizik izražen standardnom devijacijom |
| `pe_percent` | procentualno odstupanje od UEF krive |
| `n_evaluations` | broj stvarno rešenih lokalnih problema |
| `n_cache_hits` | broj ponovljenih hromozoma pronađenih u kešu |
| `elapsed_seconds` | vreme jednog pokretanja |

## Crtanje rezultata

Nakon CCEF eksperimenta pokrenuti:

```powershell
python plot_ccef_vs_portef.py
```

Grafik prikazuje UEF krivu, sva CCEF pokretanja i najbolje rešenje za svaku vrednost `λ`. Podrazumevani izlaz je `results/ccef_vs_portef.png`.

Dostupne opcije mogu se prikazati komandom:

```powershell
python plot_ccef_vs_portef.py --help
```

Primer prilagođenog izlaza:

```powershell
python plot_ccef_vs_portef.py --ccef results/ccef_results.csv --output results/poredjenje.png --dpi 300 --show
```

## PE metrika

Percentage-deviation Error meri udaljenost CCEF tačke `(standardna devijacija, prinos)` od teorijske UEF krive. Izračunavaju se horizontalno odstupanje pri fiksnom prinosu i vertikalno odstupanje pri fiksnom riziku, uz linearnu interpolaciju susednih UEF tačaka. Rezultat je manja apsolutna vrednost ta dva procentualna odstupanja. Vrednost 0 znači da tačka leži na UEF krivoj; manja vrednost je bolja.

## Direktne provere modula

Moduli `crossover.py` i `repair.py` imaju samostalne sanity provere:

```powershell
python src/crossover.py
python src/repair.py
```

`data_loader.py`, `local_search.py`, `memetic_ga.py` i `uef_benchmark.py` sadrže razvojne ulazne blokove, ali koriste istorijsku podrazumevanu putanju do podataka. Glavni eksperimentalni skriptovi eksplicitno prosleđuju projektnu putanju `data/` i zato su preporučeni način korišćenja.

## Arhivirani eksperimenti

Direktorijum `archive/` čuva pokušaje sa correlation-guided i Sharpe-guided repair operatorima, kao i intersection-fill crossover. Prema sačuvanim poređenjima, ove varijante su na uparenom Wilcoxon signed-rank testu bile lošije od jednostavnog modela sa uniformnim crossoverom i nasumičnom popravkom. Fajlovi su zadržani kao prateći materijal za diskusiju rezultata, ali nisu deo preporučenog toka pokretanja.

## Reproduktivnost i praktične napomene

- Isto seme i ista verzija biblioteka daju ponovljivo slučajno generisanje, ali male numeričke razlike SLSQP optimizatora mogu postojati između platformi.
- Uslov izvodljivosti je `K · eps ≤ 1 ≤ K · delta`. Ako nije ispunjen, lokalni problem nema dozvoljeno rešenje.
- `λ=0` optimizuje samo prinos, a `λ=1` samo varijansu.
- Na Windows-u je multiprocessing zaštićen odgovarajućim `if __name__ == "__main__"` ulazom i koristi `freeze_support()`.
- Postojeći `ccef_results.csv` utiče na resume mehanizam; proveriti ga pre promene konfiguracije eksperimenta.
