<script setup lang="ts">
import { onMounted } from 'vue'
import AppShell from '@/components/AppShell.vue'
import ErrorState from '@/components/ErrorState.vue'
import LoadingIndicator from '@/components/LoadingIndicator.vue'
import UserRow from '@/components/UserRow.vue'
import { useSendPaymentViewModel } from '@/viewmodels/useSendPaymentViewModel'

const props = defineProps<{ to?: string }>()

const { recipient, isLoading, error, isRecipientMissing, load } = useSendPaymentViewModel(props.to)

// The recipient is asked again on every visit, so a reload keeps it (US-13).
onMounted(load)
</script>

<template>
  <AppShell title="Enviar" back>
    <LoadingIndicator v-if="isLoading" />

    <section v-else-if="error" class="card">
      <ErrorState :message="error" :retryable="!isRecipientMissing" @retry="load" />
      <router-link v-if="isRecipientMissing" :to="{ name: 'payments' }" class="choose-again">
        Torna a triar el destinatari
      </router-link>
    </section>

    <section v-else-if="recipient" class="card">
      <ul class="recipient">
        <UserRow :user="recipient" />
      </ul>
    </section>
  </AppShell>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 0.5rem 1.25rem;
}

.recipient {
  margin: 0;
  padding: 0;
}

.choose-again {
  margin: 0 auto 1rem;
  font-weight: 600;
}
</style>
