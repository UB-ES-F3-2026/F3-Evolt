<script setup lang="ts">
import { onMounted } from 'vue'
import AppShell from '@/components/AppShell.vue'
import CodeInput from '@/components/CodeInput.vue'
import { useVerifyViewModel } from '@/viewmodels/useVerifyViewModel'

const { identifier, code, codeLength, error, notice, isLocked, isSubmitting, isResending, start, resend } =
  useVerifyViewModel()

onMounted(start)
</script>

<template>
  <AppShell title="Verifica el teu compte">
    <section class="card">
      <p class="intro">Hem enviat un codi de {{ codeLength }} números a {{ identifier }}.</p>

      <CodeInput
        v-model="code"
        :length="codeLength"
        label="Codi de verificació"
        :invalid="error !== null"
        :disabled="isLocked || isSubmitting"
      />

      <p v-if="error" class="message error" role="alert">{{ error }}</p>
      <p v-else-if="notice" class="message notice" role="status">{{ notice }}</p>

      <button type="button" class="link" :disabled="isResending" @click="resend">
        Envia'm un codi nou
      </button>
    </section>
  </AppShell>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius);
  padding: 1.25rem;
  text-align: center;
}

.intro {
  margin: 0 0 1rem;
  color: var(--color-muted);
  font-size: 0.875rem;
}

.message {
  margin: 0.75rem 0 0;
  font-size: 0.875rem;
}

.error {
  color: var(--color-error);
}

.notice {
  color: var(--color-muted);
}

.link {
  margin-top: 1rem;
  padding: 0;
  border: none;
  background: none;
  color: var(--color-primary);
  font: inherit;
  cursor: pointer;
}

.link:disabled {
  color: var(--color-muted);
  cursor: not-allowed;
}
</style>
