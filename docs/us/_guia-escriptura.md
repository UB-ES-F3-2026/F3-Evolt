# Guia d'escriptura de User Stories

> Document de treball intern de l'equip. Respon directament a la crítica del professor: les US anteriors eren **massa vagues**. Referències: format obligatori a [`docs/P1/AGENTS.md`](../P1/AGENTS.md) §"User Stories — format obligatori" i §"Regla dels 3 criteris d'acceptació"; plantilla a [`_plantilla.md`](_plantilla.md); índex a [`README.md`](README.md). Exemple de referència completa: l'exemple farcit US-19 dins [`_plantilla.md`](_plantilla.md).

## 1. La crítica i què canvia

El professor va dir que les US anteriors eren **massa vagues** («el usuario ve una pantalla», criteris genèrics, res verificable). La solució és **especificitat extrema**: pantalla amb ruta i component concrets, copy literal exacte, missatges d'error exactes amb la seva reacció a la UI, i reacció UI per a cada error d'API. I **exactament 3 criteris d'acceptació forts** — res de llistes llargues de coses cosmètiques.

## 2. Regla dels 3 criteris d'acceptació (vinculant)

- **EXACTAMENT 3 AC per US, mai més.** 3 forts valen més que 6 febles.
- **Cadascun prova funcionalitat real i integritat de dades, MAI cosmètica.**
  - ❌ PROHIBITS: «el botó es posa vermell», «surt l'etiqueta En progrés», «apareix el toast», «queda com el mockup».
  - ✅ PERMESOS: els diners s'han mogut; els dos saldos han canviat de manera atòmica; el registre ha quedat desat; l'operació il·legal s'ha refusat i no ha canviat res; la sol·licitud caducada es calcula com a caducada; el mateix usuari no surt a la seva cerca; es refusa una divisa repetida en el mateix compte; només es pot cancel·lar la sol·licitud pendent.
- **Els 3 angles, sempre en aquest ordre:**
  1. **Happy path de punta a punta** — amb xifres i noms concrets (qui, quant, des de/on) i l'estat final del sistema.
  2. **Invariant / protecció** — l'operació il·legal es **refusa I res no canvia** (saldos, registres, llistes: tot intacte).
  3. **Estat / persistència / propagació** — el resultat és **visible a tot on cal** i **sobreviu a la recàrrega** del navegador.
- **Forma de cada AC:** Gherkin **Given/When/Then**, **independent** dels altres, resultat clar **Pass/Fall**, i el PO l'ha de poder executar al navegador en **menys d'1 minut**.
- **La spec de pantalla no és AC:** estats, còpia, validacions i reaccions d'error són cos de la US (seccions 4–8), **NO AC extra**.

## 3. Errors freqüents a evitar

- ❌ Descriure la pantalla **sense ruta ni component**: «el usuario ve una pantalla» → dir la ruta real (`/pots/:potId/withdraw`) i la vista (`PotView`), o marcar **`a crear`** si encara no existeix.
- ❌ **Verbs vagues**: «gestiona», «visualitza», «interactua» → accions concretes: què es toca, què passa, què queda.
- ❌ **Missatges d'error sense text literal exacte** → sempre entre «» i copiable tal qual al codi.
- ❌ **Codis d'error d'API sense reacció UI associada** → cada error té entrada a la taula acció → reacció → resposta → toast/redirecció (secció 8).
- ❌ **AC cosmètics o més de 3.**
- ❌ **Imports sense format** (`1.250,50 €`, sortida de `formatCents`), **dates sense format** (`11 d’oct. · 21:15`, sortida de `formatDateTime`) → `frontend/src/models/money.ts` i `frontend/src/models/date.ts` són l'única font de format.
- ❌ **Textos en castellà o anglès** → tot el producte és en català, inclosos toasts, botons, errors i l'estat buit.
- ❌ **Inventar libs o endpoints que el projecte no té** → si no existeix, escriu-hi **`a crear`**.
- ❌ **Barrejar dos límits de diners diferents**: el límit de **recàrrega** (1.000,00 €/dia, **ja existeix** al projecte) amb el nou límit d'**enviament** (1.000,00 €/dia, **decisió del PO**) — no és el mateix valor ni la mateixa regla.

## 4. Checklist abans de lliurar

- [ ] Les **12 seccions** de la plantilla són totes presents (Valor… Enllaços i DoD).
- [ ] **Exactament 3 AC**, en l'ordre correcte: happy path → invariant → persistència/propagació.
- [ ] Cada AC és **Pass/Fall en <1 min** al navegador, independent i en Gherkin.
- [ ] Tots els strings són **en català** i amb **format** d'import i de data correcte.
- [ ] **Cada error d'API té reacció UI** associada a la secció 8.
- [ ] Totes les **rutes citades són reals**, o marcades **`a crear`**.
- [ ] Hi ha **imatge** (maqueta/mockup) i **diagrama Mermaid** del flux.
- [ ] Hi ha **enllaços** a Trello, issue i PR (secció 12).
- [ ] **Res de codi d'app tocat**: la US és especificació, no implementació.
- [ ] Lectura final: no hi ha cap «gestiona», «visualitza» ni pantalla sense ruta.
