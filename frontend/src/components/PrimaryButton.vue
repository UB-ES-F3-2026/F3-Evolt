<template>
  <button type="submit" class="primary-button">
    <slot />
  </button>
</template>

<style scoped>
.primary-button {
  width: 100%;
  padding: 0.75rem;
  border: none;
  border-radius: var(--radius);
  background: var(--color-primary);
  color: var(--color-surface);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.primary-button:disabled {
  background: var(--color-border);
  color: var(--color-muted);
  cursor: not-allowed;
}
</style>
