# **📱 Pla de Desenvolupament de l'Aplicació Fintech**

Aquest document recull el catàleg funcional del projecte, l'organització de l'equip i el detall de treball planificat per al **Sprint 1**.

## **👥 Equip del Projecte i Rols**

| Membre de l'Equip | Rol Principal | Àmbit de Treball |
| :---- | :---- | :---- |
| **Alicia** | **Scrum Master & Backend** | Facilitació àgil, coordinació i arquitectura backend |
| **Huabin** | **Backend Developer** | Lògica de negoci, base de dades i APIs |
| **Junhao** | **Frontend Developer** | Interfície d'usuari i integració client |
| **Jiajun** | **Frontend Developer** | Experiència d'usuari (UX/UI) i vistes d'interacció |
| **Martí** | **DevOps Engineer** | CI/CD, infraestructura i entorns de desplegament |
| **Izan** | **DevOps Engineer** | Monitorització, pipelines i seguretat de sistemes |

**Objectiu del projecte:** Desenvolupar, un neobanc inspirat en Revolut on els usuaris puguin gestionar el seu compte, pagar-se entre ells i estalviar, amb una capa de gamificació (XP, nivells, insígnies i reptes) que premiï els hàbits financers saludables. 

**Definition of Done:**

1. Tot el codi està pujat al repositori.  
2. Tots els tests de desenvolupador passen.  
3. Tots els tests d'acceptació passen.  
4. El text d'ajuda / documentació està escrit.  
5. El Product Owner ho ha acceptat.  
6. El codi ha estat revisat en una PR per almenys un altre membre *(proposta)*.  
7. El CI està en verd i la funcionalitat està desplegada a staging *(proposta)*.  
8. No hi ha cap bug crític obert relacionat amb la història *(proposta)*.

#### **EP-01 · Registre i accés**

*Tot el que necessita un usuari per crear el compte i entrar-hi de forma segura.*

**US-01 · Registre amb email o telèfon** · Fina  
Com a nou usuari, vull registrar-me amb el meu email o telèfon i una contrasenya per poder obrir un compte al neobanc.

* El formulari demana email o telèfon, contrasenya i confirmació de contrasenya.  
* La contrasenya ha de tenir mínim 8 caràcters, una majúscula i un número. Si no ho compleix, es mostra l'error sota el camp.  
* Si les dues contrasenyes no coincideixen, no es pot continuar.  
* Si l'email o el telèfon ja estan registrats, es mostra un missatge que ho indica.  
* El botó de registre està desactivat fins que s'accepten els termes i la política de privacitat.  
* Quan el formulari s'envia correctament, el compte es crea en estat "pendent de verificació".

**US-02 · Verificació del codi de registre** · Fina  
Com a nou usuari, vull confirmar el meu email o telèfon amb un codi per demostrar que són meus.

* Després del registre s'envia un codi de 6 dígits per email o SMS.  
* El codi caduca als 10 minuts.  
* Si introdueixo el codi correcte, el compte queda activat i accedeixo a la pantalla principal.  
* Si el codi és incorrecte o ha caducat, es mostra un error.  
* Puc demanar un codi nou i l'anterior deixa de ser vàlid.  
* Després de 5 intents fallits, cal demanar un codi nou.

**US-03 · Inici de sessió amb contrasenya** · Fina  
Com a usuari, vull iniciar sessió amb el meu email o telèfon i la contrasenya per accedir al meu compte.

* Amb credencials correctes, accedeixo a la pantalla principal.  
* Amb credencials incorrectes, es mostra un missatge genèric que no indica quin camp és erroni.  
* Després de 5 intents fallits seguits, el compte es bloqueja 15 minuts i rebo un avís per email.  
* Si estic 5 minuts sense activitat, la sessió es tanca i he de tornar a autenticar-me.  
* Puc tancar la sessió des del menú.

**US-04 · Recuperació de contrasenya** · Fina  
 Com a usuari, vull restablir la contrasenya si l'oblido per no perdre l'accés al compte.

* A la pantalla d'inici de sessió hi ha l'opció "He oblidat la contrasenya".  
* En introduir l'email, rebo un enllaç vàlid durant 30 minuts.  
* Si l'email no està registrat, es mostra el mateix missatge que si ho està.  
* La nova contrasenya ha de complir els mateixos requisits que al registre.  
* En canviar-la, es tanquen les sessions obertes en altres dispositius.  
* Si l'enllaç ha caducat, es mostra un avís i l'opció de demanar-ne un de nou.

---

#### **EP-02 · Compte i moviments**

*Consultar el saldo, veure els moviments i afegir diners al compte.*

**US-07 · Saldo a la pantalla principal** · Fina  
 Com a usuari, vull veure el meu saldo a la pantalla principal per saber d'un cop d'ull com tinc els diners.

* La pantalla principal mostra el saldo disponible.  
* Mostra el total estalviat a les guardioles.  
* Mostra els 5 últims moviments.  
* Quan hi ha un moviment nou, el saldo s'actualitza sense reiniciar l'app.  
* Amb la icona de l'ull puc amagar el saldo, i la preferència es manté a la sessió següent.

**US-08 · Llistat de moviments** · Fina  
 Com a usuari, vull consultar tots els meus moviments per controlar què gasto i què ingresso.

* Els moviments es mostren del més recent al més antic.  
* Cada moviment mostra import, concepte, data i si és ingrés o despesa, amb un color diferent per a cada tipus.  
* En arribar al final de la llista, se'n carreguen més.  
* Si no hi ha moviments, es mostra un missatge que ho indica.

**US-09 · Recàrrega de prova · Fina**  
 Com a usuari, vull afegir diners al compte amb una recàrrega de prova per poder fer servir els pagaments i l'estalvi.

* A la pantalla principal hi ha un botó "Afegir diners".  
* Puc introduir un import més gran que 0 i de com a màxim 500 € per recàrrega.  
* No es demanen dades de targeta: la recàrrega és simulada i s'aprova automàticament.  
* No puc recarregar més de 1.000 € en un mateix dia.  
* En confirmar, el saldo s'actualitza i la recàrrega apareix als moviments amb el concepte "Recàrrega".  
* Les recàrregues no donen XP.

**US-10 · Filtres i cerca de moviments** · Mitjana  
 Com a usuari, vull filtrar i cercar moviments per trobar ràpidament una operació concreta.

* Puc filtrar per rang de dates i per tipus (ingrés o despesa).  
* Puc cercar per concepte o pel nom del contacte.  
* Els filtres es poden combinar i esborrar.  
* Si cap moviment coincideix, es mostra "sense resultats".

**US-11 · Detall d'un moviment** · Mitjana  
Com a usuari, vull veure el detall de cada moviment per entendre exactament què ha passat amb els meus diners.

* En tocar un moviment, veig data i hora, import, estat, contrapart i referència.  
* Puc descarregar un justificant en PDF.  
* Puc reportar un problema i s'obre un formulari vinculat a aquell moviment.

**US-12 · Dades del compte (IBAN)** · Mitjana  
 Com a usuari, vull consultar el meu IBAN per poder rebre transferències d'altres bancs.

* Veig l'IBAN, el BIC i el titular del compte.  
* En tocar l'IBAN, es copia i apareix una confirmació.  
* Puc compartir les dades amb altres apps del mòbil.  
* Quan rebo una transferència externa, apareix als moviments i rebo una notificació.

---

#### **EP-03 · Pagaments entre usuaris**

*Enviar, demanar i rebre diners entre usuaris de l'app.*

**US-13 · Cercar un usuari** · Fina  
Com a usuari, vull trobar altres usuaris de l'app per poder enviar-los diners.

* Puc cercar per @usuari, telèfon o email.  
* Els resultats només mostren nom visible, @usuari i foto, mai dades financeres.  
* No apareixo als meus propis resultats de cerca.  
* Puc marcar un usuari com a favorit i apareix primer a la llista de pagament.

**US-14 Enviar diners a un usuari Fina** Fina

Com a usuari, vull enviar diners a un altre usuari a l'instant per saldar deutes de manera senzilla.

* A la Pantalla de Pagaments / Social, puc seleccionar un destinatari.  
* En seleccionar-lo, passo a la Pantalla d'Enviament, on s'habilita un teclat numèric per introduir l'import (ha de ser \> 0 i \< límit diari) i un camp de text per al concepte opcional.  
* En prémer "Continuar", s'obre una Pantalla de Confirmació que mostra el resum complet: imatge/nom del destinatari, import i concepte.  
* A la pantalla de confirmació, si clico "Confirmar enviament" i no tinc saldo suficient, es mostra un missatge d'error i l'operació es cancel·la.  
* Si tinc saldo, en confirmar, es mostra una Pantalla d'Èxit i l'enviament es fa a l'instant, actualitzant el saldo visible.  
* El dispositiu genera una notificació automàtica tant al remitent com al destinatari.  
* En tornar a la Pantalla Principal (Moviments), el pagament ja apareix reflectit a la llista d'ambdós usuaris.

**US-15 · Sol·licitar diners** · Mitjana  
 Com a usuari, vull demanar diners a un contacte perquè em torni el que em deu.

* Puc crear una sol·licitud amb destinatari, import i concepte, i el destinatari rep una notificació.  
* Veig les sol·licituds enviades amb el seu estat: pendent, pagada, rebutjada o caducada.  
* Puc cancel·lar una sol·licitud pendent.  
* Una sol·licitud sense resposta caduca als 7 dies.

**US-16 · Respondre a una sol·licitud** · Mitjana  
 Com a usuari, vull pagar o rebutjar les sol·licituds que rebo per decidir què pago.

* Puc pagar o rebutjar cada sol·licitud rebuda.  
* En pagar, el flux d'enviament s'obre amb el destinatari, l'import i el concepte ja emplenats.  
* Si la rebutjo, qui l'ha enviada rep una notificació.  
* Si no tinc saldo suficient, se m'ofereix afegir diners.

---

#### **EP-04 · Estalvi amb guardioles**

*Crear objectius d'estalvi i moure-hi diners, de forma manual o automàtica.*

**US-17 · Crear una guardiola** · Fina  
 Com a usuari, vull crear guardioles amb un objectiu per estalviar per a coses concretes.

* Puc indicar nom, import objectiu, icona i una data límit opcional.  
* L'import objectiu ha de ser més gran que 0\.  
* La guardiola nova apareix a la llista amb un progrés del 0%.  
* Puc editar el nom, la icona, l'objectiu i la data.  
* Puc eliminar una guardiola que tingui saldo 0\.

**US-18 · Aportar diners a una guardiola** · Fina  
 Com a usuari, vull moure diners del meu saldo a una guardiola per anar estalviant.

* Puc moure un import del saldo principal a una guardiola.  
* No puc aportar més del saldo disponible.  
* En confirmar, el saldo principal baixa i la guardiola puja en el mateix import.  
* L'aportació apareix a l'historial de la guardiola.  
* El progrés de la guardiola s'actualitza.

**US-19 · Retirar diners d'una guardiola** · Fina  
 Com a usuari, vull retirar diners d'una guardiola per poder fer-los servir si els necessito.

* Puc moure un import d'una guardiola al saldo principal.  
* No puc retirar més del que hi ha a la guardiola.  
* En confirmar, la guardiola baixa i el saldo principal puja en el mateix import.  
* La retirada apareix a l'historial de la guardiola.

**US-20 · Progrés i objectiu assolit** · Mitjana  
Com a usuari, vull veure com avancen les meves guardioles i celebrar quan arribo a l'objectiu per mantenir-me motivat.

* Cada guardiola mostra el percentatge completat i l'import que falta.  
* Si té data límit, mostra si s'hi arribarà a temps al ritme actual.  
* En arribar al 100%, es mostra una pantalla de celebració.  
* Un cop assolit l'objectiu, puc tancar la guardiola i passar els diners al saldo o continuar estalviant.

**US-21 · Aportació periòdica automàtica** · Mitjana  
Com a usuari, vull programar aportacions automàtiques per estalviar de forma constant sense pensar-hi.

* Puc configurar import, freqüència (setmanal o mensual) i dia.  
* En la data programada, l'import es transfereix automàticament a la guardiola.  
* Si no hi ha saldo suficient, no es fa l'aportació i rebo una notificació.  
* Puc pausar, editar o eliminar l'aportació programada.

---

#### **EP-05 · Gamificació: XP i nivells**

*El nucli de la gamificació: premiar els hàbits saludables amb XP i nivells.*

**US-23 · Guanyar XP per hàbits saludables** · Mitjana  
Com a usuari, vull guanyar XP quan faig accions financeres saludables per sentir-me motivat a mantenir bons hàbits.

* Guanyo XP en crear la primera guardiola, en aportar a una guardiola i en assolir un objectiu d'estalvi.  
* La quantitat d'XP de cada acció es defineix per configuració.  
* Quan guanyo XP, es mostra un missatge amb la quantitat i el motiu.  
* Si retiro una aportació abans de 7 dies, es resta l'XP guanyat per aquella aportació.  
* Cada acció té un límit diari d'XP per evitar trampes (per exemple, aportar 1 € cent vegades).  
* Puc consultar l'historial d'XP amb la data i el motiu de cada guany o descompte.

**US-24 · Nivells i perfil de progrés** · Mitjana  
 Com a usuari, vull pujar de nivell en acumular XP per veure el meu progrés a llarg termini.

* Quan l'XP arriba al llindar del nivell següent, pujo de nivell i es mostra una celebració.  
* Cada nivell requereix més XP que l'anterior.  
* El perfil mostra el nivell actual, l'XP total i una barra amb l'XP que falta per al nivell següent.  
* La pantalla principal mostra el nivell i la barra de progrés.

---

#### **EP-06 · Multidivisa · Èpica**

Com a usuari, vull tenir saldos en diferents divises dins del meu compte i canviar entre elles per gestionar els diners quan viatjo o pago en altres monedes.

* Puc afegir i eliminar subcomptes en diferents divises, amb un sol subcompte per divisa.  
* La pantalla principal mostra el saldo de cada divisa i el total aproximat en EUR.  
* Puc canviar diners entre divises veient abans el tipus de canvi, la comissió i l'import final.  
* Els pagaments en una divisa es cobren del subcompte d'aquella divisa si hi ha saldo; si no, de la divisa principal amb el canvi aplicat.  
* Els moviments en divisa mostren l'import original, el tipus de canvi i la comissió.

*Històries previstes:* afegir subcompte en divisa, eliminar subcompte, canviar entre divises, pagaments en divisa, límit de canvi sense comissió.

**US-06.1 Afegir subcompte en divisa** Fina 

Com a usuari, vull afegir un subcompte en una nova divisa per poder tenir saldo en aquesta moneda i gestionar-la per separat.

* A la pantalla principal, clico a l'opció d'afegir o gestionar subcomptes.  
* S'obre una pantalla amb una llista de les divises disponibles.  
* Si ja tinc un subcompte d'una divisa, aquesta apareix desactivada, ja que només hi pot haver un sol subcompte per divisa.  
   PDF  
* En seleccionar una divisa, es mostra una pantalla de confirmació o missatge d'èxit i es torna a la pantalla d'inici.  
* A la pantalla principal, el nou subcompte apareix llistat amb saldo 0\.  
* La pantalla principal mostra el saldo de cada divisa afegida i el total aproximat de totes elles en EUR.  
   PDF

**US-06.2 Eliminar subcompte en divisa** Fina

 Com a usuari, vull eliminar un subcompte en divisa per netejar la meva pantalla principal quan ja no necessito operar amb aquella moneda.

* Accedeixo als detalls o a la configuració d'un subcompte en divisa i clico "Eliminar".  
* Si el saldo d'aquella divisa és més gran que 0, es mostra un pop-up d'error indicant que s'ha de buidar abans d'eliminar el subcompte.  
* Si el saldo és 0, es mostra un diàleg de confirmació ("Estàs segur que vols eliminar aquest compte?").  
* En confirmar, retorno a la pantalla principal i el subcompte desapareix de la llista visual.

**US-06.3 Canviar entre divises** Fina

 Com a usuari, vull canviar diners entre les meves divises per disposar de saldo en la moneda que necessito en cada moment.

* Accedeixo a la pantalla de canvi i selecciono el subcompte d'origen i el de destí.  
* Amb un teclat numèric, introdueixo l'import que vull canviar.  
* Abans de finalitzar, passo a una pantalla de resum on veig el tipus de canvi aplicat, la comissió de l'operació (si n'hi ha) i l'import final exacte que rebré.  
   PDF  
* En prémer "Confirmar canvi", si hi ha saldo suficient a l'origen, es mostra una pantalla d'èxit.  
* En tornar a l'inici, els saldos d'ambdós subcomptes s'han actualitzat al moment.

**US-06.4 Pagaments en divisa** Mitjana

 Com a usuari, vull fer pagaments en una altra divisa per poder fer compres internacionals o viatjar sense preocupacions.

* Si faig un pagament en una divisa estrangera i tinc saldo suficient al subcompte d'aquella divisa, el pagament es cobra directament d'aquell saldo.  
   PDF  
* Si no hi ha saldo suficient al subcompte d'aquella divisa, el sistema cobra el pagament de la divisa principal (EUR) aplicant el canvi automàticament.  
   PDF  
* A l'historial, els moviments en divisa mostren sempre l'import original pagat, el tipus de canvi aplicat en aquell moment i la comissió si n'hi hagués.  
   PDF

**US-06.5 Límit de canvi sense comissió** Mitjana 

Com a usuari, vull tenir un límit de canvi de moneda sense comissions per estalviar diners en les meves operacions internacionals mensuals.

* El sistema em permet fer canvis de divisa amb un 0% de comissió fins arribar al meu límit d'import mensual.  
* Un cop superat el límit mensual gratuït, si intento fer un canvi, se'm mostra i se'm suma una comissió a la pantalla de resum abans d'acceptar.  
* Els moviments posteriors al límit reflecteixen correctament l'import de la comissió cobrada.

#### **EP-09 · Despeses compartides · Èpica**

Com a usuari, vull dividir despeses i estalviar en grup amb els meus amics per gestionar diners en comú sense complicacions.

* Puc dividir una despesa a parts iguals o amb imports personalitzats, i la suma ha de coincidir amb el total.  
* Cada participant rep una sol·licitud de pagament i puc veure qui ha pagat.  
* Puc crear una guardiola compartida i convidar-hi contactes.  
* Cada membre veu el total i les aportacions de tothom, i només pot retirar el que ha aportat.  
* Si un membre abandona la guardiola, se li retorna la seva aportació.

*Històries previstes:* dividir una despesa, seguiment de pagaments dividits, crear guardiola compartida, aportar, retirar i abandonar en grup.

#### **EP-10 · Anàlisi de despeses i pressupostos · Èpica**

Com a usuari, vull veure en què gasto i fixar pressupostos per controlar millor les meves finances.

* Cada despesa s'assigna automàticament a una categoria i la puc canviar manualment.  
* Veig un gràfic mensual de despesa per categoria i la variació respecte al mes anterior.  
* Puc crear un pressupost mensual per categoria amb una barra de progrés.  
* Rebo un avís en arribar al 80% del pressupost i un altre quan el supero.  
* Acabar el mes sense superar un pressupost dona XP.

*Històries previstes:* categorització automàtica i manual, gràfic mensual, crear pressupost, avisos de pressupost, XP per pressupost complert.

#### **EP-11 · Insígnies i recompenses · Èpica**

Com a usuari, vull aconseguir insígnies i desbloquejar recompenses per sentir que els meus progressos es reconeixen.

* Rebo una insígnia quan en compleixo la condició (primer estalvi, primer objectiu, 3 mesos complint el pressupost...), i cada insígnia només s'obté un cop.  
* Veig la col·lecció d'insígnies: les obtingudes amb la data i les bloquejades amb la condició i el progrés (per exemple, 7/10).  
* Puc compartir una insígnia sense mostrar cap dada financera.  
* Cada nivell pot desbloquejar recompenses (temes de l'app, marcs d'avatar, reptes exclusius) i rebo una notificació quan passa.  
* Els usuaris nous veuen un tutorial de gamificació que es pot saltar i que dona la insígnia de benvinguda.

*Històries previstes:* obtenir insígnia, col·lecció i compartició d'insígnies, recompenses per nivell, tutorial de gamificació.

#### **EP-12 · Reptes i ratxes · Èpica**

Com a usuari, vull participar en reptes d'estalvi i mantenir ratxes per tenir objectius a curt termini i crear hàbits constants.

* Veig els reptes disponibles amb descripció, durada, dificultat i recompensa, i m'hi puc unir un sol cop per repte.  
* El progrés del repte s'actualitza automàticament segons els meus moviments.  
* Si completo el repte a temps rebo la recompensa; si no, queda com a fallit a l'historial.  
* Puc abandonar un repte sense penalització.  
* Tinc una ratxa de setmanes consecutives amb aportacions, amb un avís de "ratxa en perill" i XP extra en arribar a certes fites.

*Històries previstes:* llistat de reptes, unir-se i abandonar un repte, progrés, recompensa i recordatoris, ratxes d'estalvi.

#### **EP-13 · Gamificació social · Èpica**

Com a usuari, vull competir i col·laborar amb els meus amics per motivar-nos mútuament a estalviar.

* Puc crear reptes i convidar-hi amics, que poden acceptar o rebutjar la invitació.  
* El progrés dels altres participants es mostra en percentatge, mai en imports.  
* Hi ha un rànquing setmanal d'XP entre contactes que es reinicia cada dilluns.  
* El rànquing només mostra XP i nivell, mai saldos.  
* Puc sortir del rànquing des dels ajustos de privacitat.

*Històries previstes:* reptes amb amics, invitacions a reptes, rànquing setmanal, privacitat del rànquing.

#### **EP-14 · Perfil i preferències · Èpica**

Com a usuari, vull gestionar les meves dades i preferències per adaptar l'app a mi.

* Puc editar el nom visible, la foto i l'adreça.  
* Per canviar l'email o el telèfon he de verificar la nova dada amb un codi.  
* El nom legal i la data de naixement no es poden editar des de l'app.  
* Puc canviar la contrasenya introduint l'actual.  
* Puc activar o desactivar cada tipus de notificació, excepte les de seguretat.

*Històries previstes:* editar perfil, canviar email o telèfon, canviar contrasenya, preferències de notificacions.

#### **EP-15 · Administració de la gamificació · Èpica**

Com a administrador, vull configurar reptes, insígnies i valors d'XP des d'un panell per mantenir la gamificació al dia sense publicar noves versions de l'app.

* Puc crear reptes i insígnies amb nom, descripció, condició, durada, recompensa i dates de publicació.  
* Puc activar i desactivar reptes i insígnies, i els canvis es veuen a l'app sense actualitzar-la.  
* No puc editar la condició d'un repte que té participants actius.  
* Puc modificar l'XP de cada acció i els llindars de nivell, i els canvis s'apliquen a partir d'aquell moment.

