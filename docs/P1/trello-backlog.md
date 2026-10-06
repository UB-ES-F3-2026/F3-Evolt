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

---

# P1 — Alta i primers passos

## US-01 Registre amb email o telèfon

**Labels:** Fina, Alta, Alta-compte, P1

**Descripció:**

```
COM: a nou usuari
VULL: registrar-me amb email o telèfon i contrasenya
PER: obrir un compte al neobanc.

Assumptes:
- Contrasenya: mínim 8 caràcters, 1 majúscula, 1 número
- Compte nou en estat "pendent de verificació"
- Cal acceptar termes i política de privacitat

Estimació: SP 5 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
El formulari demana email o telèfon, contrasenya i confirmació
Contrasenya no vàlida → error sota el camp
Contrasenyes no coincideixen → no es pot continuar
Email/telèfon ja registrats → missatge que ho indica
Botó registre desactivat fins acceptar termes i privacitat
En enviar correctament, el compte queda "pendent de verificació"
```

---

## US-02 Verificació del codi de registre

**Labels:** Fina, Alta, Alta-compte, P1

**Descripció:**

```
COM: a nou usuari
VULL: confirmar el meu email o telèfon amb un codi
PER: demostrar que són meus.

Assumptes:
- Codi de 6 dígits per email o SMS
- Caducitat: 10 minuts
- Màxim 5 intents fallits

Estimació: SP 3 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
Després del registre s'envia un codi de 6 dígits
El codi caduca als 10 minuts
Codi correcte → compte activat i accedo a la pantalla principal
Codi incorrecte o caducat → error
Puc demanar un codi nou i l'anterior deixa de ser vàlid
Després de 5 intents fallits, cal demanar un codi nou
```

---

## US-03 Inici de sessió amb contrasenya

**Labels:** Fina, Alta, Alta-compte, P1

**Descripció:**

```
COM: a usuari
VULL: iniciar sessió amb email o telèfon i contrasenya
PER: accedir al meu compte.

Assumptes:
- Missatge d'error genèric (no diu quin camp falla)
- Bloqueig temporal després de 5 intents
- Timeout de sessió: 5 minuts sense activitat

Estimació: SP 4 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
Credencials correctes → accedo a la pantalla principal
Credencials incorrectes → missatge genèric
5 intents fallits → compte bloquejat 15 minuts + avís per email
5 minuts sense activitat → sessió tancada, cal tornar a autenticar
Puc tancar la sessió des del menú
```

---

## US-04 Recuperació de contrasenya

**Labels:** Fina, Alta, Alta-compte, P1

**Descripció:**

```
COM: a usuari
VULL: restablir la contrasenya si l'oblido
PER: no perdre l'accés al compte.

Assumptes:
- Enllaç vàlid 30 minuts
- Email no registrat → mateix missatge que si ho està (no revelar)
- En canviar-la, es tanquen sessions obertes en altres dispositius

Estimació: SP 3 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A Inici de sessió hi ha "He oblidat la contrasenya"
En introduir l'email, rebo un enllaç vàlid 30 minuts
Email no registrat → mateix missatge que si ho està
Nova contrasenya ha de complir els mateixos requisits que al registre
En canviar-la, es tanquen sessions en altres dispositius
Enllaç caducat → avís i opció de demanar-ne un de nou
```

---

## US-09 Recàrrega de prova

**Labels:** Fina, Alta, Compte, P1

**Descripció:**

```
COM: a usuari
VULL: afegir diners amb una recàrrega de prova
PER: poder fer servir els pagaments i l'estalvi.

Assumptes:
- Recàrrega simulada, sense targeta
- Límits: > 0 i ≤ 500 € per recàrrega; ≤ 1.000 € al dia
- Les recàrregues no donen XP

Estimació: SP 3 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A la pantalla principal hi ha "Afegir diners"
Puc introduir un import > 0 i ≤ 500 € per recàrrega
No es demanen dades de targeta; s'aprova automàticament
No puc recarregar més de 1.000 € en un mateix dia
En confirmar, el saldo s'actualitza i apareix als moviments com "Recàrrega"
Les recàrregues no donen XP
```

---

### EP-01 Registre i accés

**Labels:** Èpica, Alta-compte, P1

**Descripció:**

```
COM: nou usuari
VULL: crear el compte i entrar-hi de forma segura
PER: utilitzar el neobanc.

Assumptes:
- Contenidor de US-01, US-02, US-03, US-04

Estimació: per definir en refinement
```

**Checklist Acceptance Criteria:**

```
L'àrea té almenys una US al backlog
El PO accepta l'èpica com a contenidor
```

---

# P3 — Pantalla principal i XP

## US-07 Saldo a la pantalla principal

**Labels:** Fina, Alta, Home, P3

**Descripció:**

```
COM: a usuari
VULL: veure el meu saldo a la pantalla principal
PER: saber d'un cop d'ull com tinc els diners.

Assumptes:
- Saldo disponible + total estalviat a guardioles
- Últims 5 moviments
- Icona d'ull per amagar el saldo (preferència persistent)

Estimació: SP 4 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
La pantalla principal mostra el saldo disponible
Mostra el total estalviat a les guardioles
Mostra els 5 últims moviments
Amb moviment nou, el saldo s'actualitza sense reiniciar l'app
Amb la icona d'ull puc amagar el saldo
La preferència d'amagar es manté a la sessió següent
```

---

## US-23 Guanyar XP per hàbits saludables

**Labels:** Mitjana, Gamificació, XP, P3

**Descripció:**

```
COM: a usuari
VULL: guanyar XP quan faig accions financeres saludables
PER: sentir-me motivat a mantenir bons hàbits.

Assumptes:
- XP en: crear 1a guardiola, aportar, assolir objectiu
- Límit diari d'XP per evitar trampes
- Retirar aportació abans de 7 dies → es resta l'XP

Estimació: SP 4 · VP 7 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Guanyo XP en crear la primera guardiola
Guanyo XP en aportar a una guardiola
Guanyo XP en assolir un objectiu d'estalvi
Quan guanyo XP, es mostra missatge amb quantitat i motiu
Si retiro una aportació abans de 7 dies, es resta l'XP d'aquella aportació
Cada acció té límit diari d'XP
Puc consultar l'historial d'XP amb data i motiu
```

---

## US-24 Nivells i perfil de progrés

**Labels:** Mitjana, Gamificació, XP, P3

**Descripció:**

```
COM: a usuari
VULL: pujar de nivell en acumular XP
PER: veure el meu progrés a llarg termini.

Assumptes:
- Cada nivell requereix més XP que l'anterior
- Celebració en pujar de nivell

Estimació: SP 3 · VP 6 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Quan l'XP arriba al llindar del nivell següent, pujo de nivell
Es mostra una celebració en pujar de nivell
Cada nivell requereix més XP que l'anterior
El perfil mostra nivell actual, XP total i barra amb XP que falta
La pantalla principal mostra el nivell i la barra de progrés
```

---

### EP-05 Gamificació: XP i nivells

**Labels:** Èpica, Gamificació, P3

**Descripció:**

```
COM: usuari del neobanc
VULL: guanyar XP i pujar de nivell per hàbits financers saludables
PER: mantenir-me motivat a estalviar i gestionar bé els diners.

Assumptes:
- Contenidor de US-23, US-24
- Es connecta amb EP-04 (guardioles) i EP-11/EP-12

Estimació: per definir en refinement
```

**Checklist Acceptance Criteria:**

```
L'àrea té almenys una US al backlog
El PO accepta l'èpica com a contenidor
```

---

### EP-15 Administració de la gamificació

**Labels:** Èpica, Gamificació, P3

**Descripció:**

```
COM: a administrador
VULL: configurar reptes, insígnies i valors d'XP des d'un panell
PER: mantenir la gamificació al dia sense publicar noves versions.

Assumptes:
- Contenidor de panell admin (crear/activar reptes i insígnies, canvis d'XP)

Estimació: per definir en refinement
```

**Checklist Acceptance Criteria:**

```
L'àrea té almenys una US o spike al backlog
El PO accepta l'èpica com a contenidor
```

---

# P2 — Estalvi

## US-17 Crear guardiola

**Labels:** Fina, Alta, Estalvi, P2

**Descripció:**

```
COM: a usuari registrat
VULL: crear una guardiola amb nom i objectiu opcional
PER: estalviar per a una meta concreta.

Assumptes:
- L'usuari ha d'estar registrat i amb sessió iniciada
- Mínim 1 guardiola per usuari a la demo
- L'objectiu (target) és opcional; si s'introdueix, ha de ser un import positiu
- La guardiola nova neix amb saldo 0
- Cada guardiola pot tenir nom, import objectiu i icona (opcional)

Estimació: SP 5 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
Accedir a Estalvi/Guardioles des de la home
Veure llista o estat buit amb CTA
Obrir formulari (nom, objectiu opcional, icona)
Validar nom obligatori i objectiu > 0
Crear guardiola amb saldo 0
Error xarxa no perd les dades
Funciona en mòbil
```

---

## US-18 Aportar diners a una guardiola

**Labels:** Fina, Alta, Estalvi, P2

**Descripció:**

```
COM: a usuari amb guardioles
VULL: aportar diners des del saldo principal a una guardiola
PER: estalviar cap a un objectiu sense gastar-los del compte principal.

Assumptes:
- L'usuari té almenys 1 guardiola creada (US-17)
- L'usuari té saldo principal suficient
- L'aportació mou saldo: principal ↓, guardiola ↑
- Es registra un moviment dins de la guardiola
- Import mínim d'aportació: > 0

Estimació: SP 5 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
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

## US-19 Retirar diners d'una guardiola

**Labels:** Fina, Alta, Estalvi, P2

**Descripció:**

```
COM: a usuari amb guardioles
VULL: retirar diners d'una guardiola al saldo principal
PER: fer servir els diners estalviats quan els necessiti.

Assumptes:
- L'usuari té almenys 1 guardiola amb saldo > 0
- La retirada mou saldo: guardiola ↓, principal ↑
- Es registra un moviment de retirada
- Import mínim de retirada: > 0
- No es pot retirar més del que té la guardiola

Estimació: SP 3 · VP 6 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
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

## US-20 Progrés i objectiu assolit

**Labels:** Fina, Alta, Estalvi, P2

**Descripció:**

```
COM: a usuari amb guardioles amb objectiu
VULL: veure el progrés cap a cada objectiu i saber quan l'he assolit
PER: mantenir la motivació d'estalviar i celebrar les metes.

Assumptes:
- Sense objectiu no es mostra barra de progrés
- Progrés = saldo / objectiu, en percentatge
- Quan saldo ≥ objectiu → estat "objectiu assolit"
- Es connecta amb gamificació endavant (EP-11/EP-12)

Estimació: SP 3 · VP 5 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
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

### EP-04 Estalvi amb guardioles

**Labels:** Èpica, Estalvi, P2

**Descripció:**

```
COM: usuari del neobanc
VULL: crear objectius d'estalvi i moure-hi diners
PER: estalviar de forma estructurada per a coses concretes.

Assumptes:
- Contenidor de US-17, US-18, US-19, US-20, US-21
- Refinament endavant: aportació periòdica, guardioles compartides

Estimació: per definir en refinement
```

**Checklist Acceptance Criteria:**

```
L'àrea té almenys una US al backlog
El PO accepta l'èpica com a contenidor
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
- Relació: refina P2 (Estalvi)
- Reptes d'estalvi, ratxes, XP per aportar

Estimació: per definir en refinement
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
COM: equip / PO
VULL: refinar insígnies i recompenses connectades amb hàbits financers
PER: celebrar metes i objectius assolits.

Assumptes:
- Es connecta amb guardioles i XP (EP-04, EP-05)
- Insignies: primer estalvi, primer objectiu, pressupost complert

Estimació: per definir en refinement
```

**Checklist Acceptance Criteria:**

```
L'àrea té almenys una US futura o spike associat
El PO accepta l'èpica com a contenidor del backlog
```

---

# P4 — Moviments

## US-08 Llistat de moviments

**Labels:** Fina, Alta, Moviments, P4

**Descripció:**


COM: a usuari del neobanc
VULL: consultar tots els meus moviments
PER: controlar què gasto i què ingresso.

Assumptes:
- Ordenació: del més recent al més antic
- Paginació / infinite scroll
- Estat buit amb missatge

Estimació: SP 3 · VP 7 · Prioritat Alta


**Checklist Acceptance Criteria:**

```
Els moviments es mostren del més recent al més antic
Cada moviment mostra import, concepte, data i tipus (ingrés/despesa)
Ingrés i despesa es diferencien amb color
En arribar al final, se'n carreguen més
Sense moviments, es mostra un missatge que ho indica
```

---

## US-10 Filtres i cerca de moviments

**Labels:** Mitjana, Moviments, P4

**Descripció:**

```
COM: a usuari del neobanc
VULL: filtrar i cercar moviments
PER: trobar ràpidament una operació concreta.

Assumptes:
- Filtres combinables
- Cerca per concepte o contacte
- Buidar filtres

Estimació: SP 3 · VP 5 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Puc filtrar per rang de dates
Puc filtrar per tipus (ingrés o despesa)
Puc cercar per concepte o nom del contacte
Els filtres es poden combinar i esborrar
Sense coincidències, es mostra "sense resultats"
```

---

## US-11 Detall d'un moviment

**Labels:** Mitjana, Moviments, P4

**Descripció:**

```
COM: a usuari del neobanc
VULL: veure el detall de cada moviment
PER: entendre exactament què ha passat amb els meus diners.

Assumptes:
- PDF descarregable
- Formulari de problema vinculat al moviment

Estimació: SP 3 · VP 5 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
En tocar un moviment, veig data i hora, import, estat, contrapart i referència
Puc descarregar un justificant en PDF
Puc reportar un problema amb formulari vinculat a aquell moviment
```

---

### EP-10 Anàlisi de despeses i pressupostos

**Labels:** Èpica, Moviments, P4

**Descripció:**

```
COM: usuari del neobanc
VULL: veure en què gasto i fixar pressupostos
PER: controlar millor les meves finances.

Assumptes:
- Contenidor de categorització, gràfics, pressupostos i XP per pressupost
- Es refinaran en sprints posteriors

Estimació: per definir en refinement
```

**Checklist Acceptance Criteria:**

```
L'àrea té almenys una US al backlog
El PO accepta l'èpica com a contenidor
```

---

# P5 — Social

## US-13 Cercar un usuari

**Labels:** Fina, Alta, Social, P5

**Descripció:**

```
COM: a usuari del neobanc
VULL: trobar altres usuaris de l'app
PER: poder-los-hi enviar diners.

Assumptes:
- Cerca per @usuari, telèfon o email
- Mai es mostren dades financeres als resultats
- No apareixo als meus resultats

Estimació: SP 2 · VP 6 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
Puc cercar per @usuari, telèfon o email
Els resultats mostren nom visible, @usuari i foto (mai dades financeres)
No apareixo als meus propis resultats
Puc marcar un usuari com a favorit i apareix primer
```

---

## US-15 Sol·licitar diners

**Labels:** Mitjana, Social, P5

**Descripció:**

```
COM: a usuari del neobanc
VULL: demanar diners a un contacte
PER: que em torni el que em deu.

Assumptes:
- Estats: pendent, pagada, rebutjada, caducada
- Caducitat: 7 dies sense resposta

Estimació: SP 3 · VP 6 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Puc crear una sol·licitud amb destinatari, import i concepte
El destinatari rep una notificació
Veig les sol·licituds enviades amb el seu estat
Puc cancel·lar una sol·licitud pendent
Una sol·licitud sense resposta caduca als 7 dies
```

---

## US-16 Respondre a una sol·licitud

**Labels:** Mitjana, Social, P5

**Descripció:**

```
COM: a usuari del neobanc
VULL: pagar o rebutjar les sol·licituds que rebo
PER: decidir què pago.

Assumptes:
- En pagar s'obre el flux d'enviament pre-emplenat
- Sense saldo: opció d'afegir diners

Estimació: SP 3 · VP 6 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Puc pagar o rebutjar cada sol·licitud rebuda
En pagar, el flux d'enviament s'obre amb destinatari, import i concepte pre-emplenats
Si la rebutjo, qui l'ha enviada rep una notificació
Si no tinc saldo suficient, se m'ofereix afegir diners
```

---

### EP-09 Despeses compartides

**Labels:** Èpica, Social, P5

**Descripció:**

```
COM: usuari del neobanc
VULL: dividir despeses i estalviar en grup
PER: gestionar diners en comú sense complicacions.

Assumptes:
- Contenidor de dividir despesa, guardioles compartides
- Es refinarà en sprints posteriors

Estimació: per definir en refinement
```

**Checklist Acceptance Criteria:**

```
L'àrea té almenys una US al backlog
El PO accepta l'èpica com a contenidor
```

---

### EP-13 Gamificació social

**Labels:** Èpica, Social, P5

**Descripció:**

```
COM: usuari del neobanc
VULL: competir i col·laborar amb amics
PER: motivar-nos mútuament a estalviar.

Assumptes:
- Contenidor de reptes amb amics, rànquing setmanal
- Privacitat: mai saldos als rànquings

Estimació: per definir en refinement
```

**Checklist Acceptance Criteria:**

```
L'àrea té almenys una US al backlog
El PO accepta l'èpica com a contenidor
```

---

# P6 — Transferències

## US-12 Dades del compte (IBAN)

**Labels:** Mitjana, Transferències, P6

**Descripció:**

```
COM: a usuari del neobanc
VULL: consultar el meu IBAN
PER: poder rebre transferències d'altres bancs.

Assumptes:
- IBAN, BIC i titular visibles
- Copiar al portapapers

Estimació: SP 2 · VP 5 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Veig l'IBAN, el BIC i el titular del compte
En tocar l'IBAN, es copia i apareix una confirmació
Puc compartir les dades amb altres apps del mòbil
Quan rebo una transferència externa, apareix als moviments i rebo notificació
```

---

## US-14 Enviar diners a un usuari

**Labels:** Fina, Alta, Transferències, P6

**Descripció:**

```
COM: a usuari del neobanc
VULL: enviar diners a un altre usuari a l'instant
PER: saldar deutes de manera senzilla.

Assumptes:
- Import > 0 i < límit diari
- Concepte opcional
- Notificació a remitent i destinatari

Estimació: SP 5 · VP 8 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
A Pagaments/Social selecciono un destinatari
A la pantalla d'enviament introdueixo import (> 0) i concepte opcional
"Continuar" obre pantalla de confirmació amb resum complet
Sense saldo, error i operació cancel·lada
Amb saldo, pantalla d'èxit i enviament a l'instant
El saldo visible s'actualitza
Notificació automàtica a remitent i destinatari
A la pantalla principal el pagament ja apareix a ambdós
```

---

## US-21 Aportació periòdica automàtica

**Labels:** Mitjana, Estalvi, Transferències, P6

**Descripció:**

```
COM: a usuari del neobanc
VULL: programar aportacions automàtiques a guardioles
PER: estalviar de forma constant sense pensar-hi.

Assumptes:
- Freqüència setmanal o mensual
- Sense saldo: no es fa l'aportació + notificació

Estimació: SP 4 · VP 6 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Puc configurar import, freqüència (setmanal/mensual) i dia
En la data programada, l'import es transfereix automàticament a la guardiola
Sense saldo suficient, no es fa l'aportació i rebo una notificació
Puc pausar, editar o eliminar l'aportació programada
```

---

## US-25 Afegir subcompte en divisa

**Labels:** Fina, Mitjana, Multidivisa, P6

**Descripció:**

```
COM: a usuari del neobanc
VULL: afegir un subcompte en una nova divisa
PER: poder tenir saldo en aquesta moneda i gestionar-la per separat.

Assumptes:
- Un sol subcompte per divisa
- A la pantalla principal hi ha opció d'afegir/gestionar subcomptes
- El nou subcompte neix amb saldo 0
- El total es mostra aproximadament en EUR

Estimació: SP 4 · VP 6 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
A la pantalla principal, clico a afegir o gestionar subcomptes
S'obre una llista de divises disponibles
Si ja tinc un subcompte d'aquella divisa, surt desactivada
En seleccionar una divisa, hi ha confirmació o missatge d'èxit
Torno a la pantalla principal i el subcompte hi és amb saldo 0
La home mostra el saldo de cada divisa i el total aproximat en EUR
```

---

## US-26 Eliminar subcompte en divisa

**Labels:** Fina, Mitjana, Multidivisa, P6

**Descripció:**

```
COM: a usuari del neobanc
VULL: eliminar un subcompte en divisa
PER: netejar la pantalla principal quan ja no opero amb aquella moneda.

Assumptes:
- Només es pot eliminar si el saldo és 0
- Si hi ha saldo, cal buidar-lo abans

Estimació: SP 2 · VP 4 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Accedeixo a detalls o configuració del subcompte i clico "Eliminar"
Si saldo > 0, pop-up d'error: s'ha de buidar abans
Si saldo és 0, diàleg de confirmació
En confirmar, torno a la home i el subcompte ja no hi és
```

---

## US-27 Canviar entre divises

**Labels:** Fina, Mitjana, Multidivisa, P6

**Descripció:**

```
COM: a usuari del neobanc
VULL: canviar diners entre les meves divises
PER: disposar de saldo en la moneda que necessito en cada moment.

Assumptes:
- Calen dos subcomptes amb saldo
- Es mostra tipus de canvi i comissió abans de confirmar

Estimació: SP 5 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
Accedeixo a la pantalla de canvi
Selecciono subcompte d'origen i de destí
Introdueixo l'import amb teclat numèric
Veig resum: tipus de canvi, comissió i import final
Si hi ha saldo suficient, pantalla d'èxit
En tornar a l'inici, els saldos d'ambdós subcomptes s'han actualitzat
```

---

## US-28 Pagaments en divisa

**Labels:** Mitjana, Multidivisa, P6

**Descripció:**

```
COM: a usuari del neobanc
VULL: fer pagaments en una altra divisa
PER: comprar a l'estranger o viatjar sense preocupacions.

Assumptes:
- Si hi ha saldo al subcompte de la divisa, es cobra d'allà
- Si no, es cobra de EUR amb canvi automàtic
- L'historial mostra import original, tipus de canvi i comissió

Estimació: SP 5 · VP 7 · Prioritat Alta
```

**Checklist Acceptance Criteria:**

```
Pagament en divisa amb saldo al subcompte → es cobra d'aquella divisa
Sense saldo a la divisa → es cobra de EUR amb canvi automàtic
A l'historial hi ha import original, tipus de canvi i comissió
```

---

## US-29 Límit de canvi sense comissió

**Labels:** Mitjana, Multidivisa, P6

**Descripció:**

```
COM: a usuari del neobanc
VULL: un límit mensual de canvi sense comissió
PER: estalviar diners a les operacions internacionals.

Assumptes:
- Fins al límit mensual: 0% comissió
- Un cop superat: comissió visible abans d'acceptar

Estimació: SP 3 · VP 5 · Prioritat Mitjana
```

**Checklist Acceptance Criteria:**

```
Canvis dins del límit mensual: 0% de comissió
Superat el límit, la pantalla de resum mostra la comissió abans d'acceptar
Els moviments posteriors reflecteixen la comissió cobrada
```

---

### EP-06 Multidivisa

**Labels:** Èpica, Multidivisa, P6

**Descripció:**

```
COM: usuari del neobanc
VULL: tenir saldos en diferents divises i canviar-hi
PER: gestionar diners quan viatjo o pago en altres monedes.

Assumptes:
- Contenidor de US-25, US-26, US-27, US-28, US-29
- Un subcompte per divisa; total aproximat en EUR

Estimació: per definir en refinement
```

**Checklist Acceptance Criteria:**

```
L'àrea té almenys una US al backlog
El PO accepta l'èpica com a contenidor
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
