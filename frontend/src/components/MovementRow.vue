<script setup lang="ts">
import { computed } from 'vue'
import {
  ArrowLeftRight,
  Briefcase,
  Bus,
  Receipt,
  ShoppingBag,
  Utensils,
  Wallet,
  type LucideIcon,
} from '@lucide/vue'
import MoneyAmount from '@/components/MoneyAmount.vue'
import { formatDateTime } from '@/models/date'
import type { Movement, MovementIcon } from '@/models/movement'

// The root element is an <li>: render rows inside a <ul>.
const props = withDefaults(
  defineProps<{
    movement: Movement
    /** Masks the amount, like the balance (T07.10). */
    hidden?: boolean
  }>(),
  { hidden: false },
)

// One visual icon per value of the closed `icon` list (docs/api.md §3).
const ICON_COMPONENTS: Record<MovementIcon, LucideIcon> = {
  topup: Wallet,
  salary: Briefcase,
  transfer: ArrowLeftRight,
  shopping: ShoppingBag,
  food: Utensils,
  transport: Bus,
  other: Receipt,
}

// fromApiMovement already maps unknown icons to `other`; the row still guards itself.
const iconComponent = computed(() => ICON_COMPONENTS[props.movement.icon] ?? ICON_COMPONENTS.other)
const isIncome = computed(() => props.movement.type === 'income')
</script>

<template>
  <li class="movement-row">
    <span class="icon">
      <component :is="iconComponent" :size="20" />
    </span>
    <div class="details">
      <p class="concept">{{ movement.concept }}</p>
      <time class="date" :datetime="movement.date">{{ formatDateTime(movement.date) }}</time>
    </div>
    <MoneyAmount
      class="amount"
      :class="isIncome ? 'income' : 'expense'"
      :cents="movement.amount"
      :sign="isIncome ? 'positive' : 'negative'"
      :hidden="hidden"
    />
  </li>
</template>

<style scoped>
.movement-row {
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
  background: var(--color-bg);
  color: var(--color-muted);
}

.details {
  flex: 1;
  min-width: 0;
}

.concept {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.date {
  font-size: 0.8125rem;
  color: var(--color-muted);
}

.amount {
  flex: none;
  font-weight: 600;
}

.income {
  color: var(--color-income);
}

.expense {
  color: var(--color-expense);
}
</style>
