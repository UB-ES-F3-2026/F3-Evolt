<script setup lang="ts">
import { CircleAlert, RotateCw } from '@lucide/vue'

withDefaults(
  defineProps<{
    /** Text for the user, already in Catalan (the ViewModel builds it from the error code). */
    message: string
    /** Compact, without the big icon: at the end of a list that keeps what it already loaded. */
    inline?: boolean
  }>(),
  { inline: false },
)

const emit = defineEmits<{ retry: [] }>()
</script>

<template>
  <div class="error-state" :class="{ inline }">
    <CircleAlert v-if="!inline" class="icon" :size="32" />
    <p class="message" role="alert">{{ message }}</p>
    <button type="button" class="retry" @click="emit('retry')">
      <RotateCw :size="16" />
      Reintentar
    </button>
  </div>
</template>

<style scoped>
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem 0;
  text-align: center;
}

.error-state.inline {
  gap: 0.5rem;
  padding: 0.75rem 0;
}

.icon {
  color: var(--color-error);
}

.message {
  margin: 0;
  color: var(--color-muted);
}

.inline .message {
  font-size: 0.875rem;
}

.retry {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius);
  background: transparent;
  color: var(--color-primary);
  font: inherit;
  font-size: 0.875rem;
  cursor: pointer;
}

.retry:hover {
  background: var(--color-bg);
}
</style>
