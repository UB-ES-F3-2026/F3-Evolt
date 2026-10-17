<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, useTemplateRef, watch } from 'vue'
import AppShell from '@/components/AppShell.vue'
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
    <section v-if="isLoading" class="card state">
      <p class="state-text">Carregant…</p>
    </section>

    <section v-else-if="error && items.length === 0" class="card state">
      <p class="state-text" role="alert">{{ error }}</p>
      <button type="button" class="retry" @click="retry">Reintentar</button>
    </section>

    <section v-else-if="isEmpty" class="card state">
      <p class="state-text">Encara no tens moviments</p>
    </section>

    <section v-else class="card">
      <ul class="movements">
        <MovementRow v-for="movement in items" :key="movement.id" :movement="movement" :hidden="isHidden" />
      </ul>

      <p v-if="isLoadingMore" class="state-text more">Carregant més moviments…</p>
      <div v-else-if="error" class="state more">
        <p class="state-text" role="alert">{{ error }}</p>
        <button type="button" class="retry" @click="retry">Reintentar</button>
      </div>

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

.state {
  text-align: center;
}

.state-text {
  margin: 0.5rem 0 0;
  color: var(--color-muted);
}

.more {
  text-align: center;
  padding-top: 0.5rem;
}

.retry {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius);
  background: transparent;
  color: var(--color-primary);
  font: inherit;
  font-size: 0.875rem;
  cursor: pointer;
}

.sentinel {
  height: 1px;
}
</style>
