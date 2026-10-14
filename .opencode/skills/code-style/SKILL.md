---
name: code-style
description: Load when writing or reviewing Vue 3 + JavaScript or Python FastAPI code for naming, SFC structure, composable ViewModel shape, file organization, readability, or F3-Evolt design conventions. Use for any implementation PR review or scaffold.
---

# Code style — Vue 3 + JavaScript, Python + FastAPI (F3-Evolt)

Clear and traceable — not “cutre”, not over-clever.
Stack: **Vue 3 SFC** (`<script setup>`) with composables and plain JavaScript (ES modules); **FastAPI** on the backend.

## Naming

| Kind | Convention | Example |
|------|------------|---------|
| Views | `XxxView.vue` | `HomeView.vue`, `TopUpView.vue` |
| Reusable components | `Xxx.vue` presentational | `MovementRow.vue`, `EmptyState.vue` |
| ViewModel composables | `useXxxViewModel` | `useHomeViewModel` |
| ViewModel actions | verbs | `load`, `submit`, `loadMore`, `retry` |
| Frontend services | `xxxService.js`, one function per endpoint | `homeService.js` |
| Frontend models | nouns (mappers, pure helpers) | `movement.js` |
| Backend services | `xxx_service.py` | `topup_service.py` |
| Backend routers | the resource | `routers/movements.py` |
| Backend repositories | `XxxRepository` | `MovementRepository` |
| Files | match their main export | `useHomeViewModel.js` |

Avoid: `manager`, `helper`, `misc`, `stuff`, `data2`, `handleThing`, `comp1`.

## Vue SFC shape

```
<script setup>       # props, emits, use the ViewModel
<template>           # structure + bindings only
<style scoped>       # component-local only
```

- One screen or one presentational component per file.
- `<script setup>` + `defineProps({...})` / `defineEmits([...])`.
- Reusable components: props in, events out — no service calls.
- Colours and typography come from the global CSS variables, not from values typed in a component.

## Composable ViewModel shape

```js
// frontend/src/viewmodels/useXxxViewModel.js
import { ref, computed } from 'vue'

export function useXxxViewModel() {
  const isLoading = ref(false)
  const error = ref(null)
  const canSubmit = computed(() => { /* ... */ })
  async function submit() { /* action */ }
  return { isLoading, error, canSubmit, submit }
}
```

- Named exports; one screen per composable.
- Error codes → **user-safe** strings before they reach the view.

## File shape (all layers)

- One main exported function or class per file.
- Prefer small modules over long files (open a file, know its job in 5 seconds).
- No dead code / commented-out blocks in PRs.
- `models/` files are pure: no `ref`, no HTTP.

## Clarity rules

1. **Traceable:** template → composable → service → API.
2. **Explicit names:** `amount`, `potId` over `a`, `d1`.
3. **Small functions/composables.**
4. **No clever one-liners** that need a paragraph of comments.
5. **Clear boundaries:** service functions and ViewModel actions declare what they take and return; JSDoc where it helps.
6. **Money is integer cents** everywhere; only the View shows euros.
7. **Consistent errors:** the contract's codes → ViewModel user strings.

## Design rules (SOLID/DRY light)

- One reason to change per composable/service.
- Prefer adding a function over a giant switch in a composable.
- A rule used in 2+ places goes in one module; don’t abstract two different UI copies for sport.

## What we reject

| Rejected | Instead |
|----------|---------|
| `fetch` or a service call in `.vue` | View → ViewModel → service |
| Business logic in templates | ViewModel / model / backend service |
| God composable with 20 actions | Split by screen or extract a model helper |
| Copy-paste of a rule | One module, imported twice |
| Magic money/limit numbers in views | Named constants in the model or ViewModel |
| A contract shape declared twice | One mapper in `models/`, imported |

## Self-check

- [ ] Names match the table above
- [ ] `<script setup>` and thin views
- [ ] ViewModels are `useXxxViewModel` with verb actions
- [ ] Models pure; HTTP only in `services/`
- [ ] Contract shapes come from `models/`
- [ ] Flow traceable end-to-end
- [ ] Clear enough for another junior to extend
