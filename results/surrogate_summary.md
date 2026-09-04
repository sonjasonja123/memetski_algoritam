# Rezultat eksperimenta sa surogat fitnesom

Kompletna mreža sadrži 250 konfiguracija i 30 uparenih semena po konfiguraciji:
pet skupova × pet lambda vrednosti × dve veličine populacije × pet vrednosti
`pm`. Sa dva metoda (GA i random search) dobijeno je 15.000 jedinstvenih
redova, bez neuspešnih pokretanja i duplikata.

GA je imao bolji finalni fitnes u 7.498 od 7.500 uparenih pokretanja. Random
search je bio bolji u dva pokretanja, bez izjednačenja. Jednostrani Wilcoxon
test pokazuje da je GA značajno bolji u svih 250 konfiguracija. Sirove
p-vrednosti su od `9.31e-10` do `1.86e-9`, a sve Holm-korigovane p-vrednosti
iznose `2.33e-7`, daleko ispod nivoa `0.05`.

Najveća tipična prednost među testiranim parametrima dobijena je za populaciju
10 i `pm=0.25` (medijana razlike GA − random preko grupa približno
`-6.51e-4`). Razlike između susednih `pm` vrednosti su ipak male u odnosu na
glavni nalaz: svaka testirana kombinacija je statistički značajno pobedila
random kontrolu. Zbog toga eksperiment podržava zaključak da selekcija,
ukrštanje i mutacija daju samostalan doprinos, nezavisno od SLSQP lokalne
pretrage.

Prosečan hit rate GA keša je 64.0%, dok je kod random kontrole praktično 0%,
što je očekivano jer GA često ponavlja dobre kombinacije. Benchmark na 30
istih portfolija po skupu i lambda vrednosti pokazuje medijalno ubrzanje
surogat evaluacije od 189.8× u odnosu na SLSQP (raspon 95.3×–385.8×).

Detaljni i reproduktivni rezultati nalaze se u `surrogate_results.csv`,
`surrogate_wilcoxon.csv` i `surrogate_speed.csv`.
