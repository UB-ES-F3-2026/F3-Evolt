---
name: user-stories
description: Load when writing, splitting or refining a user story or its acceptance criteria, preparing a story for a sprint (Definition of Ready), doing backlog refinement, or when you are about to build a screen and the story does not say how a screen, button, message, list or empty state looks or behaves. For the PO and for every developer.
---

# User stories (F3-Evolt)

**Nobody invents a screen.** If a screen, a button, a message or a list is not
defined by its story or its mockup, the story is not ready; the PO defines it
first. At the Sprint 1 review the professor called a developer having to make up
a screen a "mortal sin".

Format and INVEST rules: `docs/P1/AGENTS.md`. Stories live in
`docs/P1/trello-backlog.md`, on their Trello card and, once in a sprint, in their
GitHub issue: change all three together.

## 1. One story, one functionality

Smaller stories are more specific and easier to manage. Split by what the user
does, usually one screen or one action per story.

| Too big (Sprint 1) | Split into |
|--------------------|------------|
| US-17 "Crear guardiola": the pots list **and** the create form | "Veure les meves guardioles" (the list) · "Crear una guardiola" (from the button to the new pot in the list) |

The professor's example. Each part still has value and can be demonstrated on
its own; if a story needs "and" to describe what the user does, it is probably
two.

## 2. Every screen has a design

A story with UI carries a **mockup of each screen**, even a basic wireframe,
attached to the Trello card and linked from the issue. It shows everything the
professor listed for the pots screen: each element, its **position**, **icon**,
**colour** (from the style guide in `docs/P1/trello-backlog.md`), the **data**
(name, amount…), and the **arrows / navigation**. Use the app's real texts and
example data from the seed.

## 3. Acceptance criteria follow the user's flow

Start where the user starts and describe what they find at each step:

> En tocar «Veure tots» a «Inici», entro a «Moviments», que mostra els 20 més recents, del més nou al més antic…

The ACs together are the flow of the app: whoever builds it should not have to
ask "and then what?".

## 4. Definition of Ready (checklist)

A story enters a sprint only when its ACs or mockup answer all of these:

- [ ] **Entry and exit:** how I get to the screen, where I end up afterwards
- [ ] **Every element** on the screen, as in the mockup
- [ ] **Every button**, including **Cancel / Back**: what happens exactly. A
      confirmation pop-up (with what text)? Back to the previous screen or to
      «Inici»? Is the typed data lost?
- [ ] **Every message, word for word:** success, each validation error, each
      error `code` the API can return for it (`docs/api.md`), "torna-ho a provar"
- [ ] **States:** loading, **empty** ("and if there is nothing?"), error with retry
- [ ] **Lists:** how many items appear first (10, 20, 50?), order, "load more",
      pagination or scroll, what changes **with and without filters**, what shows
      when nothing matches
- [ ] **Formats:** amounts and dates as in the style guide
- [ ] **Non-functional** where it matters: limits, security, response time
- [ ] **Mockup** attached; each AC is testable with a clear pass/fail
- [ ] **Estimated** (SP + VP), and small enough for one sprint

## 5. Backlog refinement

Stories are not frozen: the backlog changes, and so do the stories inside a
sprint.

- **During the sprint**, the Scrum Master schedules short refinement meetings
  (about once a week): PO and developers go through the next stories with the
  checklist above. Under-specified, over-specified or wrong: change it.
- **A gap found while building** ("what does Cancel do here?"): stop that part,
  ask the PO, update the story (backlog doc, Trello, issue), then build what it
  now says. Do not fill the gap with your own guess, not even a sensible one.

## 6. For developers (and AI) before building

1. Read the story, its ACs and its mockup.
2. Check section 4. Anything missing → ask the PO; note the question in the issue.
3. Build exactly what is defined: texts, positions, states, list sizes.
4. Map each AC to a test (skill `qa-strategy`).

## What went wrong in Sprint 1, and how we avoid it

| What happened | Now |
|---------------|-----|
| The pots list (US-17) was not defined anywhere: names, icons, positions, colours, amounts and arrows were invented while building | A mockup of every screen before the story enters a sprint |
| DS-01 "Mockups de guardioles abans de Sprint 1" was in the backlog and never done | Design is part of Definition of Ready, not a separate ticket |
| One story mixed listing and creating pots | One functionality per story |
| The create form had no defined Cancel, and the error said only "el motiu en vermell" | Every button and message defined, word for word |
| The movements story shown at the review did not answer "how many appear? does it scroll? and without filters?"; part of it lived in another story (US-08) | Each story states its own flow from its entry point; lists say size, order, paging and the empty case |
| Stories were taken as frozen, so gaps were filled by guessing | Backlog refinement during the sprint |

## Self-check

- [ ] One functionality per story
- [ ] Mockup of every screen attached
- [ ] ACs follow the flow from the entry point
- [ ] Definition of Ready checklist complete
- [ ] Backlog doc, Trello card and issue say the same
