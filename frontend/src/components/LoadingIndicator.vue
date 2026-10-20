<script setup lang="ts">
import { LoaderCircle } from '@lucide/vue'

withDefaults(
  defineProps<{
    label?: string
    /** Small, in a row: at the end of a list while the next page loads. */
    inline?: boolean
  }>(),
  { label: 'Carregant…', inline: false },
)
</script>

<template>
  <div class="loading" :class="{ inline }" role="status">
    <LoaderCircle class="spinner" :size="inline ? 18 : 32" />
    <span class="label">{{ label }}</span>
  </div>
</template>

<style scoped>
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  min-height: 40vh;
  color: var(--color-muted);
}

.loading.inline {
  flex-direction: row;
  gap: 0.5rem;
  min-height: 0;
  padding: 0.75rem 0;
  font-size: 0.875rem;
}

.spinner {
  color: var(--color-primary);
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .spinner {
    animation: none;
  }
}
</style>
