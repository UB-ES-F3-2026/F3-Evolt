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
  }>(),
  { to: undefined },
)

// Only who the person is: never an amount or a balance (US-13).
const name = computed(() => displayName(props.user))
const username = computed(() => atUsername(props.user))
const avatar = computed(() => initials(props.user))
</script>

<template>
  <li class="user-row">
    <component :is="to ? RouterLink : 'div'" :to="to" class="row">
      <span class="avatar" aria-hidden="true">{{ avatar }}</span>
      <div class="details">
        <p class="name">{{ name }}</p>
        <p class="username">{{ username }}</p>
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
