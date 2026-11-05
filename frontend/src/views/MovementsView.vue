<script setup lang="ts">
import { Search, SlidersHorizontal } from '@lucide/vue'
import { nextTick, onBeforeUnmount, onMounted, useTemplateRef, watch } from 'vue'
import AppShell from '@/components/AppShell.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import FormField from '@/components/FormField.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MovementRow from '@/components/MovementRow.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useMovementsViewModel } from '@/viewmodels/useMovementsViewModel'

const {
  items,
  isLoading,
  isLoadingMore,
  error,
  hasMore,
  isEmpty,
  hasNoResults,
  search,
  dateFrom,
  dateTo,
  type,
  typeOptions,
  dateError,
  areFiltersOpen,
  canClearFilters,
  loadFirstPage,
  loadMore,
  retry,
  toggleFilters,
  clearFilters,
} = useMovementsViewModel()
const { isHidden } = useBalanceVisibility()

// Infinite scroll: an empty element after the last row asks for the next page
// when it comes close to the screen.
const sentinel = useTemplateRef<HTMLElement>('sentinel')
let observer: IntersectionObserver | null = null

// Observing again re-checks it now: a page that does not fill the screen leaves
// the sentinel in view, and the observer only reports changes.
function watchSentinel(): void {
  if (!observer || !sentinel.value) return
  observer.unobserve(sentinel.value)
  observer.observe(sentinel.value)
}

onMounted(() => {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries.some((entry) => entry.isIntersecting)) loadMore()
    },
    { rootMargin: '200px' },
  )
  loadFirstPage()
})

watch(
  () => items.value.length,
  () => nextTick(watchSentinel),
)

onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <AppShell title="Moviments" back>
    <section class="card filters">
      <div class="search">
        <Search class="search-icon" :size="18" aria-hidden="true" />
        <input
          v-model="search"
          class="search-input"
          type="search"
          placeholder="Cerca per concepte o contacte"
          aria-label="Cerca per concepte o contacte"
        />
      </div>

      <div class="toolbar">
        <button
          type="button"
          class="filters-button"
          :aria-expanded="areFiltersOpen"
          aria-controls="movement-filters"
          @click="toggleFilters"
        >
          <SlidersHorizontal :size="18" aria-hidden="true" />
          Filtres
        </button>
        <button v-if="canClearFilters" type="button" class="link-button" @click="clearFilters">
          Esborrar filtres
        </button>
      </div>

      <div v-if="areFiltersOpen" id="movement-filters" class="filter-panel">
        <div class="dates">
          <FormField id="date-from" v-model="dateFrom" label="Data d'inici" type="date" :max="dateTo || undefined" />
          <FormField
            id="date-to"
            v-model="dateTo"
            label="Data final"
            type="date"
            :min="dateFrom || undefined"
            :error="dateError"
          />
        </div>

        <fieldset class="types">
          <legend class="types-legend">Tipus</legend>
          <label
            v-for="option in typeOptions"
            :key="option.value"
            class="type-option"
            :class="[option.value, { selected: type === option.value }]"
          >
            <input v-model="type" class="type-radio" type="radio" name="movement-type" :value="option.value" />
            {{ option.label }}
          </label>
        </fieldset>
      </div>
    </section>

    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="error && items.length === 0" class="card">
      <ErrorState :message="error" @retry="retry" />
    </section>

    <section v-else-if="isEmpty" class="card">
      <EmptyState />
    </section>

    <section v-else-if="hasNoResults" class="card no-results">
      <EmptyState message="No hi ha resultats" />
      <button type="button" class="link-button" @click="clearFilters">Esborrar filtres</button>
    </section>

    <section v-else class="card">
      <ul class="movements">
        <MovementRow
          v-for="movement in items"
          :key="movement.id"
          :movement="movement"
          :hidden="isHidden"
          :to="{ name: 'movement', params: { movementId: movement.id } }"
        />
      </ul>

      <!-- A failed next page keeps the rows already loaded; the error goes after them. -->
      <LoadingIndicator v-if="isLoadingMore" inline label="Carregant més moviments…" />
      <ErrorState v-else-if="error" inline :message="error" @retry="retry" />

      <div v-if="hasMore" ref="sentinel" class="sentinel" aria-hidden="true" />
    </section>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
}

.card + .card {
  margin-top: 1rem;
}

.search {
  position: relative;
}

.search-icon {
  position: absolute;
  top: 50%;
  left: 0.75rem;
  transform: translateY(-50%);
  color: var(--color-muted);
}

.search-input {
  width: 100%;
  padding: 0.75rem 0.75rem 0.75rem 2.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
}

.search-input::placeholder {
  color: var(--color-muted);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 1px var(--color-primary);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.75rem;
}

.filters-button {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  cursor: pointer;
}

.filters-button[aria-expanded='true'] {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.link-button {
  padding: 0.5rem 0;
  border: none;
  background: none;
  color: var(--color-primary);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.filter-panel {
  margin-top: 1rem;
}

/* minmax(0, …): a date picker is wider than half a phone screen and would overflow the card. */
.dates {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 0.75rem;
}

.types {
  display: flex;
  gap: 0.5rem;
  margin: 0;
  padding: 0;
  border: none;
}

.types-legend {
  margin-bottom: 0.25rem;
  padding: 0;
  font-size: 0.875rem;
  color: var(--color-muted);
}

.type-option {
  --option-color: var(--color-text);

  flex: 1;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  color: var(--option-color);
  text-align: center;
  cursor: pointer;
}

.type-option.income {
  --option-color: var(--color-income);
}

.type-option.expense {
  --option-color: var(--color-expense);
}

.type-option.selected {
  border-color: var(--option-color);
  background: color-mix(in srgb, var(--option-color) 10%, var(--color-surface));
  font-weight: 600;
}

.type-option:focus-within {
  box-shadow: 0 0 0 2px var(--color-primary);
}

/* The radio stays for the keyboard and screen readers; the whole pill is the target. */
.type-radio {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.no-results {
  text-align: center;
}

.movements {
  margin: 0;
  padding: 0;
}

.sentinel {
  height: 1px;
}
</style>
