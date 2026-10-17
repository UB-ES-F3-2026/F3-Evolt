// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import type { Movement } from '@/models/movement'
import MovementRow from './MovementRow.vue'

function movement(overrides: Partial<Movement> = {}): Movement {
  return {
    id: 'mov-1',
    amount: 180000,
    concept: "Nòmina d'octubre",
    date: '2026-10-01T09:00:00+02:00',
    type: 'income',
    icon: 'salary',
    ...overrides,
  }
}

describe('MovementRow', () => {
  it('shows concept, date and an income in green with +', () => {
    const row = mount(MovementRow, { props: { movement: movement() } })

    expect(row.text()).toContain("Nòmina d'octubre")
    expect(row.find('time').attributes('datetime')).toBe('2026-10-01T09:00:00+02:00')
    expect(row.find('.amount').classes()).toContain('income')
    expect(row.find('.amount').text()).toMatch(/^\+1\.800,00\s€$/)
  })

  it('shows an expense in red with −', () => {
    const row = mount(MovementRow, {
      props: { movement: movement({ amount: 2350, type: 'expense', icon: 'food' }) },
    })

    expect(row.find('.amount').classes()).toContain('expense')
    expect(row.find('.amount').text()).toMatch(/^−23,50\s€$/)
  })

  it('masks the amount when amounts are hidden, but keeps the colour', () => {
    const row = mount(MovementRow, { props: { movement: movement({ type: 'expense' }), hidden: true } })

    expect(row.find('.amount').text()).toBe('••••')
    expect(row.text()).not.toContain('1.800')
    expect(row.find('.amount').classes()).toContain('expense')
  })

  it('still renders with an icon outside the closed list', () => {
    const unknownIcon = { ...movement(), icon: 'pizza' } as unknown as Movement
    const row = mount(MovementRow, { props: { movement: unknownIcon } })

    expect(row.find('svg').exists()).toBe(true)
    expect(row.text()).toContain("Nòmina d'octubre")
  })
})
