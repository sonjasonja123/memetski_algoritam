# Pregled svih eksperimenata

| Eksperiment | Šta testira | Opseg | Pobednik | Primenjeno u glavnom modelu? |
|---|---|---|---|---|
| [generations_sweep](generations_sweep/) | broj generacija | 10–100 | 100 (Nikkei osetljiv) | ✅ da |
| [popsize_sweep](popsize_sweep/) | veličina populacije | 50–150 | 100 (samo izolovano) | ❌ ne, videti combined_verification |
| [pm_sweep_high](pm_sweep_high/) | verovatnoća mutacije | 0.10–0.40 | 0.10 | ❌ ne, videti niže |
| [pm_sweep_low](pm_sweep_low/) | verovatnoća mutacije | 0.00–0.10 | 0.02 (≈0.00) | ❌ ne, videti niže |
| [combined_verification](combined_verification/) | pun 2³ dizajn: POP × GEN × PM (originalna vs. sweep-pobednik vrednost) | — | bez znac. poboljšanja `combined_best` nasp. originala | — (potvrđuje da se originalna konfiguracija zadržava) |
| [surrogate_fitness](surrogate_fitness/) | GA doprinos bez SLSQP-a | — | GA znač. bolji od random search-a u svih 250/250 poređenja | informativno, nije deo glavnog modela |

Zašto finalni model i dalje koristi `pop_size=50`, `n_generations=100`,
`pm=0.15` uprkos tome što su pojedinačni sweep-ovi našli "bolje" izolovane
vrednosti (pop=100, pm=0.02)? Zato što su ti sweep-ovi rađeni sa pozadinskom
konfiguracijom koja se razlikuje od finalnog modela (npr. generacije=15 u
`popsize_sweep`, `pm_sweep_high` i `pm_sweep_low`), pa "pobednik" izolovanog
sweep-a ne mora da važi kada se kombinuje sa ostatkom finalne konfiguracije.

`combined_verification` je prošireno na pun 2³ faktorijalni dizajn (8
konfiguracija = svaka kombinacija POP∈{50,100} × GEN∈{100,50} × PM∈{0.15,0.02},
na `port5`, svih 5 λ, 30 semena) da bi se izračunali glavni efekti i efekti
interakcije, ne samo uporedile četiri ad-hoc tačke. Nalaz je precizniji nego
"nema poboljšanja": **od tri izolovano "bolja" parametra, samo POP=100 je
zaista povoljan** kada se posmatra zajedno sa druga dva faktora (poboljšava PE
za ≈0.41 procentnih poena, statistički značajno); GEN=50 i PM=0.02 su u ovom
uravnoteženom dizajnu zapravo **nepovoljni** (pogoršavaju PE za ≈0.12,
odnosno ≈0.21 p.p., oba značajno) — suprotno utisku iz izolovanih
`generations_sweep`/`pm_sweep_low`, koji su rađeni sa drugačijom pozadinskom
konfiguracijom. Razlika `combined_best − baseline` se matematički tačno
razlaže na zbir tri glavna efekta i trostruke interakcije (dvostruke
interakcije se poništavaju na ta dva suprotna ugla kocke): ≈ −0.41 + 0.12 +
0.21 + 0.03 ≈ **−0.07 p.p.** — POP-ovo poboljšanje je gotovo u potpunosti
poništeno pogoršanjem od GEN i PM, pa je neto razlika premala da bude
statistički značajna naspram varijacije između semena. Videti
[`combined_verification/FINDINGS.md`](combined_verification/FINDINGS.md) za
punu tabelu efekata (po λ i usrednjeno) i obrazloženje. `surrogate_fitness` je
odvojen, informativni eksperiment (proverava doprinos GA operatora bez
SLSQP-a) i ne utiče na izbor parametara glavnog modela.
