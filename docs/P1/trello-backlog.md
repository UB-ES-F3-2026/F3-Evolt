# Cards Trello — copiar i enganxar

> Obre el tauler → **Backlog** → **+ Afegeix una tarjeta**
> 1. Enganxa el **títol**
> 2. Obre la card → enganxa **Descripció**
> 3. **Checklist** → nom `Acceptance Criteria` → enganxa els items
> 4. Labels si en tens
>
> **No hi ha import automàtic.** Tot a mà des d'aquest fitxer.

**Numeració:** `US-XX` sencera (01…42), com al doc de l'equip. Sense decimals. Les US-39 a US-42 venen de dividir la US-16, la US-21 i la US-28 (25/11/2026).

| Persona | Bloc | US |
|---------|------|-----|
| **P1** | Alta i primers passos | US-01, US-02, US-03, US-04, US-09, US-36…US-38 |
| **P2** | Estalvi | US-17…US-20 |
| **P3** | Pantalla principal i XP | US-07, US-23, US-24 |
| **P4** | Moviments | US-08, US-10, US-11, US-33…US-35 |
| **P5** | Social | US-13, US-15, US-16, US-39, US-40, US-30…US-32 |
| **P6** | Transferències + Multidivisa | US-12, US-14, US-21, US-41, US-25…US-29, US-42 |

**Sincronitzat amb el Trello el 25/11/2026** (backlog de l'Sprint 3: 11 històries Fina a To Do, 9 Mitjana i les èpiques). Les històries fetes porten aquí només la descripció i els criteris; el detall complet és a `docs/us/US-XX.md`. Si canvies una card al Trello, canvia-la també aquí.

## Perfils d'usuari

Cada història diu a quin perfil afecta (camp COM i línia Perfil).

- **Visitant:** persona que té l'app però encara no té compte. Només surt al registre (US-01).
- **Client nou:** s'acaba de registrar i encara no té moviments ni guardioles. Serveix per a la verificació del codi i per als estats buits.
- **Client estàndard:** usuari registrat amb el compte actiu, amb saldo, moviments i guardioles. És el perfil de la majoria d'històries.
- **Client premium:** com el client estàndard, però amb un límit de canvi de divisa sense comissió més alt (5.000 € al mes en lloc de 1.000 €, US-29).
- **Administrador:** persona de l'equip d'Evolt amb permisos de gestió (no és un client). Configura la gamificació des d'un panell (EP-15).

## Guia d'estil

Els criteris d'acceptació descriuen la pantalla amb aquestes paraules:

- **Lletra:** la del sistema (la que porta el mòbil o l'ordinador).
- **Fons:** gris molt clar. El contingut va dins de targetes blanques amb les cantonades arrodonides.
- **Color principal:** lila, per als botons i els enllaços.
- **Text:** el principal en gris fosc gairebé negre; el secundari (etiquetes, dates, ajudes) en gris clar.
- **Ingressos:** en verd, amb el signe "+". **Despeses:** en vermell, amb el signe "−". **Errors:** en vermell.
- **Imports:** en euros, amb coma decimal i el símbol al final, per exemple "1.250,50 €".
- **Dates:** dia, mes i hora, per exemple "11 d'oct. · 21:15".

---

# P1 — Alta i primers passos

## US-01 Registre amb email o telèfon

**Labels:** Fina, Alta, Alta-compte, P1

**Descripció:**

```
COM: visitant
VULL: registrar-me amb el meu email o telèfon i una contrasenya
PER: poder obrir un compte.

Perfil: visitant, és a dir, una persona que té l'app però encara no té compte. En acabar el registre passa a ser client nou.

Assumptes:
- Contrasenya: mínim 8 caràcters, 1 majúscula i 1 número
- El compte nou queda en estat "pendent de verificació"
- Cal acceptar els termes i la política de privacitat

Estimació: SP 5 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
La pantalla "Crear compte" té tres caselles, una sota l'altra: "Email o telèfon", "Contrasenya" i "Repeteix la contrasenya", i a sota el botó lila "Crear compte"
Si la contrasenya no té mínim 8 caràcters, una majúscula i un número, la casella es posa vermella i a sota surt en vermell "La contrasenya ha de tenir 8 caràcters, una majúscula i un número"
Si les dues contrasenyes no coincideixen, surt en vermell sota la segona casella "Les contrasenyes no coincideixen" i el botó "Crear compte" queda desactivat
Si l'email o el telèfon ja estan registrats, surt en vermell "Aquest email o telèfon ja té un compte" i l'enllaç lila "Inicia sessió"
Sota les caselles hi ha una casella per marcar "Accepto els termes i la política de privacitat"; mentre no està marcada, el botó "Crear compte" surt desactivat (gris clar)
Quan el formulari s'envia bé, el compte es crea en estat "pendent de verificació"
Després de crear el compte, l'app passa sola a la pantalla "Verifica el teu compte" (US-2)
```

---

## US-02 Verificació del codi de registre

**Labels:** Fina, Alta, Alta-compte, P1

**Descripció:**

```
COM: client nou
VULL: confirmar el meu email o telèfon amb un codi
PER: demostrar que són meus.

Perfil: client nou, que s'acaba de registrar i té el compte "pendent de verificació".

Assumptes:
- Codi de 6 dígits per email o SMS
- El codi caduca als 10 minuts
- Màxim 5 intents fallits

Estimació: SP 3 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
Després del registre arriba un codi de 6 números per email o SMS, i l'app mostra la pantalla "Verifica el teu compte" amb 6 caselles, una per número
Si han passat més de 10 minuts des que s'ha enviat, el codi ja no serveix
Amb el codi correcte, el compte queda activat i l'app obre la pantalla "Inici"
Si el codi és incorrecte o ha caducat, les caselles es posen vermelles i surt en vermell "El codi no és correcte o ha caducat"
A sota hi ha l'enllaç lila "Envia'm un codi nou"; en tocar-lo arriba un codi nou i l'anterior deixa de servir
Després de 5 codis incorrectes, les caselles es bloquegen i surt "Has fet massa intents. Demana un codi nou"
```

---

## US-03 Inici de sessió amb contrasenya

**Labels:** Fina, Alta, Alta-compte, P1

**Descripció:**

```
COM: client estàndard
VULL: iniciar sessió amb el meu email o telèfon i la contrasenya
PER: accedir al meu compte.

Perfil: client estàndard amb el compte ja verificat. També serveix per al client nou un cop verificat.

Assumptes:
- Missatge d'error genèric: no diu quina casella falla
- Bloqueig de 15 minuts després de 5 intents fallits
- La sessió es tanca després de 5 minuts sense activitat

Estimació: SP 4 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A la pantalla "Inicia sessió", amb l'email o telèfon i la contrasenya correctes, en tocar el botó lila "Entrar" s'obre la pantalla "Inici"
Amb dades incorrectes surt en vermell "L'email, el telèfon o la contrasenya no són correctes", sense dir quina casella falla
Després de 5 intents fallits seguits, el compte es bloqueja 15 minuts, surt en vermell "Compte bloquejat durant 15 minuts" i arriba un avís per email
Si estic 5 minuts sense fer res, la sessió es tanca, l'app torna a "Inicia sessió" i surt "La sessió s'ha tancat per inactivitat"
Al menú hi ha l'opció "Tancar sessió", que torna a la pantalla "Inicia sessió"
```

---

## US-04 Recuperació de contrasenya

**Labels:** Fina, Alta, Alta-compte, P1

**Descripció:**

```
COM: client estàndard que ha oblidat la contrasenya
VULL: restablir la contrasenya
PER: no perdre l'accés al compte.

Perfil: client estàndard que no recorda la contrasenya i no pot entrar.

Assumptes:
- L'enllaç funciona durant 30 minuts
- Si l'email no està registrat, surt el mateix missatge que si ho està
- En canviar-la, es tanquen les sessions obertes en altres dispositius

Estimació: SP 3 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A la pantalla "Inicia sessió", sota el botó "Entrar", hi ha l'enllaç lila "He oblidat la contrasenya"
En escriure l'email i tocar "Enviar", arriba un email amb un enllaç que funciona durant 30 minuts
Tant si l'email està registrat com si no, surt el mateix missatge: "Si l'email és correcte, rebràs un enllaç per canviar la contrasenya"
La contrasenya nova ha de complir el mateix que al registre (8 caràcters, una majúscula i un número), amb el mateix error en vermell si no ho fa
En canviar-la, es tanquen les sessions obertes en altres dispositius i surt un tic verd amb "Contrasenya canviada"
Si l'enllaç ha caducat, surt "Aquest enllaç ha caducat" i el botó lila "Demanar-ne un de nou"
```

---

## US-09 Recàrrega de prova

**Labels:** Fina, Alta, Compte, P1

**Descripció:**

```
COM: client estàndard
VULL: afegir diners de prova al meu compte
PER: tenir saldo per provar l'app sense una targeta real.

Perfil: client estàndard (usuari registrat amb el compte actiu, amb saldo, moviments i guardioles). El client nou també pot recarregar.

Assumptes:
- Màxim 500 € per recàrrega i 1.000 € al dia
- Sense targeta: la recàrrega s'aprova a l'instant
- Les recàrregues no donen XP

Estimació: SP 3 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A Inici, sota el saldo, hi ha un botó lila amb el text en blanc "+ Afegir diners", que obre la pantalla "Afegir diners"
Es pot escriure un import més gran que 0 i de com a màxim 500 € (sota la casella hi ha l'ajuda en gris "Màxim 500,00 € per recàrrega"); si l'import no és vàlid, la casella es posa vermella, surt el motiu en vermell sota la casella i el botó "Confirmar" queda desactivat
Si una recàrrega fa passar de 1.000 € en un mateix dia, no es fa i surt en vermell "Has superat el límit diari de recàrrega. Avui encara pots recarregar X €."
En confirmar surt un tic verd amb el text "Recàrrega feta: +X €"; després l'app torna sola a Inici, amb el saldo ja actualitzat i la recàrrega a dalt de tot dels moviments, en verd i amb el concepte "Recàrrega"
La recàrrega no suma XP
```

---

## US-36 Editar el perfil

**Labels:** Mitjana, P1

**Descripció:**

```
COM: client estàndard
VULL: editar les meves dades
PER: mantenir-les al dia.

Perfil: client estàndard.

Assumptes:
- «Perfil» és la pantalla de la US-24
- Canviar l'email o el telèfon demana verificar-los amb un codi, com a la US-2
- El nom legal i la data de naixement no es poden editar

Estimació: SP 3 · VP 4 · Prioritat Mitjana

Èpica: EP-14. Granularitat mitjana: el detall de pantalles i missatges es fa quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
A «Perfil» (US-24) hi ha «Editar el perfil», on puc canviar el nom visible i la foto
Per canviar l'email o el telèfon he de posar el codi que s'envia a la dada nova (com a la US-2)
El nom legal i la data de naixement es veuen però no es poden editar
Si l'email o el telèfon ja els fa servir un altre usuari surt «Aquest email ja està registrat.» o «Aquest telèfon ja està registrat.»
```

---

## US-37 Canviar la contrasenya

**Labels:** Mitjana, P1

**Descripció:**

```
COM: client estàndard
VULL: canviar la meva contrasenya
PER: mantenir el compte segur.

Perfil: client estàndard amb la sessió iniciada.

Assumptes:
- La nova contrasenya segueix les regles de la US-1
- Cal posar la contrasenya actual

Estimació: SP 2 · VP 5 · Prioritat Mitjana

Èpica: EP-14. Granularitat mitjana: el detall de pantalles i missatges es fa quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
A «Perfil» hi ha «Canviar la contrasenya», amb la contrasenya actual, la nova i repetir la nova
La nova ha de complir les regles de la US-1; si no, surt el mateix missatge que al registre
Si l'actual no és correcta surt «La contrasenya actual no és correcta.» i no es canvia res
En canviar-la surt «Contrasenya canviada.» i a la bústia arriba un avís de seguretat
```

---

## US-38 Preferències de notificacions

**Labels:** Mitjana, P1

**Descripció:**

```
COM: client estàndard
VULL: triar quins avisos rebo
PER: no rebre avisos que no m'interessen.

Perfil: client estàndard.

Assumptes:
- Els avisos de seguretat no es poden desactivar
- Les preferències es guarden al servidor

Estimació: SP 2 · VP 3 · Prioritat Baixa

Èpica: EP-14. Granularitat mitjana: el detall de pantalles i missatges es fa quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
A «Perfil» hi ha «Notificacions», amb un interruptor per tipus: pagaments, sol·licituds, guardioles i gamificació
Si desactivo un tipus, aquests avisos ja no arriben a la bústia
Els avisos de seguretat (contrasenya i inici de sessió) surten sense interruptor i sempre arriben
Les preferències es guarden al servidor: no canvien en tancar la sessió ni des d'un altre dispositiu
```

---

### EP-01 Registre i accés

**Labels:** Èpica, Alta-compte, P1

**Descripció:**

```
Tot el que necessita un usuari per crear el compte i entrar-hi de forma segura.

Perfil: visitant (registre), client nou (verificació del codi) i client estàndard (inici de sessió i recuperar la contrasenya). Històries: US-1, US-2, US-3 i US-4.
```

**Checklist Acceptance Criteria:**

```
Un visitant es pot registrar amb email o telèfon i verificar el compte amb un codi (US-1, US-2)
Un client pot iniciar sessió amb la contrasenya (US-3)
Un client pot recuperar la contrasenya (US-4)
```

---

### EP-14 Perfil i preferències

**Labels:** Èpica

**Descripció:**

```
COM: client estàndard
VULL: gestionar les meves dades i preferències
PER: adaptar l'app a mi.

Perfil: client estàndard.

Històries (Mitjana, 24/11): US-36 Editar el perfil (inclou canviar l'email o el telèfon), US-37 Canviar la contrasenya i US-38 Preferències de notificacions.

Estimació: 7 SP (suma de les històries) · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Puc editar el nom visible, la foto i l'adreça.
Per canviar l'email o el telèfon he de verificar la nova dada amb un codi.
El nom legal i la data de naixement no es poden editar des de l'app.
Puc canviar la contrasenya introduint l'actual.
Puc activar o desactivar cada tipus de notificació, excepte les de seguretat.
```

---

# P3 — Pantalla principal i XP

## US-07 Saldo a la pantalla principal

**Labels:** Fina, Alta, Home, P3

**Descripció:**

```
COM: client estàndard
VULL: veure el meu saldo i resum financer a la pantalla principal
PER: saber d'un cop d'ull com tinc els diners i controlar la meva activitat.

Perfil: client estàndard (usuari registrat amb el compte actiu, amb saldo, moviments i guardioles). El client nou, que encara no té moviments, veu el saldo i un missatge que ho indica.

Assumptes:
- Saldo disponible i total estalviat a guardioles
- Els 5 últims moviments
- Icona d'ull per amagar els imports, i l'app ho recorda
- Ingressos en verd amb "+" i despeses en vermell amb "−"

Estimació: SP 4 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
En entrar, la pantalla "Inici" mostra a dalt el saldo disponible, amb la lletra més gran de la pantalla i en negreta, sota l'etiqueta "Saldo disponible" en gris
Sota el saldo surt "Total estalviat a guardioles:" en lletra petita i gris, amb l'import en negreta
A la part de baix, a la secció "Últims moviments", surten els 5 moviments més recents, cadascun amb la seva icona, el concepte i l'import (ingressos en verd amb "+", despeses en vermell amb "−")
Al costat del saldo hi ha una icona d'ull; en tocar-la, tots els imports de la pantalla es canvien per "••••", i en tornar-la a tocar es tornen a veure
Si amago els imports i tanco l'app, en tornar a entrar segueixen amagats
```

---

## US-23 Guanyar XP per hàbits saludables

**Labels:** Fina, Mitjana, Gamificació, XP, P3

**Descripció:**

```
COM: client estàndard
VULL: guanyar XP quan faig accions financeres saludables
PER: sentir-me motivat a mantenir bons hàbits d'estalvi.

Perfil: client estàndard.

Assumptes:
- Els XP i els límits diaris són en un sol fitxer de configuració del backend; el panell de l'administrador és l'EP-15 (decisió F, 24/11)
- Valors: primera guardiola +50 XP, aportació +10 XP (màxim 3 per dia), objectiu assolit +100 XP
- L'historial d'XP és a «Perfil» (US-24); aquesta història es demostra amb els avisos «+X XP»

Estimació: SP 3 · VP 7 · Prioritat Mitjana

Revisió del 25/11: L'historial d'XP passa a la US-24. S'aclareix que cada aportació només es resta una vegada i què és la «primera guardiola».
```

**Checklist Acceptance Criteria:**

```
Guanyo XP en: crear la primera guardiola de la meva vida (+50 XP; si ja en tenia alguna, no), aportar a una guardiola (+10 XP, com a màxim 3 aportacions amb XP per dia) i assolir l'objectiu d'una guardiola (+100 XP, una sola vegada per guardiola encara que hi torni a arribar)
Els XP de cada acció i el màxim per dia són en un sol fitxer de configuració del backend; canviar-los no demana tocar cap pantalla
Quan guanyo XP surt a dalt, sobre la pantalla on soc, un avís lila amb «+X XP · <motiu>» durant 3 s (per exemple «+10 XP · Aportació a Vacances»); se'n va sol o en tocar-lo
Si una aportació fa assolir l'objectiu surten els dos avisos, primer «+10 XP · Aportació a <nom>» i després «+100 XP · Objectiu assolit»
Un cop fetes 3 aportacions amb XP en un dia, les següents es fan igual però no donen XP ni surt l'avís. El dia es compta en hora de Madrid
Enviar, demanar, pagar o rebutjar sol·licituds i canviar divises no donen XP
Si retiro d'una guardiola menys de 7 dies després d'una aportació que em va donar XP, es resten els XP d'aquella aportació (la més recent de la guardiola que encara no s'havia restat) i surt l'avís vermell «−10 XP · Retirada de <nom>». Cada aportació només es resta una vegada: una segona retirada resta la següent aportació, si n'hi ha, i si no, no resta res. Els XP mai baixen de 0
Els XP es guarden al servidor: tancar la sessió o entrar des d'un altre dispositiu no els canvia
```

---

## US-24 Nivells, perfil i historial d'XP

**Labels:** Fina, Mitjana, Gamificació, XP, P3

**Descripció:**

```
COM: client estàndard
VULL: pujar de nivell en acumular XP i veure com els he guanyat
PER: veure el meu progrés financer a llarg termini.

Perfil: client estàndard.

Assumptes:
- Depèn de la US-23 (XP)
- La taula de nivells és al mateix fitxer de configuració que els XP: 1 amb 0 XP, 2 amb 100, 3 amb 250, 4 amb 450 i 5 amb 700
- L'historial d'XP ve de la US-23 (revisió del 25/11)

Estimació: SP 4 · VP 6 · Prioritat Mitjana

Revisió del 25/11: S'hi afegeix l'historial d'XP, que abans era a la US-23.
```

**Checklist Acceptance Criteria:**

```
Els nivells són al mateix fitxer de configuració que els XP: 1 amb 0 XP, 2 amb 100, 3 amb 250, 4 amb 450 i 5 amb 700. Un usuari nou comença al nivell 1 amb 0 XP («0 / 100 XP»)
Al menú ☰ hi ha «Perfil» (capçalera «← Inici» · «Perfil»)
«Perfil» mostra «Nivell» i el número en gran en lila, a sota «X XP en total», la barra lila de progrés amb «180 / 250 XP» i «Et falten 70 XP per al nivell 3»; a baix, la fila «Historial d'XP ›». Al nivell 5 (el màxim) la barra surt plena i diu «Has arribat al nivell màxim»
Quan una acció fa arribar els XP al mínim del nivell següent pujo de nivell sol: després de l'avís «+X XP» surt la pantalla de celebració amb una estrella lila, «Has pujat al nivell X!», «X XP en total» i el botó lila «Continuar», que torna a la pantalla on era. Si en pujo dos de cop, diu el nivell final
A Inici, sota el saldo i «Total estalviat a guardioles», surt «Nivell X» en lila i a la dreta «180 / 250 XP», amb una barra petita a sota; en tocar-la s'obre «Perfil»
Si perdo XP (US-23) el nivell no baixa, i la barra mostra els XP que falten des del total actual
«Historial d'XP» mostra una fila per canvi: el motiu, la data («24 de nov. · 18:20») i a la dreta els XP, en verd amb «+» o en vermell amb «−», el més recent a dalt
Sense cap canvi, «Historial d'XP» diu «Encara no has guanyat XP. Crea una guardiola per començar.»
Si no es pot carregar «Perfil» o l'historial surt «S'ha produït un error inesperat. Torna-ho a provar més tard.» amb el botó «Reintentar»
```

---

### EP-05 Gamificació: XP i nivells

**Labels:** Èpica, Gamificació, P3

**Descripció:**

```
El nucli de la gamificació: premiar els hàbits saludables amb XP i nivells.

Perfil: client estàndard. A l'Sprint 3 els valors d'XP i els nivells són en un fitxer de configuració del backend (decisió F, 24/11); el panell de l'administrador és l'EP-15. Històries: US-23 i US-24.
```

**Checklist Acceptance Criteria:**

```
Guanya XP per hàbits d'estalvi saludables (US-23)
Puja de nivell i veu el progrés i l'historial d'XP al seu perfil (US-24)
```

---

### EP-15 Administració de la gamificació

**Labels:** Èpica, Gamificació, P3

**Descripció:**

```
COM: administrador
VULL: configurar reptes, insígnies i valors d'XP des d'un panell
PER: mantenir la gamificació al dia sense publicar noves versions de l'app.

Perfil: administrador, és a dir, una persona de l'equip d'Evolt amb permisos de gestió (no és un client).

Assumptes:
- A l'Sprint 3 els valors d'XP i els nivells són en un fitxer de configuració del backend (decisió F, 24/11); aquest panell el substituirà
- Cal un rol d'administrador amb accés restringit

Històries previstes: accés al panell amb rol d'administrador, editar els valors d'XP i els nivells, gestionar reptes i gestionar insígnies.

Estimació: ~13 SP · Prioritat Baixa. Es divideix en històries quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
L'administrador pot crear i publicar reptes i insígnies des del panell.
L'administrador pot activar o desactivar reptes i insígnies en temps real.
El sistema bloqueja l'edició de les condicions d'un repte si ja té usuaris actius.
L'administrador pot modificar els valors d'XP per acció i els llindars de nivell.
```

---

### EP-02 Compte i moviments

**Labels:** Èpica, P3/P4

**Descripció:**

```
Consultar el saldo, veure els moviments i afegir diners al compte.

Perfil: client estàndard. El client nou, sense moviments, veu els estats buits. Històries: US-07 a US-12.
```

**Checklist Acceptance Criteria:**

```
El client veu el saldo a Inici i la llista de moviments (US-07, US-08)
Pot afegir diners amb una recàrrega de prova (US-09)
Pot filtrar i cercar els moviments i veure'n el detall (US-10, US-11)
Pot consultar i compartir el seu IBAN per rebre transferències d'altres bancs (US-12)
```

---

# P2 — Estalvi

## US-17 Crear guardiola

**Labels:** Fina, Alta, Estalvi, P2

**Descripció:**

```
COM: client estàndard
VULL: crear una guardiola amb nom i objectiu opcional
PER: estalviar per a una meta concreta.

Perfil: client estàndard amb la sessió iniciada. El client nou també pot crear la seva primera guardiola.

Assumptes:
- L'objectiu és opcional; si s'escriu, ha de ser un import positiu
- La guardiola nova neix amb saldo 0
- Cada guardiola té nom i, si es vol, objectiu i color
- A la demo no hi ha límit de guardioles

Estimació: SP 5 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A "Inici" hi ha l'accés "Guardioles", que obre la pantalla "Guardioles"
Si no en tinc cap, surt el missatge gris "Encara no tens cap guardiola" i el botó lila "Crear guardiola"; si en tinc, surt la llista amb el nom i el saldo de cadascuna
El botó "Crear guardiola" obre un formulari amb les caselles "Nom" i "Objectiu (opcional)" i una fila de colors per triar
Si el nom està buit o l'objectiu és 0 o negatiu, la casella es posa vermella, surt el motiu en vermell a sota i el botó "Crear" queda desactivat
En tocar "Crear", la guardiola nova surt a la llista amb saldo 0,00 €
```

---

## US-18 Aportar diners a una guardiola

**Labels:** Fina, Alta, Estalvi, P2

**Descripció:**

```
COM: client estàndard amb guardioles
VULL: aportar diners des del saldo principal a una guardiola
PER: estalviar cap a un objectiu sense gastar-los del compte principal.

Perfil: client estàndard que ja té almenys una guardiola.

Assumptes:
- Cal tenir prou saldo principal
- El saldo principal baixa i el de la guardiola puja
- Es registra un moviment a la guardiola
- L'import ha de ser més gran que 0

Estimació: SP 5 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A la pantalla d'una guardiola hi ha el botó lila "Aportar", que obre la pantalla "Aportar a <nom de la guardiola>"
A dalt es veu el saldo principal disponible i el nom i el saldo de la guardiola
L'import ha de ser més gran que 0 i no més gran que el saldo principal; si no, la casella es posa vermella, surt el motiu en vermell i el botó "Confirmar" queda desactivat
En confirmar, el saldo principal baixa i el de la guardiola puja exactament el mateix import
Surt un tic verd amb "Has aportat X € a <nom>"
A l'historial de la guardiola surt l'aportació en verd amb "+" i el concepte "Aportació"
Si el servidor falla, surt el missatge d'error en vermell i cap dels dos saldos canvia
Mai es queda a mitges: o canvien els dos saldos o no en canvia cap
```

---

## US-19 Retirar diners d'una guardiola

**Labels:** Fina, Alta, Estalvi, P2

**Descripció:**

```
COM: client estàndard amb guardioles
VULL: retirar diners d'una guardiola al saldo principal
PER: fer servir els diners estalviats quan els necessiti.

Perfil: client estàndard amb almenys una guardiola amb saldo.

Assumptes:
- El saldo de la guardiola baixa i el principal puja
- Es registra un moviment de retirada
- L'import ha de ser més gran que 0
- No es pot retirar més del que té la guardiola
```

**Checklist Acceptance Criteria:**

```
Al detall de la guardiola hi ha «Retirar» al costat d'«Aportar». Amb 0,00 € surt desactivat (gris, no enfocable) i «Aportar» continua actiu.
«Retirar de <nom>» mostra «Saldo de la guardiola», «Import», «Confirmar» i «Cancel·lar».
Import buit: cap missatge i «Confirmar» desactivat. Import ≤ 0: «L'import ha de ser més gran que 0.»
Més que el saldo de la guardiola: «La guardiola no té prou saldo per aquesta retirada.» i «Confirmar» desactivat. Retirar exactament tot el saldo sí que es pot.
Èxit: tic verd «Has retirat 30,00 € de Vacances» amb «Saldo disponible: … · Vacances: …»; 1,5 s després torna al detall ja actualitzat.
La guardiola baixa i el principal puja el mateix import. A l'historial surt «−30,00 €» «Retirada» en vermell i al compte, «Retirada de Vacances».
Error del servidor o de xarxa: «S'ha produït un error inesperat. Torna-ho a provar més tard.» / «No hi ha connexió amb el servidor. Torna-ho a provar.» L'import es queda escrit i cap saldo canvia.
```

---

## US-20 Veure progrés i objectiu assolit

**Labels:** Fina, Alta, Estalvi, P2

**Descripció:**

```
COM: client estàndard amb guardioles amb objectiu
VULL: veure el progrés cap a cada objectiu i saber quan l'he assolit
PER: mantenir la motivació d'estalviar i celebrar les metes.

Perfil: client estàndard amb almenys una guardiola que té objectiu.

Assumptes:
- Sense objectiu no hi ha barra de progrés
- Progrés = saldo / objectiu, en percentatge arrodonit a l'enter
- Quan el saldo arriba a l'objectiu, la guardiola passa a "Objectiu assolit"
- Es connecta amb la gamificació (EP-11 i EP-12)
```

**Checklist Acceptance Criteria:**

```
El detall d'una guardiola amb objectiu mostra «150,00 € de 1.000,00 €», la barra, «15 %» i l'etiqueta.
Saldo < objectiu: barra lila i etiqueta grisa «En progrés». Saldo ≥ objectiu: barra verda plena i etiqueta verda «Objectiu assolit».
El percentatge s'arrodoneix mig cap amunt (62,5 → 63).
Per sobre del 100 % el número diu el valor real («125 %») i la barra queda plena, sense passar-se.
Sense objectiu: ni barra, ni percentatge, ni línia «Objectiu:».
A la llista, només les guardioles amb objectiu tenen barra petita i «15 %» sota el nom.
Després d'aportar o retirar, el detall i la llista surten actualitzats sense recarregar.
El percentatge sempre és text visible: el color no és mai l'únic senyal.
```

---

### EP-04 Estalvi amb guardioles

**Labels:** Èpica, Estalvi, P2

**Descripció:**

```
Crear objectius d'estalvi i moure-hi diners, de forma manual o automàtica.

Perfil: client estàndard. El client nou també pot crear la seva primera guardiola. Històries: US-17 a US-21 i US-41 (la US-21 es va dividir en dues el 25/11).
```

**Checklist Acceptance Criteria:**

```
Pot crear guardioles i aportar-hi diners (US-17, US-18)
Pot retirar-ne diners i veure el progrés cap a l'objectiu (US-19, US-20)
Pot programar aportacions automàtiques i pausar-les, editar-les o eliminar-les (US-21, US-41)
```

---

### EP-12 Reptes i ratxes

**Labels:** Èpica, P2

**Descripció:**

```
COM: client estàndard
VULL: superar reptes d'estalvi i mantenir ratxes
PER: convertir l'estalvi en un hàbit.

Perfil: client estàndard amb almenys una guardiola.

Assumptes:
- Depèn de l'XP (US-23) i de les aportacions (US-18, US-21)
- Els reptes els crea l'administrador (EP-15)

Històries previstes: apuntar-se a un repte d'estalvi, progrés i recompensa del repte, ratxa setmanal d'aportacions.

Estimació: ~10 SP · Prioritat Baixa. Es divideix en històries quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
Puc apuntar-me a un repte d'estalvi (per exemple «Estalvia 50 € aquesta setmana») i en veig el progrés
Completar un repte dona XP (US-23)
Cada setmana amb almenys una aportació suma 1 a la ratxa; una setmana sense cap aportació la torna a 0
La ratxa actual i la millor ratxa surten a «Perfil» (US-24)
```

---

### EP-11 Insígnies i recompenses

**Labels:** Èpica

**Descripció:**

```
COM: client estàndard
VULL: aconseguir insígnies i desbloquejar recompenses
PER: sentir que els meus progressos es reconeixen i mantenir la motivació.

Perfil: client estàndard. El client nou veu el tutorial de benvinguda.

Assumptes:
- Depèn de l'XP i els nivells (US-23, US-24)
- Les insígnies es configuren des del panell de l'EP-15

Històries previstes: insígnies per fites d'estalvi, pantalla d'insígnies amb el progrés de les bloquejades, compartir una insígnia sense dades financeres, recompenses visuals en pujar de nivell i tutorial de benvinguda.

Estimació: ~15 SP · Prioritat Baixa. Es divideix en històries quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
L'usuari rep insígnies úniques en complir determinades condicions financeres o d'estalvi.
Existeix una pantalla on l'usuari pot consultar les insígnies assolides i el progrés de les bloquejades.
L'usuari pot compartir les seves insígnies sense mostrar dades financeres privades.
En pujar de nivell es desbloquegen recompenses visuals (temes, marcs d'avatar).
Els nous usuaris disposen d'un tutorial de benvinguda de gamificació.
```

---

# P4 — Moviments

## US-08 Llistat de moviments

**Labels:** Fina, Alta, Moviments, P4

**Descripció:**

```
COM: client estàndard
VULL: consultar tots els meus moviments en una llista
PER: controlar què gasto i què ingresso.

Perfil: client estàndard (usuari registrat amb el compte actiu, amb saldo, moviments i guardioles). El client nou, que encara no té moviments, veu un missatge de llista buida.

Assumptes:
- Ordre del més recent al més antic
- Es carreguen de 20 en 20 en arribar al final (scroll infinit)
- Ingressos en verd amb "+" i despeses en vermell amb "−"

Estimació: SP 3 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
Els moviments surten del més recent al més antic, dins d'una targeta blanca
Cada moviment mostra a l'esquerra la icona del tipus; al mig, el concepte i a sota la data en lletra més petita i gris; i a la dreta l'import en negreta
Els ingressos surten en verd amb "+" (per exemple "+1.800,00 €") i les despeses en vermell amb "−" (per exemple "−23,50 €")
En baixar fins al final de la llista, se'n carreguen 20 més sense tocar cap botó, i es veu "Carregant més moviments…" mentre arriben
El client nou, que no té moviments, veu el missatge "Encara no tens moviments" en gris
A Inici, l'enllaç lila "Veure tots" obre la pantalla "Moviments"
Mentre la llista carrega es veu "Carregant…"; si falla, surt el missatge d'error en vermell i un botó "Reintentar"
A dalt a l'esquerra hi ha el botó "← Inici", que torna a la pantalla principal
```

---

## US-10 Filtres i cerca de moviments

**Labels:** Mitjana, Moviments, P4

**Descripció:**

```
COM: client estàndard
VULL: filtrar i cercar els meus moviments
PER: trobar ràpidament una operació concreta.

Perfil: client estàndard amb moviments.

Assumptes:
- Els filtres es poden combinar
- Cerca per concepte o contacte
- Botó per esborrar els filtres

Estimació: SP 3 · VP 5 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
A dalt de la pantalla "Moviments" hi ha el botó "Filtres", que permet triar una data d'inici i una de final; la llista només mostra els moviments entre aquestes dues dates
Als filtres hi ha tres opcions: "Tots", "Ingressos" (en verd) i "Despeses" (en vermell); en triar-ne una, la llista només mostra aquest tipus
A dalt de tot hi ha una barra de cerca amb el text gris "Cerca per concepte o contacte"; mentre escric, la llista només mostra els moviments que contenen aquest text
Les dates, el tipus i la cerca es poden fer servir alhora, i el botó "Esborrar filtres" els treu tots i torna a mostrar la llista completa
Si cap moviment compleix els filtres, surt el missatge gris "No hi ha resultats" amb el botó "Esborrar filtres"
```

---

## US-11 Detall d'un moviment

**Labels:** Mitjana, Moviments, P4

**Descripció:**

```
COM: client estàndard
VULL: veure el detall de cada moviment
PER: entendre exactament què ha passat amb els meus diners.

Perfil: client estàndard amb moviments.

Assumptes:
- Justificant en PDF descarregable
- Formulari de problema vinculat al moviment

Estimació: SP 3 · VP 5 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
En tocar un moviment de la llista s'obre la pantalla "Detall del moviment": a dalt l'import en gran (en verd amb "+" si és un ingrés, en vermell amb "−" si és una despesa) i a sota, en files, la data i l'hora, l'estat ("Completat" o "Pendent"), la contrapart (qui paga o qui cobra) i la referència
Hi ha el botó "Descarregar justificant", que baixa un PDF amb aquestes mateixes dades
Hi ha l'enllaç "Reportar un problema", que obre un formulari amb el moviment ja indicat i una casella per explicar què passa
```

---

## US-33 Categoritzar moviments

**Labels:** Mitjana, Moviments, P4

**Descripció:**

```
COM: client estàndard
VULL: que cada despesa tingui una categoria
PER: saber en què gasto.

Perfil: client estàndard amb moviments.

Assumptes:
- Categories fixes: Menjar, Transport, Oci, Compres, Casa i Altres
- La categoria automàtica surt de paraules clau del concepte; sense cap coincidència, «Altres» (resol el dubte de l'EP-10 sobre les despeses sense comerç)
- La categoria es pot canviar a mà

Estimació: SP 3 · VP 5 · Prioritat Mitjana

Èpica: EP-10. Granularitat mitjana: el detall de pantalles i missatges es fa quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
Cada despesa té una categoria de la llista fixa: Menjar, Transport, Oci, Compres, Casa i Altres
La categoria es posa sola segons paraules clau del concepte (per exemple «sopar» → Menjar); si no en coincideix cap, «Altres»
Al detall del moviment (US-11) puc canviar la categoria, i el canvi es guarda
A «Moviments» puc filtrar per categoria, junt amb els filtres de la US-10
```

---

## US-34 Despeses del mes per categoria

**Labels:** Mitjana, Moviments, P4

**Descripció:**

```
COM: client estàndard
VULL: veure un gràfic de les despeses del mes per categoria
PER: entendre on van els meus diners.

Perfil: client estàndard amb moviments.

Assumptes:
- Depèn de la US-33
- Només compten les despeses, no els ingressos ni els moviments entre guardioles

Estimació: SP 3 · VP 5 · Prioritat Mitjana

Èpica: EP-10. Granularitat mitjana: el detall de pantalles i missatges es fa quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
Al menú ☰ hi ha «Anàlisi», amb el total gastat del mes i un gràfic de les despeses per categoria (US-33)
Per defecte es mostra el mes actual, i puc canviar de mes amb fletxes
Cada categoria mostra l'import, el percentatge del total i la variació respecte al mes anterior
Sense despeses aquell mes surt «Aquest mes encara no tens despeses.»
```

---

## US-35 Pressupost mensual per categoria

**Labels:** Mitjana, Moviments, P4

**Descripció:**

```
COM: client estàndard
VULL: fixar un pressupost mensual per categoria
PER: no gastar més del que vull.

Perfil: client estàndard amb moviments.

Assumptes:
- Depèn de la US-33 i la US-34
- L'XP per complir el pressupost depèn de la US-23

Estimació: SP 3 · VP 5 · Prioritat Mitjana

Èpica: EP-10. Granularitat mitjana: el detall de pantalles i missatges es fa quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
A «Anàlisi» puc posar un pressupost mensual a cada categoria, i canviar-lo o treure'l
Cada categoria amb pressupost mostra una barra «gastat / pressupost»
En arribar al 80 % del pressupost arriba un avís a la bústia, i un altre en superar-lo
Acabar el mes sense superar cap pressupost dona XP (US-23)
```

---

### EP-10 Anàlisi de despeses i pressupostos

**Labels:** Èpica, Moviments, P4

**Descripció:**

```
COM: client estàndard
VULL: veure en què gasto i fixar pressupostos
PER: controlar millor les meves finances.

Perfil: client estàndard amb moviments.

Assumptes:
- Depèn del sistema d'XP (US-23) per a l'XP del pressupost complert
- Una despesa sense comerç es categoritza per paraules clau del concepte i, si no en coincideix cap, va a «Altres» (US-33)

Històries (Mitjana, 24/11): US-33 Categoritzar moviments, US-34 Despeses del mes per categoria i US-35 Pressupost mensual per categoria.

Estimació: 9 SP (suma de les històries) · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Cada despesa s'assigna automàticament a una categoria i la puc canviar manualment
Veig un gràfic mensual de despesa per categoria i la variació respecte al mes anterior
Puc crear un pressupost mensual per categoria amb una barra de progrés
Rebo un avís en arribar al 80% del pressupost i un altre quan el supero
Acabar el mes sense superar un pressupost dona XP
```

---

# P5 — Social

## US-13 Cercar un usuari

**Labels:** Fina, Alta, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: trobar altres usuaris de l'app
PER: poder enviar-los diners.

Perfil: client estàndard que vol enviar o demanar diners.

Assumptes:
- Cerca per @usuari, telèfon o email
- Mai es mostren dades financeres als resultats
- No apareixo als meus propis resultats
- `User` porta `username` i `phone`, i el seed té 8 usuaris (T13.2)
```

**Checklist Acceptance Criteria:**

```
A «Enviar diners» (`/pagaments`, des de l'enllaç d'Inici) hi ha la barra amb el text gris «@usuari, telèfon o email» i els resultats surten mentre escric.
Cada fila només té inicials (o foto), nom i «@usuari» en gris: cap import ni saldo. Un usuari sense nom mostra el «@usuari» com a nom.
«611 22 33 02», «+34 611 22 33 02» i «611223302» donen la mateixa fila.
Cercar el meu nom, «@demo», el meu email o el meu telèfon no em retorna mai.
Sense coincidències surt «No hi ha resultats»; amb el camp buit torna la llista inicial sense aquest text.
Tocar una fila obre `/pagaments/enviar?to=<id>`, i recarregar-la manté el destinatari.
Amb més de 64 caràcters surt «Les dades no són vàlides. Revisa-les i torna-ho a provar.» amb «Reintentar».
```

---

## US-15 Sol·licitar diners

**Labels:** Fina, Mitjana, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: demanar diners a un contacte
PER: que em torni el que em deu.

Perfil: client estàndard.

Assumptes:
- Estats: pendent, pagada, rebutjada i caducada
- Una sol·licitud sense resposta caduca als 7 dies
```

**Checklist Acceptance Criteria:**

```
S'hi entra des d'Inici → menú hamburguesa → «Sol·licituds enviades» (`/requests`). Inici es queda amb els 4 botons.
Dins de `/requests`, el botó «Demanar diners» obre `/requests/new` amb destinatari (cerca de la US-13), import i concepte.
«Enviar sol·licitud» queda desactivat fins que hi ha destinatari, import vàlid (fins a 1.000.000,00 €) i concepte d'1 a 140 caràcters.
Demanar-me a mi mateix: «No et pots demanar diners a tu mateix.»
Èxit: «Sol·licitud enviada a <nom>.» i, 1,5 s després, `/requests` amb la nova la primera. La bústia simulada rep «<nom> et demana X €: <concepte>.». Si hi ha un error, les dades es mantenen.
`/requests` mostra cada sol·licitud amb la seva etiqueta. Hi ha quatre estats (Pendent, Pagada, Rebutjada, Caducada); en aquest sprint només es poden veure «Pendent» i «Caducada» (Pagada i Rebutjada arriben amb la US-16).
Sense resposta, es veu «Caducada» a partir del dia 7 (dia natural de Madrid).
Només les «Pendent» tenen «Cancel·lar», que obre el diàleg «Cancel·lar sol·licitud». «Cancel·lar», Esc o clic fora el tanquen sense fer res.
En confirmar surt «Sol·licitud cancel·lada.» i la sol·licitud s'esborra: desapareix de `/requests` per sempre (no hi ha estat «Cancel·lada»).
Una sol·licitud no mou diners: ni saldo, ni moviments, ni XP.
```

---

## US-16 Veure les sol·licituds rebudes

**Labels:** Fina, Mitjana, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: veure les sol·licituds de diners que he rebut
PER: saber qui em demana diners i quant.

Perfil: client estàndard que ha rebut alguna sol·licitud (US-15).

Assumptes:
- «Sol·licituds rebudes» s'obre des del menú, sota «Sol·licituds enviades» (decisió B, 24/11)
- Pagar és la US-39 i rebutjar és la US-40
- Al seed, l'usuari de la demo té sol·licituds rebudes en els quatre estats

Estimació: SP 1 · VP 5 · Prioritat Mitjana

Revisió del 25/11: La US-16 original («Respondre a una sol·licitud») es divideix en US-16 (veure), US-39 (pagar) i US-40 (rebutjar).
```

**Checklist Acceptance Criteria:**

```
Al menú ☰, sota «Sol·licituds enviades», hi ha «Sol·licituds rebudes», que obre /requests/received (capçalera «← Inici» · «Sol·licituds rebudes»). Inici es queda amb els 4 botons
Cada sol·licitud rebuda és una targeta, la més nova a dalt: a l'esquerra el nom i, a sota en gris, l'@usuari, el concepte i la data («23 de nov. · 19:30»); a la dreta l'import en negreta i l'etiqueta d'estat: «Pendent» (groc), «Pagada» (verd), «Rebutjada» (vermell) o «Caducada» (gris)
Una sol·licitud passa a «Caducada» a partir del dia 7 (dia natural de Madrid), com a la US-15
Només les «Pendent» tenen, a baix i un al costat de l'altre, els botons «Pagar» (lila ple, US-39) i «Rebutjar» (blanc amb el text en vermell, US-40). Les altres no tenen cap botó
Sense cap sol·licitud rebuda surt una icona grisa i «Encara no has rebut cap sol·licitud.»
Si no es pot carregar la llista surt «S'ha produït un error inesperat. Torna-ho a provar més tard.» amb el botó «Reintentar»
```

---

## US-39 Pagar una sol·licitud rebuda

**Labels:** Fina, Mitjana, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: pagar una sol·licitud que he rebut
PER: tornar els diners sense haver d'escriure res.

Perfil: client estàndard amb una sol·licitud «Pendent» a «Sol·licituds rebudes» (US-16).

Assumptes:
- Depèn de la US-16 (llista) i reutilitza «Confirmar» de la US-14
- Pagar és un enviament de la US-14: compta per al límit diari i envia els mateixos avisos
- Les sol·licituds són sempre en euros (US-15)

Estimació: SP 2 · VP 6 · Prioritat Mitjana

Revisió del 25/11: Ve de la US-16 original («Respondre a una sol·licitud»).
```

**Checklist Acceptance Criteria:**

```
«Pagar» obre «Confirmar» de la US-14 amb el destinatari, l'import i el concepte ja posats, que no es poden canviar, i el «Saldo disponible». «← Rebudes» torna a la llista sense pagar
Si l'import supera el saldo, a «Confirmar» surt en vermell «No tens prou saldo.» i, en lloc de «Confirmar enviament», el botó lila «Afegir diners», que obre la recàrrega (US-09). La sol·licitud continua «Pendent»
Si l'import passa el límit diari de la US-14, surt en vermell «Has superat el límit diari de 1.000,00 €.» i no es pot confirmar
En confirmar: tic verd «Has pagat 25,00 € a Alicia» amb «Saldo disponible: …»; 1,5 s després torna a «Sol·licituds rebudes» amb la sol·licitud «Pagada» i sense botons
A «Sol·licituds enviades» de qui la va fer (US-15), la sol·licitud surt «Pagada»
El pagament és un enviament de la US-14: −25,00 € als moviments de qui paga, +25,00 € als de qui la va fer, amb el concepte de la sol·licitud, i els avisos de la US-14 a la bústia
Si en confirmar la sol·licitud ja no és pendent (ha caducat o s'ha respost en un altre dispositiu), surt «Aquesta sol·licitud ja no està pendent.», no es paga res i torna a la llista recarregada
Error del servidor o de xarxa: «S'ha produït un error inesperat. Torna-ho a provar més tard.» / «No hi ha connexió amb el servidor. Torna-ho a provar.» sota el botó; la sol·licitud continua «Pendent» i cap saldo canvia
```

---

## US-40 Rebutjar una sol·licitud rebuda

**Labels:** Fina, Mitjana, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: rebutjar una sol·licitud que he rebut
PER: que qui me l'ha enviat sàpiga que no la pagaré.

Perfil: client estàndard amb una sol·licitud «Pendent» a «Sol·licituds rebudes» (US-16).

Assumptes:
- Depèn de la US-16 (llista)
- Rebutjar no mou cap diner
- No es demana cap motiu

Estimació: SP 1 · VP 4 · Prioritat Mitjana

Revisió del 25/11: Ve de la US-16 original («Respondre a una sol·licitud»).
```

**Checklist Acceptance Criteria:**

```
«Rebutjar» obre el diàleg «Rebutjar sol·licitud» amb «Segur que vols rebutjar la sol·licitud de <nom> de X €?», «Cancel·lar» i «Rebutjar» (vermell). «Cancel·lar», Esc o clic fora el tanquen sense fer res
En confirmar surt a dalt «Sol·licitud rebutjada.» en verd i la targeta passa a «Rebutjada», sense botons
A «Sol·licituds enviades» de qui la va fer surt «Rebutjada», i a la seva bústia arriba «<nom> ha rebutjat la teva sol·licitud»
No es mou cap diner: els saldos i els moviments de tots dos no canvien
Si en confirmar la sol·licitud ja no és pendent, surt «Aquesta sol·licitud ja no està pendent.» i la llista es recarrega
Error del servidor o de xarxa: «S'ha produït un error inesperat. Torna-ho a provar més tard.» / «No hi ha connexió amb el servidor. Torna-ho a provar.» sota el botó; la sol·licitud continua «Pendent»
```

---

## US-30 Dividir una despesa

**Labels:** Mitjana, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: dividir una despesa amb altres usuaris
PER: no haver de calcular qui em deu què.

Perfil: client estàndard que ha pagat una despesa compartida.

Assumptes:
- Fa servir les sol·licituds de la US-15: cada participant en rep una amb la seva part
- A parts iguals o amb imports personalitzats
- La meva part no genera cap sol·licitud

Estimació: SP 3 · VP 5 · Prioritat Mitjana

Èpica: EP-09. Granularitat mitjana: el detall de pantalles i missatges es fa quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
A «Demanar diners» puc triar «Dividir una despesa», posar l'import total i el concepte, i afegir participants per @usuari (US-13)
Per defecte es divideix a parts iguals entre els participants i jo; els cèntims que sobren me'ls quedo jo
Puc canviar la part de cada participant; si la suma no és igual al total surt «La suma de les parts ha de ser igual al total.» i no es pot continuar
En confirmar, cada participant rep una sol·licitud (US-15) amb la seva part i el concepte
```

---

## US-31 Seguiment d'una despesa dividida

**Labels:** Mitjana, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: veure qui m'ha pagat la seva part d'una despesa dividida
PER: saber què em falta cobrar.

Perfil: client estàndard que ha dividit una despesa (US-30).

Assumptes:
- Depèn de la US-30
- L'estat de cada part és el de la seva sol·licitud (US-15, US-16)

Estimació: SP 2 · VP 4 · Prioritat Baixa

Èpica: EP-09. Granularitat mitjana: el detall de pantalles i missatges es fa quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
A «Sol·licituds enviades» una despesa dividida surt com una sola targeta amb el total, «X de Y han pagat» i l'import pendent
En obrir-la veig cada participant amb la seva part i l'estat: «Pendent», «Pagada», «Rebutjada» o «Caducada»
Puc tornar a enviar la sol·licitud a qui l'ha rebutjada o li ha caducat
Quan tothom ha pagat, la targeta passa a «Completada»
```

---

## US-32 Guardiola compartida

**Labels:** Mitjana, Estalvi, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: crear una guardiola amb altres usuaris
PER: estalviar junts per a un objectiu comú.

Perfil: client estàndard que vol estalviar amb contactes de l'app.

Assumptes:
- Amplia les guardioles de la US-17 a la US-20
- Cada membre aporta del seu saldo principal
- Les invitacions arriben a la bústia

Estimació: SP 5 · VP 5 · Prioritat Mitjana

Èpica: EP-09. Granularitat mitjana: el detall de pantalles i missatges es fa quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
En crear una guardiola (US-17) puc marcar «Compartida» i convidar usuaris per @usuari; reben un avís a la bústia i poden acceptar o rebutjar
Cada membre veu el total, l'objectiu i quant ha aportat cada membre
Cada membre només pot retirar el que ha aportat ell
Si un membre abandona la guardiola, el que ha aportat torna al seu saldo principal
Només qui l'ha creat la pot eliminar, i en eliminar-la cada membre recupera la seva aportació
```

---

### EP-09 Despeses compartides

**Labels:** Èpica, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: dividir despeses i estalviar en grup
PER: gestionar diners en comú sense complicacions.

Perfil: client estàndard que comparteix despeses o estalvis amb altres clients.

Històries (Mitjana, 24/11): US-30 Dividir una despesa, US-31 Seguiment d'una despesa dividida i US-32 Guardiola compartida.

Estimació: 10 SP (suma de les històries) · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Puc dividir una despesa a parts iguals o amb imports personalitzats, i la suma ha de coincidir amb el total.
Cada participant rep una sol·licitud de pagament i puc veure qui ha pagat.
Puc crear una guardiola compartida i convidar-hi contactes.
Cada membre veu el total i les aportacions de tothom, i només pot retirar el que ha aportat.
Si un membre abandona la guardiola, se li retorna la seva aportació.
```

---

### EP-13 Gamificació social

**Labels:** Èpica, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: competir i col·laborar amb amics
PER: motivar-nos mútuament a estalviar.

Perfil: client estàndard que té contactes a l'app.

Assumptes:
- Depèn de l'XP (US-23) i dels reptes (EP-12)
- Mai es mostren saldos ni imports d'altres usuaris

Històries previstes: reptes amb amics, invitacions a reptes, rànquing setmanal d'XP i privacitat del rànquing.

Estimació: ~13 SP · Prioritat Baixa. Es divideix en històries quan entri en un sprint.
```

**Checklist Acceptance Criteria:**

```
Puc crear reptes i convidar-hi amics, que poden acceptar o rebutjar la invitació.
El progrés dels altres participants es mostra en percentatge, mai en imports.
Hi ha un rànquing setmanal d'XP entre contactes que es reinicia cada dilluns.
El rànquing només mostra XP i nivell, mai saldos.
Puc sortir del rànquing des dels ajustos de privacitat.
```

---

### EP-03 Pagaments entre usuaris

**Labels:** Èpica, P5/P6

**Descripció:**

```
Enviar, demanar i rebre diners entre usuaris de l'app.

Perfil: client estàndard. Històries: US-13, US-14, US-15, US-16, US-39 i US-40 (la US-16 es va dividir en tres el 25/11).
```

**Checklist Acceptance Criteria:**

```
Pot cercar un altre usuari de l'app (US-13)
Pot enviar-li diners, amb un límit diari (US-14)
Pot demanar-li diners (US-15)
Veu les sol·licituds que rep i les pot pagar o rebutjar (US-16, US-39, US-40)
```

---

# P6 — Transferències + Multidivisa

## US-12 Dades del compte (IBAN)

**Labels:** Fina, Mitjana, Transferències, P6

**Descripció:**

```
COM: client estàndard
VULL: consultar el meu IBAN
PER: poder rebre transferències d'altres bancs.

Perfil: client estàndard amb el compte actiu.

Assumptes:
- Cada usuari té un IBAN espanyol fix al seed, amb el dígit de control correcte, i el BIC és el mateix per a tothom (decisió D, 24/11)
- La transferència d'un altre banc es simula amb una ruta de desenvolupament, com la recàrrega de prova
- L'IBAN es pot copiar i compartir

Estimació: SP 2 · VP 5 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Al menú ☰ hi ha «Dades del compte» (capçalera «← Inici» · «Dades del compte»)
Una targeta mostra, una sota l'altra i amb l'etiqueta a l'esquerra: «IBAN» en grups de 4 caràcters (24 en total, per exemple «ES91 2100 0418 4502 0005 1332»), «BIC» («EVOLESB1XXX») i «Titular» (el nom de l'usuari; sense nom, l'@usuari)
Cada usuari té el seu IBAN, sempre el mateix, amb el dígit de control correcte; dos usuaris no tenen mai el mateix
En tocar l'IBAN es copia sense espais, i a baix surt durant 2 s «IBAN copiat»
«Compartir» (botó blanc) obre el menú del mòbil amb el text «IBAN: … · BIC: … · Titular: …»; si el navegador no ho permet, copia aquest text i surt «Dades copiades»
Una transferència d'un altre banc (simulada amb una ruta de desenvolupament) suma l'import al saldo principal i surt a Inici i a Moviments en verd: «Transferència rebuda · <ordenant>» i «+120,00 €»
A la bústia arriba «Has rebut 120,00 € de <ordenant>»
Si no es poden carregar les dades surt «S'ha produït un error inesperat. Torna-ho a provar més tard.» amb el botó «Reintentar»
```

---

## US-14 Enviar diners a usuaris

**Labels:** Fina, Alta, Transferències, P6

**Descripció:**

```
COM: client estàndard
VULL: enviar diners a un altre usuari a l'instant
PER: saldar deutes de manera senzilla.

Perfil: client estàndard amb saldo.

Assumptes:
- Import més gran que 0 i per sota del límit diari
- Concepte opcional
- Notificació a qui envia i a qui rep
- Depèn de la US-13 (llista i cerca de destinataris)
```

**Checklist Acceptance Criteria:**

```
En triar el destinatari (llista o cerca de la US-13) s'obre «Enviar»: destinatari a dalt, «Import» amb teclat numèric i «Concepte» opcional.
Sense prou saldo, a «Enviar» surt «No tens prou saldo.» en vermell i «Continuar» queda desactivat; no s'envia res.
Límit de 1.000,00 €/dia, igualtat permesa: si avui he enviat 20,00 €, encara puc enviar 980,00 €. Si l'import el supera, a «Enviar» surt «Has superat el límit diari de 1.000,00 €. Avui encara pots enviar 980,00 €.» en vermell i «Continuar» queda desactivat. El límit no és editable en aquest sprint.
«Continuar» obre «Confirmar» amb el destinatari, l'import i el concepte, i el botó «Confirmar enviament». El servidor torna a comprovar saldo i límit: si han canviat, surt el mateix missatge i no s'envia res.
Enviar-me a mi mateix: «No et pots enviar diners a tu mateix.» i no es mou res.
Destinatari inexistent: «No hem trobat aquest destinatari.» i «Torna a triar el destinatari».
Èxit: tic verd «Has enviat 20,00 € a Usuari nou» i «Saldo disponible: …»; 1,5 s després torna a Inici.
A Inici surt «−20,00 €» en vermell a qui envia i «+20,00 €» en verd a qui rep, i recarregar no ho perd. Sense concepte: «Transferència enviada» / «Transferència rebuda».
A la bústia simulada hi ha «Has enviat X € a <nom>» i «<nom> t'ha enviat X €». No hi ha avisos dins de l'app.
```

---

## US-21 Programar una aportació automàtica

**Labels:** Fina, Mitjana, Estalvi, Transferències, P6

**Descripció:**

```
COM: client estàndard amb guardioles
VULL: programar una aportació automàtica a una guardiola
PER: estalviar de forma constant sense pensar-hi.

Perfil: client estàndard que ja té almenys una guardiola.

Assumptes:
- Freqüència setmanal o mensual
- Les aportacions que ja toquen es fan en llegir les dades, com la caducitat de la US-15; no hi ha cap tasca programada (decisió E, 24/11)
- El dia es compta en hora de Madrid
- Pausar, editar i eliminar són la US-41

Estimació: SP 3 · VP 6 · Prioritat Mitjana

Revisió del 25/11: La US-21 original es divideix en US-21 (programar) i US-41 (pausar, editar i eliminar). S'hi afegeixen la regla del primer dia i la pausa en assolir l'objectiu.
```

**Checklist Acceptance Criteria:**

```
Al detall de la guardiola, sota «Aportar» i «Retirar», hi ha la targeta «Aportació automàtica ›» amb «Encara no n'has programat cap.»
El formulari «Aportació automàtica» té «Import» (en euros, amb 2 decimals com a màxim), «Freqüència» («Cada setmana» o «Cada mes») i «Dia» (de dilluns a diumenge si és setmanal; del 1 al 28 si és mensual), i el botó lila «Programar». «Programar» queda desactivat fins que hi ha import i dia; amb import ≤ 0 surt «L'import ha de ser més gran que 0.»
En programar no es comprova el saldo. Surt «Aportació automàtica programada.» i torna al detall, on la targeta mostra «25,00 € cada mes», «El dia 1 · propera: 1 de des.» i l'etiqueta «Activa». Cada guardiola en té com a màxim una
La primera aportació és el primer dia programat a partir de demà: si la programo avui amb el dia d'avui, avui no es fa
Un cop passat el dia programat (des de les 00:00 de Madrid), la propera vegada que obro l'app l'import ja ha passat del saldo principal a la guardiola, amb el concepte «Aportació automàtica» i la data del dia programat. Si n'han passat diversos, se'n fa una per cada dia, de la més antiga a la més nova
El saldo es comprova en fer cada aportació. Si no n'hi ha prou, aquella no es fa ni es torna a intentar, i a la bústia arriba «No s'ha pogut fer l'aportació automàtica a <nom>: saldo insuficient»
Una aportació automàtica compta com una aportació normal: actualitza el progrés (US-20) i dona XP (US-23), dins del màxim del dia
Quan la guardiola arriba a l'objectiu, l'aportació automàtica es pausa sola: la targeta mostra l'etiqueta «Pausada» amb «Objectiu assolit» a sota, i a la bústia arriba «<nom> ha arribat a l'objectiu: s'ha pausat l'aportació automàtica»
Si s'elimina la guardiola, també s'elimina la seva aportació automàtica
Error del servidor o de xarxa: «S'ha produït un error inesperat. Torna-ho a provar més tard.» / «No hi ha connexió amb el servidor. Torna-ho a provar.» sota el botó; no es programa res
```

---

## US-41 Pausar, editar i eliminar l'aportació automàtica

**Labels:** Fina, Mitjana, Estalvi, Transferències, P6

**Descripció:**

```
COM: client estàndard amb una aportació automàtica
VULL: pausar, canviar o eliminar l'aportació automàtica
PER: adaptar l'estalvi quan canvia la meva situació.

Perfil: client estàndard amb una aportació automàtica programada (US-21).

Assumptes:
- Depèn de la US-21
- Les aportacions que ja s'han fet no es toquen mai

Estimació: SP 2 · VP 4 · Prioritat Mitjana

Revisió del 25/11: Ve de la US-21 original («Aportació periòdica automàtica»).
```

**Checklist Acceptance Criteria:**

```
La targeta d'una aportació automàtica té els botons «Pausar», «Editar» i «Eliminar» (aquest en vermell)
«Pausar» canvia l'etiqueta a «Pausada» i el botó a «Reprendre». Mentre està pausada no es fa cap aportació, ni tampoc després les dels dies que han passat en pausa
«Reprendre» torna l'etiqueta a «Activa»; la propera aportació és el primer dia programat a partir de demà. També es pot reprendre una aportació pausada per objectiu assolit (US-21)
«Editar» obre el formulari de la US-21 amb les dades actuals i el botó «Desar»; en desar surt «Aportació automàtica actualitzada.» i la propera aportació es torna a calcular amb la mateixa regla
«Eliminar» obre el diàleg «Eliminar aportació automàtica» («Ja no es faran més aportacions de X € a <nom>. Les que ja s'han fet es queden.») amb «Cancel·lar» i «Eliminar». En eliminar, la targeta torna a «Encara no n'has programat cap.»
Error del servidor o de xarxa: «S'ha produït un error inesperat. Torna-ho a provar més tard.» / «No hi ha connexió amb el servidor. Torna-ho a provar.» sota el botó; l'aportació automàtica queda com estava
```

---

## US-25 Afegir subcompte en divisa

**Labels:** Fina, Mitjana, Multidivisa, P6

**Descripció:**

```
COM: client estàndard
VULL: afegir un subcompte en una nova divisa
PER: tenir saldo en aquesta moneda i gestionar-la per separat.

Perfil: client estàndard que vol tenir diners en una altra moneda.

Assumptes:
- Un sol subcompte per divisa
- El subcompte nou neix amb saldo 0
- El total de totes les divises es mostra aproximat en euros
```

**Checklist Acceptance Criteria:**

```
A Inici hi ha el botó «Divises» i la card «Divises» amb «Total ≈ … €».
`/divises` mostra els comptes i el botó «Afegir divisa».
«Afegir divisa» mostra EUR, USD, GBP, CHF i JPY amb codi i nom. Les que ja tinc (inclòs l'EUR) surten en gris amb «ja la tens».
En triar-ne una surt el tic verd «Subcompte en USD creat» i, 1,5 s després, torna a Inici, on surt amb «0,00 $».
Divisa repetida: «Ja tens un subcompte en aquesta divisa.» Divisa fora de la llista: «Aquesta divisa no és a la llista de divises disponibles.»
Un subcompte nou no mou el total. El JPY no té decimals («1.234 ¥»).
```

---

## US-26 Eliminar subcompte en divisa

**Labels:** Fina, Mitjana, Multidivisa, P6

**Descripció:**

```
COM: client estàndard amb subcomptes en divisa
VULL: eliminar un subcompte en divisa
PER: netejar la pantalla principal quan ja no necessito aquella moneda.

Perfil: client estàndard que té almenys un subcompte en divisa.

Assumptes:
- Només es pot eliminar si el saldo és 0
- Si té saldo, cal buidar-lo abans
```

**Checklist Acceptance Criteria:**

```
El detall del subcompte té el botó vermell «Eliminar subcompte». Al de l'EUR no surt, i el servidor respon «El compte en euros no es pot eliminar.»
Amb saldo diferent de 0 (n'hi ha prou amb 0,01 $) surt «Abans d'eliminar-lo has de deixar el saldo a 0» amb «D'acord», i no s'elimina.
Amb saldo 0 surt «Segur que vols eliminar aquest subcompte?» amb «Cancel·lar» i «Eliminar».
En confirmar surt el tic «Subcompte eliminat», l'app torna sola a Inici i el subcompte ja no hi és. La divisa torna a estar disponible a «Afegir divisa».
Els moviments antics es queden a l'historial.
El subcompte no té botó «Aportar» en aquest sprint: el saldo només s'omple (i es buida) amb «Canviar» (US-27).
```

---

## US-27 Canviar entre divises

**Labels:** Fina, Alta, Multidivisa, P6

**Descripció:**

```
COM: client estàndard amb subcomptes en divisa
VULL: canviar diners entre les meves divises
PER: tenir saldo en la moneda que necessito en cada moment.

Perfil: client estàndard amb almenys dos subcomptes, un d'ells amb saldo.

Assumptes:
- Calen dos subcomptes i saldo a l'origen
- Es mostra el tipus de canvi i la comissió abans de confirmar
```

**Checklist Acceptance Criteria:**

```
Amb un sol subcompte, «Canviar» mostra «Necessites dos subcomptes per canviar divises.» i el botó «Divises».
A «Canviar» trio l'origen i el destí. L'origen surt en gris al selector de destí.
Amb el teclat surt «Rebràs aproximadament». Si l'import és massa petit: «L'import és massa petit per canviar.» i «Continuar» queda desactivat.
El resum mostra el tipus, la comissió (sempre n'hi ha: 1,5 %, mínim 0,50 €), el càrrec a l'origen i «Rebràs exactament». No s'envia res fins a «Confirmar canvi».
Saldo insuficient (import + comissió): «No tens prou saldo» en vermell.
Èxit: tic «Canvi fet» i torna a Inici amb els dos saldos i el total actualitzats.
Tot o res: o canvien els dos saldos i els dos moviments, o no en canvia cap.
```

---

## US-28 Pagar en divisa des del subcompte

**Labels:** Fina, Alta, Multidivisa, P6

**Descripció:**

```
COM: client estàndard amb subcomptes en divisa
VULL: enviar diners a un altre usuari en una divisa des del meu subcompte
PER: pagar despeses de viatges i compres internacionals amb amics.

Perfil: client estàndard que té almenys un subcompte en divisa (US-25).

Assumptes:
- És un enviament de la US-14 amb una divisa triada (decisió C, 24/11)
- Aquí es paga només des del subcompte d'aquella divisa; pagar des dels euros és la US-42
- Qui rep ho rep en la mateixa divisa si té aquell subcompte; si no, en euros al tipus de canvi, sense comissió
- El límit diari de 1.000,00 € de la US-14 compta l'equivalent en euros

Estimació: SP 3 · VP 7 · Prioritat Alta

Revisió del 25/11: La US-28 original («Pagaments en divisa») es divideix en US-28 (des del subcompte) i US-42 (des dels euros).
```

**Checklist Acceptance Criteria:**

```
A «Enviar» (US-14), si tinc algun subcompte en divisa, sota el destinatari hi ha el selector «Divisa» amb EUR i els meus subcomptes amb el seu saldo (per exemple «USD · Dòlar nord-americà · 109,61 $»); per defecte, EUR. Sense subcomptes no surt i «Enviar» és com a la US-14
Amb una divisa triada, l'import s'escriu en aquella divisa amb el símbol al final («20,00 $»; el ien, sense decimals) i a sota, en gris, «Saldo en USD: 109,61 $». Amb l'import a 0, «Continuar» queda desactivat
Si el subcompte en té prou, «Confirmar» mostra el destinatari, l'import en la divisa, «Es cobra de: Subcompte USD» i el saldo que hi quedarà. No hi ha comissió
Si el subcompte no en té prou, surt en vermell «No tens prou saldo en USD.» i «Continuar» queda desactivat (la US-42 hi afegeix pagar des dels euros)
El límit diari de 1.000,00 € de la US-14 compta l'equivalent en euros al tipus de canvi del moment: per sobre surt «Has superat el límit diari de 1.000,00 €.» i «Continuar» queda desactivat
En confirmar: tic verd «Has enviat 20,00 $ a Izan» amb el saldo que queda al subcompte; 1,5 s després torna a Inici
Qui rep ho rep al seu subcompte d'aquella divisa si el té («+20,00 $»); si no, al compte en euros al tipus de canvi i sense comissió («+18,18 €»). A la seva bústia arriba «<nom> t'ha enviat 20,00 $»
A l'historial del subcompte de qui envia surt en vermell «−20,00 $» amb el nom i el concepte
Si el saldo o el límit canvien entre «Continuar» i «Confirmar enviament», surt el mateix missatge i no s'envia res
Error del servidor o de xarxa: «S'ha produït un error inesperat. Torna-ho a provar més tard.» / «No hi ha connexió amb el servidor. Torna-ho a provar.» sota el botó; no canvia cap saldo
```

---

## US-42 Pagar en divisa des dels euros

**Labels:** Fina, Mitjana, Multidivisa, P6

**Descripció:**

```
COM: client estàndard
VULL: enviar diners en una divisa encara que el meu subcompte no en tingui prou
PER: poder pagar igualment des dels meus euros.

Perfil: client estàndard o premium que paga en una divisa (US-28) sense prou saldo al subcompte.

Assumptes:
- Depèn de la US-28 (selector de divisa)
- Es fa servir el tipus de canvi i la comissió de la US-27 (1,5 %, mínim 0,50 €)
- Per al client premium compta com un canvi per al límit mensual sense comissió de la US-29
- Mai es barregen els dos orígens: o tot del subcompte o tot dels euros

Estimació: SP 3 · VP 6 · Prioritat Mitjana

Revisió del 25/11: Ve de la US-28 original («Pagaments en divisa»). Defineix què paga el client premium.
```

**Checklist Acceptance Criteria:**

```
Si el subcompte no en té prou però els euros sí, ja no surt «No tens prou saldo en USD.»: «Continuar» queda actiu i «Confirmar» mostra «Es cobra de: Compte en euros», el tipus de canvi («1 € = 1,10 $»), la comissió en vermell i «Se't descomptaran X €» (import en euros + comissió)
Si tampoc hi ha prou euros per a l'import i la comissió, a «Enviar» surt en vermell «No tens prou saldo.» i «Continuar» queda desactivat
Per al client premium, aquest pagament compta per al límit de 5.000,00 € al mes de la US-29, com un canvi: dins del límit, «Confirmar» diu «Sense comissió» en verd; si el passa, la comissió és només de la part que el passa
En confirmar: tic verd «Has enviat 150,00 $ a Izan» amb el saldo en euros que queda; 1,5 s després torna a Inici
Als moviments de qui paga surt a Inici i a Moviments en vermell l'import en euros («−138,41 €») i a sota, en gris, «150,00 $ · 1 € = 1,10 $» i «Comissió: 2,05 €» (sense comissió, aquesta última línia no surt)
Qui rep ho rep igual que a la US-28
El tipus de canvi i la comissió els calcula el servidor: si canvien entre «Continuar» i «Confirmar enviament», surt «El tipus de canvi ha canviat. Revisa l'import.» amb les xifres noves i no s'envia res fins que es torna a confirmar
Error del servidor o de xarxa: «S'ha produït un error inesperat. Torna-ho a provar més tard.» / «No hi ha connexió amb el servidor. Torna-ho a provar.» sota el botó; no canvia cap saldo
```

---

## US-29 Canvi sense comissió per al client premium

**Labels:** Fina, Mitjana, Multidivisa, P6

**Descripció:**

```
COM: client premium
VULL: tenir un límit mensual de canvi de moneda sense comissió
PER: estalviar diners en les meves operacions internacionals.

Perfil: client premium (límit de 5.000 € al mes sense comissió). El client estàndard no canvia: sempre paga la comissió de la US-27 (1,5 %, mínim 0,50 €) (decisió A, 24/11).

Assumptes:
- Al seed hi ha un usuari premium per a la demo
- Fins al límit del mes, 0 % de comissió; el límit compta l'import en euros de cada canvi
- També compten els pagaments en divisa cobrats dels euros (US-42)
- Un canvi que passa el límit paga comissió només sobre la part que el passa
- El límit torna a començar el dia 1 de cada mes, en hora de Madrid

Estimació: SP 3 · VP 5 · Prioritat Mitjana

Revisió del 25/11: S'aclareix que els pagaments en divisa cobrats dels euros (US-42) compten per al límit.
```

**Checklist Acceptance Criteria:**

```
Al seed hi ha un usuari premium per a la demo. Per al client premium, els canvis fins a 5.000,00 € al mes (sumant l'import en euros de cada canvi) no tenen comissió
Els pagaments en divisa cobrats dels euros (US-42) compten per al mateix límit, igual que un canvi
Mentre no arriba al límit, el resum del canvi (US-27) diu «Sense comissió» en verd en lloc de «Comissió: …» i a sota, en gris, «Et queden X € sense comissió aquest mes»; «Se't descomptaran» és igual a l'import
Si un canvi passa el límit, la comissió (1,5 %, mínim 0,50 €) es calcula només sobre la part que el passa, surt en vermell i a sota diu «Passes el límit en X €: només pagues comissió d'aquesta part»
Un cop passat el límit, els canvis tenen la comissió normal de la US-27 fins al dia 1 del mes següent a les 00:00 de Madrid
Als moviments, els canvis amb comissió la mostren en gris sota l'import; els que no en tenen, no
Per al client estàndard no canvia res: el resum mostra sempre la comissió de la US-27 i mai «Sense comissió»
El càlcul el fa el servidor: si el límit canvia entre el resum i «Confirmar canvi», s'aplica el que toca i el tic mostra la comissió cobrada
```

---

### EP-06 Multidivisa

**Labels:** Èpica, Multidivisa, P6

**Descripció:**

```
COM: client estàndard
VULL: tenir saldos en diferents divises dins del meu compte i canviar entre elles
PER: gestionar els diners quan viatjo o pago en altres monedes.

Perfil: client estàndard i client premium (el premium té un límit de canvi sense comissió més alt, US-29). Històries: US-25 a US-29 i US-42 (la US-28 es va dividir en dues el 25/11).
```

**Checklist Acceptance Criteria:**

```
L'usuari pot afegir i eliminar subcomptes en diferents divises (un subcompte per divisa).
La pantalla principal mostra el saldo de cada divisa i el total aproximat en EUR.
L'usuari pot canviar diners entre divises visualitzant el tipus de canvi, la comissió i l'import final abans de confirmar.
Els pagaments es cobren de la divisa corresponent si hi ha saldo (US-28), o de la principal aplicant el canvi (US-42).
Els moviments mostren l'import original, el tipus de canvi i la comissió de les operacions en divises.
```

---

# Tech / Sprint 0

## TR-05 CI/CD pipeline

**Labels:** Tech, DevOps, Sprint0

**Descripció:**

```
COM: equip tècnic
VULL: tenir pipeline de CI/CD abans de codi de producte
PER: fer build i tests automàtics a cada push.

Assumptes:
- GitHub Actions o similar
- Build + tests al fer push

Estimació: Sprint 0
```

**Checklist Acceptance Criteria:**

```
Cada push executa build i tests automàticament
Un test fallit deixa el pipeline en vermell
```

---

## TR-06 Entorn de demo desplegable

**Labels:** Tech, DevOps, Sprint0

**Descripció:**

```
COM: equip tècnic
VULL: poder desplegar la demo a un entorn compartit
PER: mostrar el producte a la classe.

Assumptes:
- Decidir hosting
- Config entorn demo

Estimació: Sprint 0
```

**Checklist Acceptance Criteria:**

```
Demo accessible per URL
Reinici possible sense perdre dades demo
```

---

## Spike-01 Stack frontend/backend

**Labels:** Tech, Spike, Sprint0

**Descripció:**

```
COM: equip tècnic
VULL: triar stack que l'equip pugui mantenir en 4 sprints
PER: no perdre temps en tecnologia que no dominem.

Assumptes:
- Comparar opcions ràpides
- Decisió registrada al repo

Estimació: Sprint 0
```

**Checklist Acceptance Criteria:**

```
Decisió documentada
Prototip mínim de stack executant-se
```
