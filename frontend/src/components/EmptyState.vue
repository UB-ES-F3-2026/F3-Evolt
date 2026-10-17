<script setup lang="ts">
import { Inbox } from '@lucide/vue'

withDefaults(defineProps<{ message?: string }>(), { message: 'Encara no tens moviments' })
</script>

<template>
  <div class="empty-state">
    <Inbox class="icon" :size="32" />
    <p class="message">{{ message }}</p>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem 0;
  text-align: center;
}

.icon {
  color: var(--color-muted);
}

.message {
  margin: 0;
  color: var(--color-muted);
}
</style>
