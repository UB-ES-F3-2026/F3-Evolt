# Proves d'acceptació · Multidivisa (US-25, US-26 i US-27)

Proves d'acceptació de les històries de multidivisa, escrites a partir de `docs/us/US-25.md`, `US-26.md` i `US-27.md`, dels criteris de les issues #186, #187 i #188, i del contracte de l'[apartat 12 de `docs/api.md`](api.md#12-multidivisa-subcomptes-i-canvi-us-25-us-26-i-us-27). Tasca: T25.1 (issue #166).

## Índex

1. [Com fer servir aquest document](#com-fer-servir-aquest-document)
2. [Dades de partida](#dades-de-partida)
3. [US-25 · Afegir subcompte en divisa](#us-25--afegir-subcompte-en-divisa)
4. [US-26 · Eliminar subcompte en divisa](#us-26--eliminar-subcompte-en-divisa)
5. [US-27 · Canviar entre divises](#us-27--canviar-entre-divises)
6. [Criteris d'acceptació i proves](#criteris-dacceptació-i-proves)

---

## Com fer servir aquest document

Cada història té dues taules:

- **API:** proves del backend. Cada fila es converteix en un test de pytest a la tasca indicada, amb l'identificador de la fila al nom del test (skill `qa-strategy`). Els valors esperats són els d'aquestes taules, escrits tal qual: no es tornen a calcular amb el codi que es prova.
- **Pantalla:** proves del frontend. Es comproven a mà amb l'app arrencada contra el backend real i, quan es pugui, amb un test de Vitest del ViewModel.

L'usuari de cada petició és el de la sessió (`Authorization: Bearer`, [`api.md` §8.2](api.md#82-sessió)). «Usuari 1» és `demo@evolt.test` i «usuari 2», `buit@evolt.test`, totes dues amb la contrasenya `Evolt2026` (P13).

Sense botó «Aportar», un subcompte només té saldo i moviments si s'hi fa un canvi (US-27). Per això:

- **A pytest**, les proves de la US-26 que en necessiten (EL-04 i EL-07) els preparen directament al repositori, perquè la T26.1 no depengui de la T27.1.
- **Al navegador**, la US-27 ha d'arribar abans que la US-26.

Els imports van en la unitat menor de cada divisa ([`api.md` §12.1](api.md#121-divises-i-tipus-de-canvi)): cèntims d'euro, cèntims de dòlar o iens sencers.

## Dades de partida

- Seed acabat de carregar (`POST /api/dev/reset` o un client nou de pytest).
- **Usuari 1:** el compte principal en euros (`main`) amb **3.795,21 €** (`379521`) i cap subcompte en divisa. Els seus 30 moviments van de `mov-01` a `mov-30`, així que el moviment següent és `mov-31`, amb la referència `EVT-000031`.
- **Usuari 2:** el compte principal en euros amb 0,00 € i cap subcompte en divisa.
- Els subcomptes nous comencen per `sub-01` i les entrades d'historial per `smov-01` (P63).
- Tipus fixos (P50): `EUR` `10000`, `USD` `9123`, `GBP` `11680`, `CHF` `10355` i `JPY` `5700`.
- Rellotge fixat a **T0 = `2026-11-19T10:00:00+01:00`** a les proves que miren la data d'un moviment.
- Com que el seed no té subcomptes en divisa, les proves en creen un primer. «DV-03 fet» vol dir que l'usuari 1 ja té el subcompte en dòlars `sub-01`, a 0,00 $.

---

## US-25 · Afegir subcompte en divisa

### API (T25.2)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **DV-01** | Seed | `GET /api/subaccounts` (usuari 1) | `200` `{ items: [{ id: "main", currency: "EUR", balance: 379521, isMain: true, rateBps: 10000 }], totalInEuros: 379521 }`. |
| **DV-02** | Seed | `GET /api/subaccounts` (usuari 2) | `200` amb un sol compte, `main`, amb `balance: 0`, i `totalInEuros: 0`. |
| **DV-03** | Seed | `POST /api/subaccounts` amb `{ "currency": "USD" }` | `201` `{ id: "sub-01", currency: "USD", balance: 0, isMain: false, rateBps: 9123 }`. |
| **DV-04** | DV-03 fet | `GET /api/subaccounts` | Dos comptes, en aquest ordre: `main` (`379521`) i `sub-01` (`0`). `totalInEuros` continua sent `379521`: un subcompte nou no mou el total. |
| **DV-05** | DV-03 fet | `POST /api/subaccounts` amb `{ "currency": "USD" }` | `422 CURRENCY_EXISTS`, «Ja tens un subcompte en aquesta divisa.». `GET /api/subaccounts` continua tornant 2 comptes. |
| **DV-06** | Seed | `POST /api/subaccounts` amb `{ "currency": "EUR" }` | `422 CURRENCY_EXISTS`: l'EUR principal ja és un compte de l'usuari. |
| **DV-07** | Seed | `POST /api/subaccounts` amb `{ "currency": "BTC" }` | `422 CURRENCY_NOT_SUPPORTED`, «Aquesta divisa no és a la llista de divises disponibles.». |
| **DV-08** | Seed | `POST /api/subaccounts` amb `{ "currency": "usd" }` | `422 CURRENCY_NOT_SUPPORTED`: el codi distingeix majúscules. |
| **DV-09** | Seed | `POST /api/subaccounts` amb `{}`, i amb `{ "currency": 840 }` | `422 VALIDATION_ERROR` en tots dos casos. |
| **DV-10** | Seed | `POST /api/subaccounts` amb `"BTC"` i després amb `"USD"` | El segon respon `201` amb `id: "sub-01"`: un error no gasta cap `id`. |
| **DV-11** | Seed | `POST /api/subaccounts` amb `{ "currency": "JPY" }` | `201` `{ id: "sub-01", currency: "JPY", balance: 0, isMain: false, rateBps: 5700 }`. |
| **DV-12** | Seed | `POST /api/subaccounts` amb `USD`, `GBP`, `CHF` i `JPY`, en aquest ordre | Quatre `201`, de `sub-01` a `sub-04`. `GET /api/subaccounts` torna 5 comptes en l'ordre `main`, USD, GBP, CHF i JPY: no se'n pot afegir cap més. |
| **DV-13** | Seed | Dos `POST /api/subaccounts` amb `"USD"` alhora | Un `201` i un `422 CURRENCY_EXISTS`. `GET /api/subaccounts` torna 2 comptes. |
| **DV-14** | DV-03 fet | L'usuari 2 fa `POST /api/subaccounts` amb `"USD"` | `201` amb `id: "sub-02"`: els ids són únics a tot el sistema. L'usuari 1 no veu el subcompte de l'usuari 2, ni a l'inrevés. |
| **DV-15** | Sense sessió | `GET /api/subaccounts` i `POST /api/subaccounts` | `401 UNAUTHENTICATED` a totes dues. |
| **DV-16** | DV-03 fet | `POST /api/dev/reset` i després `GET /api/subaccounts` | Només `main`. El subcompte següent torna a ser `sub-01`. |

### Pantalla (T25.3)

| Id | Què fas | Què ha de sortir |
|---|---|---|
| **DVP-01** | Entra amb l'usuari 1 i mira «Inici». | El botó «Divises» i la card «Divises» amb «Total ≈ 3.795,21 €». |
| **DVP-02** | Toca «Divises». | S'obre `/divises` amb el compte «EUR · Euro» (3.795,21 €) i el botó «Afegir divisa». |
| **DVP-03** | Toca «Afegir divisa». | EUR, USD, GBP, CHF i JPY, amb codi i nom. L'EUR surt en gris amb «ja la tens». |
| **DVP-04** | Tria USD. | El tic verd «Subcompte en USD creat». 1,5 s després, l'app torna sola a «Inici», on l'USD surt amb «0,00 $» i el total continua sent «Total ≈ 3.795,21 €». |
| **DVP-05** | Torna a «Afegir divisa». | L'USD també surt en gris amb «ja la tens». |
| **DVP-06** | Obre «Afegir divisa» en dues pestanyes. Tria USD a la primera i, després, a la segona. | A la segona surt «Ja tens un subcompte en aquesta divisa.»: el servidor ho torna a validar. |
| **DVP-07** | Després de CVP-10, mira la fila del JPY. | «1.754 ¥», sense decimals. |

Una divisa fora de la llista no es pot triar des de la pantalla: només la prova l'API (DV-07).

---

## US-26 · Eliminar subcompte en divisa

### API (T26.1: eliminar i l'historial)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **EL-01** | DV-03 fet | `POST /api/subaccounts/sub-01/delete` | `200` `{ "status": "ok" }`. `GET /api/subaccounts` només torna `main`, i `totalInEuros` continua sent `379521`. |
| **EL-02** | EL-01 fet | `POST /api/subaccounts` amb `"USD"` | `201` amb `id: "sub-02"` i `balance: 0`: la divisa torna a estar disponible. `GET /api/subaccounts/sub-02/movements` torna `{ "items": [] }`. |
| **EL-03** | Seed | `POST /api/subaccounts/main/delete` | `422 MAIN_ACCOUNT_NOT_DELETABLE`, «El compte en euros no es pot eliminar.». Té `379521`, però es comprova abans que el saldo. |
| **EL-04** | USD a 0,01 $ (al navegador, CV-14; a pytest, preparat al repositori) | `POST /api/subaccounts/sub-01/delete` | `422 SUBACCOUNT_NOT_EMPTY`, «Només pots eliminar un subcompte amb saldo 0.». El subcompte continua amb `balance: 1`. |
| **EL-05** | Seed | `POST /api/subaccounts/sub-99/delete` | `404 SUBACCOUNT_NOT_FOUND`. |
| **EL-06** | DV-03 fet (de l'usuari 1) | L'usuari 2 fa `POST /api/subaccounts/sub-01/delete` | `404 SUBACCOUNT_NOT_FOUND`, la mateixa resposta que EL-05. L'usuari 1 encara té `sub-01`. |
| **EL-07** | CV-06 fet, i després EL-01 (a pytest, els moviments es preparen al repositori) | `GET /api/movements` i `GET /api/subaccounts/sub-01/movements` | Els dos moviments del compte principal es queden: `mov-31`, «Canvi EUR → USD», `29405`, i `mov-32`, «Canvi USD → EUR», `28542`. L'historial del subcompte eliminat respon `404 SUBACCOUNT_NOT_FOUND` (P61). |
| **EL-08** | EL-01 fet | `POST /api/subaccounts/sub-01/delete` un altre cop | `404 SUBACCOUNT_NOT_FOUND`. |
| **EL-09** | Sense sessió | `POST /api/subaccounts/sub-01/delete` i `GET /api/subaccounts/sub-01/movements` | `401 UNAUTHENTICATED` a totes dues. |
| **EL-10** | Seed | `GET /api/subaccounts/main/movements` | `404 SUBACCOUNT_NOT_FOUND`, «No s'ha trobat el subcompte.»: l'historial del compte en euros és `GET /api/movements`. |
| **EL-11** | DV-03 fet (de l'usuari 1) | L'usuari 2 fa `GET /api/subaccounts/sub-01/movements` | `404 SUBACCOUNT_NOT_FOUND`. |

### Pantalla (T26.2)

| Id | Què fas | Què ha de sortir |
|---|---|---|
| **ELP-01** | Amb l'USD creat, a `/divises` toca la fila de l'USD. | El detall «USD · Dòlar nord-americà», amb el saldo, «Últims moviments» i el botó vermell «Eliminar subcompte». |
| **ELP-02** | Obre el detall de l'EUR. | No hi surt el botó «Eliminar subcompte». |
| **ELP-03** | Amb l'USD a 0,01 $ (CV-14), toca «Eliminar subcompte». | «Abans d'eliminar-lo has de deixar el saldo a 0», amb «D'acord». No s'elimina. |
| **ELP-04** | Amb l'USD a 0,00 $, toca «Eliminar subcompte». | «Segur que vols eliminar aquest subcompte?», amb «Cancel·lar» i «Eliminar». |
| **ELP-05** | Toca «Eliminar». | El tic «Subcompte eliminat». L'app torna sola a «Inici» i l'USD ja no hi és. A «Afegir divisa», l'USD torna a estar disponible. |
| **ELP-06** | Després d'eliminar un USD amb canvis fets, obre «Moviments». | Els moviments en euros dels canvis («Canvi EUR → USD» i «Canvi USD → EUR») continuen a l'historial. |
| **ELP-07** | Mira el detall d'un subcompte en divisa. | No hi ha cap botó «Aportar» (decisió del PO, #189). |

---

## US-27 · Canviar entre divises

### API (T27.1)

| Id | Situació inicial | Acció | Resultat esperat |
|---|---|---|---|
| **CV-01** | DV-03 fet | `POST /api/exchanges` amb `{ "fromCurrency": "EUR", "toCurrency": "USD", "amount": 10000 }` | `201` `{ from: { id: "main", currency: "EUR", balance: 369371, isMain: true, rateBps: 10000 }, to: { id: "sub-01", currency: "USD", balance: 10961, isMain: false, rateBps: 9123 }, amount: 10000, commission: 150, received: 10961 }`. |
| **CV-02** | CV-01 fet | `GET /api/subaccounts` | `main` amb `369371`, `sub-01` amb `10961` i `totalInEuros: 379371`: ha baixat `150`, la comissió. |
| **CV-03** | CV-01 fet | `GET /api/home` i `GET /api/movements` | `balance: 369371`. El primer moviment és `mov-31`: «Canvi EUR → USD», `expense`, `10150`, `icon: "transfer"`, `counterparty: null`, `status: "completed"` i `reference: "EVT-000031"`. |
| **CV-04** | CV-01 fet | `GET /api/subaccounts/sub-01/movements` | Una entrada: `smov-01`, `10961`, «Canvi EUR → USD», `income`. |
| **CV-05** | DV-03 fet | `POST /api/exchanges` d'EUR a USD amb `amount: 1000` | `201` amb `commission: 50`, el mínim (l'1,5 % serien `15`), i `received: 1096`. El compte principal queda a `378471`. |
| **CV-06** | DV-03 fet | D'EUR a USD amb `amount: 28970`, i després d'USD a EUR amb `amount: 31286` (exemple de la US-26) | El primer: `commission: 435`, `received: 31755` (l'USD a 317,55 $). El segon: `commission: 469`, `received: 28542`; l'USD queda a `0` i el compte principal a `378658`. |
| **CV-07** | DV-03 fet | D'EUR a EUR amb `amount: 1000` | `422 SAME_CURRENCY`. No canvia res. |
| **CV-08** | Seed (sense USD) | D'EUR a USD amb `amount: 1000`, i d'EUR a `"BTC"` | `404 SUBACCOUNT_NOT_FOUND` en tots dos casos. |
| **CV-09** | DV-03 fet | D'EUR a USD amb `amount: 0`, i amb `amount: -100` | `422 INVALID_AMOUNT` en tots dos casos. |
| **CV-10** | CV-01 fet | D'USD a EUR amb `amount: 1` | `422 AMOUNT_TOO_SMALL`, «L'import és massa petit per canviar.»: `1 × 9123 < 10000`. |
| **CV-11** | DV-11 fet (JPY) | D'EUR a JPY amb `amount: 1` | `201`: `received: 2` (1 cèntim són 1,75 ¥, arrodonit a 2) i `commission: 50`. El compte principal queda a `379470`. |
| **CV-12** | DV-03 fet | D'EUR a USD amb `amount: 379521`, tot el saldo | `422 INSUFFICIENT_BALANCE`: amb la comissió de `5693`, calen `385214`. No canvia res. |
| **CV-13** | CV-01 fet | D'USD a EUR amb `amount: 10799` | `201`: `commission: 162`, i el càrrec és `10961`, tot el saldo. L'USD queda a `0`, `received: 9852` i el compte principal queda a `379223`. |
| **CV-14** | CV-01 fet | D'USD a EUR amb `amount: 10798` | `201`: `commission: 162`. L'USD queda a `1` (0,01 $), `received: 9851` i el compte principal queda a `379222`. |
| **CV-15** | DV-11 fet (JPY) | D'EUR a JPY amb `amount: 1000` | `201`: `received: 1754` (1.754 ¥) i `commission: 50`. `GET /api/subaccounts`: el JPY amb `1754`, el compte principal amb `378471` i `totalInEuros: 379471` (els 1.754 ¥ compten `1000`). |
| **CV-16** | CV-15 fet | De JPY a EUR amb `amount: 100` | `201`: `commission: 88`, el mínim en iens, i `received: 57`. El JPY queda a `1566` i el compte principal a `378528`. |
| **CV-17** | DV-03 fet | Cos sense `amount`; amb `amount: "1000"`; amb `amount: 10.5`; i amb `fromCurrency: 978` | `422 VALIDATION_ERROR` en tots els casos. |
| **CV-18** | DV-03 fet | D'EUR a EUR amb `amount: 0` | `422 SAME_CURRENCY`: les divises es comproven abans que l'import. |
| **CV-19** | CV-01 fet | Dos canvis d'USD a EUR amb `amount: 6000` alhora (`6090` cadascun, amb la comissió) | Un `201` i un `422 INSUFFICIENT_BALANCE`. L'USD queda a `4871` i mai és negatiu. |
| **CV-20** | DV-03 fet | D'EUR a USD amb `amount: 10000`, fent fallar una de les quatre escriptures a mig camí | L'error surt i no canvia cap saldo ni cap moviment. No es gasta cap `id` ni cap referència. |
| **CV-21** | CV-01 fet | Dues `POST /api/topups` de `50000` | `201` totes dues: el canvi no compta per al límit diari de recàrrega. |
| **CV-22** | DV-12 fet | D'EUR a GBP amb `amount: 10000`, i després de GBP a USD amb `amount: 1000` | El segon canvi no crea cap moviment al compte principal: a `GET /api/movements` només hi ha el del primer. |
| **CV-23** | Sense sessió | `POST /api/exchanges` | `401 UNAUTHENTICATED`. |

### Pantalla (T27.2)

| Id | Què fas | Què ha de sortir |
|---|---|---|
| **CVP-01** | Amb només l'EUR, a `/divises` toca «Canviar». | «Necessites dos subcomptes per canviar divises.» i el botó «Divises». No surt cap selector ni cap teclat. |
| **CVP-02** | Amb l'EUR i l'USD, a «Canviar» tria l'EUR com a origen. | Al selector de destí, l'EUR surt en gris. |
| **CVP-03** | Tria l'USD com a destí i escriu `100`. | «Rebràs aproximadament 110,00 $». |
| **CVP-04** | Amb l'USD amb saldo (CV-01), tria USD → EUR i escriu `0,01`. | «L'import és massa petit per canviar.», i «Continuar» queda desactivat. |
| **CVP-05** | Amb EUR → USD i `100`, toca «Continuar». | El resum: «100,00 € → USD», «1 € = 1,10 $», «Comissió: 1,50 €», «Se't descomptaran 101,50 € del subcompte d'origen» i «Rebràs exactament 109,61 $». No s'ha enviat res. |
| **CVP-06** | Amb EUR → USD i `10`, toca «Continuar». | «Comissió: 0,50 €». |
| **CVP-07** | Amb EUR → USD, prova de canviar tot el saldo (3.795,21 €). | «No tens prou saldo», en vermell sota el botó. |
| **CVP-08** | Des del resum de CVP-05, toca «Confirmar canvi». | El tic «Canvi fet», i l'app torna a «Inici»: l'EUR a 3.693,71 €, l'USD a 109,61 $ i «Total ≈ 3.793,71 €». |
| **CVP-09** | A «Inici», mira «Últims moviments». | El primer és «Canvi EUR → USD», −101,50 €. |
| **CVP-10** | Amb el JPY creat, canvia 10,00 € a JPY. | El resum diu «Rebràs exactament 1.754 ¥» i «Comissió: 0,50 €». |

---

## Criteris d'acceptació i proves

| Criteri d'acceptació | Proves |
|---|---|
| US-25 · A Inici hi ha el botó «Divises» i la card «Divises» amb «Total ≈ … €» | DV-01, DV-02, DVP-01 |
| US-25 · `/divises` mostra els comptes i el botó «Afegir divisa» | DV-01, DV-04, DV-12, DVP-02 |
| US-25 · «Afegir divisa» mostra EUR, USD, GBP, CHF i JPY amb codi i nom. Les que ja tinc (inclòs l'EUR) surten en gris amb «ja la tens» | DV-06, DVP-03, DVP-05 |
| US-25 · En triar-ne una surt el tic verd «Subcompte en USD creat» i, 1,5 s després, torna a Inici, on surt amb «0,00 $» | DV-03, DV-04, DV-11, DVP-04 |
| US-25 · Divisa repetida: «Ja tens un subcompte en aquesta divisa.» Divisa fora de la llista: «Aquesta divisa no és a la llista de divises disponibles.» | DV-05, DV-06, DV-07, DV-08, DV-13, DVP-06 |
| US-25 · Un subcompte nou no mou el total. El JPY no té decimals («1.234 ¥») | DV-04, DV-11, CV-15, DVP-04, DVP-07 |
| US-26 · El detall del subcompte té el botó vermell «Eliminar subcompte». Al de l'EUR no surt, i el servidor respon «El compte en euros no es pot eliminar.» | EL-03, ELP-01, ELP-02 |
| US-26 · Amb saldo diferent de 0 (n'hi ha prou amb 0,01 $) surt «Abans d'eliminar-lo has de deixar el saldo a 0» amb «D'acord», i no s'elimina | EL-04, CV-14, ELP-03 |
| US-26 · Amb saldo 0 surt «Segur que vols eliminar aquest subcompte?» amb «Cancel·lar» i «Eliminar» | ELP-04 |
| US-26 · En confirmar surt el tic «Subcompte eliminat», l'app torna sola a Inici i el subcompte ja no hi és. La divisa torna a estar disponible a «Afegir divisa» | EL-01, EL-02, ELP-05 |
| US-26 · Els moviments antics es queden a l'historial | EL-07, ELP-06 |
| US-26 · El subcompte no té botó «Aportar» en aquest sprint: el saldo només s'omple (i es buida) amb «Canviar» (US-27) | CV-06, CV-13, ELP-07 |
| US-27 · Amb un sol subcompte, «Canviar» mostra «Necessites dos subcomptes per canviar divises.» i el botó «Divises» | CV-08, CVP-01 |
| US-27 · A «Canviar» trio l'origen i el destí. L'origen surt en gris al selector de destí | CV-07, CV-18, CVP-02 |
| US-27 · Amb el teclat surt «Rebràs aproximadament». Si l'import és massa petit: «L'import és massa petit per canviar.» i «Continuar» queda desactivat | CV-10, CV-11, CVP-03, CVP-04 |
| US-27 · El resum mostra el tipus, la comissió (sempre n'hi ha: 1,5 %, mínim 0,50 €), el càrrec a l'origen i «Rebràs exactament». No s'envia res fins a «Confirmar canvi» | CV-01, CV-05, CV-06, CV-15, CV-16, CVP-05, CVP-06, CVP-10 |
| US-27 · Saldo insuficient (import + comissió): «No tens prou saldo» en vermell | CV-12, CV-19, CVP-07 |
| US-27 · Èxit: tic «Canvi fet» i torna a Inici amb els dos saldos i el total actualitzats | CV-01, CV-02, CV-03, CV-04, CVP-08, CVP-09 |
| US-27 · Tot o res: o canvien els dos saldos i els dos moviments, o no en canvia cap | CV-12, CV-19, CV-20 |

Proves que no surten d'un criteri, sinó del contracte: DV-09 i DV-10 (format del cos i ids), DV-14 (ids únics i comptes de cada usuari), DV-15, EL-09 i CV-23 (sense sessió), DV-16 (reinici de dades), EL-05, EL-06, EL-08 i EL-11 (subcomptes inexistents, d'altres usuaris o ja eliminats), EL-10 (l'historial del compte en euros), CV-09 i CV-17 (import i format), CV-21 (límit de recàrrega) i CV-22 (canvi sense l'EUR).
