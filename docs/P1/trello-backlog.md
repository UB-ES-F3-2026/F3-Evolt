# Cards Trello — copiar i enganxar

> Obre el tauler → **Backlog** → **+ Afegeix una tarjeta**
> 1. Enganxa el **títol**
> 2. Obre la card → enganxa **Descripció**
> 3. **Checklist** → nom `Acceptance Criteria` → enganxa els items
> 4. Labels si en tens
>
> **No hi ha import automàtic.** Tot a mà des d'aquest fitxer.

**Numeració:** `US-XX` sencera (01…29), com al doc de l'equip. Sense decimals.

| Persona | Bloc | US |
|---------|------|-----|
| **P1** | Alta i primers passos | US-01, US-02, US-03, US-04, US-09 |
| **P2** | Estalvi | US-17…US-20 |
| **P3** | Pantalla principal i XP | US-07, US-23, US-24 |
| **P4** | Moviments | US-08, US-10, US-11 |
| **P5** | Social | US-13, US-15, US-16 |
| **P6** | Transferències + Multidivisa | US-12, US-14, US-21, US-25…US-29 |

**Sincronitzat amb el Trello el 20/10/2026.** Si canvies una card al Trello, canvia-la també aquí.

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

### EP-01 Registre i accés

**Labels:** Èpica, Alta-compte, P1

**Descripció:**

```
Tot el que necessita un usuari per crear el compte i entrar-hi de forma segura.

Perfil: visitant (registre), client nou (verificació del codi) i client estàndard (inici de sessió i recuperar la contrasenya). Històries: US-1, US-2, US-3 i US-4.
```

---

### EP-14 Perfil i preferències

**Labels:** Èpica

**Descripció:**

```
COM: client estàndard
VULL: gestionar les meves dades i preferències
PER: adaptar l’app a mi

Històries previstes: editar perfil, canviar email o telèfon, canviar contrasenya, preferències de notificacions

Perfil: client estàndard.
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

**Labels:** Mitjana, Gamificació, XP, P3

**Descripció:**

```
COM: client estàndard
VULL: guanyar XP quan faig accions financeres saludables
PER: sentir-me motivat a mantenir bons hàbits d'estalvi.

Perfil: client estàndard. Els XP de cada acció els configura l'administrador (EP-15).

Assumptes:
- XP en crear la primera guardiola, aportar i assolir un objectiu
- Límit diari d'XP per acció per evitar trampes
- Retirar una aportació abans de 7 dies resta els XP que havia donat

Estimació: SP 4 · VP 7 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Guanyo XP en crear la primera guardiola, en aportar a una guardiola i en assolir un objectiu d'estalvi
Els XP que dona cada acció es defineixen en una configuració que l'administrador pot canviar (EP-15), no a cada pantalla
Quan guanyo XP, surt a dalt de la pantalla durant uns segons un avís amb "+X XP" en lila i el motiu (per exemple "+20 XP · Aportació a Viatge")
Si retiro una aportació abans de 7 dies, es resten sols els XP que m'havia donat i a l'historial surt "−X XP" en vermell
Cada acció té un màxim d'XP per dia; un cop arribat, l'acció es pot fer però ja no dona XP
La pantalla "Historial d'XP" mostra una fila per cada canvi amb la data, el motiu i els XP (en verd si en guanyo, en vermell si en perdo)
```

---

## US-24 Nivells i perfil de progrés

**Labels:** Mitjana, Gamificació, XP, P3

**Descripció:**

```
COM: client estàndard
VULL: pujar de nivell en acumular XP
PER: veure el meu progrés financer a llarg termini.

Perfil: client estàndard.

Assumptes:
- Cada nivell necessita més XP que l'anterior
- Celebració en pujar de nivell

Estimació: SP 3 · VP 6 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Quan els XP arriben al mínim del nivell següent, pujo de nivell sol, sense fer res
En pujar de nivell surt una pantalla de celebració amb el text "Has pujat al nivell X!" i el botó lila "Continuar"
Cada nivell necessita més XP que l'anterior (per exemple: nivell 2 amb 100 XP i nivell 3 amb 250 XP)
La pantalla "Perfil" mostra el nivell actual en gran, els XP totals i una barra lila amb els XP que falten per al nivell següent (per exemple "180 / 250 XP")
A "Inici", sota el saldo, surt en petit el nivell actual i la seva barra de progrés
```

---

### EP-05 Gamificació: XP i nivells

**Labels:** Èpica, Gamificació, P3

**Descripció:**

```
El nucli de la gamificació: premiar els hàbits saludables amb XP i nivells.

Perfil: client estàndard. Els valors d'XP i els nivells els configura l'administrador (EP-15). Històries: US-23 i US-24.
```

---

### EP-15 Administració de la gamificació

**Labels:** Èpica, Gamificació, P3

**Descripció:**

```
COM: administrador
VULL: configurar reptes, insígnies i valors d'XP des d'un panell
PER: mantenir la gamificació al dia sense publicar noves versions de l'app

Perfil: administrador, és a dir, una persona de l'equip d'Evolt amb permisos de gestió (no és un client).
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

Estimació: SP 3 · VP 6 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A la pantalla d'una guardiola hi ha el botó "Retirar", que obre la pantalla "Retirar de <nom de la guardiola>"
A dalt es veu el saldo que té la guardiola
L'import ha de ser més gran que 0 i no més gran que el saldo de la guardiola; si no, la casella es posa vermella, surt el motiu en vermell i el botó "Confirmar" queda desactivat
En confirmar, el saldo de la guardiola baixa i el principal puja exactament el mateix import
Surt un tic verd amb "Has retirat X € de <nom>"
A l'historial de la guardiola surt la retirada en vermell amb "−" i el concepte "Retirada"
Si el servidor falla, surt el missatge d'error en vermell i cap dels dos saldos canvia
Si la guardiola té 0,00 €, el botó "Retirar" surt desactivat (gris clar)
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

Estimació: SP 3 · VP 5 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
La pantalla d'una guardiola amb objectiu mostra el saldo i l'objectiu (per exemple "120,00 € de 500,00 €"), una barra de progrés i el percentatge
La part plena de la barra, en lila, correspon al percentatge: amb un 24 %, la barra està plena una quarta part aproximadament
Si el saldo és menor que l'objectiu, surt l'etiqueta grisa "En progrés"
Si el saldo arriba o passa l'objectiu, la barra es posa verda i surt l'etiqueta verda "Objectiu assolit"
A la llista de guardioles, cada guardiola amb objectiu té una barra petita sota el nom
Les guardioles sense objectiu no tenen barra, només el saldo
Després d'aportar o retirar, la barra i el percentatge ja surten actualitzats
El percentatge també surt escrit amb números (per exemple "24 %"), no només com a barra
```

---

### EP-04 Estalvi amb guardioles

**Labels:** Èpica, Estalvi, P2

**Descripció:**

```
Crear objectius d'estalvi i moure-hi diners, de forma manual o automàtica.

Perfil: client estàndard. El client nou també pot crear la seva primera guardiola. Històries: US-17 a US-21.
```

---

### EP-12 Reptes i ratxes

**Labels:** Èpica, P2

**Descripció:**

```
COM: equip / PO
VULL: refinar l'àrea de reptes i ratxes d'estalvi
PER: tenir claredat abans dels sprints que ho implementen.

Assumptes:
- Relació: refina P2
- Reptes d'estalvi, ratxes, XP per aportar

Estimació: per definir en refinement

Perfil: les futures històries seran de client estàndard.
```

**Checklist Acceptance Criteria:**

```
L'àrea té almenys una US futura o spike associat
El PO accepta l'èpica com a contenidor del backlog
```

---

### EP-11 Insígnies i recompenses

**Labels:** Èpica

**Descripció:**

```
COM: client estàndard
VULL: aconseguir insígnies i desbloquejar recompenses
PER: sentir que els meus progressos es reconeixen i mantenir la motivació

Perfil: client estàndard. El client nou veu el tutorial de benvinguda.
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

### EP-10 Anàlisi de despeses i pressupostos

**Labels:** Èpica, Moviments, P4

**Descripció:**

```
COM: client estàndard
VULL: veure en què gasto i fixar pressupostos
PER: controlar millor les meves finances.

Assumptes:
- Històries previstes: categorització automàtica i manual, gràfic mensual, crear pressupost, avisos de pressupost, XP per pressupost complert
- Depèn del sistema d'XP (US-23)
- Pendent de decidir com es categoritza una despesa sense comerços

Estimació: per definir en refinement

Perfil: client estàndard amb moviments.
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

Estimació: SP 2 · VP 6 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A la pantalla "Enviar diners" hi ha una barra de cerca amb el text gris "@usuari, telèfon o email", i mentre escric surten els usuaris que coincideixen
Cada resultat mostra només la foto rodona, el nom visible i, a sota en gris, el @usuari; mai cap saldo ni moviment
Si busco el meu propi nom o @usuari, no surto als resultats
```

---

## US-15 Sol·licitar diners

**Labels:** Mitjana, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: demanar diners a un contacte
PER: que em torni el que em deu.

Perfil: client estàndard.

Assumptes:
- Estats: pendent, pagada, rebutjada i caducada
- Una sol·licitud sense resposta caduca als 7 dies

Estimació: SP 3 · VP 6 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Amb el botó "Demanar diners" trio el destinatari, escric l'import i un concepte; en tocar el botó lila "Enviar sol·licitud", el destinatari rep la notificació "<nom> et demana X €"
A "Sol·licituds enviades" veig cada sol·licitud amb el seu estat en una etiqueta de color: "Pendent" (gris), "Pagada" (verd), "Rebutjada" (vermell) o "Caducada" (gris clar)
Les sol·licituds pendents tenen el botó "Cancel·lar", que demana confirmació i la treu de la llista
Si en 7 dies ningú respon, la sol·licitud passa sola a "Caducada"
```

---

## US-16 Respondre a una sol·licitud

**Labels:** Mitjana, Social, P5

**Descripció:**

```
COM: client estàndard
VULL: pagar o rebutjar les sol·licituds que rebo
PER: decidir què pago.

Perfil: client estàndard que ha rebut una sol·licitud.

Assumptes:
- En pagar s'obre l'enviament amb les dades ja posades
- Sense saldo, s'ofereix afegir diners

Estimació: SP 3 · VP 6 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
A "Sol·licituds rebudes" cada sol·licitud té dos botons: "Pagar" (lila) i "Rebutjar" (blanc amb el text en vermell)
En tocar "Pagar" s'obre la pantalla "Confirmar" de l'enviament (US-14) amb el destinatari, l'import i el concepte ja posats
En tocar "Rebutjar", qui l'ha enviada rep la notificació "<nom> ha rebutjat la teva sol·licitud"
Si no tinc prou saldo per pagar-la, surt en vermell "No tens prou saldo" i el botó lila "Afegir diners", que obre la recàrrega
```

---

### EP-09 Despeses compartides

**Labels:** Èpica, Social, P5

**Descripció:**

```
Dividir despeses i estalviar en grup per gestionar diners en comú sense complicacions.

(Històries previstes: dividir una despesa, seguiment de pagaments dividits, crear guardiola compartida, aportar, retirar i abandonar en grup.)

Perfil: client estàndard que comparteix despeses o estalvis amb altres clients.
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
Competir i col·laborar amb amics per motivar-nos mútuament a estalviar.

(Històries previstes: reptes amb amics, invitacions a reptes, rànquing setmanal, privacitat del rànquing.)

Perfil: client estàndard que té contactes a l'app.
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

Perfil: client estàndard. Històries: US-13, US-14, US-15 i US-16.
```

---

# P6 — Transferències + Multidivisa

## US-12 Dades del compte (IBAN)

**Labels:** Mitjana, Transferències, P6

**Descripció:**

```
COM: client estàndard
VULL: consultar el meu IBAN
PER: poder rebre transferències d'altres bancs.

Perfil: client estàndard amb el compte actiu.

Assumptes:
- IBAN, BIC i titular visibles
- L'IBAN es pot copiar

Estimació: SP 2 · VP 5 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
A la pantalla "Dades del compte" surten, una sota l'altra, l'IBAN (en grups de 4 caràcters, per exemple "ES12 3456 7890 ..."), el BIC i el nom del titular
En tocar l'IBAN es copia, i a baix surt durant uns segons el missatge "IBAN copiat"
El botó "Compartir" obre el menú del mòbil per enviar les dades per WhatsApp, email o altres apps
Quan arriba una transferència d'un altre banc, surt als moviments en verd amb "+" i arriba la notificació "Has rebut X €"
```

---

## US-14 Enviar Diners a Usuaris

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

Estimació: SP 5 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A la pantalla "Pagaments" puc triar un destinatari de la llista o amb la cerca (US-13)
En triar-lo s'obre la pantalla "Enviar", amb la foto i el nom del destinatari a dalt, un teclat numèric per escriure l'import (més gran que 0 i per sota del límit diari) i una casella opcional "Concepte"
En tocar el botó lila "Continuar" s'obre la pantalla "Confirmar" amb el resum: foto i nom del destinatari, import en gran i concepte
Si en tocar "Confirmar enviament" no tinc prou saldo, surt en vermell "No tens prou saldo" i no s'envia res
Si tinc saldo, surt un tic verd amb "Has enviat X € a <nom>", els diners arriben a l'instant i el saldo ja surt actualitzat
Tots dos reben una notificació: "Has enviat X € a <nom>" i "<nom> t'ha enviat X €"
En tornar a "Inici", el pagament surt a la llista de moviments de tots dos: en vermell amb "−" per a qui envia i en verd amb "+" per a qui rep
```

---

## US-21 Aportació periòdica automàtica

**Labels:** Mitjana, Estalvi, Transferències, P6

**Descripció:**

```
COM: client estàndard amb guardioles
VULL: programar aportacions automàtiques
PER: estalviar de forma constant sense pensar-hi.

Perfil: client estàndard que ja té almenys una guardiola.

Assumptes:
- Freqüència setmanal o mensual
- Sense saldo, no es fa l'aportació i arriba una notificació

Estimació: SP 4 · VP 6 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
A la pantalla d'una guardiola, l'opció "Aportació automàtica" permet triar l'import, la freqüència ("Cada setmana" o "Cada mes") i el dia
El dia programat, l'import passa sol del saldo principal a la guardiola i surt als moviments amb el concepte "Aportació automàtica"
Si aquell dia no hi ha prou saldo, no es fa l'aportació i arriba la notificació "No s'ha pogut fer l'aportació automàtica a <nom>: saldo insuficient"
L'aportació programada té els botons "Pausar", "Editar" i "Eliminar" (aquest últim en vermell i amb confirmació)
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

Estimació: SP 4 · VP 6 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
A "Inici" hi ha el botó "Divises", que obre la gestió de subcomptes
El botó "Afegir divisa" obre la llista de divises disponibles, cadascuna amb el codi i el nom (per exemple "USD · Dòlar americà")
Les divises de les quals ja tinc subcompte surten en gris i no es poden triar, perquè només hi pot haver un subcompte per divisa
En triar una divisa surt un tic verd amb "Subcompte en USD creat" i l'app torna a "Inici"
A "Inici", el subcompte nou surt a la llista amb saldo 0 i el símbol de la seva moneda (per exemple "0,00 $")
A "Inici" es veu el saldo de cada divisa i, a sota, el total aproximat en euros (per exemple "Total ≈ 1.540,20 €")
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

Estimació: SP 2 · VP 4 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
A la pantalla d'un subcompte hi ha el botó vermell "Eliminar subcompte"
Si el subcompte té saldo, surt una finestra amb el text "Abans d'eliminar-lo has de deixar el saldo a 0" i no s'elimina
Si el saldo és 0, surt una finestra que pregunta "Segur que vols eliminar aquest subcompte?" amb els botons "Cancel·lar" i "Eliminar" (en vermell)
En confirmar, l'app torna a "Inici" i el subcompte ja no surt a la llista
```

---

## US-27 Canviar entre divises

**Labels:** Fina, Mitjana, Multidivisa, P6

**Descripció:**

```
COM: client estàndard amb subcomptes en divisa
VULL: canviar diners entre les meves divises
PER: tenir saldo en la moneda que necessito en cada moment.

Perfil: client estàndard amb almenys dos subcomptes, un d'ells amb saldo.

Assumptes:
- Calen dos subcomptes i saldo a l'origen
- Es mostra el tipus de canvi i la comissió abans de confirmar

Estimació: SP 5 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A la pantalla "Canviar" trio el subcompte d'origen (a dalt) i el de destí (a sota)
Amb un teclat numèric escric l'import que vull canviar, i a sota surt en gris quant rebré aproximadament
En tocar "Continuar" surt la pantalla de resum amb el tipus de canvi (per exemple "1 € = 1,08 $"), la comissió (o "Sense comissió") i l'import exacte que rebré
En tocar el botó lila "Confirmar canvi", si tinc prou saldo a l'origen surt un tic verd amb "Canvi fet"; si no, surt en vermell "No tens prou saldo"
En tornar a "Inici", els saldos dels dos subcomptes ja surten actualitzats
```

---

## US-28 Pagaments en divisa

**Labels:** Mitjana, Multidivisa, P6

**Descripció:**

```
COM: client estàndard amb subcomptes en divisa
VULL: fer pagaments en una altra divisa
PER: fer compres internacionals o viatjar sense preocupacions.

Perfil: client estàndard que paga en una moneda que no és l'euro.

Assumptes:
- Si hi ha saldo al subcompte d'aquella divisa, es cobra d'allà
- Si no, es cobra dels euros amb el canvi aplicat sol
- Els moviments mostren l'import original, el tipus de canvi i la comissió

Estimació: SP 5 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
Si pago en una divisa estrangera i tinc prou saldo al subcompte d'aquella divisa, el pagament es treu d'aquest subcompte
Si no tinc prou saldo en aquella divisa, el pagament es treu del compte principal en euros, aplicant el canvi sol
Als moviments, un pagament en divisa mostra en vermell l'import original (per exemple "−20,00 $") i a sota, en gris, el tipus de canvi aplicat i la comissió si n'hi ha
```

---

## US-29 Límit de canvi sense comissió

**Labels:** Mitjana, Multidivisa, P6

**Descripció:**

```
COM: client estàndard o client premium
VULL: tenir un límit mensual de canvi de moneda sense comissions
PER: estalviar diners en les meves operacions internacionals.

Perfil: client estàndard (límit de 1.000 € al mes sense comissió) i client premium (límit de 5.000 € al mes).

Assumptes:
- Fins al límit del mes, 0 % de comissió
- Un cop passat el límit, la comissió es mostra abans d'acceptar
- El límit torna a començar el dia 1 de cada mes

Estimació: SP 3 · VP 5 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Fins al límit del mes (1.000 € per al client estàndard i 5.000 € per al client premium), els canvis de divisa tenen 0 % de comissió i al resum surt "Sense comissió"
Un cop passat el límit, la pantalla de resum mostra en vermell la comissió que se suma (per exemple "Comissió: 2,50 €") abans de tocar "Confirmar canvi"
Als moviments posteriors al límit, la comissió cobrada surt en gris sota l'import
```

---

### EP-06 Multidivisa

**Labels:** Èpica, Multidivisa, P6

**Descripció:**

```
COM: client estàndard
VULL: tenir saldos en diferents divises dins del meu compte i canviar entre elles
PER: gestionar els diners quan viatjo o pago en altres monedes

Perfil: client estàndard i client premium (el premium té un límit de canvi sense comissió més alt, US-29). Històries: US-25 a US-29.
```

**Checklist Acceptance Criteria:**

```
L'usuari pot afegir i eliminar subcomptes en diferents divises (un subcompte per divisa).
La pantalla principal mostra el saldo de cada divisa i el total aproximat en EUR.
L'usuari pot canviar diners entre divises visualitzant el tipus de canvi, la comissió i l'import final abans de confirmar.
Els pagaments es cobren de la divisa corresponent si hi ha saldo, o de la principal aplicant el canvi.
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
Pipeline es pot executar
Falla si els tests KO
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
