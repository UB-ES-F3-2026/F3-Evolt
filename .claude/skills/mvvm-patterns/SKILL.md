---
name: mvvm-patterns
description: Load when creating or changing Vue frontend UI — screens, components, forms, composable ViewModels, state, events, props. Use for any Vue 3 screen on F3-Evolt (home, movements, top-up, auth, savings, transfers, gamification). Frontend-specific MVVM.
---

# Vue MVVM — Model · ViewModel · View

Stack: **Vue 3** (`<script setup lang="ts">`) + TypeScript + Vite + Vue Router. No Pinia.
A ViewModel is a **composable** named `useXxxViewModel`.

## Layers (Vue mapping)

| Layer | Place | Vue piece | Does | Does not |
|-------|-------|-----------|------|----------|
| **View** | `frontend/src/views/`, `components/` | `*.vue` SFC | Template and styles; renders what the ViewModel exposes | Business logic, API calls |
| **ViewModel** | `frontend/src/viewmodels/` | `useXxxViewModel.ts` composable | State, validations and actions of one screen | HTML, styles |
| **Model** | `frontend/src/models/`, `services/` | plain `.ts` | Types, data, JSON mapping and API calls | Screen state |

```
View (.vue)
  → useXxxViewModel()        // ViewModel composable
      → service              // services/xxxService.ts → apiClient.ts → API
      → model (pure)         // models/
```

## Canonical flow (example: contribute to pot)

Helper names (`eurosToCents`, `toUserMessage`) only show the shape.

```vue
<!-- frontend/src/views/ContributeView.vue -->
<script setup lang="ts">
import { useContributeViewModel } from '@/viewmodels/useContributeViewModel'

const props = defineProps<{ potId: string }>()
const emit = defineEmits<{ (e: 'done'): void }>()
const { amount, error, isSubmitting, canSubmit, submit } = useContributeViewModel(props.potId)

async function onSubmit() {
  const ok = await submit()
  if (ok) emit('done')
}
</script>
```

```ts
// frontend/src/viewmodels/useContributeViewModel.ts
export function useContributeViewModel(potId: string) {
  const amount = ref('')
  const error = ref<string | null>(null)
  const isSubmitting = ref(false)
  const canSubmit = computed(() => eurosToCents(amount.value) !== null && !isSubmitting.value)

  async function submit(): Promise<boolean> {
    error.value = null
    const cents = eurosToCents(amount.value) // model — pure
    if (cents === null) {
      error.value = 'Introdueix un import vàlid'
      return false
    }
    isSubmitting.value = true
    try {
      await contributeToPot(potId, cents) // service
      return true
    } catch (failure) {
      error.value = toUserMessage(failure)
      return false
    } finally {
      isSubmitting.value = false
    }
  }

  return { amount, error, isSubmitting, canSubmit, submit }
}
```

## Vue rules

1. **SFC View is thin:** template + props/emit + calls to ViewModel actions. No `if (balance > amount)` business branches beyond trivial display.
2. **One composable per screen** when possible: `useHomeViewModel`, `useMovementsViewModel`, `useTopUpViewModel`.
3. **`<script setup lang="ts">`** — no Options API.
4. **Props in, events out** for the reusable pieces in `components/`, typed with `defineProps<{…}>()` and `defineEmits<{…}>()`.
5. **Derived UI data** (formatted state, `canSubmit`, `hasMore`) in the ViewModel as `computed`, not scattered in templates.
6. **Loading / empty / error** are part of the ViewModel state — views just render them.
7. **Never** call a service or `fetch` from a `.vue` file.
8. **No Pinia:** the state of a screen stays in its composable.
9. **Destructure the ViewModel in the View** (`const { balance, load } = useHomeViewModel()`): a template only unwraps refs that are top-level names, so `v-if="viewModel.error"` would always be true.
10. **A View imports only its ViewModel and `components/`** — never `models/` or `services/`. The ViewModel hands it display-ready data, formatted amounts included (`balanceText`, not `formatCents(balance)` in the template).

## Types

- The types of the contract's objects (`Movement`, error codes) live in `models/` and are imported; never redeclare them in a ViewModel or a View.
- Give `ref` its type when the first value does not show it: `ref<string | null>(null)`, `ref<Movement[]>([])`.
- No `any`.

## Errors

- Services reject with the contract's `{ code, message, details? }` (`docs/api.md`).
- The ViewModel turns the **`code`** (and `details`) into a user-safe message in Catalan, through the shared module in `models/` (skill `middle-services`). It never reads the `message` text to decide.

## Forms & validation

| Kind | Layer |
|------|--------|
| Domain (amount > 0, per-top-up limit, daily limit) | Backend service is the owner; the ViewModel repeats it for faster feedback |
| Presentation (required, input format, decimals) | ViewModel composable |
| Same rule twice in the frontend | Fix DRY — one owner only |

## Reusable UI (`components/`)

- Presentational: props + emits only.
- No ViewModel and no service call inside a reusable component.

## What “clear” looks like

**Good**

```vue
<!-- CreatePotView.vue -->
<form @submit.prevent="submit">
  <input v-model="name" :disabled="isSubmitting" />
  <p v-if="error" role="alert">{{ error }}</p>
  <button type="submit" :disabled="!canSubmit">
    {{ isSubmitting ? 'Creant…' : 'Crear' }}
  </button>
</form>
```

**Bad**

```vue
<script setup lang="ts">
async function submit() {
  if (name.value.length > 0) {
    await fetch('/api/pots', { method: 'POST', body: JSON.stringify({ name: name.value }) })
  }
}
</script>
```

## Self-check

- [ ] The `.vue` file has no `fetch` and imports only its ViewModel and `components/` (no `models/`, no `services/`)
- [ ] The ViewModel is a composable `useXxxViewModel` with named actions (verbs)
- [ ] `models/` stays pure TypeScript (no `ref`/`reactive`, no HTTP)
- [ ] Loading / error / empty states handled
- [ ] `canSubmit` and derived values live in the ViewModel
- [ ] Types come from `models/`; no `any`
- [ ] Flow is traceable: template → composable → service
