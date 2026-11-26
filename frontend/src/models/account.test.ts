import { describe, expect, it } from 'vitest'
import { groupIban, shareText } from './account'

describe('groupIban', () => {
  it('IBP-02: groups the 24 characters in fours', () => {
    expect(groupIban('ES9121000418450200051332')).toBe('ES91 2100 0418 4502 0005 1332')
  })

  it('leaves an already grouped IBAN as it was', () => {
    expect(groupIban('ES91 2100 0418 4502 0005 1332')).toBe('ES91 2100 0418 4502 0005 1332')
  })
})

describe('shareText', () => {
  it('IBP-04: the text of «Compartir», with the grouped IBAN', () => {
    expect(shareText({ iban: 'ES9121000418450200051332', bic: 'EVOLESB1XXX', holder: 'Usuari demo' })).toBe(
      'IBAN: ES91 2100 0418 4502 0005 1332 · BIC: EVOLESB1XXX · Titular: Usuari demo',
    )
  })
})
