# MCDA Python

Jednostavan edukativni komplet za višekriterijsko odlučivanje. Svaka od 21 metode i šest normalizacija ima vlastiti modul. Rezultati su rječnici s izvornom matricom, relevantnim međukoracima i konačnim ishodom. Računanje koristi punu `float64` preciznost; `decimals` se odnosi samo na prikaz i Excel.

## Instalacija

Windows PowerShell (u direktoriju `MCDA-Python`):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python main.py --method saw --file data/example.xlsx --normalization minmax
```

Lokalni Jupyter: otvorite `notebooks/MCDA_Colab.ipynb` i pokrenite ćelije redom. Google Colab: [otvorite notebook direktno iz GitHuba](https://colab.research.google.com/github/WaydenDunford/MCDA-Python/blob/main/notebooks/MCDA_Colab.ipynb). Prva ćelija automatski preuzima projekt i instalira pakete; u drugoj učitajte svoj Excel fajl. `METHOD`, `TASK`, `NORMALIZATION`, `SHEET` i `METHOD_PARAMS` mijenjaju se u odjeljku 3.2.

Zavisnosti: NumPy, pandas, SciPy (MACBETH linearno programiranje), openpyxl, pytest i nbformat (provjera bilježnice). Nema web servera ni baze podataka.

## Primjeri

```python
from excel import load_data
from engine import run
from display import show_results
from export import export_excel

data = load_data('data/example.xlsx', method='saw')
saw = run('saw', **data, normalization='minmax')
show_results(saw, show_steps=True)
export_excel(saw, 'results/SAW_results.xlsx')

topsis = run('topsis', **data, normalization='vector')
entropy = run('entropy', matrix=data['matrix'], types=data['types'], task='weights')
topsis_from_entropy = run('topsis', matrix=data['matrix'], types=data['types'],
                          weights=entropy['weights'], normalization='vector')

ahp = run('ahp', **load_data('data/ahp_example.xlsx', 'ahp'), task='weights')
hierarchy = run('ahp', **load_data('data/ahp_example.xlsx', 'ahp', task='ranking'), task='ranking')
dematel = run('dematel', **load_data('data/dematel_example.xlsx', 'dematel'))
macbeth = run('macbeth', **load_data('data/macbeth_example.xlsx', 'macbeth'))
```

```python
from comparison import compare
from sensitivity import analyze

comparison = compare(['saw', 'topsis', 'vikor', 'waspas'],
                     data['matrix'], data['types'], data['weights'])
print(comparison['ranks'])
print(comparison['spearman'])
export_excel(comparison, 'results/comparison.xlsx')

sensitivity = analyze('saw', data['matrix'], data['types'], data['weights'],
                      criterion='C1', new_weight=0.5, normalization='minmax')
print(sensitivity['comparison'])
export_excel(sensitivity, 'results/sensitivity.xlsx')
```

## Excel formati

`data/example.xlsx`: jedan red zaglavlja `Alternative, C1, C2, ...`, zatim proizvoljni nazivi alternativa, red `max/min` ili `Cilj` i opcioni red `weights` ili `Težina (w)`. Dozvoljeni smjerovi: `max`, `min`, `+`, `-`, `benefit`, `cost`. Prazni redovi se preskaču. Svaki red ili kolona sa samim nulama preskače se uz upozorenje; pojedinačne nule u inače popunjenom redu ili koloni ostaju. Ako se ukloni kriterij s pozitivnom težinom, preostale težine proporcionalno se normaliziraju na zbir 1. Za zadržavanje potpuno nultih redova i kolona koristite `load_data(..., skip_all_zero=False)`. Stari argument `skip_trailing_zero_rows` ostaje podržan. Broj alternativa i kriterija nije ograničen fiksnom veličinom. Zaglavlje se traži po identifikatorima `C1`, `C2`, itd. Težine se nikad automatski ne zamjenjuju jednakim težinama.

`data/ahp_example.xlsx`: list `Criteria` je kvadratna recipročna matrica kriterija. Za hijerarhijski ranking listovi `C1`, `C2`, ... sadrže recipročne matrice istih alternativa. `load_data(..., 'ahp', task='ranking', sheet='Criteria')` čita sve. Razlomci poput `1/3` su dopušteni.

`data/dematel_example.xlsx`: kvadratna matrica uticaja s istim nazivima redova i kolona, nenegativnim vrijednostima i nultom dijagonalom.

`data/macbeth_example.xlsx`: kvadratna matrica kvalitativnih sudova. Upišite sud za svaki par **samo u jedno** od dva simetrična polja; red s upisom označava bolju opciju. Prihvaćene kategorije su `no`, `very weak`, `weak`, `moderate`, `strong`, `very strong`, `extreme` ili brojevi `0..6`. Primjer ima opcije poredane od najbolje prema najgoroj i posljednja je sidro 0. Nije podržano intervalno ili neodređeno prosuđivanje.

Ako se format ili orijentacija ne slažu s odabranom metodom, čitač vraća grešku. `export_excel` odbija izlaznu putanju jednaku izvornoj Excel putanji.

## Metode i matematičke varijante

Svaka metoda prima `matrix`; standardne rangirne metode primaju `types` i `weights` sa zbirom 1. `rules.py` navodi zadatke, ulaznu strukturu i podržane vanjske normalizacije. Za metode s izvornom internom formulom vanjska normalizacija nije dopuštena.

| Metoda | Zadatak i varijanta | Glavni međukoraci i izlaz | Uslovi |
|---|---|---|---|
| AHP | Težine/hijerarhijski ranking, glavni Perronov svojstveni vektor | normalizirana matrica za pregled, λmax, CI, RI, CR, lokalni/globalni prioriteti | pozitivna recipročna matrica; RI tabela do 15 |
| ARAS | aditivni omjer prema idealu | ideal, proširena matrica, ponderisani zbir, omjer | strogo pozitivni ulazi |
| CODAS | euklidska pa taksist udaljenost od antiideala, prag `tau=.02` | obje udaljenosti, parna procjena, zbir | strogo pozitivni ulazi |
| COPRAS | proporcionalna procjena benefit/cost suma | normalizirana matrica, S+, S−, Q, korisnost % | strogo pozitivni ulazi |
| CRITIC | objektivne težine `σj Σk(1-rjk)` | min-max matrica, σ, korelacija, konflikt, informacija | bez ukupnog kontrasta nema težina |
| DEMATEL | `N=X/s`, `T=N(I-N)^-1` | D, R, D+R, D−R, cause/effect | spektralni radijus N < 1 |
| EDAS | udaljenost od prosjeka | PDA, NDA, SP, SN, NSP, NSN | pozitivni prosjeci |
| Entropy | Shannonova entropija na min-max korisnosti | proporcije, entropija, divergencija, težine | barem 2 alternative |
| MABAC | pomaknuta min-max i geometrijska granica | granična aproksimacija, razlike, zbir | konstantan kriterij dobiva korisnost 1 |
| MACBETH | kvalitativne razlike kao sistem linearnih nejednakosti | LP skala, matrica razlika, ocjene 0–100 | potpuni parni sudovi; kanonsko LP rješenje, ne cijeli interaktivni M-MACBETH protokol |
| MAIRCA | jednaka početna preferencija `1/m` | teorijska, realna ocjena i jaz | niži jaz bolji |
| MARCOS | odnos prema idealu i antiidealu | K+, K−, njihove funkcije i ukupna korisnost | strogo pozitivni ulazi |
| MEREC | efekat uklanjanja kriterija | log performanse sa/bez kriterija, efekti, težine | strogo pozitivni ulazi |
| MOORA | ratio system, benefit minus cost | vektorska matrica, pozitivni/negativni doprinosi | nenulta norma stupca |
| PROMETHEE II | neto tok preferencija | parne matrice, pozitivni/negativni/neto tok | šest funkcija: usual, u_shape, v_shape, level, linear, gaussian; parametri `q`, `p`, `s` |
| PSI | varijacija, preferencija `1−Σ(r−r̄)^2` | težine i opcioni ranking | pozitivni ulazi; negativne preferencije se odbijaju |
| SAW | `Σwj rij` | normalizirana/ponderisana matrica, ocjene | vanjske normalizacije ispod |
| TODIM | teorija perspektive, referentna najveća težina, `theta=1` | kriterijska dominacija, zbir, skala 0–1 | `theta>0` |
| TOPSIS | klasična vektorska normalizacija sirovog x | ideali, D+, D−, relativna blizina | nenulta norma, različiti ideali |
| VIKOR | S, R, Q, `v=.5` | best/worst, jaz, kompromis i dva uslova | nekonstantni kriteriji |
| WASPAS | `λ` ponderisani zbir + `(1−λ)` proizvod | obje komponente, ukupna ocjena | pozitivni ulazi; `λ∈[0,1]` |

Normalizacije u `normalizations/`: `max` koristi `x/max` i `min/x`; `minmax` rastuću korisnost 0–1; `sum` koristi `x/Σx` i `(1/x)/Σ(1/x)`; `vector` koristi `x/||x||` i `(1/x)/||1/x||`; `nonlinear` potencira omjere iz `max` eksponentom `p>0` (podrazumijevano 2); `ln` koristi `ln(x)/Σln(x)` za benefit i `(1−ln(x)/Σln(x))/(m−1)` za cost. Logaritamska varijanta zahtijeva `x>1` i barem dvije alternative. Potencijalna i logaritamska transformacija su ponuđene samostalno; nisu nametnute metodama koje imaju vlastitu normalizaciju. SAW prihvata `max`, `minmax`, `sum`, `vector`, `nonlinear`; TOPSIS samo svoju vektorsku normalizaciju.

MEREC slijedi originalno obrnuto omjerno skaliranje: benefit `min(x)/x`, cost `x/max(x)`. AHP rangiranje koristi glavni svojstveni vektor, a kolonski normalizirana matrica služi samo za pregled. MACBETH LP traži numeričke razlike najmanje 1 za sve pozitivne sudove i najmanje 1 veće razlike za višu kategoriju; skala se preslikava na 0–100. Ovaj LP daje konzistentnu skalu, ali ne zamjenjuje četiri LP koraka i interakciju originalnog softvera.

## Ograničenja i provjera

Mnoge metode rangiranja imaju konkurentne varijante. Ovdje su izabrane konkretne formule iz tabele; metodološki različite ocjene ne smiju se direktno prosječiti. `compare` upoređuje rangove i Spearmanove korelacije. Analiza osjetljivosti proporcionalno skalira ostale težine faktorom `(1−nova)/(1−stara)`.

Pokrenite `python -m pytest -q`. Testovi uključuju ručno izračunate SAW/TOPSIS slučajeve, konzistentan AHP, analitički DEMATEL, sve metode, šest normalizacija, Excel čitanje/izvoz i sintaksu bilježnice. Testiranje na jednoj maloj matrici ne dokazuje ispravnost za sve ulaze; provjerite osjetljivost i pretpostavke na vlastitim podacima.

Osnovni izvori: [Saaty, AHP](https://doi.org/10.1287/mnsc.31.3.326), [Opricovic i Tzeng, VIKOR/TOPSIS](https://www.sciencedirect.com/science/article/pii/S0377221703000201), [Keshavarz-Ghorabaee et al., MEREC](https://www.mdpi.com/2073-8994/13/4/525), [Bana e Costa et al., MACBETH](https://eprints.lse.ac.uk/22759/1/03061.pdf), [Zavadskas i Turskis, logaritamska normalizacija](https://journals.sagepub.com/doi/10.3233/INF-2008-19%282%2909).
