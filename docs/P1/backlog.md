# Product Backlog — P1 (Fintech + Gamificació)

> **Font única per a Trello.** Cada US és una card. Copiar la secció "Card Trello" al tauler.
>
> **Estat fins a Class 3:** Deliver Backlog. No s'assigna a sprint encara (Sprint 0 es planifica a la Class 3).
>
> **Enfoc de prioritat:** banca bàsica primer, després gamificació compartida. Dins de P2, les US de guardioles són el nucli.

---

## A. Resum del backlog (context de l'equip)

### Persones i blocs (de la taula de planificació)

| Persona | Bloc | Històries | Èpiques que refina |
|---------|------|-----------|-------------------|
| **P1** | Alta i primers passos | Registre, Verificació del codi, Inici de sessió, Recuperació de contrasenya, Recàrrega de prova | EP-14 Perfil i preferències |
| **P2** | Estalvi | Crear guardiola, Aportar, Retirar, Progrés i objectiu assolit | EP-12 Reptes i ratxes |
| **P3** | Pantalla principal i XP | Saldo a la pantalla principal, Guanyar XP, Nivells i perfil de progrés | EP-11 Insignies i recompenses, EP-15 Administració |
| **P4** | Moviments | Llistat de moviments, Filtres i cerca, Detall d'un moviment | EP-10 Anàlisi de despeses |
| **P5** | Social | Cercar un usuari, Sol·licitar diners, Respondre a una sol·licitud | EP-09 Despeses compartides, EP-13 Gamificació social |
| **P6** | Transferències | Enviar diners, Dades del compte (IBAN), Aportació periòdica | EP-06 Multidivisa |

### Numeració del backlog

Format `US-{persona}.{n}` on persona = P1…P6:

- `US-1.x` — P1 Alta i primers passos
- `US-2.x` — **P2 Estalvi** *(documentades a fons en aquest doc)*
- `US-3.x` — P3 Pantalla principal i XP
- `US-4.x` — P4 Moviments
- `US-5.x` — P5 Social
- `US-6.x` — P6 Transferències

### Granularitat (20% / 20% / 60%)

| Granularitat | US | On són |
|--------------|----|--------|
| **Fines** (AC amb pantalles) | Registre, Login, Saldo, Enviar diners, **Guardioles (P2)** | Detallades més avall o a refinar pel responsable |
| **Mitjanes** (AC clars) | Llistat moviments, Filtres, Detall moviment, Cercar usuari, Sol·licitar/Respondre, Progrés XP | Responsables de cada bloc |
| **Èpiques** | EP-06, EP-09, EP-10, EP-11, EP-12, EP-13, EP-14, EP-15 | Secció C |

### Prioritat de producte (ordre de valor)

1. **Banca bàsica** (P1 alta, P6 transferències, P3 saldo, P4 moviments) — sense això no hi ha app
2. **Estalvi guardioles (P2)** — nucli diferenciador de l'equip
3. **Gamificació compartida** (XP, nivells, insignies, reptes) — es connecta amb compres i estalvi

---

## B. US de P2 — Estalvi (detall complet)

> Granularitat **fina**: AC de principi a fi amb passos de pantalla. Són les històries d'aquest membre per a lliurar a la Class 3.

---

### US-2.1 Crear guardiola

**Valor (AS A / I WANT TO / SO I CAN):**

> Com a **usuari registrat**, vull **crear una guardiola amb nom i, opcionalment, un objectiu d'estalvi**, per tal de **separar diners per a una meta concreta i no gastar-los sense voler-ho**.

**Assumptes:**

- L'usuari ha d'estar registrat i amb sessió iniciada
- Mínim 1 guardiola per usuari a la demo
- L'objectiu (target) és opcional; si s'introdueix, ha de ser un import positiu
- La guardiola nova neix amb saldo 0
- Cada guardiola pot tenir nom, import objectiu i color/icona (opcional)
- No cal límit de guardioles a la demo (però el backlog pot afegir-ne un de 10 després)

**Acceptance Criteria:**

1. L'usuari és a la pantalla principal autenticat
2. Accedeix a la secció "Estalvi" / "Guardioles" (botó de la navegació o card de la home)
3. Es mostra la llista de guardioles; si no n'hi ha cap, estat buit amb CTA "Crear la primera guardiola"
4. L'usuari toca "Crear guardiola"
5. S'obre el formulari de creació amb camps: **nom** (obligatori), **import objectiu** (opcional), **color/icona** (opcional)
6. Omple el nom (ex. "Vacances") i, opcionalment, l'objectiu (ex. 500 €)
7. Toca "Crear"
8. **Validació frontend:**
   - Nom buit → error inline "El nom és obligatori"
   - Objectiu introduït ≤ 0 → error inline "L'import ha de ser positiu"
   - Objectiu no numèric → error inline "Introdueix un import vàlid"
9. **Èxit:** la nova guardiola apareix a la llista amb saldo 0 i, si hi ha objectiu, la barra de progrés al 0%
10. **Èxit:** l'usuari pot tornar a la pantalla principal i la guardiola es manté
11. **Error backend / xarxa:** missatge "No s'ha pogut crear la guardiola. Torna-ho a provar" i el formulari conserva les dades introduïdes
12. **No funcionals:** el formulari és usable en mòbil (camps grans, teclat adequat); el nom es desa tal com s'ha escrit (respecte majúscules/minúscules)

**Estimació:** 5 Story Points / 8 Value Points
**Prioritat:** Alta (nucli P2)
**INVEST:** ✔ Independent (només crear), ✔ Negotiable (UI negociable), ✔ Valuable, ✔ Estimable, ✔ Small, ✔ Testable

**Card Trello:**

```
Títol: US-2.1 Crear guardiola
Labels: Fina, Alta, Estalvi, P2
Description:
COM: a usuari registrat,
VULL: crear una guardiola amb nom i objectiu opcional
PER: estalviar per a una meta concreta.

Assumptes:
- L'usuari ha d'estar registrat i amb sessió iniciada
- Mínim 1 guardiola per usuari a la demo
- L'objectiu (target) és opcional; si s'introdueix, ha de ser un import positiu
- La guardiola nova neix amb saldo 0
- Cada guardiola pot tenir nom, import objectiu i color/icona (opcional)
- No cal límit de guardioles a la demo

Estimació: SP 5 · VP 8 · Prioritat Alta

Checklist "Acceptance Criteria":
Accedir a Estalvi/Guardioles des de la home
Veure llista o estat buit amb CTA
Obrir formulari (nom, objectiu opcional, color)
Validar nom obligatori i objectiu > 0
Crear guardiola amb saldo 0
Error xarxa no perd les dades
Funciona en mòbil
```

---

### US-2.2 Aportar diners a una guardiola

**Valor (AS A / I WANT TO / SO I CAN):**

> Com a **usuari amb guardioles**, vull **aportar un import des del meu saldo principal a una guardiola**, per tal de **posar diners al costat per assolir el meu objectiu sense que surtin del compte principal**.

**Assumptes:**

- L'usuari té almenys 1 guardiola creada (US-2.1)
- L'usuari té saldo principal suficient (o la comprovació ho gestiona)
- L'aportació mou saldo: principal ↓, guardiola ↑
- Es registra un moviment dins de la guardiola (i es reflecteix al llistat de moviments si P4 ho mostra)
- Import mínim d'aportació: > 0

**Acceptance Criteria:**

1. L'usuari és a la llista de guardioles o al detall d'una guardiola
2. Selecciona una guardiola i toca "Aportar"
3. S'obre la pantalla d'aportació amb: camp d'import, saldo disponible del compte principal visible, resum de la guardiola destí
4. Introdueix un import (ex. 50 €)
5. Toca "Confirmar aportació"
6. **Validació:**
   - Import ≤ 0 → error "Introdueix un import positiu"
   - Import > saldo principal → error "Saldo insuficient al compte principal"
   - Import no numèric → error "Introdueix un import vàlid"
7. **Èxit:** la guardiola mostra el nou saldo (anterior + import); el saldo principal disminueix en el mateix import
8. **Èxit:** es mostra confirmació "Has aportat 50 € a Vacances"
9. **Èxit:** el moviment queda registrat (data, import, tipus "Aportació", guardiola destí)
10. **Èxit:** des de la home, l'usuari veu el saldo principal actualitzat
11. **Error backend:** missatge "No s'ha pogut completar l'aportació. Torna-ho a provar" i cap saldo s'ha modificat (consistència)
12. **No funcionals:** l'operació de saldo és atòmica (o bé completa tota, o bé cap canvi)

**Estimació:** 5 Story Points / 8 Value Points
**Prioritat:** Alta (nucli P2, sense això les guardioles no serveixen)
**INVEST:** ✔ Independent, ✔ Negotiable, ✔ Valuable, ✔ Estimable, ✔ Small, ✔ Testable

**Card Trello:**

```
Títol: US-2.2 Aportar diners a una guardiola
Labels: Fina, Alta, Estalvi, P2
Description:
COM: a usuari amb guardioles,
VULL: aportar diners des del saldo principal a una guardiola
PER: estalviar cap a un objectiu sense gastar-los del compte principal.

Assumptes:
- L'usuari té almenys 1 guardiola creada (US-2.1)
- L'usuari té saldo principal suficient (o la comprovació ho gestiona)
- L'aportació mou saldo: principal ↓, guardiola ↑
- Es registra un moviment dins de la guardiola
- Import mínim d'aportació: > 0

Estimació: SP 5 · VP 8 · Prioritat Alta

Checklist "Acceptance Criteria":
Seleccionar guardiola i tocar "Aportar"
Veure saldo principal i destí
Validar import > 0 i <= saldo principal
Saldo principal ↓ i guardiola ↑
Confirmació visible
Moviment registrat
Error backend no canvia saldos
Operació atòmica
```

---

### US-2.3 Retirar diners d'una guardiola

**Valor (AS A / I WANT TO / SO I CAN):**

> Com a **usuari amb guardioles**, vull **retirar un import d'una guardiola al meu saldo principal**, per tal de **fer servir els diners estalviats quan els necessiti sense perdre el control de les metes**.

**Assumptes:**

- L'usuari té almenys 1 guardiola amb saldo > 0 (o la gestió d'errors ho cobreix)
- La retirada mou saldo: guardiola ↓, principal ↑
- Es registra un moviment de retirada
- Import mínim de retirada: > 0
- No es pot retirar més del que té la guardiola

**Acceptance Criteria:**

1. L'usuari és al detall d'una guardiola amb saldo > 0
2. Toca "Retirar"
3. S'obre la pantalla de retirada amb: camp d'import, saldo de la guardiola visible
4. Introdueix un import (ex. 20 €)
5. Toca "Confirmar retirada"
6. **Validació:**
   - Import ≤ 0 → error "Introdueix un import positiu"
   - Import > saldo de la guardiola → error "Saldo insuficient a la guardiola"
   - Guardiola a 0 → CTA desactivat o error "Aquesta guardiola està buida"
7. **Èxit:** la guardiola mostra el nou saldo (anterior − import); el saldo principal augmenta en el mateix import
8. **Èxit:** es mostra confirmació "Has retirat 20 € de Vacances"
9. **Èxit:** el moviment queda registrat (data, import, tipus "Retirada", guardiola origen)
10. **Èxit:** des de la home, l'usuari veu el saldo principal actualitzat
11. **Error backend:** missatge "No s'ha pogut completar la retirada. Torna-ho a provar" i cap saldo s'ha modificat
12. **No funcionals:** operació atòmica; si l'objectiu es trenca per la retirada, no cal bloquejar (això és EP-12 més endavant)

**Estimació:** 3 Story Points / 6 Value Points
**Prioritat:** Alta (complementa US-2.2; cicle complet d'estalvi)
**INVEST:** ✔ Independent, ✔ Negotiable, ✔ Valuable, ✔ Estimable, ✔ Small, ✔ Testable

**Card Trello:**

```
Títol: US-2.3 Retirar diners d'una guardiola
Labels: Fina, Alta, Estalvi, P2
Description:
COM: a usuari amb guardioles,
VULL: retirar diners d'una guardiola al saldo principal
PER: fer servir els diners estalviats quan els necessiti.

Assumptes:
- L'usuari té almenys 1 guardiola amb saldo > 0
- La retirada mou saldo: guardiola ↓, principal ↑
- Es registra un moviment de retirada
- Import mínim de retirada: > 0
- No es pot retirar més del que té la guardiola

Estimació: SP 3 · VP 6 · Prioritat Alta

Checklist "Acceptance Criteria":
Des de detall guardiola, tocar "Retirar"
Veure saldo de la guardiola
Validar import > 0 i <= saldo guardiola
Guardiola ↓ i principal ↑
Confirmació visible
Moviment registrat
Error backend no canvia saldos
Guardiola buida no permet retirar
```

---

### US-2.4 Veure progrés i objectiu assolit

**Valor (AS A / I WANT TO / SO I CAN):**

> Com a **usuari amb guardioles amb objectiu**, vull **veure el progrés cap a cada objectiu i saber quan l'he assolit**, per tal de **mantenir la motivació d'estalviar i celebrar les metes**.

**Assumptes:**

- La guardiola pot tenir objectiu o no; sense objectiu, no es mostra barra de progrés (només saldo)
- Progrés = saldo actual / objectiu, en percentatge (arrodonit a l'enter)
- Quan saldo ≥ objectiu → estat "objectiu assolit"
- Es connecta amb gamificació endavant (EP-11/EP-12): la demo pot mostrar un badge senzill o un missatge d'enhorabona
- La llista de guardioles mostra mini-progrés si hi ha objectiu

**Acceptance Criteria:**

1. L'usuari és al detall d'una guardiola **amb** objectiu definit
2. Es mostra: saldo actual, objectiu, **barra de progrés** i **percentatge** (ex. 120 € / 500 € → 24%)
3. La barra reflecteix visualment el percentatge (0% buida, 100% plena)
4. Quan el saldo és **inferior** a l'objectiu, l'estat és "En progrés"
5. Quan el saldo és **igual o superior** a l'objectiu, l'estat canvia a **"Objectiu assolit"** (badge o text destacat +, si hi ha gamificació preparada, notificació/celebració)
6. A la **llista de guardioles**, cada guardiola amb objectiu mostra saldo + mini barra o % ; les sense objectiu mostren saldo sol
7. Si l'usuari **no** ha posat objectiu, al detall no es mostra barra ni %, només saldo i operacions (aportar/retirar)
8. El progrés s'actualitza després d'una aportació (US-2.2) o retirada (US-2.3) sense necessitat de re-carregar manualment (o amb refresh explícit acceptable a la demo)
9. **Error / buit:** guardiola sense dades de progrés no mostra barra trencada; mostra saldo correcte
10. **No funcionals:** la barra és llegible en mòbil; el % es mostra com a text accessible (no només color)

**Estimació:** 3 Story Points / 5 Value Points
**Prioritat:** Mitjana-Alta (tancar el cicle P2; connector amb gamificació)
**INVEST:** ✔ Independent, ✔ Negotiable, ✔ Valuable, ✔ Estimable, ✔ Small, ✔ Testable

**Card Trello:**

```
Títol: US-2.4 Veure progrés i objectiu assolit
Labels: Fina, Alta, Estalvi, P2
Description:
COM: a usuari amb guardioles amb objectiu,
VULL: veure el progrés cap a cada objectiu i saber quan l'he assolit
PER: mantenir la motivació d'estalviar i celebrar les metes.

Assumptes:
- La guardiola pot tenir objectiu o no; sense objectiu, no es mostra barra
- Progrés = saldo actual / objectiu, en percentatge (arrodonit a l'enter)
- Quan saldo ≥ objectiu → estat "objectiu assolit"
- Es connecta amb gamificació endavant (EP-11/EP-12)
- La llista de guardioles mostra mini-progrés si hi ha objectiu

Estimació: SP 3 · VP 5 · Prioritat Alta

Checklist "Acceptance Criteria":
Detall guardiola amb objectiu mostra saldo, objectiu, barra i %
Barra reflecteix el percentatge
Estat "En progrés" si saldo < objectiu
Estat "Objectiu assolit" si saldo >= objectiu
Llista mostra mini-progrés
Sense objectiu, no es mostra barra
S'actualitza després d'aportar/retirar
% accessible com a text
```

---

## C. Èpiques (refinament P2 i connexons)

> Granularitat èpica (60% del backlog). Es detallen quan arribin els sprints corresponents.

| ID | Títol | Relació amb P2 | Què pot incloure endavant |
|----|-------|----------------|---------------------------|
| **EP-12** | Reptes i ratxes | Refina P2 | Reptes d'estalvi (ex. "Aporta 3 vegades aquesta setmana"), ratxes d'estalvi diari, XP per aportar |
| **EP-11** | Insignies i recompenses | Es connecta amb guardioles | Insignia "Primera guardiola", "Objectiu assolit", recompenses per estalvi consistent |
| **EP-13** | Gamificació social | Endavant | Comparar progrés d'estalvi amb altres usuaris (si P5 ho permet) |
| **EP-06** | Multidivisa | Endavant | Guardioles en altres divises (si es vol més endavant) |
| **EP-09** | Despeses compartides | Endavant | Guardioles compartides |
| **EP-10** | Anàlisi de despeses | P4 | Categorització de moviments d'aportació/retirada |
| **EP-14** | Perfil i preferències | P1 | Configuració d'usuari que afecta estalvi |
| **EP-15** | Administració | P3 | Vistes admin/demo per gestionar usuaris i dades |

---

## D. Ítems no-US (per complir DEEP)

> El Product Backlog ha d'incloure més que US. Aquesta secció és el contenidor; s'omple quan sorgeixin.

### Technical requirements (placeholders)

- TR-01: Persistència de guardioles i saldos (DB + API)
- TR-02: Autenticació de sessió abans d'operar estalvi
- TR-03: Transaccions atòmiques en aportar/retirar
- TR-04: Model de dades: User, Account, SavingPot, Transaction
- TR-05: CI/CD pipeline (GitHub Actions o similar)
- TR-06: Entorn de demo desplegable

### Code spikes (placeholders)

- Spike-01: Decisió de stack frontend/backend (pendent a Sprint 0)
- Spike-02: Com integrar XP/gamificació al model de transaccions

### Technical debt (placeholders)

- TD-01: Validació de formularis només frontend (moure a backend)
- TD-02: Sense testos d'integració de saldo encara

### Bugs

- (buit fins que hi hagi demo)

### Canvis de disseny / altres

- DS-01: Mockups de guardioles (Figma o similar) abans de Sprint 1
- DS-02: Flows de confirmació i error (copywriting de missatges)

---

## E. Trello

Font de les cards: **`trello-backlog.md`** (un sol fitxer).

### Automàtic

```sh
python3 import_trello.py
```

Demana API key (https://trello.com/app-key) + token + URL del tauler. Després crea tot: cards, labels i checklists.

### Manual

1. Obrir `trello-backlog.md`
2. Enganxar **TÍTOLS** a la columna Backlog
3. Per cada card: **Descripció** + **Checklist Acceptance Criteria**

### Ordre de les cards P2

1. US-2.1 Crear guardiola — Fina, Alta, Estalvi, P2 — SP 5 / VP 8
2. US-2.2 Aportar diners a una guardiola — Fina, Alta, Estalvi, P2 — SP 5 / VP 8
3. US-2.3 Retirar diners d'una guardiola — Fina, Alta, Estalvi, P2 — SP 3 / VP 6
4. US-2.4 Veure progrés i objectiu assolit — Fina, Alta, Estalvi, P2 — SP 3 / VP 5
5. EP-12 Reptes i ratxes — Èpica, P2
6. EP-11 Insignies i recompenses — Èpica, Estalvi
7. TR-05 / TR-06 / Spike-01 — Tech, Sprint 0

---

## Checkpoint abans de la Class 3 (Deliver Backlog)

- [ ] Aquest `backlog.md` és la font de veritat
- [ ] Les 4 US de P2 són a Trello amb AC i estimació
- [ ] Èpiques EP-11 i EP-12 a Trello com a cards d'èpica
- [ ] TR-05, TR-06, Spike-01 a Trello (base per a Sprint 0)
- [ ] Cada membre pot explicar les seves US (value + AC)
- [ ] Granularitat 20/20/60 visible al tauler (fines vs mitjanes vs èpiques)
- [ ] El PO accepta el backlog com a punt de partida
- [ ] GitHub: repo creat, estructura producte vs develop separada
