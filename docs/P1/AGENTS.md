# AGENTS.md — Projecte P1 (Software Engineering 2026)

## Visió del producte

Aplicació fintech estil **Revolut / N26 / Trade Republic** amb una capa de **gamificació** on les compres generen beneficis (XP, nivells, insignies, reptes) als usuaris.

**Punt fort de l'equip:** gestió de diners + aparellat gamificat, ben relacionat entre totes les pàgines.

El fintech es construeix **des de zero** (no és una còpia directa; és un rough copy dels models reals).

## Context del curs

- **Equip:** 5-7 persones, ownership compartit de tecnologia
- **Lliurament:** examen demo; sprints **0 → 3** + part d'explicació
- **Metodologia:** Scrum / Agile
- **Eines:**
  - **GitHub** — obligatori (repositori, CI/CD, separació producte vs develop)
  - **Trello** — backlog i planificació
  - Slack o similar per a coordinació
- **IA:** permès com a co-pilot (AI-SDLC); les decisions estratègiques, d'arquitectura i de producte són humanes

### Calendari de referència (Classes)

| Classe | Què cal tenir |
|--------|----------------|
| Class 1 (22-23 set) | Project kickoff |
| Class 2 (29-30 set) | Backlog check |
| **Class 3 (6-7 oct)** | **Deliver Backlog. Start Sprint 0** |
| Class 4 (13-14 oct) | Sprint 0 check |
| Class 5 (20-21 oct) | Deliver Demo S0 + Retro S0 + Start S1 |
| Class 6 (27-28 oct) | Sprint 1 check [Q1] |
| Class 7 (10-11 nov) | Deliver Demo S1 + Retro S1 + Start S2 |
| Class 8 (17-18 nov) | Sprint 2 check |
| Class 9 (24-25 nov) | Deliver Demo S2 + Retro S2 + Start S3 |
| Class 10 (1-2 des) | Sprint 3 check [Q2] |
| Class 11 (15-16 des) | Deliver Final Product (S3) |
| 22 des | Final Pitch |

**Fins a la Class 3:** el que es lliura és el **backlog** (US + èpiques + estimació), no el codi.

## Rols

### Rols Scrum
- **Scrum Master** (part-time): coordinació, pujada de carga setmanal, facilitar cerimònies
- **Product Owner** (part-time): visió de producte, canvis de backlog, acceptació de les US

### Rols Tech (mínim 2 rols diferents durant el projecte)
- Frontend developer
- Backend developer
- DevOps
- QA

### Rol IA-SDLC (complementa, no substitueix)
- **Developers:** AI com a assistent de codi; l'humà revisa arquitectura i patró de decisions
- **Product Owner:** AI ajuda a esborronar US; l'humà valida valor de mercat i visió
- **Scrum Master:** AI accelera; l'humà defineix límits i accountability
- **QA:** AI ajuda a generar tests; l'humà valida cobertura i criteris
- **DevOps:** AI ajuda amb pipelines; l'humà valida seguretat i desplegament

## Metodologia (exigència de les classes)

### User Stories — format obligatori

```
AS A (QUI)
I WANT TO (QUÈ)
SO I CAN / IN ORDER TO (PER QUÈ)
```

**Exemple WRONG:** "I want to login using my username and password"
**Exemple RIGHT:** "I want to access my account"

Cada US té:
1. **Value statement** (format de dalt)
2. **Assumptes / Comments**
3. **Acceptance criteria**

### Acceptance criteria (AC)

- Cada US té **com a mínim 1** AC
- Es escriuen **abans** de la implementació
- Cada AC és **independentment testable**
- Resultat clar **Pass / Fall**
- Enfoc en el **Què** (resultat final), no el **Com** (aproximació tècnica)
- Incloure criteris funcionals i no funcionals quan sigui rellevant
- Les US **fines** detallen els passos de principi a fi amb les pantalles (per a l'equip i per a QA)

### INVEST (qualitat de cada US)

| Criteri | Significat |
|---------|------------|
| **I**ndependent | Una funció/necessitat per story |
| **N**egotiable | Oberta a discussió, sense solucions sobre-escrites |
| **V**aluable | Benefici clar per a l'usuari o el negoci |
| **E**stimable | Scope adequat per estimar esforç |
| **S**mall | Completable dins d'un sprint |
| **T**estable | Resultats verificables |

### Granularitat del backlog (Product Backlog DEEP)

| Granularitat | % del backlog | Detall |
|--------------|---------------|--------|
| **US fines** | Top 20% | AC amb passos de pantalla de principi a fi |
| **US mitjanes** | Següent 20% | AC clars i testables, sense detall de pantalles |
| **Èpiques** | Resta 60% | Àrees grans, es refinaran endavant |

**DEEP:**
- **D**etailed appropriately (el que cal per conversar i comprometre's)
- **E**mergent (creix i s'organitza amb nova informació)
- **E**stimated (en complexitat)
- **P**rioritized (ordenat per valor)

### Contingut del Product Backlog

- User stories
- Technical requirements
- Code spikes
- Technical debt
- Bugs
- (i la resta de feina: disseny, canvis, etc.)

### Estimació

- Les US **més rellevants** es estimen en **Story Points** i **Value Points**
- Permetre Sprint planning adequat

### Definition of Done (per cada sprint)

1. Tot el codi està checked in
2. Tot el developer test passa
3. Tot l'acceptance test passa
4. Help / doc text escrit
5. Product Owner accepta

### Backlog Review (checklist abans de lliurar)

- [ ] Cada US té com a mínim 1 AC
- [ ] Hi ha prou US per descriure el sistema
- [ ] Està utilitzant Trello
- [ ] El Product Backlog és DEEP
- [ ] Granularitat 20/20/60 respectada
- [ ] Tots els tipus d'ítems inclosos (US, bugs, debt, spikes, req. tècniques)
- [ ] Les US més rellevants estimades en SP + VP

## Estructura del projecte (repo GitHub)

Separar (com demana el curs):
- **Definició de producte** (backlog, docs, US)
- **Tasca de develop** (codi, branches, PRs)
- **CI/CD** (pipelines, desplegament)

## Documents del projecte

- `MEMORY.md` — decisions i flux de treball
- `plantejament.md` — notes de l'enfocament del projecte
- `trello-backlog.md` — cards per copiar a Trello (COM/VULL/PER + checklist AC)
- `PDFs/` — materials de classe

### Trello

Sense import automàtic. Copiat a mà des de `trello-backlog.md`:

1. Backlog → **+ Afegeix una tarjeta** → títol
2. Card → **Descripció** (COM/VULL/PER + assumptes + estimació)
3. **Checklist** → `Acceptance Criteria`
4. Labels (`Fina`/`Mitjana`, `P2`/`P6`, `Estalvi`/`Multidivisa`, `Èpica`…)

**Numeració:** `US-XX` **sencera** (sense decimals). P2 = Estalvi (US-17…20). P6 = Multidivisa (US-25…29).

## Directrius IA

- L'IA **accelera** execució, drafting de US, generació de tests, patterns
- L'humà **proporciona** intuïció d'enginyeria, visió de producte, arquitectura, decisions
- L'equip és l'**últim owner** de la tecnologia
- Quan s'usa IA per escriure US, l'equip les **valida** contra INVEST i el valor de mercat

## Codificació i IA (projecte)

L'estàndard d'arquitectura, skills, commits i PRs viu al **`AGENTS.md` arrel** del repo (i `README.md` per al resum).

- **Stack:** Vue 3 + TypeScript (frontend) · Firebase (backend)
- **MVVM:** Model · ModelView · View dins de cada feature
- **Clean Architecture** + **shared services** (capa middle)
- **Screaming Architecture** (carpetes per features de negoci)
- **SOLID** i **DRY**
- Skills AI lazy: `.claude/skills/` i `.opencode/skills/` (Vue, Firebase, gitflow…)
- Commits: Conventional Commits + `US-XX`
- Branches: `develop` = base de PR; `feature/<slug>`; `main` = demo/release
- PR: una US / una tasca tècnica per PR

Producte i backlog: aquest directori `docs/P1/`.
