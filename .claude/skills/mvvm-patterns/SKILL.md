---
name: mvvm-patterns
description: Load when creating or changing Vue frontend UI — screens, components, forms, composable ModelViews, state, events, props. Use for any Vue 3 feature on F3-Evolt (auth, savings, transfers, gamification, multidivisa). Frontend-specific MVVM.
---

# Vue MVVM — Model · ModelView · View

Stack: **Vue 3** (`<script setup lang="ts">`) + TypeScript.  
Team naming: **ModelView** = ViewModel, implemented as a **composable**.

## Layers (Vue mapping)

| Layer | Place | Vue piece | Does | Does not |
|-------|-------|-----------|------|----------|
| **View** | `features/<f>/view/` | `*.vue` SFC | Render, emit events, bind props | Business rules, Firebase SDK |
| **ModelView** | `features/<f>/modelview/` | `useXxxModelView.ts` composable | State, commands, derived UI data | Template layout, raw Firestore |
| **Model** | `features/<f>/model/` | pure `.ts` types + fns | Entities, money math, domain validation | Vue reactivity, Firebase |
| **Services** | `features/<f>/services/` | plain TS (or thin composable) | Use cases, ports, Firebase adapters | Template / component markup |

```
View (.vue)
  → useXxxModelView()          // ModelView composable
      → service / port
          → adapter (Firebase)
      → model (pure)
```

## Canonical flow (example: contribute to pot)

```ts
// features/savings/view/ContributeView.vue
<script setup lang="ts">
const props = defineProps<{ potId: string }>()
const emit = defineEmits<{ (e: 'done'): void }>()
const mv = useContributeModelView(props.potId)

async function onSubmit() {
  const ok = await mv.submitContribution()
  if (ok) emit('done')
}
</script>
```

```ts
// features/savings/modelview/useContributeModelView.ts
export function useContributeModelView(potId: string) {
  const amount = ref('')
  const error = ref<string | null>(null)
  const loading = ref(false)
  const service = useSavingsService()

  async function submitContribution(): Promise<boolean> {
    error.value = null
    const money = Money.parse(amount.value) // model — pure
    if (!money) {
      error.value = 'Introdueix un import vàlid'
      return false
    }
    loading.value = true
    try {
      await service.contribute(potId, money) // service
      return true
    } catch (e) {
      error.value = toUserMessage(e)
      return false
    } finally {
      loading.value = false
    }
  }

  return { amount, error, loading, submitContribution }
}
```

## Vue rules

1. **SFC View is thin:** template + props/emit + calls ModelView commands. No `if (balance > amount)` business branches in the template logic beyond trivial display.
2. **One composable per screen/flow** when possible: `useHomeModelView`, `useCreatePotModelView`.
3. **`<script setup lang="ts">`** — no Options API unless the team already agreed otherwise for a file.
4. **Props in, events out** for shared components under `view/` or `shared/components/`.
5. **Derived UI data** (progress %, formatted money, canSubmit) in the ModelView as `computed`, not scattered in templates.
6. **Loading / empty / error** are part of the ModelView state — views just render them.
7. **Never** import `firebase/*` or repositories in `.vue` files.
8. **Pinia** (if used): global/session state only (auth user, theme). Feature ModelView state stays in the composable unless the rule is truly global.

## Forms & validation

| Kind | Layer |
|------|--------|
| Domain (amount > 0, balance, daily limit) | model / service |
| Presentation (required, input format) | ModelView composable |
| Same rule twice | Fix DRY — one owner only |

## Shared UI (`shared/components/`)

- Presentational: props + emits only.
- No composables that hit Firebase inside shared UI.

## What “clear” looks like

**Good**

```vue
<!-- CreatePotView.vue -->
<form @submit.prevent="mv.submit">
  <input v-model="mv.name" :disabled="mv.loading" />
  <p v-if="mv.error" role="alert">{{ mv.error }}</p>
  <button type="submit" :disabled="mv.loading || !mv.canSubmit">
    {{ mv.loading ? 'Creant…' : 'Crear' }}
  </button>
</form>
```

**Bad**

```vue
<script setup>
import { getFirestore, addDoc, collection } from 'firebase/firestore'
async function submit() {
  if (name.value.length > 0) {
    await addDoc(collection(getFirestore(), 'pots'), { name: name.value })
  }
}
</script>
```

## Self-check

- [ ] Vue SFC has no Firebase/repository imports
- [ ] ModelView is a composable with named commands (verbs)
- [ ] Model stays pure TS (no `ref`/`reactive` in domain models)
- [ ] Loading / error / empty states handled
- [ ] `canSubmit` and derived values live in ModelView
- [ ] Flow is traceable: template → composable → service
