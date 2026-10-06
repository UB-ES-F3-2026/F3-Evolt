---
name: code-style
description: Load when writing or reviewing Vue 3 + Firebase + TypeScript code for naming, SFC structure, composable ModelView shape, file organization, readability, or F3-Evolt design conventions. Use for any implementation PR review or scaffold on the frontend or shared code.
---

# Code style — Vue 3 + TypeScript (F3-Evolt)

Clear and traceable — not “cutre”, not over-clever.  
Stack: **Vue 3 SFC** (`<script setup lang="ts">`), composables, TypeScript, Firebase adapters.

## Naming

| Kind | Convention | Example |
|------|------------|---------|
| Features (folders) | business words | `savings`, `transfers`, `auth` |
| Models | nouns (pure TS) | `SavingPot`, `Transaction`, `Money` |
| ModelView composables | `useXxxModelView` | `useContributeModelView` |
| ModelView commands | verbs | `submitContribution`, `logoutUser` |
| Vue views | `XxxView.vue` or feature screen names | `ContributeView.vue` |
| Shared components | `Xxx.vue` presentational | `EmptyState.vue` |
| Services / use cases | `XxxService` / `CreateXxx` | `CreateSavingPot` |
| Ports | `XxxRepository` / `XxxGateway` | `UserRepository` |
| Adapters | `FirebaseXxxAdapter` / `FirestoreXxxAdapter` | `FirestoreUserAdapter` |
| Files | match main type | `savingPot.ts`, `useSavingsModelView.ts` |

Avoid: `manager`, `helper`, `misc`, `stuff`, `data2`, `handleThing`, `comp1`.

## Vue SFC shape

```
<template>   # structure + bindings only
<script setup lang="ts">  # props, emits, use ModelView
<style scoped>            # component-local only
</style>
```

- One screen or one presentational component per file.
- Prefer `<script setup lang="ts">` + `defineProps` / `defineEmits`.
- Shared UI: props in, events out — no Firebase imports.

## Composable ModelView shape

```ts
// features/<f>/modelview/useXxxModelView.ts
export function useXxxModelView(...args) {
  const state = reactive({ loading: false, error: null as string | null })
  const service = useXxxService()
  async function submit() { /* command */ }
  const canSubmit = computed(() => { ... })
  return { ...toRefs(state), submit, canSubmit }
}
```

- Named exports; one main responsibility per composable.
- Domain errors → **user-safe** strings before return to the view.

## File shape (all layers)

- One main exported type/function per file.
- Prefer small modules over long files (open a file, know its job in 5 seconds).
- No dead code / commented-out blocks in PRs.
- Pure model files: no `ref`, no `firebase/*`.

## Clarity rules

1. **Traceable:** template → composable → service → adapter.
2. **Explicit names:** `amount`, `potId` over `a`, `d1`.
3. **Small functions/composables.**
4. **No clever one-liners** that need a paragraph of comments.
5. **Typed boundaries** at service/function edges.
6. **Consistent errors:** typed domain codes → ModelView user strings.

## Design rules (SOLID/DRY light)

- One reason to change per composable/service.
- Prefer adding a use case over a giant switch in a composable.
- Extract shared **rules** to `shared/services`; don’t abstract two different UI copies for sport.
- Ports owned by the consumer where practical; Firebase behind adapters.

## What we reject

| Rejected | Instead |
|----------|---------|
| Firebase in `.vue` | Service → port → adapter |
| Business logic in templates | ModelView / model / service |
| God composable with 20 commands | Split by flow or extract services |
| Copy-paste across features | Shared service |
| Magic money/limit numbers in views | Named constants in model/service |

## Self-check

- [ ] Names match the table above
- [ ] `<script setup lang="ts">` and thin views
- [ ] ModelViews are `useXxxModelView` with verb commands
- [ ] Models pure; Firebase only in adapters/functions
- [ ] Flow traceable end-to-end
- [ ] Clear enough for another junior to extend
