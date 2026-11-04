// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import type { RouteLocationNormalized } from 'vue-router'
import { closeSession, saveToken } from '@/services/session'
import { accessGuard } from './accessGuard'

function route(name: string, isPublic = false) {
  return { name, meta: { public: isPublic } } as unknown as RouteLocationNormalized
}

beforeEach(() => {
  sessionStorage.clear()
})

afterEach(() => {
  closeSession()
})

describe('without a session', () => {
  it.each(['home', 'movements', 'topup'])('%s leads to the login', (name) => {
    expect(accessGuard(route(name))).toEqual({ name: 'login' })
  })

  it.each(['login', 'register', 'verify'])('%s opens', (name) => {
    expect(accessGuard(route(name, true))).toBe(true)
  })
})

describe('with a session', () => {
  beforeEach(() => {
    saveToken('token-1')
  })

  it('private routes open', () => {
    expect(accessGuard(route('home'))).toBe(true)
  })

  it('the login leads to Home', () => {
    expect(accessGuard(route('login', true))).toEqual({ name: 'home' })
  })

  it('other public routes still open', () => {
    expect(accessGuard(route('register', true))).toBe(true)
  })
})
