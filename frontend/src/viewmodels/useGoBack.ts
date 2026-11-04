import { useRouter, type RouteLocationRaw } from 'vue-router'

/**
 * Back to the screen this one was opened from, so the detail of a movement returns to
 * Inici or to Moviments depending on where it was tapped. `fallback` is for a screen
 * opened directly, with no previous screen in the app.
 */
export function useGoBack(fallback: RouteLocationRaw): () => void {
  const router = useRouter()

  return () => {
    if (router.options.history.state.back) router.back()
    else void router.push(fallback)
  }
}
