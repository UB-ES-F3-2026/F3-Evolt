import { useRouter } from 'vue-router'
import type { StatusJson } from '@/models/auth'
import { logout } from '@/services/authService'
import { closeSession, hasSession } from '@/services/session'

export interface SessionMenuDependencies {
  hasSession: () => boolean
  logout: () => Promise<StatusJson>
  closeSession: () => void
  goToLogin: () => Promise<unknown>
}

/** The header menu (US-03): whether to show it, and leaving the session. */
export function useSessionMenuViewModel(dependencies: SessionMenuDependencies = defaultDependencies()) {
  const isLoggedIn = dependencies.hasSession()

  async function logOut(): Promise<void> {
    // The person wants out: a request that fails must not keep them in.
    await dependencies.logout().catch(() => undefined)
    dependencies.closeSession()
    await dependencies.goToLogin()
  }

  return { isLoggedIn, logOut }
}

function defaultDependencies(): SessionMenuDependencies {
  const router = useRouter()
  return {
    hasSession,
    logout,
    closeSession,
    goToLogin: () => router.replace({ name: 'login' }),
  }
}
