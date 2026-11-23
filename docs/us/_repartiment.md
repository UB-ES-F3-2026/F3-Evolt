# Repartiment provisional · Sprint 2 (F3-Evolt)

> Document de treball (provisional fins a ratificació al Sprint Planning). Font: PDF *Tasques del Sprint 2* (31 tasques = 30 del sprint + TR06.3, **76 h** de 90 h) i rols finals confirmats pel PO.

**Per què aquesta estructura (3 línies):**
1. Les **31 h de pantalles** (29 h de fase G + la integració T14.4) requereixen **els dos frontend a tots els blocs**: cap bloc té un FE propi.
2. Per tant **les parelles es defineixen per ROL** (Frontend, Backend, QA, DevOps), no per bloc.
3. **Els blocs (Estalvi / Pagaments / Multidivisa) queden com a etiqueta** només per als rituals de revisió creuada (L0) i les cerimònies.

## 1. Taula d'equip (rols finals del PO)

| Membre | Handle | Rol tècnic | Rol Scrum | Parella |
|---|---|---|---|---|
| Martí Lázaro Bagué | @sudo-Itramplay | **Frontend** | **PO** | FRONTEND |
| Izan (Izan Farreny Heredia) | @IzanFarreny47 | **Frontend** | `[per confirmar — probablement SM]` | FRONTEND |
| Alicia | @Aliciaa415 | **Backend** | — | BACKEND |
| Junhao | @Junhaoozhang | **Backend** | — | BACKEND |
| Huabin (Fu Huabin) | @123huabin123 | **QA** | — | QA |
| Jiajun (Jiajun Wang) | @YAYUUUN | **DevOps** | — | DEVOPS |

## 2. Parelles per rol i hores

| Parella | Membres | Feina | Hores membres | Límit |
|---|---|---|---|---|
| **FRONTEND** | Martí (PO) + Izan | Totes les pantalles (29 de les 31 h FE; T26.2 → QA) + T14.4 | 14 + 15 = **29** | ≤30 ✔ |
| **BACKEND** | Alicia + Junhao | Contractes E i backend (29 de les 33 h BE; T19.1/T14.2 → DevOps, T26.1 → QA) | 15 + 14 = **29** | ≤30 ✔ |
| **QA** | Huabin | 6 revisions R (L0) + T26.1 + T26.2 (Huabin revisa també T20.3 amb Jiajun, que en porta l'hora) | **12** | ≤15 ✔ |
| **DEVOPS** | Jiajun | TR06.3 + T19.1 + T14.2 + T20.3 + T26.3 | **6** | ≤15 ✔ |
| **Total** | 6 | 31 tasques | **76** | 90 disponibles ✔ |

**Hores per persona (≤15 h):** Martí **14** · Izan **15** · Alicia **15** · Junhao **14** · Huabin **12** · Jiajun **6** = **76** ✔

## 3. Blocs com a etiqueta (ritual de revisió creuada, L0)

| Bloc (etiqueta) | Històries | Punts | Hores | Hores disp. | Revisió creuada (assignats de les R) |
|---|---|---|---|---|---|
| **Estalvi** | US-19, US-20, US-15 | 9 | 25 | 30 | Huabin (QA) + **Martí** (FE amb menys feina al bloc: 4 h vs 7 h d'Izan; T20.3 R va a Jiajun) |
| **Pagaments** | US-13, US-14 | 7 | 24 | 30 | Huabin (QA) + **Martí** (Izan hi ha fet les pantalles; Martí només la integració) |
| **Multidivisa** | US-25, US-26, US-27 | 11 | 26 | 30 | Huabin (QA) + **Izan** (no ha construït res del bloc; T26.3 R va a Jiajun, T25.4 i T27.3 segueixen sent de Huabin + Izan) |
| Pendent S1 | TR06.3 | — | 1 | — | — |
| **Total** | 8 històries | 27 | **76** | **90** | cap >15 h/persona ✔ |

*El desempat per al segon assignat de les R és «el FE que menys hi ha construït»; a Estalvi i Pagaments tots dos FEs hi toquen alguna cosa, a Multidivisa Izan no hi toca res. La revisió de PR de l'altre bloc segueix sent obligatòria (mode L0).*

## 4. Assignació provisional, tasca per tasca

| # | Tasca | Bloc | Fase | H | Responsable | R assignats (L0) |
|---|---|---|---|---|---|---|
| T19.1 | Contracte retirada/guardioles + proves | Estalvi | E | 2 | **Jiajun** (DevOps; doc + test-spec, no codi) | — |
| T19.2 | Retirada atòmica + historial (backend) | Estalvi | G | 3 | Junhao (BE) | — |
| T19.3 | Botó «Retirar» i pantalla | Estalvi | G | 3 | Izan (FE) | — |
| T19.4 | Revisar US-19 | Estalvi | **R · L0** | 1 | — | **Huabin + Martí** |
| T20.1 | Percentatge i «Objectiu assolit» (backend) | Estalvi | G | 2 | Junhao (BE) | — |
| T20.2 | Barra de progrés (detall + llista) | Estalvi | G | 4 | Martí (FE) | — |
| T20.3 | Revisar US-20 | Estalvi | **R · L0** | 1 | — | **Huabin + Jiajun** |
| T15.1 | Contracte de sol·licituds + proves | Estalvi | E | 1 | Junhao (BE) | — |
| T15.2 | Sol·licituds amb estats i caducitat (backend) | Estalvi | G | 3 | Junhao (BE) | — |
| T15.3 | Pantalles «Demanar diners» i «Sol·licituds enviades» | Estalvi | G | 4 | Izan (FE) | — |
| T15.4 | Revisar US-15 | Estalvi | **R · L0** | 1 | — | **Huabin + Martí** |
| T13.1 | Contracte cerca + enviaments + proves | Pagaments | E | 2 | Junhao (BE) | — |
| T13.2 | @usuari i cerca sense dades financeres (backend) | Pagaments | G | 3 | Junhao (BE) | — |
| T13.3 | Barra de cerca a «Enviar diners» | Pagaments | G | 3 | Izan (FE) | — |
| T13.4 | Revisar US-13 | Pagaments | **R · L0** | 1 | — | **Huabin + Martí** |
| T14.1 | Enviament atòmic amb límit diari (backend) | Pagaments | G | 5 | Alicia (BE) | — |
| T14.2 | Avisos «Has enviat» / «t'ha enviat» (backend) | Pagaments | G | 1 | Jiajun (DevOps, plumbing) | — |
| T14.3 | Pantalles «Pagaments», «Enviar» i «Confirmar» | Pagaments | G | 5 | Izan (FE) | — |
| T14.4 | Integrar enviament amb saldo d'Inici i moviments | Pagaments | I | 2 | Martí (FE, propietari d'Inici) | — |
| T14.5 | Revisar US-14 | Pagaments | **R · L0** | 2 | — | **Huabin + Martí** |
| T25.1 | Contracte subcomptes/eliminar/canvi + proves | Multidivisa | E | 2 | Alicia (BE) | — |
| T25.2 | Subcomptes en divisa i total en euros (backend) | Multidivisa | G | 4 | Alicia (BE) | — |
| T25.3 | Botó «Divises», llista i fila total a Inici | Multidivisa | G | 4 | Martí (FE) | — |
| T25.4 | Revisar US-25 | Multidivisa | **R · L0** | 2 | — | **Huabin + Izan** |
| T26.1 | Eliminar subcompte només amb saldo 0 (backend) | Multidivisa | G | 1 | Huabin (QA, amb tests) | — |
| T26.2 | Botó «Eliminar subcompte» amb 2 confirmacions (UI) | Multidivisa | G | 2 | Huabin (QA: escriu els diàlegs i els testa) | — |
| T26.3 | Revisar US-26 | Multidivisa | **R · L0** | 1 | — | **Jiajun + Izan** |
| T27.1 | Canvi atòmic amb tipus i comissió (backend) | Multidivisa | G | 4 | Alicia (BE) | — |
| T27.2 | Pantalles «Canviar» i resum | Multidivisa | G | 4 | Martí (FE) | — |
| T27.3 | Revisar US-27 | Multidivisa | **R · L0** | 2 | — | **Huabin + Izan** |
| TR06.3 | Auto-desplegament de main i prova (#144) | — | I | 1 | Jiajun (DevOps) | — |

**Totals:** Martí 14 (T20.2+T25.3+T27.2+T14.4) · Izan 15 (T19.3+T15.3+T13.3+T14.3) · Junhao 14 (T19.2+T20.1+T15.2+T13.2+T13.1+T15.1) · Alicia 15 (T14.1+T25.1+T25.2+T27.1) · Huabin 12 (9 R + T26.1 + T26.2) · Jiajun 6 (TR06.3+T19.1+T14.2+T20.3+T26.3) = **76** ✔ (cap >15).

## 5. Repartiment FrontEnd per fitxers (evitar conflictes)

| Persona | Àrea | Fitxers | Tasques |
|---|---|---|---|
| **Izan** | **Retirar · Sol·licituds · Enviar/Confirmar** | `PotView.vue` (Retirar); **nous**: vistes «Demanar diners»/«Sol·licituds enviades», «Pagaments», «Enviar», «Confirmar» (+ rutes) | T19.3, T15.3, T13.3, T14.3 |
| **Martí** | **Fila total d'Inici · Divises · Canviar** | `HomeView.vue` (**propietari únic d'Inici**: fila total, widget Divises, T14.4); **nous**: `DivisesView` (T25.3), vista «Canviar» (T27.2); `PotsView.vue`/`PotRow.vue` (barra, T20.2) | T20.2, T25.3, T27.2, T14.4 |

- `DivisesView.vue` el té Martí però la **T26.2** (botó «Eliminar» + 2 diàlegs) la fa **Huabin (QA)** → edit coordinada amb el propietari, mai tots dos alhora.
- T14.4 es fusiona **abans** que qualsevol canvi posterior d'Inici; components compartits (`MoneyAmount`, `PrimaryButton`, `AppShell`…) es toquen mínim; `router/index.ts` per ordre de fusió.

## 6. Rols Scrum

**PO (@sudo-Itramplay, Martí)**
- Accepta **al navegador** cada tasca R (8 R, mode L0) després que QA executi les proves.
- **Decisions bloquejants (ja decidides, a escriure als contractes):** (1) límit diari **1.000,00 €/dia** → abans de **T13.1**; (2) comissió **1,5 % (mín. 0,50 €)** → abans de **T25.1**; (3) `@usuari` = **part local del correu** → abans de T13.1.
- Backlog grooming + **regla 3-AC**: cada US amb ≥3 AC, escrits abans d'implementar, testables, Pass/Fall.

**Scrum Master `[per confirmar — probablement SM]` (Izan, sense confirmar)** — deures:
- Higiene del tauler (GitHub Project `IzanFarreny47/projects/2`: Backlog · To do · In progress · Review · Done; Trello `trello.com/b/LxXzo6NC/kanban`).
- **Límit WIP: Review ≤ 3 targetes** — abans d'obrir una PR nova, revisa la d'algú altre (README).
- **Sprint 2 check: Class 8 (17-18 nov)**; Class 9 (24-25 nov) = Demo S2 + Retro S2. Bloquejos i cerimònies (planning/daily/review/retro): hores `[per confirmar]`.

## 7. Camí crític i dependències

**Decisions del PO → contractes E (T19.1, T13.1, T25.1, T15.1) → backend G → pantalles → integració I (T14.4, TR06.3) → revisió R (L0, QA + FE creuat) → acceptació PO.**

| Bloqueja | Bloquejat per |
|---|---|
| Límit diari + `@usuari` | T13.1 → tot Pagaments |
| Comissió 1,5 % | T25.1 → tot Multidivisa |
| T19.1 / T13.1 / T25.1 / T15.1 (contractes) | backend del bloc → després pantalles; **T27.x depenen de la US-25** |
| T13.3 (cerca de la US-13) | **T15.3** (US-15 depèn de la cerca de la US-13) |
| T14.1 + T14.3 | **T14.4** (Inici) → es fusiona abans que qualsevol canvi posterior d'Inici |
| T25.2 (Divises existeix) | T26.2 (Huabin, `DivisesView`) |
| FE / BE / QA / DevOps | **paral·lels entre ells**; dins de cada fluxe E → G → I → R |

## 8. Pla de canvi i suports

**A ratificar al Sprint Planning:** parelles per rol (FE/BE/QA/DevOps); qui és **Scrum Master** (probablement Izan); valors de les 3 decisions del PO; hores de cerimònies; modes L0/L1/L2 (no definits al repo).

**Desviacions forçades (documentades):** 1) **T26.2 → Huabin**: FE a 14/15 h, sense marge per a 2 h més (Huabin ja fa el flux d'esborrat). 2) **T19.1 → Jiajun**: és `docs/api.md` + test-spec, no codi d'aplicació. 3) **T14.2 → Jiajun** (plumbing) i **T26.1 → Huabin** (tests): allibera 3 h del backend perquè cap BE passi de 15 h. 4) **Jiajun a 6 h** → suport CI/CD on-call i **fallback del parell BACKEND**.

**Plans de suport:**
- **QA (Huabin, 12 h):** proves dels 4 contractes (amb els autors) → proves de l'esborrat (T26.1) → diàlegs de confirmació (T26.2) → execució de l'acceptació al navegador de les 6 R en ordre de camí crític (Estalvi → Pagaments → Multidivisa) abans que el PO accepti.
- **DevOps (Jiajun, 6 h + on-call):** TR06.3 auto-desplegament de main i `/api/health`; T19.1 (contracte US-19/20); T14.2 notificacions; revisions R T20.3 (US-20) i T26.3 (US-26); CI/merge de les PR de contracte i verificació a Render.

**Si cau algú:** primer **es retorna la US-15 (9 h) al pendent** (buffer del PDF); després absorbeix el **fallback** nominat dins de 15 h: **FRONTEND → Jiajun** (9 h de marge) · **BACKEND → Jiajun** · **QA → Junhao** · **DEVOPS → Alicia**. Dues baixes → replanificació amb el PO.

## 9. Mapping per aplicar després

**Trello** (`https://trello.com/b/LxXzo6NC/kanban`) — ids per omplir:

| Targeta | Membres (owners de tasques) | id Trello |
|---|---|---|
| US-19, US-20 | @YAYUUUN, @Junhaoozhang, @IzanFarreny47, @sudo-Itramplay, @123huabin123 | `<trello-id-…>` |
| US-15 | @Junhaoozhang, @IzanFarreny47, @123huabin123, @sudo-Itramplay | `<trello-id-…>` |
| US-13, US-14 | @Junhaoozhang, @IzanFarreny47, @Aliciaa415, @YAYUUUN, @sudo-Itramplay, @123huabin123 | `<trello-id-…>` |
| US-25, US-26, US-27 | @Aliciaa415, @sudo-Itramplay, @123huabin123, @YAYUUUN | `<trello-id-…>` |
| TR06.3 (#144) | @YAYUUUN | `<trello-id-yayuuun>` |

**GitHub Issues #146–#175** (aplicats i verificats; un assignat per tasca, dues assignacions a les R):

```sh
gh issue edit 146 --add-assignee YAYUUUN                                 # T19.1
gh issue edit 147 --add-assignee Junhaoozhang                            # T19.2
gh issue edit 148 --add-assignee IzanFarreny47                           # T19.3
gh issue edit 149 --add-assignee 123huabin123 --add-assignee sudo-Itramplay   # T19.4 R
gh issue edit 150 --add-assignee Junhaoozhang                            # T20.1
gh issue edit 151 --add-assignee sudo-Itramplay                          # T20.2
gh issue edit 152 --add-assignee 123huabin123 --add-assignee YAYUUUN         # T20.3 R
gh issue edit 153 --add-assignee Junhaoozhang                            # T15.1
gh issue edit 154 --add-assignee Junhaoozhang                            # T15.2
gh issue edit 155 --add-assignee IzanFarreny47                           # T15.3
gh issue edit 156 --add-assignee 123huabin123 --add-assignee sudo-Itramplay   # T15.4 R
gh issue edit 157 --add-assignee Junhaoozhang                            # T13.1
gh issue edit 158 --add-assignee Junhaoozhang                            # T13.2
gh issue edit 159 --add-assignee IzanFarreny47                           # T13.3
gh issue edit 160 --add-assignee 123huabin123 --add-assignee sudo-Itramplay   # T13.4 R
gh issue edit 161 --add-assignee Aliciaa415                              # T14.1
gh issue edit 162 --add-assignee YAYUUUN                                 # T14.2
gh issue edit 163 --add-assignee IzanFarreny47                           # T14.3
gh issue edit 164 --add-assignee sudo-Itramplay                          # T14.4
gh issue edit 165 --add-assignee 123huabin123 --add-assignee sudo-Itramplay   # T14.5 R
gh issue edit 166 --add-assignee Aliciaa415                              # T25.1
gh issue edit 167 --add-assignee Aliciaa415                              # T25.2
gh issue edit 168 --add-assignee sudo-Itramplay                          # T25.3
gh issue edit 169 --add-assignee 123huabin123 --add-assignee IzanFarreny47   # T25.4 R
gh issue edit 170 --add-assignee 123huabin123                            # T26.1
gh issue edit 171 --add-assignee 123huabin123                            # T26.2
gh issue edit 172 --add-assignee YAYUUUN --add-assignee IzanFarreny47        # T26.3 R
gh issue edit 173 --add-assignee Aliciaa415                              # T27.1
gh issue edit 174 --add-assignee sudo-Itramplay                          # T27.2
gh issue edit 175 --add-assignee 123huabin123 --add-assignee IzanFarreny47   # T27.3 R
gh issue edit 144 --add-assignee YAYUUUN                                 # TR06.3 (pendent)
```

*Fonts: PDF Tasques del Sprint 2, rols finals del PO, `docs/P1/…`, `README.md` (WIP), `frontend/src/views/`, `gh api`. Cap git executat per a aquest document.*
