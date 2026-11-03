<script setup lang="ts">
import { onMounted } from 'vue'
import { Plus } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import PotRow from '@/components/PotRow.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { usePotsViewModel } from '@/viewmodels/usePotsViewModel'

const { pots, isLoading, error, isEmpty, load } = usePotsViewModel()
const { isHidden } = useBalanceVisibility()

// Every visit reloads, so a pot created on the form shows up when coming back.
onMounted(load)
</script>

<template>
  <AppShell title="Guardioles" back>
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="error" class="card">
      <ErrorState :message="error" @retry="load" />
    </section>

    <section v-else-if="isEmpty" class="card empty">
      <EmptyState message="Encara no tens cap guardiola" />
      <router-link to="/pots/new" class="create">Crear guardiola</router-link>
    </section>

    <template v-else>
      <section class="card">
        <ul class="pots">
          <PotRow v-for="pot in pots" :key="pot.id" :pot="pot" :hidden="isHidden" />
        </ul>
      </section>
      <router-link to="/pots/new" class="create">
        <Plus :size="18" />
        Crear guardiola
      </router-link>
    </template>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-bottom: 1.5rem;
}

.pots {
  margin: 0;
  padding: 0;
}

.create {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.625rem 1rem;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: var(--color-surface);
  font-weight: 600;
}
</style>
