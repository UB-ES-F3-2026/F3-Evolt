---
name: code-style
description: Load when writing or reviewing Vue 3 + TypeScript or Python FastAPI code for naming, SFC structure, composable ViewModel shape, file organization, readability, or F3-Evolt design conventions. Use for any implementation PR review or scaffold.
---

# Code style — Vue 3 + TypeScript, Python + FastAPI (F3-Evolt)

Clear and traceable — not “cutre”, not over-clever.
Stack: **Vue 3 SFC** (`<script setup lang="ts">`) with composables and strict TypeScript; **FastAPI** on the backend.

## Naming

| Kind | Convention | Example |
|------|------------|---------|
| Views | `XxxView.vue` | `HomeView.vue`, `TopUpView.vue` |
| Reusable components | `Xxx.vue` presentational | `MovementRow.vue`, `EmptyState.vue` |
| ViewModel composables | `useXxxViewModel` | `useHomeViewModel` |
| ViewModel actions | verbs | `load`, `submit`, `loadMore`, `retry` |
| Frontend services | `xxxService.ts`, one function per endpoint | `homeService.ts` |
| Frontend models and types | nouns | `movement.ts`, `Movement` |
| Backend services | `xxx_service.py` | `topup_service.py` |
| Backend routers | the resource | `routers/movements.py` |
| Backend repositories | `XxxRepository` | `MovementRepository` |
| Files | match their main export | `useHomeViewModel.ts` |

Avoid: `manager`, `helper`, `misc`, `stuff`, `data2`, `handleThing`, `comp1`.

## Vue SFC shape

```
<script setup lang="ts">   # props, emits, use the ViewModel
<template>                 # structure + bindings only
<style scoped>             # component-local only
```

- One screen or one presentational component per file.
- `<script setup lang="ts">` + `defineProps<{…}>()` / `defineEmits<{…}>()`.
- Reusable components: props in, events out — no service calls.
- Colours and typography come from the global CSS variables, not from values typed in a component.

## Composable ViewModel shape

```ts
// frontend/src/viewmodels/useXxxViewModel.ts
export function useXxxViewModel() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const canSubmit = computed(() => { ... })
  async function submit() { /* action */ }
  return { isLoading, error, canSubmit, submit }
}
```

- Named exports; one screen per composable.
- Error codes → **user-safe** strings before they reach the view.

## File shape (all layers)

- One main exported function, class or type per file.
- Prefer small modules over long files (open a file, know its job in 5 seconds).
- No dead code / commented-out blocks in PRs.
- `models/` files are pure: no `ref`, no HTTP.

## Clarity rules

1. **Traceable:** template → composable → service → API.
2. **Explicit names:** `amount`, `potId` over `a`, `d1`.
3. **Small functions/composables.**
4. **No clever one-liners** that need a paragraph of comments.
5. **Typed boundaries:** service functions and ViewModel actions declare what they take and return; no `any`.
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
| `any`, or a contract type declared twice | One type in `models/`, imported |

## Self-check

- [ ] Names match the table above
- [ ] `<script setup lang="ts">` and thin views
- [ ] ViewModels are `useXxxViewModel` with verb actions
- [ ] Models pure; HTTP only in `services/`
- [ ] No `any`; contract types come from `models/`
- [ ] Flow traceable end-to-end
- [ ] Clear enough for another junior to extend
