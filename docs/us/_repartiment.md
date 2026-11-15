# Repartiment provisional · Sprint 2 (F3-Evolt)

> Document de treball (provisional fins a ratificació al Sprint Planning). Font: PDF *Tasques del Sprint 2* (31 tasques = 30 del sprint + TR06.3, **76 h** de 90 h disponibles) i rols finals confirmats pel PO. Regles: ≤15 h/persona, ≤30 h/parella-bloc, revisions creuades del PDF (**mode L0**).

## 1. Taula d'equip (rols finals del PO)

| Membre | Handle | Rol tècnic | Rol Scrum | Parella |
|---|---|---|---|---|
| Martí Lázaro Bagué | @sudo-Itramplay | **Frontend** | **PO** | C |
| Izan (Izan Farreny Heredia) | @IzanFarreny47 | **Frontend** | `[per confirmar — probablement SM]` | B |
| Alicia | @Aliciaa415 | **Backend** | — | B |
| Junhao | @Junhaoozhang | **Backend** | — | A |
| Huabin (Fu Huabin) | @123huabin123 | **QA** | — | A |
| Jiajun (Jiajun Wang) | @YAYUUUN | **DevOps** | — | C |

## 2. Parelles (role-balanced), blocs i hores

| Parella | Membres | Bloc | Històries | Punts | Hores bloc | Disp. | Marge | Hores dels membres |
|---|---|---|---|---|---|---|---|---|
| **A** | Huabin (QA) + Junhao (BE) | **Estalvi** | US-19, US-20, US-15 | 9 | 25 | 30 | 5 | 15 + 13 = **28** ≤30 |
| **B** | Izan (FE) + Alicia (BE) | **Pagaments** | US-13, US-14 | 7 | 24 | 30 | 6 | 15 + 14 = **29** ≤30 |
| **C** | Martí (FE, PO) + Jiajun (DevOps) | **Multidivisa** + TR06.3 | US-25, US-26, US-27 | 11 | 26 (+1) | 30 | 4 | 14 + 5 = **19** ≤30 |
| **Total** | 6 persones | 3 blocs | 8 històries | 27 | **76** | **90** | 14 | **76** |

- Revisió creuada (PDF): **A revisa B · B revisa C · C revisa A** — la revisió de PR de la parella creuada és **obligatòria**, encara que l'hora de la tasca R es compti a QA.
- Les hores de tasca s'assignen **per rol a nivell d'sprint** (només hi ha 2 FE i 2 BE): la parella és l'estructura de bloc i de revisió, no un límit de tasques.
- US-15 es queda a Estalvi (a Pagaments serien 33 h > 30 h).

**Hores per persona (≤15 h):** Huabin **15** · Jiajun **5** · Junhao **13** · Alicia **14** · Izan **15** · Martí **14** → **76** ✔

## 3. Assignació provisional, tasca per tasca (mode L0 a les R)

| # | Tasca | Fase | H | Responsable | Revisió creuada |
|---|---|---|---|---|---|
| T19.1 | Contracte retirada/guardioles + proves | E | 2 | Junhao (1, contracte) + Jiajun (1, CI PR) | C |
| T19.2 | Retirada atòmica + historial (backend) | G | 3 | Junhao (BE) | — |
| T19.3 | Botó «Retirar» i pantalla | G | 3 | Izan (FE) | — |
| T19.4 | Revisar US-19 | **R · L0** | 1 | Huabin (QA) | **C** (+ Martí) |
| T20.1 | Percentatge i «Objectiu assolit» (backend) | G | 2 | Junhao (BE) | — |
| T20.2 | Barra de progrés (detall + llista) | G | 4 | Martí (FE) | — |
| T20.3 | Revisar US-20 | **R · L0** | 1 | Huabin (QA) | **C** (+ Martí) |
| T15.1 | Contracte de sol·licituds + proves | E | 1 | Huabin (QA, proves d'acceptació) | C |
| T15.2 | Sol·licituds amb estats i caducitat (backend) | G | 3 | Junhao (BE) | — |
| T15.3 | Pantalles «Demanar diners» i «Sol·licituds enviades» | G | 4 | Izan (FE) | — |
| T15.4 | Revisar US-15 | **R · L0** | 1 | Huabin (QA) | **C** (+ Martí) |
| T13.1 | Contracte cerca + enviaments + proves | E | 2 | Junhao (1, contracte) + Jiajun (1, CI PR) | A |
| T13.2 | @usuari i cerca sense dades financeres (backend) | G | 3 | Junhao (BE) | — |
| T13.3 | Barra de cerca a «Enviar diners» | G | 3 | Izan (FE) | — |
| T13.4 | Revisar US-13 | **R · L0** | 1 | Huabin (QA) | **A** (+ Junhao) |
| T14.1 | Enviament atòmic amb límit diari (backend) | G | 5 | Alicia (BE) | — |
| T14.2 | Avisos «Has enviat» / «t'ha enviat» (backend) | G | 1 | Jiajun (DevOps, plumbing) | — |
| T14.3 | Pantalles «Pagaments», «Enviar» i «Confirmar» | G | 5 | Izan (FE) | — |
| T14.4 | Integrar enviament amb saldo d'Inici i moviments | I | 2 | Martí (FE, propietari d'Inici) | — |
| T14.5 | Revisar US-14 | **R · L0** | 2 | Huabin (QA) | **A** (+ Junhao) |
| T25.1 | Contracte subcomptes/eliminar/canvi + proves | E | 2 | Alicia (1, contracte) + Jiajun (1, CI PR) | B |
| T25.2 | Subcomptes en divisa i total en euros (backend) | G | 4 | Alicia (BE) | — |
| T25.3 | Botó «Divises», llista i fila total a Inici | G | 4 | Martí (FE) | — |
| T25.4 | Revisar US-25 | **R · L0** | 2 | Huabin (QA) | **B** (+ Izan) |
| T26.1 | Eliminar subcompte només amb saldo 0 (backend) | G | 1 | Huabin (QA, amb tests) | — |
| T26.2 | Botó «Eliminar subcompte» amb confirmacions | G | 2 | Huabin (QA, diàlegs + tests) | — |
| T26.3 | Revisar US-26 | **R · L0** | 1 | Huabin (QA) | **B** (+ Izan) |
| T27.1 | Canvi atòmic amb tipus i comissió (backend) | G | 4 | Alicia (BE) | — |
| T27.2 | Pantalles «Canviar» i resum | G | 4 | Martí (FE) | — |
| T27.3 | Revisar US-27 | **R · L0** | 2 | Huabin (QA) | **B** (+ Izan) |
| TR06.3 | Auto-desplegament de main i prova (#144) | I | 1 | Jiajun (DevOps) | — |

**Comprovació de regles:** contractes E → BE (Junhao/Alicia) ✔ · pantalles → FE (Izan/Martí) ✔ excepte **T26.2 → Huabin** (forçat: el FE donaria 15,5 h cadascun; és el candidat que el PO va indicar per moure) ✔documentat · R → QA Huabin + parella creuada (L0) ✔ · T14.4 → FE Martí ✔.

**Totals:** Huabin 15 (11 R + T15.1 1 + T26.1 1 + T26.2 2) · Jiajun 5 (TR06.3 + T14.2 + 1 h CI × 3 PR de contracte) · Junhao 13 · Alicia 14 · Izan 15 · Martí 14 = **76** ✔ (cap >15) · Desviacions respecte al repartiment ideal documentades a §7.

## 4. Repartiment FrontEnd per fitxers (evitar conflictes)

| Persona | Àrea (decisió del PO) | Fitxers | Tasques |
|---|---|---|---|
| **Izan** (B) | **Retirar · Enviar/Confirmar · Sol·licituds** | `PotView.vue` (Retirar); **nous**: vistes «Demanar diners»/«Sol·licituds enviades», «Pagaments», «Enviar», «Confirmar» (+ rutes) | T19.3, T15.3, T13.3, T14.3 |
| **Martí** (C) | **Fila total d'Inici · Divises · Canviar** | `HomeView.vue` (**propietari únic d'Inici**: fila total, widget Divises i T14.4); **nous**: `DivisesView` (T25.3), vista «Canviar» (T27.2); `PotsView.vue`/`PotRow.vue` (barra, T20.2) | T20.2, T25.3, T27.2, T14.4 |

- `DivisesView.vue` el té Martí però la T26.2 (botó «Eliminar») la fa **Huabin (QA)** → edit coordinada amb el propietari (mai tots dos alhora).
- T14.4 es fusiona **abans** que qualsevol canvi posterior d'Inici; components compartits (`MoneyAmount`, `PrimaryButton`, `AppShell`…) es toquen mínim; `router/index.ts` per ordre de fusió.

## 5. Rols Scrum

**PO (@sudo-Itramplay, Martí)**
- Accepta **al navegador** cada tasca R (8 R, mode L0) després que QA executi les proves: «Les proves passen i el PO l'accepta al navegador».
- **Decisions bloquejants (ja decidides, a escriure als contractes):** (1) límit diari **1.000,00 €/dia** → abans de **T13.1**; (2) comissió **1,5 % (mín. 0,50 €)** → abans de **T25.1**; (3) `@usuari` = **part local del correu** → abans de T13.1.
- Backlog grooming + **regla 3-AC**: cada US amb ≥3 AC, escrits abans d'implementar, testables, Pass/Fall.

**Scrum Master `[per confirmar — probablement SM]` (Izan, sense confirmar)** — deures:
- Higiene del tauler (GitHub Project `IzanFarreny47/projects/2`: Backlog · To do · In progress · Review · Done; Trello `trello.com/b/LxXzo6NC/kanban`).
- **Límit WIP: Review ≤ 3 targetes** — abans d'obrir una PR nova, revisa la d'algú altre (README).
- **Sprint 2 check: Class 8 (17-18 nov)**; Class 9 (24-25 nov) = Demo S2 + Retro S2. Bloquejos i cerimònies (planning/daily/review/retro): hores `[per confirmar]`.

## 6. Camí crític i dependències

**Decisions del PO → contractes E (T19.1, T13.1, T25.1, T15.1) → backend G → pantalles → integració I (T14.4, TR06.3) → revisió R (L0, QA) → acceptació PO.**

| Bloqueja | Bloquejat per |
|---|---|
| Límit diari + `@usuari` | T13.1 → tot Pagaments |
| Comissió 1,5 % | T25.1 → tot Multidivisa |
| T19.1 / T13.1 / T25.1 (contractes) | T19.2/T20.1 · T13.2/T13.3 · T25.2/T25.3 → T26.x i **T27.x depenen de la US-25** |
| T13.3 (cerca de la US-13) | **T15.3** (US-15 depèn de la cerca de la US-13) |
| T14.1 + T14.3 | **T14.4** (Inici) → es fusiona abans que qualsevol canvi posterior d'Inici |
| T25.2 (Divises existeix) | T26.2 (Huabin, `DivisesView`) |
| Parelles A, B, C | **paral·leles entre si**; dins de cada fluxe E → G → I → R |

## 7. Pla de canvi i deviations

**A ratificar al Sprint Planning:** parelles A/B/C (role-balanced); qui és **Scrum Master** (probablement Izan); valors de les 3 decisions del PO; hores de cerimònies; modes L0/L1/L2 (no definits al repo).

**Desviacions forçades (documentades):**
1. **T26.2 (2 h) → Huabin (QA):** el FE donaria 15,5 h/persona; Izan ja és a 15 i Martí a 14. Huabin implementa els diàlegs amb els seus tests, coordinat amb Martí (propietari de `DivisesView`).
2. **T26.1 (1 h) → Huabin** (no Izan): Izan al límit de 15 h → «unavoidable» segons el PO.
3. **T15.1 (1 h) → Huabin:** proves d'acceptació del contracte de sol·licituds (el PO ja va escriure les specs).
4. **Jiajun: 1 h de CI per PR de contracte a T19.1/T13.1/T25.1** (T15.1 el gestiona QA); on-call per a la 4a PR.

**Si cau algú:** la parella restant assumeix el bloc; primer **es retorna la US-15 (9 h) al pendent** (buffer del PDF); després absorbeix el **fallback** nominat dins de 15 h: **A → Jiajun** (10 h de marge) · **B → Junhao** · **C → Alicia**. Dues baixes → replanificació amb el PO.

**Plans de suport:**
- **QA (Huabin, 15 h):** 1) proves dels contractes — T15.1 pròpia + revisió de les de T19.1/T13.1/T25.1 amb els autors; 2) proves de l'esborrat (T26.1); 3) diàlegs de confirmació (T26.2); 4) execució de l'acceptació al navegador de les 8 R en ordre de camí crític (Estalvi → Pagaments → Multidivisa) abans que el PO accepti.
- **DevOps (Jiajun, 5 h + on-call):** TR06.3 auto-desplegament de main i `/api/health`; T14.2 notificacions; CI/merge de les PR de contracte; verificació del desplegament a Render. **Molt infrapassat (5/15) → fallback del parell de backend (Alicia + Junhao).**

## 8. Mapping per aplicar després

**Trello** (`https://trello.com/b/LxXzo6NC/kanban`) — ids per omplir:

| Targeta | Membres (owners de tasques) | id Trello |
|---|---|---|
| US-19, US-20 | @Junhaoozhang, @IzanFarreny47, @123huabin123, @YAYUUUN, @sudo-Itramplay | `<trello-id-…>` |
| US-15 | @123huabin123, @Junhaoozhang, @IzanFarreny47 | `<trello-id-…>` |
| US-13, US-14 | @Junhaoozhang, @YAYUUUN, @IzanFarreny47, @Aliciaa415, @sudo-Itramplay, @123huabin123 | `<trello-id-…>` |
| US-25, US-26, US-27 | @Aliciaa415, @YAYUUUN, @sudo-Itramplay, @123huabin123 | `<trello-id-…>` |
| TR06.3 (#144) | @YAYUUUN | `<trello-id-yayuuun>` |

**GitHub Issues #146–#175** (aplicats; `<N>` = número):

```sh
gh issue edit 146 --add-assignee Junhaoozhang --add-assignee YAYUUUN     # T19.1
gh issue edit 147 --add-assignee Junhaoozhang                            # T19.2
gh issue edit 148 --add-assignee IzanFarreny47                           # T19.3
gh issue edit 149 --add-assignee 123huabin123 --add-assignee sudo-Itramplay   # T19.4 R (L0)
gh issue edit 150 --add-assignee Junhaoozhang                            # T20.1
gh issue edit 151 --add-assignee sudo-Itramplay                          # T20.2
gh issue edit 152 --add-assignee 123huabin123 --add-assignee sudo-Itramplay   # T20.3 R (L0)
gh issue edit 153 --add-assignee 123huabin123                            # T15.1
gh issue edit 154 --add-assignee Junhaoozhang                            # T15.2
gh issue edit 155 --add-assignee IzanFarreny47                           # T15.3
gh issue edit 156 --add-assignee 123huabin123 --add-assignee sudo-Itramplay   # T15.4 R (L0)
gh issue edit 157 --add-assignee Junhaoozhang --add-assignee YAYUUUN     # T13.1
gh issue edit 158 --add-assignee Junhaoozhang                            # T13.2
gh issue edit 159 --add-assignee IzanFarreny47                           # T13.3
gh issue edit 160 --add-assignee 123huabin123 --add-assignee Junhaoozhang    # T13.4 R (L0)
gh issue edit 161 --add-assignee Aliciaa415                              # T14.1
gh issue edit 162 --add-assignee YAYUUUN                                 # T14.2
gh issue edit 163 --add-assignee IzanFarreny47                           # T14.3
gh issue edit 164 --add-assignee sudo-Itramplay                          # T14.4
gh issue edit 165 --add-assignee 123huabin123 --add-assignee Junhaoozhang    # T14.5 R (L0)
gh issue edit 166 --add-assignee Aliciaa415 --add-assignee YAYUUUN       # T25.1
gh issue edit 167 --add-assignee Aliciaa415                              # T25.2
gh issue edit 168 --add-assignee sudo-Itramplay                          # T25.3
gh issue edit 169 --add-assignee 123huabin123 --add-assignee IzanFarreny47   # T25.4 R (L0)
gh issue edit 170 --add-assignee 123huabin123                            # T26.1
gh issue edit 171 --add-assignee 123huabin123                            # T26.2
gh issue edit 172 --add-assignee 123huabin123 --add-assignee IzanFarreny47   # T26.3 R (L0)
gh issue edit 173 --add-assignee Aliciaa415                              # T27.1
gh issue edit 174 --add-assignee sudo-Itramplay                          # T27.2
gh issue edit 175 --add-assignee 123huabin123 --add-assignee IzanFarreny47   # T27.3 R (L0)
gh issue edit 144 --add-assignee YAYUUUN                                 # TR06.3 (pendent)
```

*Fonts: PDF Tasques del Sprint 2, rols finals del PO, `docs/P1/…`, `README.md` (WIP), `frontend/src/views/`, `gh api`. Cap git executat per a aquest document.*
