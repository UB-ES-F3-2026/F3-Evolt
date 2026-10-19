# Prova completa en local · Sprint 0

Guia pas a pas per arrencar l'aplicació al teu ordinador i comprovar a mà que compleix tots els criteris d'acceptació de **US-07** (saldo a la pantalla principal), **US-08** (llistat de moviments) i **US-09** (recàrrega de prova). No cal conèixer el codi: només cal seguir els passos en ordre.

- Tasca: T09.8 (issue #27). El resultat l'aprofita T09.9 (issue #28) per marcar el tauler i preparar la demo.
- Contracte de referència: [`docs/api.md`](api.md).

Les ordres estan escrites per a **PowerShell** (Windows). Si fas servir macOS o Linux, mira l'[annex](#annex-macos-i-linux).

## Índex

- [Part A · Preparar l'ordinador (només la primera vegada)](#part-a--preparar-lordinador-només-la-primera-vegada)
- [Part B · Arrencar l'aplicació](#part-b--arrencar-laplicació)
- [Part C · Pantalla principal (US-07)](#part-c--pantalla-principal-us-07)
- [Part D · Llistat de moviments (US-08)](#part-d--llistat-de-moviments-us-08)
- [Part E · Recàrrega i límits (US-09)](#part-e--recàrrega-i-límits-us-09)
- [Part F · Flux complet](#part-f--flux-complet)
- [Part G · Usuari sense moviments](#part-g--usuari-sense-moviments)
- [Part H · Simulació de retard i de fallada](#part-h--simulació-de-retard-i-de-fallada)
- [Part I · Apuntar els resultats i obrir incidències](#part-i--apuntar-els-resultats-i-obrir-incidències)
- [Problemes habituals](#problemes-habituals)
- [Annex: macOS i Linux](#annex-macos-i-linux)

## Com marcar cada comprovació

Cada comprovació té un identificador (p. ej. **C3**) i el que **has de veure**. Si ho veus tal qual, és **OK**; si veus qualsevol altra cosa, és **KO**: apunta què has vist i continua amb la següent. Al final ho passaràs tot a la taula de la [Part I](#part-i--apuntar-els-resultats-i-obrir-incidències).

---

## Part A · Preparar l'ordinador (només la primera vegada)

### A1. Comprova que tens Python i Node

1. Obre **PowerShell** (tecla Windows → escriu `PowerShell` → Enter).
2. Escriu `python --version` i prem Enter. Ha de sortir `Python 3.12` o superior.
3. Escriu `node --version` i prem Enter. Ha de sortir `v20` o superior.

Si alguna de les dues ordres dona error, instal·la el que falti des de <https://www.python.org/downloads/> o <https://nodejs.org/> i torna a obrir PowerShell.

### A2. Ves a la carpeta del projecte

Escriu (canvia la ruta per la del teu ordinador):

```powershell
cd "C:\ruta\a\F3-Evolt"
```

Comprova que hi ets: `ls` ha de mostrar les carpetes `backend`, `docs` i `frontend`.

### A3. Baixa l'última versió de `develop`

```powershell
git checkout develop
git pull
```

### A4. Prepara el backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
```

- `python -m venv .venv` crea la carpeta `.venv`: un Python només per a aquest projecte.
- Després d'`Activate.ps1`, la línia de PowerShell comença per `(.venv)`.
- Si `Activate.ps1` dona un error de «execution policy», executa una vegada `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, respon `S` (o `Y`) i torna-ho a provar.

### A5. Prepara el frontend

```powershell
cd frontend
npm install
cd ..
```

Pot trigar un parell de minuts. Pots tancar aquesta finestra de PowerShell.

---

## Part B · Arrencar l'aplicació

Necessites **tres finestres de PowerShell** obertes a la carpeta del projecte (pas A2 a cadascuna):

| Finestra | Per a què |
|---|---|
| **T1 · Backend** | El servidor de l'API. S'ha de quedar oberta. |
| **T2 · Frontend** | El servidor de la web. S'ha de quedar oberta. |
| **T3 · Ordres** | Per reiniciar les dades quan una part d'aquest document ho demani (C, D, E i F). |

### B1. Arrenca el backend (T1)

```powershell
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Has de veure una línia com `Uvicorn running on http://127.0.0.1:8000`. **No tanquis aquesta finestra.**

### B2. Comprova que el backend respon

Obre al navegador <http://localhost:8000/api/health>. Ha de sortir:

```json
{"status":"ok"}
```

### B3. Arrenca el frontend (T2)

```powershell
cd frontend
$env:VITE_USE_MOCKS = "false"
npm run dev
```

Has de veure `Local: http://localhost:5173/`. **No tanquis aquesta finestra.**

> **Important.** La línia `$env:VITE_USE_MOCKS = "false"` fa que la web parli amb el backend de veritat. Sense ella, la web fa servir dades de mentida i la prova no serveix.
>
> **Important.** L'adreça ha de ser exactament `http://localhost:5173`. Si surt un altre port (5174, 5175…), mira [Problemes habituals](#problemes-habituals).

### B4. Obre l'aplicació

1. Obre <http://localhost:5173> al navegador (Chrome o Firefox).
2. Mira la finestra **T1**: hi ha d'haver aparegut una línia amb `GET /api/home`. Això confirma que la web parla amb el backend.

### B5. Com reiniciar les dades (T3)

Les dades viuen en memòria. Més endavant, al començament de les parts C, D, E i F, trobaràs la frase **«Abans de començar: reinicia les dades (B5)»**. Quan la vegis, torna aquí i escriu a **T3**:

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/api/dev/reset
```

Ha de respondre `status : ok`. Després, al navegador, prem **F5** per tornar a carregar la pàgina.

### B6. Com esborrar la preferència del saldo ocult

Al començament de la part C trobaràs **«esborra la preferència (B6)»**. Quan la vegis, fes això:

1. Al navegador, amb l'aplicació oberta a `http://localhost:5173`, prem **F12**.
2. Ves a la pestanya **Console**.
3. Escriu aquesta línia i prem **Enter**:

   ```js
   localStorage.removeItem('evolt.balanceHidden')
   ```

   Ha de respondre `undefined`. És normal: vol dir que s'ha esborrat.
4. Tanca les eines (F12) i prem **F5**.

> Si enganxes la línia en lloc d'escriure-la, alguns navegadors (Chrome, Opera, Edge) la bloquegen i demanen que escriguis `allow pasting` primer. Escriu-ho, prem Enter i torna a enganxar la línia.

---

## Part C · Pantalla principal (US-07)

**Abans de començar:** reinicia les dades (B5) i esborra la preferència (B6).

Obre <http://localhost:5173>. La pantalla té el títol **Inici**.

| Id | Què fas | Què has de veure |
|---|---|---|
| **C1** | Mira la primera targeta. | A sota de «Saldo disponible»: **3.795,21 €**. |
| **C2** | Mira la mateixa targeta. | «Total estalviat a guardioles: **300,00 €**». |
| **C3** | Mira la targeta «Últims moviments». | Exactament **5** moviments, en aquest ordre: Restaurant La Plaça (−23,50 €), Bizum enviat (−10,00 €), Supermercat (−45,90 €), Fruiteria (−18,30 €), Cinema (−9,50 €). |
| **C4** | Clica la icona de l'ull (a la dreta de «Saldo disponible»). | Els imports (saldo, total estalviat i moviments) queden ocults i la icona canvia a un ull ratllat. |
| **C5** | Torna a clicar l'ull. | Els imports tornen a sortir. |
| **C6** | Clica l'ull per amagar-los. Tanca la pestanya del navegador. Obre una pestanya nova i ves a <http://localhost:5173>. | Els imports **continuen ocults**. |
| **C7** | Clica l'ull per tornar-los a mostrar. | Els imports tornen a sortir. |

El criteri «amb moviment nou, el saldo s'actualitza sense reiniciar l'app» es comprova a la [Part F](#part-f--flux-complet).

---

## Part D · Llistat de moviments (US-08)

**Abans de començar:** reinicia les dades (B5).

A la pantalla **Inici**, clica **Veure tots** (a la targeta «Últims moviments»). S'obre la pantalla **Moviments**.

| Id | Què fas | Què has de veure |
|---|---|---|
| **D1** | Mira els primers moviments. | El primer és **Restaurant La Plaça** (−23,50 €), d'ahir. Després **Bizum enviat** i després **Supermercat** (−45,90 €), tots dos amb la mateixa data i hora. |
| **D2** | Mira unes quantes files. | Cada fila mostra el **concepte**, la **data i hora**, l'**import** (amb `+` o `−`, format `1.234,56 €`) i una icona. |
| **D3** | Busca **Bizum rebut** (+15,00 €) i **Cinema** (−9,50 €). | Els dos imports tenen **colors diferents** (un per a ingrés i un altre per a despesa). |
| **D4** | Fes scroll fins a baix de tot. | Un moment surt «Carregant més moviments…» i apareixen més moviments a sota. |
| **D5** | Continua fins al final de la llista. | L'últim moviment és **Ingrés inicial** (+1.000,00 €). En total n'hi ha **30** i no se'n repeteix cap. |
| **D6** | Clica **← Inici** (a dalt a l'esquerra). | Tornes a **Inici**. |

El criteri «sense moviments es mostra un missatge» es comprova a la [Part G](#part-g--usuari-sense-moviments).

---

## Part E · Recàrrega i límits (US-09)

**Abans de començar:** reinicia les dades (B5). Avui encara no s'ha fet cap recàrrega, així que es poden recarregar 1.000,00 €.

| Id | Què fas | Què has de veure |
|---|---|---|
| **E1** | A **Inici**, mira la primera targeta. | Hi ha un botó **Afegir diners**. |
| **E2** | Clica **Afegir diners**. | S'obre la pantalla **Afegir diners**, amb un sol camp «Import» i el text «Recàrrega de prova: no cal cap targeta i s'aprova a l'instant.». **No es demana cap dada de targeta.** |
| **E3** | Escriu `0` al camp. | Surt «L'import ha de ser més gran que 0.» i el botó **Confirmar** està desactivat. |
| **E4** | Esborra el camp i escriu `500,01`. | Surt «L'import màxim per recàrrega és de 500,00 €.» i el botó **Confirmar** està desactivat. |
| **E5** | Esborra el camp i escriu `500`. Prem F12, ves a la pestanya **Network** (Xarxa) i deixa-la oberta. Clica **Confirmar**. | Surt «Recàrrega feta: +500,00 €» i, al cap d'un segon i mig, tornes sol a **Inici**. No hi ha hagut cap pas d'aprovació. |
| **E6** | A la pestanya **Network**, clica la petició **topups** → pestanya **Response** (Resposta). Tanca F12 després. | La resposta només té `balance` i `movement`. **No hi ha res d'XP.** |
| **E7** | Mira **Inici**. | Saldo **4.295,21 €**. El primer dels últims moviments és **Recàrrega** (+500,00 €). No es mostra res d'XP enlloc. |
| **E8** | Clica **Afegir diners**, escriu `500` i **Confirmar**. | «Recàrrega feta: +500,00 €». A **Inici**, saldo **4.795,21 €**. Avui ja portes exactament 1.000,00 €, que és el màxim permès. |
| **E9** | Clica **Afegir diners**, escriu `0,01` i **Confirmar**. | Surt «Has superat el límit diari de recàrrega. Avui encara pots recarregar 0,00 €.» i **no** tornes a Inici. |
| **E10** | Clica **← Inici** (a dalt a l'esquerra). | A **Inici**, el saldo continua sent **4.795,21 €**. |
| **E11** | Clica **Veure tots**. | Els dos primers moviments són **Recàrrega** (+500,00 €), amb el color d'ingrés. |

---

## Part F · Flux complet

**Abans de començar:** reinicia les dades (B5) i ves a **Inici**.

| Id | Què fas | Què has de veure |
|---|---|---|
| **F1** | Mira el saldo. | **3.795,21 €**. |
| **F2** | Clica **Afegir diners**, escriu `10` i clica **Confirmar**. | «Recàrrega feta: +10,00 €» i, sol, tornes a **Inici**. |
| **F3** | Mira el saldo **sense prémer F5**. | **3.805,21 €**: el saldo s'ha actualitzat sense reiniciar l'app. |
| **F4** | Mira «Últims moviments». | El primer és **Recàrrega** (+10,00 €). Continuen sortint només 5 moviments. |
| **F5** | Clica **Veure tots**. | El primer moviment és **Recàrrega** (+10,00 €), amb el color d'ingrés. |
| **F6** | Prem **F5** a la pantalla Moviments i després torna a Inici i prem **F5** una altra vegada. | Tot es manté: saldo 3.805,21 € i la recàrrega a les dues pantalles. |

---

## Part G · Usuari sense moviments

Ara arrencaràs la web amb l'**usuari 2**, que té un compte buit. El backend (T1) no es toca.

### G0. Torna a arrencar el frontend amb l'usuari 2

1. A **T2**, prem **Ctrl+C** per aturar el frontend. Si pregunta alguna cosa, respon `S` (o `Y`).
2. **Tanca la finestra T2** i obre'n una de nova a la carpeta del projecte (pas A2).
3. Escriu:

```powershell
cd frontend
$env:VITE_USE_MOCKS = "false"
$env:VITE_DEMO_USER = "2"
npm run dev
```

4. Al navegador, prem **F5** a <http://localhost:5173>.

| Id | Què fas | Què has de veure |
|---|---|---|
| **G1** | Mira **Inici**. | Saldo **0,00 €**, total estalviat **0,00 €** i, a «Últims moviments», el missatge **«Encara no tens moviments»**. |
| **G2** | Clica **Veure tots**. | La pantalla **Moviments** mostra **«Encara no tens moviments»** i cap error. |
| **G3** | Torna a Inici, clica **Afegir diners**, escriu `20` i **Confirmar**. | A **Inici**, saldo **20,00 €** i la **Recàrrega** (+20,00 €) a «Últims moviments». |
| **G4** | Clica **Veure tots**. | Un sol moviment: **Recàrrega** (+20,00 €). |

### G5. Torna a l'usuari 1

1. A **T2**, **Ctrl+C** i **tanca la finestra**.
2. Obre una finestra nova i torna a fer el pas **B3** (sense `VITE_DEMO_USER`).

---

## Part H · Simulació de retard i de fallada

El backend pot fer veure que va lent o que falla, per comprovar que la web ho aguanta. Es configura en arrencar el backend (T1). El frontend (T2) es queda com està, amb l'usuari 1.

Cada apartat següent (H1, H2 i H3) comença amb **«Rearrenca el backend amb:»** i unes ordres. Cada vegada:

1. A **T1**, prem **Ctrl+C**.
2. Esborra les variables de simulació que hi pugui haver d'abans (a PowerShell es queden guardades fins que tanques la finestra):

   ```powershell
   Remove-Item Env:SIMULATE_ERROR_RATE, Env:SIMULATE_DELAY_MS -ErrorAction SilentlyContinue
   ```

   Si ho prefereixes, tanca la finestra T1 i obre'n una de nova a la carpeta del projecte (pas A2).
3. Escriu les ordres de l'apartat.

### H1. Backend lent

Rearrenca el backend amb:

```powershell
cd backend
.venv\Scripts\Activate.ps1
$env:SIMULATE_DELAY_MS = "2000"
uvicorn app.main:app --reload
```

| Id | Què fas | Què has de veure |
|---|---|---|
| **H1.1** | Ves a **Inici** i prem **F5**. | Uns 2 segons un indicador de càrrega i després les dades. |
| **H1.2** | Clica **Veure tots** i fes scroll fins a baix. | Indicador de càrrega en entrar i «Carregant més moviments…» en arribar a baix. |
| **H1.3** | Ves a **Afegir diners**, escriu `5` i clica **Confirmar**. | Mentre espera, el botó diu **«Enviant…»** i no es pot tornar a clicar. Després, la confirmació. |

### H2. Backend que sempre falla

Rearrenca el backend amb:

```powershell
cd backend
.venv\Scripts\Activate.ps1
$env:SIMULATE_ERROR_RATE = "100"
uvicorn app.main:app --reload
```

| Id | Què fas | Què has de veure |
|---|---|---|
| **H2.1** | Ves a <http://localhost:5173> i prem **F5**. | «S'ha produït un error inesperat. Torna-ho a provar més tard.» i un botó **Reintentar**. La pàgina no queda en blanc. |
| **H2.2** | Ves a <http://localhost:5173/movements>. | El mateix missatge amb **Reintentar**. |
| **H2.3** | Ves a <http://localhost:5173/topup>, escriu `10` i clica **Confirmar**. | El missatge d'error surt sota el camp i **no** tornes a Inici. |
| **H2.4** | A **T1**, prem **Ctrl+C** i escriu `Remove-Item Env:SIMULATE_ERROR_RATE, Env:SIMULATE_DELAY_MS -ErrorAction SilentlyContinue` i després `uvicorn app.main:app --reload`. Torna a <http://localhost:5173> i clica **Reintentar**. | Les dades tornen a sortir. |

### H3. Backend que falla de tant en tant

Rearrenca el backend amb:

```powershell
cd backend
.venv\Scripts\Activate.ps1
$env:SIMULATE_ERROR_RATE = "30"
uvicorn app.main:app --reload
```

| Id | Què fas | Què has de veure |
|---|---|---|
| **H3.1** | Durant un minut, navega entre Inici i Moviments, prem F5 i fes scroll. | De vegades surt l'error amb **Reintentar**; en clicar-lo, acaba carregant. Mai no queden moviments repetits ni la pantalla a mitges. |

### H4. Backend aturat

| Id | Què fas | Què has de veure |
|---|---|---|
| **H4.1** | A **T1**, prem **Ctrl+C** (deixa el backend aturat). Al navegador, prem **F5** a Inici. | «No hi ha connexió amb el servidor. Torna-ho a provar.» amb **Reintentar**. |

Per acabar, rearrenca el backend normal: a **T1**, `Remove-Item Env:SIMULATE_ERROR_RATE, Env:SIMULATE_DELAY_MS -ErrorAction SilentlyContinue` i després `uvicorn app.main:app --reload`.

---

## Part I · Apuntar els resultats i obrir incidències

### I1. Omple la taula

Data de la prova: 19/10/2026 · Qui la fa: Izan Farreny Heredia · Commit provat (`git log -1 --oneline`): `ad796ae` (`develop`)

| Criteri d'acceptació | Comprovacions | Resultat | Incidència |
|---|---|---|---|
| US-07 · Mostra el saldo disponible | C1 | OK | — |
| US-07 · Mostra el total estalviat a les guardioles | C2 | OK | — |
| US-07 · Mostra els 5 últims moviments | C3, F4 | OK | — |
| US-07 · Amb moviment nou, el saldo s'actualitza sense reiniciar l'app | F3 | OK | — |
| US-07 · Amb la icona d'ull puc amagar el saldo | C4, C5 | OK | — |
| US-07 · La preferència d'amagar es manté a la sessió següent | C6 | OK | — |
| US-08 · Del més recent al més antic | D1 | OK | — |
| US-08 · Import, concepte, data i tipus | D2 | OK | — |
| US-08 · Ingrés i despesa es diferencien amb color | D3 | OK | — |
| US-08 · En arribar al final, se'n carreguen més | D4, D5 | OK | — |
| US-08 · Sense moviments, missatge que ho indica | G1, G2 | OK | — |
| US-09 · A la pantalla principal hi ha «Afegir diners» | E1 | OK | — |
| US-09 · Import > 0 i ≤ 500 € | E3, E4, E5 | OK | — |
| US-09 · Sense dades de targeta; s'aprova automàticament | E2, E5 | OK | — |
| US-09 · No més de 1.000 € en un dia | E8, E9, E10 | OK | — |
| US-09 · El saldo s'actualitza i surt als moviments com «Recàrrega» | E7, E11 | OK | — |
| US-09 · Les recàrregues no donen XP | E6, E7 | OK | — |
| Flux complet | F1–F6 | OK | — |
| Usuari sense moviments | G1–G4 | OK | — |
| Simulació de retard | H1.1–H1.3 | OK | — |
| Simulació de fallada | H2.1–H2.4, H3.1, H4.1 | OK | — |

Un criteri és **OK** només si totes les seves comprovacions són OK.

**Resultat:** tots els criteris d'acceptació de US-07, US-08 i US-09 i totes les comprovacions addicionals són **OK**. No s'ha obert cap incidència.

### I2. Obre una incidència per cada KO

1. Ves a la pestanya **Issues** del repositori a GitHub → **New issue**.
2. Títol: `Bug: <Id> — <què falla>`. Exemple: `Bug: D5 — l'scroll repeteix moviments`.
3. Al cos, copia aquesta plantilla i omple-la:

```markdown
**Comprovació:** <Id> de docs/prueba-sprint0.md
**Passos:** <què has fet, en ordre>
**Esperat:** <el que diu aquest document>
**Obtingut:** <el que has vist>
**Captura:** <arrossega-la aquí si cal>
```

4. A **Assignees**, posa qui va fer la tasca d'aquella part. Si no ho saps, mira la PR que va tocar aquella pantalla a la pestanya **Pull requests** (filtre `is:merged`).
5. Escriu el número de la incidència (p. ex. `#55`) a la columna **Incidència** de la taula.

---

## Problemes habituals

| Problema | Solució |
|---|---|
| `python` o `node` «no es reconeix» | No està instal·lat o cal tancar i tornar a obrir PowerShell (pas A1). |
| `Activate.ps1` dona un error de «execution policy» | Executa `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` una vegada (pas A4). |
| El backend falla amb `ZoneInfoNotFoundError` o `No module named 'fastapi'` | No has activat l'entorn: falta `.venv\Scripts\Activate.ps1` (la línia ha de començar per `(.venv)`). Si persisteix, torna a fer `pip install -r requirements.txt`. |
| A T1 no apareix cap `GET /api/home` en obrir la web | El frontend està fent servir dades de mentida. Tanca T2 i torna a fer el pas B3 **amb** `$env:VITE_USE_MOCKS = "false"`. |
| Vite obre el port 5174 o un altre en lloc del 5173 | Ja hi ha un altre `npm run dev` obert. Tanca totes les finestres de frontend i torna a fer B3. Amb un port diferent el backend rebutja les peticions (CORS) i la web només mostra errors. |
| Després de la part H el backend continua lent o fallant | Les variables de simulació s'han quedat guardades a T1. Prem Ctrl+C i escriu `Remove-Item Env:SIMULATE_ERROR_RATE, Env:SIMULATE_DELAY_MS -ErrorAction SilentlyContinue` abans de tornar a arrencar. Comprova-ho amb `Get-ChildItem Env:SIMULATE*`: no ha de mostrar res. |
| Les xifres no coincideixen amb aquest document | Has fet recàrregues abans. Reinicia les dades (B5) i prem F5. |
| Les dades han tornat al principi sense voler | El backend s'ha reiniciat sol (passa amb `--reload` si es desa un fitxer del backend). Torna a començar la part on eres. |

---

## Annex: macOS i Linux

Fes servir **Terminal** en lloc de PowerShell. Les ordres que canvien:

| Pas | PowerShell (Windows) | Terminal (macOS / Linux) |
|---|---|---|
| Activar l'entorn | `.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |
| Frontend (B3) | `$env:VITE_USE_MOCKS = "false"` i després `npm run dev` | `VITE_USE_MOCKS=false npm run dev` |
| Usuari 2 (G0) | `$env:VITE_USE_MOCKS = "false"`, `$env:VITE_DEMO_USER = "2"` i després `npm run dev` | `VITE_USE_MOCKS=false VITE_DEMO_USER=2 npm run dev` |
| Backend lent (H1) | `$env:SIMULATE_DELAY_MS = "2000"` i després `uvicorn …` | `SIMULATE_DELAY_MS=2000 uvicorn app.main:app --reload` |
| Backend que falla (H2, H3) | `$env:SIMULATE_ERROR_RATE = "100"` i després `uvicorn …` | `SIMULATE_ERROR_RATE=100 uvicorn app.main:app --reload` |
| Reiniciar les dades (B5) | `Invoke-RestMethod -Method Post http://localhost:8000/api/dev/reset` | `curl -X POST http://localhost:8000/api/dev/reset` |

A macOS i Linux la variable només afecta aquella ordre, així que no cal tancar la finestra entre passos: n'hi ha prou amb Ctrl+C i tornar a arrencar.
