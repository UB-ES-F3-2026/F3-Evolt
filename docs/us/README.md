# Documentació de User Stories · Sprint 2 (F3-Evolt)

> Índex i punt d'entrada de les especificacions de les 8 US del Sprint 2. Aquesta branca (`docs/us-sprint2`) conté la **fundació** —la [plantilla obligatòria](_plantilla.md), el [context compartit](_context.md), la [guia d'escriptura](_guia-escriptura.md) i el [pipeline de mockups](_mockup/render.sh)— i **les 8 fitxes `US-XX.md` amb els seus mockups**. Les especificacions detallades per història són obligatòries segons [`docs/P1/AGENTS.md`](../P1/AGENTS.md) (§"User Stories — format obligatori" i §"Regla dels 3 criteris d'acceptació").

---

## 1. Índex de les 8 US del Sprint 2

| US | Títol | Bloc | Punts | Hores | Fitxer |
|---|---|---|---|---|---|
| US-19 | Retirar diners d'una guardiola | Estalvi | 3 | 9 h | [US-19.md](US-19.md) |
| US-20 | Veure progrés i objectiu assolit | Estalvi | 3 | 7 h | [US-20.md](US-20.md) |
| US-15 | Sol·licitar diners | Estalvi | 3 | 9 h | [US-15.md](US-15.md) |
| US-13 | Cercar un usuari | Pagaments | 2 | 9 h | [US-13.md](US-13.md) |
| US-14 | Enviar diners a usuaris | Pagaments | 5 | 15 h | [US-14.md](US-14.md) |
| US-25 | Afegir subcompte en divisa | Multidivisa | 4 | 12 h | [US-25.md](US-25.md) |
| US-26 | Eliminar subcompte en divisa | Multidivisa | 2 | 4 h | [US-26.md](US-26.md) |
| US-27 | Canviar entre divises | Multidivisa | 5 | 10 h | [US-27.md](US-27.md) |
| **Total** | **8 històries** | — | **27** | **76 h** (75 h de les 8 US + 1 h de TR06.3) | — |

Les vuit fitxes `US-XX.md` ja existeixen a aquesta branca. Els value statements literals (COM/VULL/PER) de les vuit US, els endpoints existents i a crear, l'inventari de frontend i les decisions del PO són al [context compartit](_context.md).

### Documents de suport

- [`_plantilla.md`](_plantilla.md) — **plantilla obligatòria** de les US (12 seccions + exemple farcit US-19).
- [`_guia-escriptura.md`](_guia-escriptura.md) — guia d'escriptura interna i checklist de lliurament.
- [`_context.md`](_context.md) — context compartit (dades seed, rutes, API, tokens de disseny).
- [`../P1/AGENTS.md`](../P1/AGENTS.md) — normes del projecte: format obligatori de US, regla dels 3 AC, Gitflow i DoD.

---

## 2. La plantilla i la regla dels 3 criteris d'acceptació

### La plantilla és obligatòria

Tota US del Sprint 2 s'escriu **copiant [`_plantilla.md`](_plantilla.md)** a `docs/us/US-XX.md`. El document final manté les **12 seccions** (esborrant-ne les instruccions; només queda contingut farcit):

1. Value statement + assumptes / prèvies
2. Taula de pantalles
3. Flux d'interacció numerat
4. Matriu d'estats
5. Còpia d'UI literal
6. Taula de validacions
7. Integració API
8. Acció → reacció UI → resposta → toast/redirecció
9. No funcionals
10. Criteris d'acceptació en Gherkin
11. Wireframes/mockups + diagrama Mermaid
12. Enllaços + Definition of Done

La *forma* de referència és l'**exemple farcit US-19** al final de la plantilla: copiar la forma, mai inventar-ne una de nova. Regla d'or: cada frase porta **números, noms, colors i literals copiables**; allò inexistent es marca **`a crear`** i les decisions pendents del PO, **[PROPOSTA — pendent de validar]**.

### Regla dels 3 criteris d'acceptació (vinculant)

Resum de [`docs/P1/AGENTS.md`](../P1/AGENTS.md) §"Regla dels 3 criteris d'acceptació" i [`_guia-escriptura.md`](_guia-escriptura.md) §2:

- **EXACTAMENT 3 AC per US, mai més.** 3 AC forts valen més que 6 febles.
- Cada AC prova **funcionalitat real i integritat de dades, mai cosmètica de presentació**.
  - ❌ **Prohibits:** «el botó es posa vermell», «surt l'etiqueta En progrés», «apareix el toast», «queda com el mockup» (i qualsevol color o string exacte com a fi en si mateix).
  - ✅ **Permesos:** els diners s'han mogut realment, els dos saldos han canviat de manera atòmica, el registre ha quedat desat, l'operació il·legal s'ha refusat i no ha canviat res, la sol·licitud caducada es calcula com a caducada, el mateix usuari no surt a la seva cerca, es refusa una divisa repetida en el mateix compte, només es pot cancel·lar una sol·licitud pendent.
- Els 3 AC cobreixen **tres angles complementaris, sempre en aquest ordre**:
  1. **Happy path de punta a punta** — un escenari complet amb xifres i noms concrets i l'estat final esperat (quants queden on).
  2. **Invariant / protecció** — l'operació il·legal es **refusa I no canvia res** (atòmic: saldo insuficient, duplicat, destí prohibit, límit superat…). El «no canvia res» és part del *Then*, no un AC a part.
  3. **Estat / persistència / propagació** — el canvi es veu a **tots els llocs on ha de veure's** (una altra vista, l'historial, el compte de l'altre usuari, un % recalculat) **i sobreviu a una recàrrega** de la pàgina.
- **Forma:** Gherkin `Given/When/Then`, **independentment** passable o fallable (Pass/Fall clar), i **verificable pel PO al navegador en menys d'1 minut** (estat concret del seed + acció + resultat observable).
- **La spec de pantalla no és AC:** estats, còpia literal, validacions i reaccions a errors d'API viuen al **cos de la US** (seccions 4–8), no com a AC extra. Els AC descriuen el *Què* verificable, no el *Com* ni la pell.

---

## 3. Convencions de nomenclatura i enllaços (Trello ↔ GitHub ↔ PR)

El **mateix identificador vincula els tres llocs** (secció 12 de la plantilla):

- **Fitxer de la US:** `docs/us/US-XX.md` — id complet, sense decimals, **mai** `US-1.5`.
- **Mockups:** font `docs/us/_mockup/src/US-XX-<pantalla>.html` → PNG generat a `docs/us/img/US-XX-<pantalla>.png`.
- **Trello:** card `US-XX` al tauler (bloc P2 Estalvi / P5 / P6), amb títol, Descripció COM/VULL/PER i checklist `Acceptance Criteria` copiats literalment del document (segons [`docs/P1/AGENTS.md`](../P1/AGENTS.md) §Trello; sense import automàtic, enganxat a mà).
- **GitHub Issue:** titulada amb `US-XX` i el títol de la card, enllaçada a la card del Trello al cos.
- **PR:** un per US o per tasca, que **refereix l'issue**, branca `feature/<slug>` i **base `develop`**, amb la convenció del repo: `<type>(<scope>): <subject> US-<id>` (p. ex. `feat(savings): withdraw from pot US-19`).
- **Mai tocar `main`:** es treballa sobre `develop` o branques derivades d'ella; només `hotfix/<slug>` surt de `main`.

---

## 4. Com generar els mockups (pipeline)

Els mockups són **HTML estàtic** (sense JS de negoci) convertits a **PNG amb Chromium headless** amb [`_mockup/render.sh`](_mockup/render.sh). Mai captures a mà: així tots comparteixen fons, lila i tipografia del producte.

**Passos:**

1. Duplica [`_mockup/base.html`](_mockup/base.html) (o un `src/*.html` existent) a `_mockup/src/US-XX-<pantalla>.html`.
2. Edita el contingut fent servir **només les classes de [`_mockup/base.css`](_mockup/base.css)** (tokens: fons `#f7f9fc`, lila `#4f46e5`, verd `#16a34a`, vermell `#dc2626`).
3. Executa **des de `docs/us/_mockup/`**:

   ```sh
   ./render.sh src/US-XX-<pantalla>.html ../img/US-XX-<pantalla>.png
   ```

**Fets del renderitzador** (vegeu la capçalera del script):

- **Detecció automàtica del navegador**, en aquest ordre: `helium` al PATH → `/opt/helium-0.15.5.1-x86_64_linux/helium` → glob `/opt/helium-*/helium` → `/home/itram/.hermes/tools/chromium-1208/chrome-linux64/chrome` → `chromium`/`chrome` (i variants) del PATH → error que llista tots els candidats provats.
- **Comandament exacte:** `--headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=2 --window-size=390,844 --screenshot=<sortida> file://<entrada>`.
- **Mai `--user-data-dir`**: penja en aquest entorn (nota del propi script).
- **Sortida: 780×1688** (marc 390×844 a escala 2x); el script **verifica que el PNG no és buit** (0 bytes) i avisa si les dimensions no coincideixen.

**Exemple provat:** la primera renderització vàlida va ser `img/exemple-retirar.png` (font `src/exemple-us19-retirar.html`), amb la comanda:

```sh
./render.sh src/exemple-us19-retirar.html ../img/exemple-retirar.png
```

**Requisits de contingut del mockup:**

- **Còpia en català** (tot el producte és en català, inclosos toasts, errors i estat buit).
- **Imports** en format ca-ES amb **NBSP abans de `€`**: `1.250,50 €`.
- **Dates** amb apòstrof tipogràfic **U+2019**: `11 d’oct. · 21:15`.
- **Colors només dels tokens de [`_mockup/base.css`](_mockup/base.css)** (mai verd/vermell per a guardioles: signifiquen ingrés/despesa).
- **Signes:** despeses amb el signe `−` (U+2212), ingressos amb `+`.

---

## 5. Estat d'aquesta documentació

Aquesta branca (`docs/us-sprint2`) conté la **fundació** (plantilla, context compartit, guia d'escriptura i pipeline de mockups `_mockup/`) i **les 8 fitxes `US-XX.md` amb els seus mockups HTML + PNG**, totes ja presents a l'índex de la secció 1.
