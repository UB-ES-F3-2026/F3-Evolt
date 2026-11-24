<script setup lang="ts">
import { onMounted } from 'vue'
import { Plus } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import { formatDateTime } from '@/models/date'
import { MONEY_REQUEST_STATUS_LABELS } from '@/models/moneyRequest'
import { atUsername, displayName } from '@/models/user'
import { useMoneyRequestsViewModel } from '@/viewmodels/requests/useMoneyRequestsViewModel'

const {
  requests,
  isLoading,
  loadError,
  isEmpty,
  requestToCancel,
  isCancelling,
  notice,
  cancelError,
  load,
  askToCancel,
  keepRequest,
  confirmCancel,
} = useMoneyRequestsViewModel()

// Every visit reads the list again, so a new request shows first (US-15).
onMounted(load)
</script>

<template>
  <AppShell title="Sol·licituds enviades" back>
    <!-- «Demanar diners» lives here, not in Inici (PO decision in US-15). -->
    <router-link :to="{ name: 'new-money-request' }" class="ask">
      <Plus :size="20" />
      Demanar diners
    </router-link>

    <p v-if="notice" class="notice" role="status">{{ notice }}</p>
    <p v-if="cancelError" class="cancel-error" role="alert">{{ cancelError }}</p>

    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="loadError" class="card">
      <ErrorState :message="loadError" @retry="load" />
    </section>

    <section v-else-if="isEmpty" class="card">
      <EmptyState message="Encara no has enviat cap sol·licitud." />
    </section>

    <ul v-else class="requests">
      <li v-for="request in requests" :key="request.id" class="card request">
        <div class="top">
          <div class="who">
            <p class="name">{{ displayName(request.to) }}</p>
            <p class="muted">{{ atUsername(request.to) }}</p>
            <p class="muted">{{ request.concept }}</p>
            <time class="muted" :datetime="request.createdAt">{{ formatDateTime(request.createdAt) }}</time>
          </div>
          <div class="side">
            <MoneyAmount class="amount" :cents="request.amount" />
            <span class="status" :class="request.status">{{ MONEY_REQUEST_STATUS_LABELS[request.status] }}</span>
          </div>
        </div>
        <!-- Only a pending request can be cancelled (US-15). -->
        <button v-if="request.status === 'pending'" type="button" class="cancel" @click="askToCancel(request)">
          Cancel·lar
        </button>
      </li>
    </ul>

    <ConfirmDialog
      v-if="requestToCancel"
      title="Cancel·lar sol·licitud"
      message="Segur que vols cancel·lar aquesta sol·licitud?"
      cancel-label="Cancel·lar"
      confirm-label="Confirmar"
      danger
      :busy="isCancelling"
      @cancel="keepRequest"
      @confirm="confirmCancel"
    />
  </AppShell>
</template>

<style scoped>
.ask {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.875rem;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: var(--color-surface);
  font-weight: 600;
}

.notice,
.cancel-error {
  margin: 0 0 0.75rem;
  font-weight: 600;
  text-align: center;
}

.notice {
  color: var(--color-income);
}

.cancel-error {
  color: var(--color-error);
}

.requests {
  margin: 0;
  padding: 0;
  list-style: none;
}

.card {
  margin-bottom: 0.75rem;
  padding: 1rem 1.25rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
}

.top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.who {
  min-width: 0;
}

.name,
.muted {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.muted {
  display: block;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.side {
  display: flex;
  flex: none;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.amount {
  font-weight: 700;
}

.status {
  padding: 0.125rem 0.625rem;
  border-radius: 999px;
  background: var(--color-border);
  font-size: 0.8125rem;
  font-weight: 700;
}

.cancel {
  width: 100%;
  margin-top: 1rem;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
</style>
