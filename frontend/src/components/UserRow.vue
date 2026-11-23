<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, type RouteLocationRaw } from 'vue-router'
import { atUsername, displayName, initials, type UserSummary } from '@/models/user'

// The root element is an <li>: render rows inside a <ul>.
const props = withDefaults(
  defineProps<{
    user: UserSummary
    /** Where tapping the row goes. Without it, the row only shows who the person is. */
    to?: RouteLocationRaw
    /** Set it to make the row a choice (the recipient of «Demanar diners», US-15): true when chosen. */
    selected?: boolean
  }>(),
  { to: undefined, selected: undefined },
)

const emit = defineEmits<{ select: [] }>()

// Only who the person is: never an amount or a balance (US-13).
const name = computed(() => displayName(props.user))
const username = computed(() => atUsername(props.user))
const avatar = computed(() => initials(props.user))
</script>

<template>
  <li class="user-row">
    <button
      v-if="selected !== undefined"
      type="button"
      class="row choice"
      :class="{ selected }"
      :aria-pressed="selected"
      @click="emit('select')"
    >
      <span class="avatar" aria-hidden="true">{{ avatar }}</span>
      <div class="details">
        <p class="name">{{ name }}</p>
        <p class="username">{{ username }}</p>
      </div>
      <span v-if="selected" class="check" aria-hidden="true">✓</span>
    </button>
    <component :is="to ? RouterLink : 'div'" v-else :to="to" class="row">
      <span class="avatar" aria-hidden="true">{{ avatar }}</span>
      <div class="details">
        <p class="name">{{ name }}</p>
        <!-- Without a name the @username is already the name: it is not repeated below (#212). -->
        <p v-if="user.name !== null" class="username">{{ username }}</p>
      </div>
    </component>
  </li>
</template>

<style scoped>
.user-row {
  list-style: none;
}

.user-row + .user-row {
  border-top: 1px solid var(--color-border);
}

.row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0;
  color: inherit;
}

.choice {
  width: 100%;
  padding-inline: 0.5rem;
  border: none;
  border-left: 3px solid transparent;
  background: none;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.choice.selected {
  border-left-color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 8%, var(--color-surface));
}

.check {
  flex: none;
  color: var(--color-primary);
  font-weight: 700;
}

.avatar {
  flex: none;
  display: grid;
  place-items: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: color-mix(in srgb, var(--color-primary) 10%, var(--color-surface));
  color: var(--color-primary);
  font-weight: 700;
}

.details {
  flex: 1;
  min-width: 0;
}

.name,
.username {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.username {
  font-size: 0.8125rem;
  color: var(--color-muted);
}
</style>
