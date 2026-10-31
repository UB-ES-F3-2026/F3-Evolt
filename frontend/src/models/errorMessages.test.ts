import { describe, expect, it } from 'vitest'
import { messageForCode, toUserMessage } from './errorMessages'

describe('toUserMessage', () => {
  it('gives each contract code its own text', () => {
    expect(toUserMessage({ code: 'INVALID_AMOUNT', message: 'x' })).toBe("L'import ha de ser més gran que 0.")
    expect(toUserMessage({ code: 'AMOUNT_OVER_LIMIT', message: 'x' })).toMatch(/màxim per recàrrega és de 500,00\s€/)
    expect(toUserMessage({ code: 'VALIDATION_ERROR', message: 'x' })).toMatch(/no són vàlides/)
    expect(toUserMessage({ code: 'NETWORK_ERROR', message: 'x' })).toMatch(/connexió/)
    expect(toUserMessage({ code: 'INTERNAL_ERROR', message: 'x' })).toMatch(/error inesperat/)
  })

  it.each([
    ['WEAK_PASSWORD', 'La contrasenya ha de tenir 8 caràcters, una majúscula i un número.'],
    ['ALREADY_REGISTERED', 'Aquest email o telèfon ja té un compte.'],
    ['INVALID_CODE', 'El codi no és correcte o ha caducat.'],
    ['CODE_EXPIRED', 'El codi no és correcte o ha caducat.'],
    ['TOO_MANY_ATTEMPTS', 'Has fet massa intents. Demana un codi nou.'],
  ])('gives the access code %s the text of docs/api.md §8.14', (code, text) => {
    expect(toUserMessage({ code, message: 'x' })).toBe(text)
  })

  it('says how much can still be topped up today, from details', () => {
    const failure = { code: 'DAILY_LIMIT_EXCEEDED', message: 'x', details: { remainingToday: 10000 } }
    expect(toUserMessage(failure)).toMatch(/límit diari.*Avui encara pots recarregar 100,00\s€\./)
  })

  it('still explains the daily limit when details are missing', () => {
    expect(messageForCode('DAILY_LIMIT_EXCEEDED')).toBe('Has superat el límit diari de recàrrega.')
  })

  it('never shows the text the backend sent', () => {
    const failure = { code: 'INVALID_AMOUNT', message: 'Text intern del servidor' }
    expect(toUserMessage(failure)).not.toContain('Text intern del servidor')
  })

  it('treats anything that is not a contract error as unexpected', () => {
    expect(toUserMessage(new Error('boom'))).toMatch(/error inesperat/)
    expect(toUserMessage({ detail: 'Not Found' })).toMatch(/error inesperat/)
    expect(toUserMessage(undefined)).toMatch(/error inesperat/)
  })
})
