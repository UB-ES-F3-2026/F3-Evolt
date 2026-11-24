<script setup lang="ts">
import { onMounted } from 'vue'
import { CircleCheck } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import CurrencyRow from '@/components/CurrencyRow.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import { useAddCurrencyViewModel } from '@/viewmodels/currencies/useAddCurrencyViewModel'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'

const { rows, isLoading, error, confirmation, load, add } = useAddCurrencyViewModel()
const { isHidden } = useBalanceVisibility()

// Every visit reloads, so the "ja la tens" badges always match the owned currencies.
onMounted(load)
</script>

<template>
  <AppShell title="Afegir divisa" back back-to="/divises" back-label="← Divises">
    <!-- The confirmation wins over everything: the screen is already on its way home. -->
    <section v-if="confirmation" class="card success" role="status">
      <CircleCheck class="success-icon" :size="40" />
      <p class="success-text">{{ confirmation }}</p>
      <p class="muted">Tornant a Inici…</p>
    </section>

    <LoadingIndicator v-else-if="isLoading" />

    <section v-else class="card">
      <ul class="rows">
        <CurrencyRow
          v-for="row in rows"
          :key="row.code"
          :code="row.code"
          :name="row.name"
          :symbol="row.symbol"
          :owned="row.owned"
          :selectable="!row.owned"
          :disabled="row.disabled"
          :hidden="isHidden"
          @select="add(row.code)"
        />
      </ul>
      <!-- Add failures surface here; a list failure means an empty picker, so no retry button. -->
      <p v-if="error" class="error" role="alert">{{ error }}</p>
    </section>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}

.rows {
  list-style: none;
  padding: 0;
  margin: 0;
}

.error {
  margin: 0.75rem 0 0;
  font-size: 0.875rem;
  color: var(--color-error);
}

.success {
  display: grid;
  place-items: center;
  text-align: center;
  gap: 0.5rem;
  padding: 2.25rem 1.5rem;
}

.success-icon {
  color: var(--color-income);
}

.success-text {
  margin: 0;
  font-size: 1.0625rem;
  font-weight: 600;
}

.muted {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}
</style>
