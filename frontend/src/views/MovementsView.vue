<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, useTemplateRef, watch } from 'vue'
import AppShell from '@/components/AppShell.vue'
import EmptyState from '@/components/EmptyState.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import MovementRow from '@/components/MovementRow.vue'
import { useBalanceVisibility } from '@/viewmodels/useBalanceVisibility'
import { useMovementsViewModel } from '@/viewmodels/useMovementsViewModel'

const { items, isLoading, isLoadingMore, error, hasMore, isEmpty, loadFirstPage, loadMore, retry } =
  useMovementsViewModel()
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
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="error && items.length === 0" class="card">
      <ErrorState :message="error" @retry="retry" />
    </section>

    <section v-else-if="isEmpty" class="card">
      <EmptyState />
    </section>

    <section v-else class="card">
      <ul class="movements">
        <MovementRow v-for="movement in items" :key="movement.id" :movement="movement" :hidden="isHidden" />
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

.movements {
  margin: 0;
  padding: 0;
}

.sentinel {
  height: 1px;
}
</style>
