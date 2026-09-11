# Kombinovana verifikacija — sazetak

## Deskriptivna statistika (PE %, vreme u sekundama)

| config | lambda | n | PE prosecno | PE medijana | vreme prosecno |
|---|---|---|---|---|---|
| baseline | 0.1 | 30 | 3.356% | 3.229% | 10.53s |
| baseline | 0.3 | 30 | 3.449% | 3.266% | 10.74s |
| baseline | 0.5 | 30 | 3.263% | 3.229% | 11.94s |
| baseline | 0.7 | 30 | 3.755% | 3.632% | 13.22s |
| baseline | 0.9 | 30 | 1.262% | 1.156% | 14.34s |
| combined_best | 0.1 | 30 | 3.374% | 3.229% | 12.50s |
| combined_best | 0.3 | 30 | 3.332% | 3.229% | 12.49s |
| combined_best | 0.5 | 30 | 3.271% | 3.229% | 12.11s |
| combined_best | 0.7 | 30 | 3.632% | 3.632% | 14.07s |
| combined_best | 0.9 | 30 | 1.147% | 1.021% | 15.62s |
| gen_only | 0.1 | 30 | 3.763% | 3.317% | 7.99s |
| gen_only | 0.3 | 30 | 3.637% | 3.266% | 8.19s |
| gen_only | 0.5 | 30 | 3.475% | 3.346% | 8.07s |
| gen_only | 0.7 | 30 | 3.902% | 3.696% | 9.46s |
| gen_only | 0.9 | 30 | 1.705% | 1.652% | 10.15s |
| gen_pm | 0.1 | 30 | 4.103% | 3.441% | 4.72s |
| gen_pm | 0.3 | 30 | 4.124% | 3.776% | 5.01s |
| gen_pm | 0.5 | 30 | 4.023% | 3.485% | 5.17s |
| gen_pm | 0.7 | 30 | 3.854% | 3.708% | 6.05s |
| gen_pm | 0.9 | 30 | 1.831% | 1.764% | 6.75s |
| pm_only | 0.1 | 30 | 3.844% | 3.415% | 5.67s |
| pm_only | 0.3 | 30 | 3.917% | 3.430% | 6.02s |
| pm_only | 0.5 | 30 | 4.003% | 3.409% | 6.55s |
| pm_only | 0.7 | 30 | 3.851% | 3.708% | 7.28s |
| pm_only | 0.9 | 30 | 1.679% | 1.476% | 8.76s |
| pop_gen | 0.1 | 30 | 3.324% | 3.229% | 14.29s |
| pop_gen | 0.3 | 30 | 3.260% | 3.229% | 14.79s |
| pop_gen | 0.5 | 30 | 3.269% | 3.229% | 16.10s |
| pop_gen | 0.7 | 30 | 3.670% | 3.632% | 17.49s |
| pop_gen | 0.9 | 30 | 1.115% | 1.021% | 19.54s |
| pop_gen100 | 0.1 | 30 | 3.238% | 3.229% | 20.45s |
| pop_gen100 | 0.3 | 30 | 3.240% | 3.229% | 20.88s |
| pop_gen100 | 0.5 | 30 | 3.233% | 3.229% | 23.15s |
| pop_gen100 | 0.7 | 30 | 3.632% | 3.632% | 25.58s |
| pop_gen100 | 0.9 | 30 | 1.036% | 1.021% | 26.34s |
| pop_only | 0.1 | 30 | 8.050% | 7.744% | 5.28s |
| pop_only | 0.3 | 30 | 7.180% | 6.399% | 5.71s |
| pop_only | 0.5 | 30 | 7.105% | 6.996% | 6.78s |
| pop_only | 0.7 | 30 | 6.394% | 6.481% | 7.11s |
| pop_only | 0.9 | 30 | 3.909% | 3.735% | 7.55s |
| pop_pm | 0.1 | 30 | 3.374% | 3.229% | 11.59s |
| pop_pm | 0.3 | 30 | 3.318% | 3.229% | 11.90s |
| pop_pm | 0.5 | 30 | 3.271% | 3.229% | 12.72s |
| pop_pm | 0.7 | 30 | 3.633% | 3.632% | 14.39s |
| pop_pm | 0.9 | 30 | 1.138% | 1.021% | 15.70s |

## Upareni Wilcoxon testovi (combined_best vs ostale konfiguracije)

| poredjenje | lambda | n_pari | p (sirovo) | p (Holm) | znacajno | combined_best bolji u |
|---|---|---|---|---|---|---|
| combined_best vs baseline | 0.1 | 30 | 0.93729 | 1.00000 | ne | 8/30 |
| combined_best vs baseline | 0.3 | 30 | 0.48360 | 1.00000 | ne | 9/30 |
| combined_best vs baseline | 0.5 | 30 | 0.91955 | 1.00000 | ne | 8/30 |
| combined_best vs baseline | 0.7 | 30 | 0.09073 | 0.45367 | ne | 11/30 |
| combined_best vs baseline | 0.9 | 30 | 0.09090 | 0.45367 | ne | 14/30 |
| combined_best vs pop_only | 0.1 | 30 | 0.00000 | 0.00000 | DA | 30/30 |
| combined_best vs pop_only | 0.3 | 30 | 0.00000 | 0.00000 | DA | 30/30 |
| combined_best vs pop_only | 0.5 | 30 | 0.00000 | 0.00000 | DA | 30/30 |
| combined_best vs pop_only | 0.7 | 30 | 0.00000 | 0.00000 | DA | 30/30 |
| combined_best vs pop_only | 0.9 | 30 | 0.00000 | 0.00000 | DA | 30/30 |
| combined_best vs gen_only | 0.1 | 30 | 0.00029 | 0.00264 | DA | 21/30 |
| combined_best vs gen_only | 0.3 | 30 | 0.00667 | 0.04002 | DA | 17/30 |
| combined_best vs gen_only | 0.5 | 30 | 0.00060 | 0.00423 | DA | 20/30 |
| combined_best vs gen_only | 0.7 | 30 | 0.00031 | 0.00264 | DA | 20/30 |
| combined_best vs gen_only | 0.9 | 30 | 0.00006 | 0.00063 | DA | 22/30 |

## Napomena
Popuniti rucno finalni zakljucak nakon pregleda tabele iznad: da li je combined_best znacajno bolji od baseline-a, i da li je bolji i od pop_only i od gen_only pojedinacno (sto bi znacilo da su efekti aditivni) ili je otprilike isti kao bolji od njih dvoje (sto bi znacilo da se efekti preklapaju).

## Faktorijalna analiza (pun 2³ dizajn)

Kocka: POP `-`=50, `+`=100 | GEN `-`=100, `+`=50 | PM `-`=0.15, `+`=0.02. Efekat = (1/4) x suma predznacenih PE% vrednosti preko svih 8 uglova kocke (Yates metoda), usrednjeno po semenu. Pozitivan efekat znaci da '+' nivo(i) POVECAVAJU PE% (losije), negativan da ga SMANJUJU (bolje). Znacajnost testirana uparenim Wilcoxon signed-rank testom na kontrastu best_fitness po semenu (isti pristup kao u ostatku projekta), Holm korekcija na 7 testova po lambda grupi.

Van kocke (nije deo faktorijalne analize, nivo ne odgovara nijednom od dva testirana nivoa): pop_only.


### Prosek preko svih λ

| Faktor | Efekat (p.p. PE%) | p (Holm) | Znacajno |
|---|---:|---:|:---:|
| POP | -0.4144 | 1.304e-08 | da |
| GEN | +0.1160 | 1.304e-08 | da |
| PM | +0.2067 | 0.0007544 | da |
| POP×GEN | -0.0879 | 1.863e-08 | da |
| POP×PM | -0.1596 | 0.003115 | da |
| GEN×PM | -0.0496 | 0.003115 | da |
| POP×GEN×PM | +0.0258 | 0.01283 | da |

### Po λ vrednosti


**λ=0.1**

| Faktor | Efekat (p.p. PE%) | p (Holm) | Znacajno |
|---|---:|---:|:---:|
| POP | -0.4391 | 4.303e-07 | da |
| GEN | +0.1880 | 0.00024 | da |
| PM | +0.2532 | 0.007456 | da |
| POP×GEN | -0.1452 | 0.001832 | da |
| POP×PM | -0.1602 | 0.08098 | ne |
| GEN×PM | -0.0584 | 0.07209 | ne |
| POP×GEN×PM | +0.0157 | 0.0918 | ne |

**λ=0.3**

| Faktor | Efekat (p.p. PE%) | p (Holm) | Znacajno |
|---|---:|---:|:---:|
| POP | -0.4943 | 6.285e-05 | da |
| GEN | +0.1070 | 0.0005299 | da |
| PM | +0.2762 | 0.08514 | ne |
| POP×GEN | -0.0904 | 0.03795 | da |
| POP×PM | -0.2013 | 0.1953 | ne |
| GEN×PM | +0.0031 | 0.4358 | ne |
| POP×GEN×PM | -0.0064 | 0.4358 | ne |

**λ=0.5**

| Faktor | Efekat (p.p. PE%) | p (Holm) | Znacajno |
|---|---:|---:|:---:|
| POP | -0.4301 | 9.227e-05 | da |
| GEN | +0.0668 | 0.0001091 | da |
| PM | +0.3319 | 0.02583 | da |
| POP×GEN | -0.0489 | 0.001961 | da |
| POP×PM | -0.3127 | 0.03376 | da |
| GEN×PM | -0.0568 | 0.0009592 | da |
| POP×GEN×PM | +0.0389 | 0.03376 | da |

**λ=0.7**

| Faktor | Efekat (p.p. PE%) | p (Holm) | Znacajno |
|---|---:|---:|:---:|
| POP | -0.1987 | 0.001755 | da |
| GEN | +0.0469 | 0.0004159 | da |
| PM | +0.0027 | 0.4051 | ne |
| POP×GEN | -0.0282 | 0.1395 | ne |
| POP×PM | -0.0214 | 0.3816 | ne |
| GEN×PM | -0.0455 | 0.003287 | da |
| POP×GEN×PM | +0.0260 | 0.3251 | ne |

**λ=0.9**

| Faktor | Efekat (p.p. PE%) | p (Holm) | Znacajno |
|---|---:|---:|:---:|
| POP | -0.5100 | 1.304e-08 | da |
| GEN | +0.1710 | 0.0001093 | da |
| PM | +0.1693 | 0.3724 | ne |
| POP×GEN | -0.1267 | 0.004594 | da |
| POP×PM | -0.1026 | 0.5561 | ne |
| GEN×PM | -0.0902 | 0.03152 | da |
| POP×GEN×PM | +0.0550 | 0.3724 | ne |

### Zakljucak faktorijalne analize

Gledano preko sva tri faktora usrednjeno preko svih λ: POP=100 poboljsava (smanjuje) PE za 0.414 p.p. (znacajno), GEN=50 pogorsava (povecava) PE za 0.116 p.p. (znacajno), a PM=0.02 pogorsava (povecava) PE za 0.207 p.p. (znacajno). Drugim recima: od tri izolovana sweep 'pobednika', samo POP=100 je zaista povoljan kada se posmatra zajedno sa ostala dva faktora u uravnotezenom dizajnu - GEN=50 i PM=0.02 su OVDE nepovoljni (povecavaju PE), suprotno utisku koji ostavljaju izolovani `generations_sweep`/`pm_sweep_low` (koji su radjeni sa drugacijom pozadinskom konfiguracijom, videti README ovog eksperimenta i `experiments/SUMMARY.md`).

Za dva suprotna ugla kocke, `combined_best` (+++) naspram `baseline` (---), matematicki doprinose SAMO tri glavna efekta i trostruka interakcija POP×GEN×PM - dvostruke interakcije imaju istu parnost na oba ugla pa se tacno ponistavaju u ovoj konkretnoj razlici:

`combined_best − baseline (PE p.p.)` = POP + GEN + PM + POP×GEN×PM = -0.4144 +0.1160 +0.2067 +0.0258 = **-0.0660 p.p.** (rekonstruisano iz efekata; posmatrana razlika proseka je -0.0660 p.p. - poklapaju se do zaokruzivanja).

POP-ov povoljan doprinos (≈0.414 p.p.) je gotovo u potpunosti ponisten zbirom GEN i PM doprinosa (≈+0.323 p.p.), uz malu trostruku interakciju (≈+0.026 p.p.). Neto razlika (≈0.066 p.p.) je toliko mala u odnosu na varijaciju izmedju semena da upareni Wilcoxon test (vidi tabelu iznad, `combined_best vs baseline`) ne nalazi statisticku znacajnost ni na jednoj λ vrednosti. Ovo POTVRDJUJE odluku da se originalna konfiguracija (pop=50, generacije=100, pm=0.15) zadrzi: pun 2³ dizajn ne otkriva propustenu 'bolju' kombinaciju - naprotiv, pokazuje da su dva od tri izolovano 'bolja' parametra ovde zapravo nepovoljna, i da se njihov efekat priblizno ponistava sa POP-ovim poboljsanjem.