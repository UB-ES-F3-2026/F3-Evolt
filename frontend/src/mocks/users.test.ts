import { describe, expect, it } from 'vitest'
import { mockSearchUsers, mockUser } from './users'

// Logged in as the user 1 of the seed, as in docs/proves-pagaments.md.
const DEMO = 'demo@evolt.test'

function names(q: string): (string | null)[] {
  return mockSearchUsers(q, DEMO).items.map((user) => user.name)
}

describe('mockSearchUsers (docs/api.md §13.2)', () => {
  it('CU-01: without a text, the other seven users sorted by visible name', () => {
    expect(names('')).toEqual(['Alicia', 'Huabin', 'Izan', 'Jiajun', 'Junhao', 'Martí', 'Usuari nou'])
  })

  it('CU-02: each user has only id, name and username', () => {
    for (const user of mockSearchUsers('', DEMO).items) {
      expect(Object.keys(user).sort()).toEqual(['id', 'name', 'username'])
    }
  })

  it('CU-03: a text of only spaces is the initial list', () => {
    expect(names('  ')).toEqual(names(''))
  })

  it.each(['hua', '@hua', '@123HUABIN123'])('CU-04: %j finds Huabin by @username', (q) => {
    expect(names(q)).toEqual(['Huabin'])
  })

  it.each(['marti', 'MARTÍ'])('CU-05: %j finds Martí by name, without case or accents', (q) => {
    expect(names(q)).toEqual(['Martí'])
  })

  it.each(['huabin@evolt.test', '  Huabin@Evolt.TEST  '])('CU-06: %j finds Huabin by the whole email', (q) => {
    expect(names(q)).toEqual(['Huabin'])
  })

  it.each(['evolt.test', 'huabin@'])('CU-07: part of an email (%j) finds nobody', (q) => {
    expect(names(q)).toEqual([])
  })

  it.each(['611 22 33 02', '+34 611 22 33 02', '611223302', '0034611223302'])(
    'CU-08: %j finds Huabin by the last 9 digits of the phone',
    (q) => {
      expect(names(q)).toEqual(['Huabin'])
    },
  )

  it('a bare "@" is no search at all, never the initial list (docs/api.md §13.2)', () => {
    expect(mockSearchUsers('@', DEMO)).toEqual({ items: [] })
    expect(mockSearchUsers('  @  ', DEMO)).toEqual({ items: [] })
  })

  it('CU-09: a phone of nobody gives an empty list, not an error', () => {
    expect(mockSearchUsers('612 34 56 78', DEMO)).toEqual({ items: [] })
  })

  it('CU-10: fewer than 9 digits is not a phone search', () => {
    expect(names('11223302')).toEqual([])
  })

  it.each(['Usuari demo', '@demo', 'demo@evolt.test', '611 22 33 07'])('CU-11: %j never finds me', (q) => {
    expect(names(q)).toEqual([])
  })

  it('CU-12: «usuari» finds only Usuari nou, never me', () => {
    expect(names('usuari')).toEqual(['Usuari nou'])
  })

  it('CU-13, CU-14: 64 characters are accepted and 65 are VALIDATION_ERROR', () => {
    expect(() => mockSearchUsers('x'.repeat(64), DEMO)).not.toThrow()
    expect(() => mockSearchUsers('x'.repeat(65), DEMO)).toThrow(
      expect.objectContaining({ code: 'VALIDATION_ERROR' }) as Error,
    )
  })
})

describe('mockUser (docs/api.md §13.3)', () => {
  it('CU-18: answers the summary of an existing user', () => {
    expect(mockUser('usr-04')).toEqual({ id: 'usr-04', name: 'Huabin', username: '123huabin123' })
  })

  it.each(['usr-99', '4', 'huabin'])('CU-19: %j is RECIPIENT_NOT_FOUND', (id) => {
    expect(() => mockUser(id)).toThrow(expect.objectContaining({ code: 'RECIPIENT_NOT_FOUND' }) as Error)
  })
})
