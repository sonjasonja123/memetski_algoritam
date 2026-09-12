# AUDIT — revizija eksperimentalnih skripti i rezultata

Ovaj dokument je Korak 0 zahtevanog posla: pregled trenutnog stanja, bez ijedne
izmene koda ili rezultata. Sadrži i dva **kritična nalaza** (odeljci 4 i 5) koji
zahtevaju odluku pre nastavka na Korak 1 — videti "STOP — nalazi koji traže
odluku" na vrhu.

---

## STOP — nalazi koji traže odluku pre Koraka 1 (REŠENO)

Korisnik je potvrdio oba nalaza. Primenjeno pre početka Koraka 1:

- `run_ccef_experiment.py`: `N_GENERATIONS` vraćeno na `100`; `README.md`
  ažuriran da ponovo dokumentuje `100`.
- `results/ccef_results.csv` i `results/ccef_best.csv` (15-generacijski
  rezultati) preimenovani u `ccef_results_15gen.csv` / `ccef_best_15gen.csv`,
  ništa obrisano.
- `results/ccef_results_100gen_baseline.csv` / `ccef_best_100gen_baseline.csv`
  preimenovani u `ccef_results.csv` / `ccef_best.csv` — sada su aktivan glavni
  rezultat, usklađen sa `ccef_vs_portef.png` koji je iz njih i generisan.
- `results/generations_sweep.csv` skraćen na prvih 3751 linija (header + 3750
  validnih redova); nadovezani nepovezan tekst (od linije 3752 nadalje)
  uklonjen. Kopija originalnog (oštećenog) fajla sačuvana u scratchpad-u pre
  izmene.

Originalan tekst nalaza (za trag šta je tačno bilo pronađeno), ispod:

1. **`run_ccef_experiment.py` je koristio `N_GENERATIONS = 15`, ne 100.**
   Ovo je tačno poznata greška iz zadatka, i dalje je aktivna (videti odeljak 4).
   Trenutni `results/ccef_results.csv` i `results/ccef_best.csv` su rezultat tog
   15-generacijskog pokretanja, dok postoji odvojen, neversionisan par fajlova
   (`ccef_results_100gen_baseline.csv`, `ccef_best_100gen_baseline.csv`) koji
   izgleda kao ispravan rezultat sa 100 generacija. Objavljeni grafik
   `results/ccef_vs_portef.png` je generisan iz 100-generacijskih podataka
   (isti datum kao baseline CSV), **ne** iz trenutnog `ccef_results.csv`.
   → **Rešeno** (korisnik potvrdio): `N_GENERATIONS` vraćen na 100, README
   ažuriran, 15-gen rezultati sačuvani po strani, 100-gen baseline promovisan
   u aktivan `ccef_results.csv`/`ccef_best.csv`. Videti vrh dokumenta.

2. **`results/generations_sweep.csv` je fizički oštećen** — posle 3751 validnog
   reda (header + 3750 podataka, što je tačno pun očekivani grid) na fajl je
   nadovezano oko 130 linija nepovezanog teksta (izgleda kao ceo prompt zadatka
   "implementacija surrogate fitness eksperimenta", počev od linije 3752).
   Podaci sami po sebi izgledaju kompletni i konzistentni sa
   `generations_sweep_wilcoxon.csv` (100 poređenja = 25 parova skup×λ × 4
   vrednosti generacija, tačno kao što bi trebalo), ali dodati tekst nije CSV i
   **srušio bi resume mehanizam** (`_load_completed_keys` bi pokušao da čita
   `row["lambda"]`, `row["n_generations"]`, `row["seed"]` iz tih linija) ako se
   `run_generations_sweep.py` ikada ponovo pokrene bez prethodnog čišćenja.
   → **Rešeno** (korisnik potvrdio): fajl skraćen na prvih 3751 linija,
   originalna (oštećena) verzija sačuvana u scratchpad-u.

Ostatak dokumenta detaljno objašnjava kontekst za oba nalaza, plus sve ostalo
traženo u Koraku 0.

---

## 1. Runner skripte (`run_*.py`)

| Skripta | Šta radi |
|---|---|
| `run_core_experiment.py` | Mali, neparalelizovani sanity-check nad svih 5 skupova, `λ=0.5`, 5 semena, ispisuje statistiku i najbolji portfolio; upisuje `results/core_experiment.csv`. |
| `run_ccef_experiment.py` | Glavni, kompletan CCEF eksperiment — 5 skupova × 5 λ × 30 semena, paralelno; upisuje `results/ccef_results.csv` i `results/ccef_best.csv`. **NE DIRATI** (osim za pomeranje duplikovane infrastrukture u Koraku 1). |
| `run_generations_sweep.py` | Sweep broja generacija `{10,15,25,50,100}`, ostalo fiksno (pop=50, pm=0.15); upisuje `results/generations_sweep.csv`. |
| `run_pm_experiment.py` | Sweep verovatnoće mutacije, viši opseg `pm∈{0.10..0.40}`, fiksno pop=100, gen=15; upisuje `results/pm_results.csv`. |
| `run_pm_low_experiment.py` | Sweep verovatnoće mutacije, niži opseg `pm∈{0.00..0.10}`, fiksno pop=100, gen=15; upisuje `results/pm_low_results.csv`. |
| `run_popsize_experiment.py` | Sweep veličine populacije `{50,75,100,150}`, fiksno gen=15, pm=0.15; upisuje `results/popsize_results.csv`. |
| `run_combined_verification.py` | Poredi 4 imenovane konfiguracije (baseline, combined_best, pop_only, gen_only) na `port5`, da proveri da li se pojedinačno "bolje" vrednosti popsize/pm zaista isplate zajedno; upisuje `results/combined_verification.csv`. |
| `run_surrogate_experiment.py` | Odvojen eksperiment: GA sa surogat (jednake težine) fitnesom umesto SLSQP-a, poređen sa random search-om; upisuje `results/surrogate_results.csv`. |
| `benchmark_surrogate_speed.py` | Meri ubrzanje surogat evaluacije naspram SLSQP-a; upisuje `results/surrogate_speed.csv`. |
| `plot_ccef_vs_portef.py` | Nije sweep, crta CCEF rezultate naspram UEF krive → `results/ccef_vs_portef.png`. |
| `plot_surrogate_vs_portef.py` | Isto za surogat eksperiment → `results/surrogate_vs_portef.png`. |
| `archive/run_final_comparison.py`, `archive/run_crossover2_comparison.py`, `archive/run_sharpe_comparison.py` | Stariji, napušteni eksperimenti (crossover varijante, Sharpe cilj). Folder je u `.gitignore`, van git istorije — tretiram kao arhivu, van obima ovog zadatka; nisam ih dirao niti dalje analizirao. |

## 2. Analyze skripte (`analyze_*.py`)

| Skripta | Čita | Piše |
|---|---|---|
| `analyze_generations_sweep.py` | `results/generations_sweep.csv` | `generations_sweep_wilcoxon.csv`, `generations_sweep_summary.md` |
| `analyze_pm_experiment.py` | `results/pm_results.csv` | `pm_wilcoxon.csv`, `pm_summary.md` |
| `analyze_pm_low_experiment.py` | `results/pm_low_results.csv` | `pm_low_wilcoxon.csv`, `pm_low_summary.md` |
| `analyze_popsize_experiment.py` | `results/popsize_results.csv` | `popsize_wilcoxon.csv`, `popsize_summary.md` |
| `analyze_combined_verification.py` | `results/combined_verification.csv` | `combined_verification_wilcoxon.csv`, `combined_verification_summary.md` |
| `analyze_surrogate_experiment.py` | `results/surrogate_results.csv` | `surrogate_wilcoxon.csv` (napomena: `surrogate_summary.md` postoji, ali ga ova skripta ne generiše — pisan je odvojeno/ručno, jer sadrži prozu koju analyze skripta ne proizvodi) |

Nema "run_ccef" analyze skripte — CCEF rezultati se koriste direktno preko
`plot_ccef_vs_portef.py`, bez statističkog testa (očekivano, jer CCEF nije
sweep poređenje dve konfiguracije).

## 3. Duplikovan kod

Upoređeno linija-po-linija/funkcija-po-funkciju između svih 6 `run_*_experiment.py`
sweep skripti (isključujem `run_core_experiment.py` jer je namerno drugačiji —
neparalelizovan, i `run_surrogate_experiment.py` koji koristi drugačiji
`SurrogateGAConfig`, ali i on ponavlja veći deo iste infrastrukture).

Skoro identično (do preimenovanja promenljivih) u **svih 6** run skripti:

- `_init_worker(cov, mu, corr, uef, dataset)` — postavljanje globalnih promenljivih
  po worker procesu, identično u svih 6.
- Konstrukcija `mp.Pool(workers, _init_worker, (data.cov, data.mu, data.corr, uef,
  dataset_name))` + `for result in pool.imap_unordered(_run_task, tasks): ...` petlja
  sa `if result["ok"]: _append(...) else: _log_error(...)` — identičan oblik u
  svih 6 (`run_ccef_experiment.py`, `run_generations_sweep.py`,
  `run_pm_experiment.py`, `run_pm_low_experiment.py`,
  `run_popsize_experiment.py`, `run_combined_verification.py`).
  `run_surrogate_experiment.py` ima varijantu istog oblika (parovi ga/random
  rezultata po zadatku umesto jednog reda).
- `_parse_list(name, default, converter)` za čitanje environment varijabli kao
  liste — identična implementacija u `run_generations_sweep.py`,
  `run_pm_experiment.py`, `run_pm_low_experiment.py`,
  `run_popsize_experiment.py`, `run_surrogate_experiment.py` (pod imenom
  `_env_list`, ista logika). `run_ccef_experiment.py` ima sopstvenu,
  pojednostavljenu inline verziju bez ove pomoćne funkcije (`_selected_settings`
  direktno parsira `CCEF_DATASETS`/`CCEF_LAMBDAS`) — nedoslednost u stilu, ne u
  ponašanju.
- Incremental CSV writing sa resume mehanizmom: `_load_completed_keys`/`_completed`
  (čitanje CSV-a, build seta ključeva već završenih kombinacija) i
  `_append_row`/`_append` (upis reda uz `write_header` na prvi upis) — identičan
  obrazac u svih 6 skripti, menja se samo tuple ključa (koje kolone čine
  jedinstvenu kombinaciju).
- `_run_task` telo: konstrukcija `GAConfig(k=K, lam=lam, pop_size=..., n_generations=...,
  pc=PC, pm=..., elitism=ELITISM, tournament_size=TOURNAMENT_SIZE, eps=EPS,
  delta=DELTA, seed=seed)` → `run_memetic_ga(...)` → računanje `ret`, `std` preko
  `_g_mu @ result.best_w` i `result.best_w @ _g_cov @ result.best_w` → `pe_percent`
  preko `percentage_deviation_error` — identično u `run_ccef_experiment.py`,
  `run_generations_sweep.py`, `run_pm_experiment.py`, `run_pm_low_experiment.py`,
  `run_popsize_experiment.py`, `run_combined_verification.py` (razlikuje se samo
  koji je parametar promenljiv).
- `if __name__ == "__main__": mp.freeze_support(); main()` — identično u svih 6.
- Ispis napretka (`print(f"Gotovo za {time...}s: ...")`) — identičan obrazac,
  razlikuje se samo tekst poruke.

U analyze skriptama, duplikovano u **5 od 6** (`analyze_generations_sweep.py`,
`analyze_pm_experiment.py`, `analyze_pm_low_experiment.py`,
`analyze_popsize_experiment.py`, `analyze_surrogate_experiment.py`):

- `_holm_adjust(p_values)` — bit-za-bit ista implementacija (razlika samo u
  formatiranju koda, ne u logici) u svih 5. `analyze_combined_verification.py`
  ima šestu, nezavisno napisanu varijantu iste Holm korekcije pod imenom
  `holm_correction` — ista matematika, drugačiji stil (npr. koristi
  `sorted(range(n), key=...)` umesto `np.argsort`).
- `_metric(rows, name, aggregate)` / `_mean` + `_median` — ista ideja
  (izvlačenje kolone iz liste redova i primena agregatne funkcije), ponavlja se
  u 4 skripte sa sitnim razlikama u imenu i potpisu.
- Grupisanje `defaultdict(lambda: defaultdict(dict))` po `(dataset, lambda)` →
  `{swept_param: {seed: row}}`, pa uparivanje `paired_seeds = sorted(set(...) &
  set(baseline_by_seed))` i Wilcoxon nad uparenim `best_fitness` — identičan
  obrazac u 4 skripte (generations, pm, pm_low, popsize); `combined_verification`
  radi konceptualno isto ali uparuje po `(lambda, seed)` sa 4 imenovane
  konfiguracije umesto po numeričkoj vrednosti parametra.
- `_write_summary` — generisanje markdown tabele po paru `(dataset, lambda)` sa
  istim kolonama (PE prosečno/medijana, vreme, Δ fitness, p Holm, značajno) —
  isti obrazac u 4 skripte, razlikuje se samo koja se kolona sweep-uje.

**Zaključak:** ovo je tačno ono što bi trebalo da bude u `experiments/common.py`
(Korak 1) — resume+CSV infrastruktura, Pool orkestracija, `GAConfig`+`run_memetic_ga`+PE
poziv, i na analitičkoj strani Holm korekcija + parovana Wilcoxon+summary šablon.
`run_surrogate_experiment.py` i `analyze_surrogate_experiment.py` dele samo deo
infrastrukture (Pool/resume/CSV/Holm) jer rade sa parom (ga, random) rezultata i
drugim `SurrogateGAConfig`-om — zajednička funkcija za `GAConfig`+PE poziv im ne
odgovara direktno, samo generička Pool/resume/CSV/Holm infrastruktura.

## 4. Nedoslednosti parametara

### 4.1 `N_GENERATIONS` u `run_ccef_experiment.py` — potvrđena greška, ISPRAVLJENO

- `src/memetic_ga.py` (`GAConfig` default): `n_generations = 100`.
- Poslednji pravi commit (`bb1464a`, "izmene instanci"): promenio je
  `run_ccef_experiment.py` sa `N_GENERATIONS = 100` na `N_GENERATIONS = 10`.
- **Trenutno, nekomitovano stanje radnog direktorijuma**: `N_GENERATIONS = 15`
  (izmenjeno posle poslednjeg commit-a, dakle greška iz `bb1464a` nije ispravljena
  na 100 — samo je promenjena sa 10 na 15, i dalje pogrešno).
- `README.md` je **takođe nekomitovano izmenjen** da opisuje `N_GENERATIONS = 15`
  kao "za kompletan CCEF eksperiment" (linije ~132, ~148 trenutnog README.md) —
  odnosno neko je uskladio dokumentaciju sa greškom, umesto da ispravi grešku.
  Ovo znači da trenutni README **ne otkriva** grešku poređenjem sa kodom (oba
  govore 15), nego samo poređenjem sa `GAConfig` defaultom (100) i sa nazivom
  fajla `results/ccef_15gen_run.log`.
- `results/ccef_results.csv` (poslednji upis: danas, nekomitovano) i
  `results/ccef_best.csv` odgovaraju 15-generacijskom pokretanju.
- Postoje odvojeni, neversionisani (untracked) fajlovi
  `results/ccef_results_100gen_baseline.csv` i `results/ccef_best_100gen_baseline.csv`
  (21. avgust) koji izgledaju kao rezultat sa ispravnih 100 generacija, i
  `results/ccef_vs_portef.png` (isti datum) je generisan iz njih, ne iz trenutnog
  `ccef_results.csv`.
- **Ispravljeno uz izričitu potvrdu korisnika** (inače bih ovo samo prijavio,
  bez samostalne izmene finalnih parametara glavnog modela). Videti "STOP"
  odeljak na vrhu za tačno šta je promenjeno.

### 4.2 Fiksni "background" parametri u sweep eksperimentima nisu međusobno usklađeni sa 100/50

Kada se sweep-uje jedan parametar, ostali se drže fiksni kao "trenutna
konfiguracija glavnog modela" — ali ta pretpostavljena konfiguracija se
razlikuje između skripti:

| Skripta | Fiksni pop_size | Fiksni n_generations | Fiksni pm |
|---|---:|---:|---:|
| `run_generations_sweep.py` (sweeps generations) | 50 ✅ | — (sweeps) | 0.15 ✅ |
| `run_pm_experiment.py` (sweeps pm, visok opseg) | 100 ⚠️ | 15 ⚠️ | — (sweeps) |
| `run_pm_low_experiment.py` (sweeps pm, nizak opseg) | 100 ⚠️ | 15 ⚠️ | — (sweeps) |
| `run_popsize_experiment.py` (sweeps pop_size) | — (sweeps) | 15 ⚠️ | 0.15 ✅ |
| `run_combined_verification.py` (`baseline` config) | 50 ✅ | 100 ✅ | 0.15 ✅ |

Samo `generations_sweep` i `combined_verification`-ov `baseline` koriste
pozadinu koja se poklapa sa `GAConfig` defaultom (50, 100, 0.15). Sva tri pm/pm_low/popsize
sweep-a su rađena sa `n_generations=15` u pozadini (a pm sweep-ovi dodatno sa
`pop_size=100`), što **nije** ista pozadina kao trenutni (nameravani) glavni
model. Ovo možda nije greška — možda je namerno (npr. da se sweep završi brže,
ili da se testira efekat parametra u kombinaciji koja je u tom trenutku bila
aktuelna) — ali nigde nije objašnjeno, i README ga uopšte ne dokumentuje (glavni
README ne pominje `pm_sweep`, `popsize_sweep`, `generations_sweep` ni
`combined_verification` nijednom rečju — samo `run_core_experiment.py`,
`run_ccef_experiment.py` i surrogate eksperiment). Ne menjam ove vrednosti;
samo ih prenosim tačno u "Fiksni parametri" sekciju svakog `experiments/<naziv>/README.md`
u Koraku 3, uključujući i ovo neslaganje kao činjenicu, ne kao nešto što treba
"ispraviti".

### 4.3 Ostalo proverено, bez neslaganja

- `K=10`, `PC=0.8`, `ELITISM=1`, `TOURNAMENT_SIZE=2`, `EPS=0.01`, `DELTA=0.15` —
  identični u svih 7 skripti koje ih definišu, i poklapaju se sa `GAConfig`
  defaultima i sa README tabelom.
- `LAMBDAS = [0.1, 0.3, 0.5, 0.7, 0.9]` — identično svuda gde se koristi puni
  skup λ (uglavnom za `port5`); ostali skupovi u pm/pm_low/popsize sweep-ovima
  koriste samo `λ=0.5` (`OTHER_DATASET_LAMBDAS`) sa 10 semena — ovo je
  dokumentovano u samom kodu i konzistentno između sve tri skripte koje tako rade.
- `N_SEEDS=30` za `port5`, `10` za ostale skupove u pm/pm_low/popsize — konzistentno.

## 5. Nedostajući / neažurni rezultati

Za svaku runner skriptu postoji odgovarajući CSV; nijedan rezultat ne
nedostaje potpuno. Dva ozbiljna problema sa postojećim rezultatima:

1. **`results/generations_sweep.csv` je oštećen** — videti STOP odeljak #2 na
   vrhu. Sami podaci (3750 redova) izgledaju kompletni i podudaraju se sa
   `generations_sweep_wilcoxon.csv` (100 = 25 parova skup×λ × 4 vrednosti
   generacija ispod 100), ali fajl ima nadovezan nepovezan tekst posle reda
   3751.
2. **`results/ccef_results.csv` trenutno odgovara pogrešnoj (15-generacijskoj)
   konfiguraciji** — videti STOP odeljak #1.

Ostale provere svežine (poklapanje vremena izmene skripte i rezultata):

| Eksperiment | Run skripta izmenjena | Rezultat izmenjen | Analiza izmenjena | Ocena |
|---|---|---|---|---|
| core | 4. sep | 21. avg (core_experiment.csv) | — | rezultat je stariji od skripte, ali skripta se od tada nije menjala na način koji bi uticao na izlaz (samo formatiranje) — u redu |
| ccef | danas (nekomitovano) | danas (nekomitovano) | — | svež po vremenu, ali pogrešna konfiguracija (vidi gore) |
| generations_sweep | 4. sep | danas (ali oštećen) | 7. sep | podaci kompletni, fajl fizički oštećen |
| pm (visok opseg) | 7. sep | 8. sep | 7. sep | svež, konzistentan |
| pm_low (nizak opseg) | 8. sep | 8. sep | 8. sep | svež, konzistentan |
| popsize | 7. sep | 7. sep | 7. sep | svež, konzistentan |
| combined_verification | 8. sep | 8. sep | 8. sep | svež, konzistentan, ali vidi napomenu ispod o nedovršenom zaključku |
| surrogate | 25. avg | 25. avg | 25. avg | svež, konzistentan |

**Nedovršena interpretacija (ne "nedostaje", ali je nepotpuna):**

- `results/combined_verification_summary.md` se završava rečenicom
  "Popuniti ručno finalni zaključak nakon pregleda tabele iznad..." — sam
  `analyze_combined_verification.py` (linije 133–139) ovo piše kao stalni
  placeholder, i **niko ga posle nije ručno popunio**. Tabele u fajlu same po
  sebi pokazuju da je `combined_best` statistički značajno bolji od
  `pop_only` i `gen_only`, ali **ne** značajno bolji od `baseline`-a — što je
  konzistentno sa zadatkom navedenim očekivanim zaključkom ("bez znac.
  poboljšanja naspram originala"), ali ta rečenica trenutno ne postoji nigde u
  repozitorijumu kao gotov tekst. Kada budem pisao `FINDINGS.md` za
  `combined_verification` u Koraku 2, prenosim brojeve i primetnu čitljivu
  tabelu, ali **neću sam dopisivati zaključnu rečenicu** — to ostavljam za
  potvrdu, pošto zadatak izričito zabranjuje da ja donosim/menjam zaključke.
- `generations_sweep_summary.md`, `pm_summary.md`, `popsize_summary.md`
  sadrže **samo tabele** (onako kako ih `_write_summary` generiše) — nema
  nijedne rečenice zaključka/tumačenja bilo gde u ta tri fajla. Samo
  `pm_low_summary.md` ima auto-generisan pasus "Zbirni nalaz" sa jednom
  rečenicom (najniži prosečan PE ima `pm=0.02`). Predloženi `SUMMARY.md` iz
  Koraka 4 već pretpostavlja konkretne "pobednike" (npr. generations_sweep→100,
  popsize→100 "samo izolovano", pm_high→0.10, pm_low→0.02) — ovi zaključci
  **jesu** dosledni onome što tabele pokazuju (najniži PE / najveći broj
  statistički značajnih poređenja), ali pošto tekstualno nigde nisu zapisani
  kao gotov "zaključak", predlažem da ih u Koraku 2 upišem u FINDINGS.md
  doslovno onako kako su formulisani u primeru iz zadatka, uz jasnu naznaku da
  su izvedeni iz priloženih tabela — a ne da izmišljam novo tumačenje.

---

## Provera posle refaktorisanja

Koraci 1–6 su završeni. Ispod je šta je urađeno i kako je provereno.

### Šta je urađeno u ovoj rundi (nastavak posla koji je Korak 0–1 i deo Koraka 2
već započeo u ranijoj sesiji)

- Dovršeno premeštanje sirovih rezultata u odgovarajuće `experiments/<naziv>/`
  foldere za `pm_sweep_high`, `pm_sweep_low`, `popsize_sweep`,
  `combined_verification` i `surrogate_fitness` (za `generations_sweep` je to
  već bilo urađeno).
- `wilcoxon.csv` i `FINDINGS.md` su ponovo generisani pokretanjem postojećeg
  `analyze.py` iz svakog foldera nad premeštenim sirovim podacima (ne ručno
  pisani) — videti verifikaciju ispod.
- Napisan `README.md` za svih 6 `experiments/<naziv>/` foldera (nedostajali su
  svi osim posredno pomenutog `generations_sweep`, koji ga takođe nije imao).
- Napisan `experiments/SUMMARY.md`.
- U glavnom `README.md`: dodata sekcija "Parametri glavnog modela i njihovo
  poreklo" (Korak 5), ažurirana sekcija o surogat eksperimentu da pokazuje na
  `experiments/surrogate_fitness/` umesto na obrisane skripte u korenu, i
  ažuriran dijagram strukture projekta da prikazuje `experiments/`.
- Obrisani stari, sada suvišni duplikati u korenu (logika je već bila
  prebačena u `experiments/*/run.py` i `analyze.py` u ranijoj sesiji, ali
  originali nisu bili obrisani): `run_generations_sweep.py`,
  `run_pm_experiment.py`, `run_pm_low_experiment.py`,
  `run_popsize_experiment.py`, `run_combined_verification.py`,
  `analyze_generations_sweep.py`, `analyze_pm_experiment.py`,
  `analyze_pm_low_experiment.py`, `analyze_popsize_experiment.py`,
  `analyze_combined_verification.py`.
  (`run_surrogate_experiment.py`, `analyze_surrogate_experiment.py`,
  `plot_surrogate_vs_portef.py` i `benchmark_surrogate_speed.py` su već bili
  obrisani/premešteni iz korena pre ove runde.)
- **Pronađena i ispravljena greška u već premeštenom
  `experiments/surrogate_fitness/plot.py`**: fajl je bio premešten jedan nivo
  dublje (iz korena u `experiments/surrogate_fitness/`) ali putanje nisu bile
  ažurirane — `ROOT_DIR = Path(__file__).resolve().parent` je pokazivao na
  `experiments/surrogate_fitness/` umesto na koren projekta, pa je
  `sys.path.insert(0, str(ROOT_DIR / "src"))` pokušavao da uveze `data_loader`
  iz nepostojećeg `experiments/surrogate_fitness/src`, a podrazumevane putanje
  za `--results`/`--output` su pokazivale na nepostojeći
  `experiments/surrogate_fitness/results/`. Ispravljeno: `ROOT_DIR` sada ide
  tri nivoa naviše (do korena projekta) za uvoz `src` modula, a
  `--results`/`--output` podrazumevano koriste sopstveni folder skripte.
  Provereno pokretanjem — grafik se sada uspešno generiše.

### Provera bez izmene brojeva (Korak 6.2)

Za svih 5 sweep/verifikacionih eksperimenata (`pm_sweep_high`, `pm_sweep_low`,
`popsize_sweep`, `combined_verification`, `surrogate_fitness`), novougenerisan
`wilcoxon.csv` je upoređen sa pred-refaktorisanim `results/*_wilcoxon.csv` —
`diff` posle sortiranja vraća prazan izlaz (bit-za-bit identično) za svih 5.
`FINDINGS.md` sadržaj se poklapa sa starim `*_summary.md` tekstom (jedina
razlika: naslov u `pm_sweep_high/FINDINGS.md` dodaje pojašnjenje "(visok
opseg)" — kozmetička izmena teksta, ne broja).

### Provera pokretanjem na malom opsegu (Korak 6.1)

Za svih 6 `experiments/<naziv>/run.py`, napravljena je izolovana kopija (u
privremenom `experiments/_verify_<naziv>/` folderu, obrisanom posle provere)
i pokrenuta sa ograničenim opsegom preko environment varijabli (npr.
`GENSWEEP_DATASETS=port1 GENSWEEP_LAMBDAS=0.5 GENSWEEP_GENERATIONS=10,100
GENSWEEP_N_SEEDS=2`). Svih 6 pokretanja je završeno bez greške. Redovi iz
izolovanog `results.csv` upoređeni su sa redovima za iste kombinacije
(dataset, sweep-ovan parametar, seme) u postojećem, punom `results.csv` —
`best_fitness`, `return`, `std`, `pe_percent`, `n_evaluations` i
`n_cache_hits` su identični do poslednje cifre; razlikuje se samo
`elapsed_seconds` (očekivano, vreme izvršavanja nije deterministično). Ovo
potvrđuje da refaktorisanje (premeštanje koda u `experiments/common.py`) nije
promenilo GA/SLSQP ponašanje niti redosled random operacija.

### Provera da ništa van obima nije dirano

- `src/*.py`, `run_ccef_experiment.py`, `results/ccef_results.csv` i
  `results/ccef_best.csv` nisu menjani u ovoj rundi (provereno preko vremena
  izmene fajlova i sadržaja — `run_ccef_experiment.py` i dalje ima
  `N_GENERATIONS = 100`, kako je i ostavljeno na kraju Koraka 0).
- Pretraga celog projekta za preostalim referencama na obrisane skripte
  (`run_pm_experiment.py` i slično) ne nalazi nijednu u `.py`/`.md` fajlovima
  osim u samom `AUDIT.md` (namerno — istorijski opis stanja pre refaktorisanja)
  i u objašnjavajućim komentarima unutar `experiments/common.py` (namerno —
  objašnjava zašto surogat eksperiment nije prebačen na zajednički modul).

### Preostalo, van strogog obima "tačno četiri stvari po folderu"

`results/` i dalje sadrži istorijske log fajlove pokretanja
(`pm_run.log`, `pm_run.err.log`, `pm_analysis.log`, i ekvivalenti za
`pm_low`/`popsize`, plus `ccef_15gen_run.log`/`.err.log`), `core_experiment.csv`
i preimenovane 15-generacijske rezervne kopije
(`ccef_results_15gen.csv`, `ccef_best_15gen.csv`) iz odluke u Koraku 0. Nijedan
od ovih fajlova nije naveden u traženoj strukturi `results/` (koja bi trebalo
da sadrži samo `ccef_results.csv`, `ccef_best.csv` i `ccef_vs_portef.png`), ali
ih nisam brisao niti premeštao bez izričitog uputstva — to su transkripti
izvršavanja i rezervne kopije, ne dupliran "rezultat", i njihovo brisanje nije
bilo eksplicitno traženo. Prijavljujem ovde radi transparentnosti; po potrebi
mogu biti obrisani ili premešteni u poseban `archive/`-stil folder.

### Spisak premeštenih/preimenovanih fajlova (stara putanja → nova putanja)

- `results/pm_results.csv` → `experiments/pm_sweep_high/results.csv`
- `results/pm_wilcoxon.csv` → `experiments/pm_sweep_high/wilcoxon.csv` (regenerisano, bit-za-bit identično)
- `results/pm_summary.md` → `experiments/pm_sweep_high/FINDINGS.md` (regenerisano, identičan sadržaj + naslov)
- `results/pm_low_results.csv` → `experiments/pm_sweep_low/results.csv`
- `results/pm_low_wilcoxon.csv` → `experiments/pm_sweep_low/wilcoxon.csv` (regenerisano, bit-za-bit identično)
- `results/pm_low_summary.md` → `experiments/pm_sweep_low/FINDINGS.md` (regenerisano, identičan sadržaj)
- `results/popsize_results.csv` → `experiments/popsize_sweep/results.csv`
- `results/popsize_wilcoxon.csv` → `experiments/popsize_sweep/wilcoxon.csv` (regenerisano, bit-za-bit identično)
- `results/popsize_summary.md` → `experiments/popsize_sweep/FINDINGS.md` (regenerisano, identičan sadržaj)
- `results/combined_verification.csv` → `experiments/combined_verification/results.csv`
- `results/combined_verification_wilcoxon.csv` → `experiments/combined_verification/wilcoxon.csv` (regenerisano, bit-za-bit identično)
- `results/combined_verification_summary.md` → `experiments/combined_verification/FINDINGS.md` (regenerisano, identičan sadržaj, placeholder napomena namerno nedirana)
- `results/surrogate_results.csv` → `experiments/surrogate_fitness/results.csv`
- `results/surrogate_wilcoxon.csv` → `experiments/surrogate_fitness/wilcoxon.csv` (regenerisano, bit-za-bit identično)
- `results/surrogate_summary.md` → `experiments/surrogate_fitness/FINDINGS.md` (premešteno doslovno, ručno pisan tekst)
- `results/surrogate_speed.csv` → `experiments/surrogate_fitness/speed.csv`
- `results/surrogate_vs_portef.png` → `experiments/surrogate_fitness/surrogate_vs_portef.png` (regenerisano posle ispravke path bug-a u `plot.py`)

Obrisano (stari duplikati u korenu, logika već postojala u `experiments/`):
`run_generations_sweep.py`, `run_pm_experiment.py`,
`run_pm_low_experiment.py`, `run_popsize_experiment.py`,
`run_combined_verification.py`, `analyze_generations_sweep.py`,
`analyze_pm_experiment.py`, `analyze_pm_low_experiment.py`,
`analyze_popsize_experiment.py`, `analyze_combined_verification.py`.

Novo (nisu premeštanja, nego novi sadržaj po Koracima 3–5):
`experiments/generations_sweep/README.md`,
`experiments/pm_sweep_high/README.md`, `experiments/pm_sweep_low/README.md`,
`experiments/popsize_sweep/README.md`,
`experiments/combined_verification/README.md`,
`experiments/surrogate_fitness/README.md`, `experiments/SUMMARY.md`, i nova
sekcija "Parametri glavnog modela i njihovo poreklo" u glavnom `README.md`.
