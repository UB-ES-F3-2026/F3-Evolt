<script setup lang="ts">
import { onMounted } from 'vue'
import { Search } from '@lucide/vue'
import AppShell from '@/components/AppShell.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import UserRow from '@/components/UserRow.vue'
import { usePaymentsViewModel } from '@/viewmodels/usePaymentsViewModel'

const { query, users, isSearching, showLoading, showNoResults, error, search } = usePaymentsViewModel()

// The initial list is there before typing anything (US-13).
onMounted(search)
</script>

<template>
  <AppShell title="Enviar diners" back>
    <label class="search">
      <Search class="search-icon" :size="20" aria-hidden="true" />
      <span class="visually-hidden">Cerca un usuari</span>
      <input
        v-model="query"
        class="search-input"
        type="search"
        placeholder="@usuari, telèfon o email"
        autocomplete="off"
        autocapitalize="off"
        spellcheck="false"
      />
    </label>

    <LoadingIndicator v-if="showLoading" />

    <section v-else-if="error" class="card">
      <ErrorState :message="error" @retry="search" />
    </section>

    <section v-else-if="showNoResults" class="card">
      <EmptyState message="No hi ha resultats" />
    </section>

    <template v-else>
      <h2 v-if="isSearching" class="label">Resultats de la cerca</h2>
      <section class="card">
        <ul class="users">
          <!-- Tapping a row goes straight to «Enviar»: no popup and no mark on the row (US-13). -->
          <UserRow
            v-for="user in users"
            :key="user.id"
            :user="user"
            :to="{ name: 'send-payment', query: { to: user.id } }"
          />
        </ul>
      </section>
    </template>
  </AppShell>
</template>

<style scoped>
.search {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
}

.search:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-primary) 15%, transparent);
}

.search-icon {
  flex: none;
  color: var(--color-muted);
}

.search-input {
  flex: 1;
  min-width: 0;
  padding: 0.75rem 0;
  border: none;
  background: transparent;
  color: var(--color-text);
  font: inherit;
}

.search-input:focus {
  outline: none;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
}

.label {
  margin: 0 0 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-muted);
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 0.25rem 1.25rem;
}

.users {
  margin: 0;
  padding: 0;
}
</style>
