<script setup lang="ts">
import { onMounted } from 'vue'
import AppShell from '@/components/AppShell.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import { formatDateTime } from '@/models/date'
import { MONEY_REQUEST_STATUS_LABELS } from '@/models/moneyRequest'
import { atUsername, displayName } from '@/models/user'
import { useReceivedMoneyRequestsViewModel } from '@/viewmodels/requests/useReceivedMoneyRequestsViewModel'

const { requests, isLoading, loadError, isEmpty, load } = useReceivedMoneyRequestsViewModel()

// Every visit reads the list again: a request can arrive or expire while the screen is closed.
onMounted(load)
</script>

<template>
  <AppShell title="Sol·licituds rebudes" back>
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="loadError" class="card">
      <ErrorState :message="loadError" @retry="load" />
    </section>

    <section v-else-if="isEmpty" class="card">
      <EmptyState message="Encara no has rebut cap sol·licitud." />
    </section>

    <!-- «Pagar» (US-39) and «Rebutjar» (US-40) go at the bottom of the pending cards; until then, no button. -->
    <ul v-else class="requests">
      <li v-for="request in requests" :key="request.id" class="card request">
        <div class="top">
          <div class="who">
            <p class="name">{{ displayName(request.from) }}</p>
            <p class="muted">{{ atUsername(request.from) }}</p>
            <p class="muted">{{ request.concept }}</p>
            <time class="muted" :datetime="request.createdAt">{{ formatDateTime(request.createdAt) }}</time>
          </div>
          <div class="side">
            <MoneyAmount class="amount" :cents="request.amount" />
            <span class="status" :class="request.status">{{ MONEY_REQUEST_STATUS_LABELS[request.status] }}</span>
          </div>
        </div>
      </li>
    </ul>
  </AppShell>
</template>

<style scoped>
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

/* The colours of the mockup US-16-sollicituds-rebudes: yellow, green, red and grey (US-16). */
.status {
  padding: 0.125rem 0.625rem;
  border-radius: 999px;
  font-size: 0.8125rem;
  font-weight: 700;
}

.status.pending {
  background: #fff4d6;
  color: #8a5a00;
}

.status.paid {
  background: #dcfce7;
  color: #166534;
}

.status.rejected {
  background: #fee2e2;
  color: #991b1b;
}

.status.expired {
  background: #e9edf5;
  color: #475569;
}
</style>
