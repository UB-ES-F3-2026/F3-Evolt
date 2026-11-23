<script setup lang="ts">
import { onMounted } from 'vue'
import { CircleCheck } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useSubaccountViewModel } from '@/viewmodels/useSubaccountViewModel'

const props = defineProps<{ subaccountId: string }>()

const {
  subaccount,
  history,
  title,
  balanceText,
  canDelete,
  hasHistory,
  isLoading,
  error,
  dialog,
  isDeleting,
  deleteError,
  confirmation,
  notFound,
  load,
  askToDelete,
  closeDialog,
  confirmDelete,
} = useSubaccountViewModel(props.subaccountId)
const { isHidden } = useBalanceVisibility()

// Every visit reloads, so an exchange made on another screen shows up (US-27).
onMounted(load)
</script>

<template>
  <AppShell :title="title" back back-to="/divises" back-label="← Divises">
    <!-- The confirmation wins over everything: the screen is already on its way home. -->
    <section v-if="confirmation" class="card success" role="status">
      <CircleCheck class="success-icon" :size="40" />
      <p class="success-text">{{ confirmation }}</p>
      <p class="muted">Tornant a Inici…</p>
    </section>

    <section v-else-if="notFound" class="card" role="alert">
      <p class="error">{{ notFound }}</p>
      <p class="muted">Tornant a Divises…</p>
    </section>

    <LoadingIndicator v-else-if="isLoading" />

    <section v-else-if="error" class="card">
      <ErrorState :message="error" @retry="load" />
    </section>

    <template v-else-if="subaccount">
      <section class="card">
        <h2 class="label">Saldo</h2>
        <p class="balance">{{ isHidden ? '••••' : balanceText }}</p>
      </section>

      <section class="card">
        <h2 class="label">Últims moviments</h2>
        <ul v-if="hasHistory" class="history">
          <li v-for="entry in history" :key="entry.id" class="entry">
            <div class="details">
              <p class="concept">{{ entry.concept }}</p>
              <time class="date" :datetime="entry.date">{{ entry.dateText }}</time>
            </div>
            <span class="amount" :class="entry.isIncome ? 'income' : 'expense'">
              {{ isHidden ? '••••' : entry.amountText }}
            </span>
          </li>
        </ul>
        <EmptyState v-else message="Encara no tens moviments" />
      </section>

      <!-- No «Aportar» this sprint (PO decision, #189): only «Canviar» (US-27) fills or empties it. -->
      <button v-if="canDelete" type="button" class="delete" @click="askToDelete">Eliminar subcompte</button>
    </template>

    <ConfirmDialog
      v-if="dialog === 'not-empty'"
      title="Abans d'eliminar-lo has de deixar el saldo a 0"
      confirm-label="D'acord"
      @confirm="closeDialog"
    />
    <ConfirmDialog
      v-if="dialog === 'confirm'"
      title="Segur que vols eliminar aquest subcompte?"
      :message="deleteError ?? 'Els moviments en euros dels canvis es queden a «Moviments».'"
      confirm-label="Eliminar"
      cancel-label="Cancel·lar"
      danger
      :busy="isDeleting"
      @confirm="confirmDelete"
      @cancel="closeDialog"
    />
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}

.label {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
}

.balance {
  margin: 0.25rem 0 0;
  font-size: 2rem;
  font-weight: 700;
}

.history {
  list-style: none;
  margin: 0.5rem 0 0;
  padding: 0;
}

.entry {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0;
  border-bottom: 1px solid var(--color-border);
}

.entry:last-child {
  border-bottom: none;
}

.details {
  flex: 1;
  min-width: 0;
}

.concept {
  margin: 0;
}

.date {
  font-size: 0.75rem;
  color: var(--color-muted);
}

.amount {
  font-weight: 600;
  white-space: nowrap;
}

.amount.income {
  color: var(--color-income);
}

.amount.expense {
  color: var(--color-expense);
}

.delete {
  /* Mockup US-26-detall-subcompte: the red button stays at the bottom of the screen. */
  position: sticky;
  bottom: 1rem;
  width: 100%;
  margin-top: 1rem;
  padding: 0.875rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-expense);
  color: var(--color-surface);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
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
  font-weight: 600;
}

.muted {
  margin: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.error {
  margin: 0 0 0.25rem;
  color: var(--color-error);
}
</style>
