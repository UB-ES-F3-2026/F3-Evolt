import type { RouteLocationNormalized, RouteLocationRaw } from 'vue-router'
import { hasSession } from '@/services/session'

declare module 'vue-router' {
  interface RouteMeta {
    /** Can be opened without a session. Everything else needs one. */
    public?: boolean
  }
}

/** Without a session every private route leads to the login (US-03). */
export function accessGuard(to: RouteLocationNormalized): RouteLocationRaw | true {
  if (to.name === 'login' && hasSession()) return { name: 'home' }
  if (to.meta.public === true || hasSession()) return true
  return { name: 'login' }
}
