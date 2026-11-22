import { describe, expect, it } from 'vitest'
import { atUsername, displayName, fromApiUser, initials, type UserSummary } from './user'

const usuariNou: UserSummary = { id: 'usr-02', name: 'Usuari nou', username: 'buit' }
const anna: UserSummary = { id: 'usr-09', name: null, username: 'anna' }

describe('user', () => {
  it('shows the name, and the @username when the person has no name (CUP-11)', () => {
    expect(displayName(usuariNou)).toBe('Usuari nou')
    expect(displayName(anna)).toBe('@anna')
    expect(atUsername(usuariNou)).toBe('@buit')
  })

  it.each([
    [usuariNou, 'UN'],
    [{ id: 'usr-03', name: 'Alicia', username: 'aliciaa415' }, 'AL'],
    [anna, 'AN'],
  ])('builds the round avatar letters of %j as %s (mockup US-13-cerca-usuaris)', (user, letters) => {
    expect(initials(user)).toBe(letters)
  })

  it('keeps a missing name as null', () => {
    expect(fromApiUser({ id: 'usr-09', name: null, username: 'anna' }).name).toBeNull()
  })
})
