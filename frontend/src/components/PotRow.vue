<script setup lang="ts">
import { PiggyBank } from '@lucide/vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import type { Pot } from '@/models/pot'

// The root element is an <li>: render rows inside a <ul>.
withDefaults(
  defineProps<{
    pot: Pot
    /** Masks the balance, like every other amount (T07.10). */
    hidden?: boolean
  }>(),
  { hidden: false },
)
</script>

<template>
  <li class="pot-row" :style="{ '--pot-color': `var(--color-pot-${pot.color})` }">
    <span class="icon">
      <PiggyBank :size="20" />
    </span>
    <span class="name">{{ pot.name }}</span>
    <MoneyAmount class="balance" :cents="pot.balance" :hidden="hidden" />
  </li>
</template>

<style scoped>
.pot-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0;
  list-style: none;
}

.icon {
  flex: none;
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: color-mix(in srgb, var(--pot-color) 14%, var(--color-surface));
  color: var(--pot-color);
}

.name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.balance {
  flex: none;
  font-weight: 600;
}
</style>
