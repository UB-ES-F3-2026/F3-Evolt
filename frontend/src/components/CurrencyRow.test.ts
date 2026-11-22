// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import CurrencyRow from './CurrencyRow.vue'

interface RowProps {
  code: string
  name: string
  symbol: string
  amountText?: string
  hidden?: boolean
  owned?: boolean
  selectable?: boolean
  disabled?: boolean
}

function rowProps(overrides: Partial<RowProps> = {}): RowProps {
  return { code: 'EUR', name: 'Euro', symbol: '€', ...overrides }
}

describe('CurrencyRow', () => {
  it('renders the owned state with a badge, greyed and not clickable', async () => {
    const row = mount(CurrencyRow, { props: rowProps({ owned: true, selectable: true }) })

    expect(row.text()).toContain('EUR · Euro')
    expect(row.find('.badge').text()).toBe('ja la tens')
    expect(row.find('.row-disabled').exists()).toBe(true)
    expect(row.find('.chevron').exists()).toBe(false)

    await row.find('.row').trigger('click')
    expect(row.emitted('select')).toBeUndefined()
  })

  it('renders a selectable row with a chevron that emits select once', async () => {
    const row = mount(CurrencyRow, { props: rowProps({ selectable: true }) })

    expect(row.find('.chevron').exists()).toBe(true)
    expect(row.find('.row-disabled').exists()).toBe(false)
    expect(row.find('button.row').exists()).toBe(true)

    await row.find('.row').trigger('click')
    expect(row.emitted('select')).toHaveLength(1)
  })

  it('renders a disabled selectable row greyed and without emitting', async () => {
    const row = mount(CurrencyRow, { props: rowProps({ selectable: true, disabled: true }) })

    expect(row.find('.row-disabled').exists()).toBe(true)
    expect(row.find('.badge').exists()).toBe(false)
    expect(row.find('button.row').attributes('disabled')).toBeDefined()

    await row.find('.row').trigger('click')
    expect(row.emitted('select')).toBeUndefined()
  })

  it('shows the pre-formatted amount and masks it when hidden', () => {
    const visible = mount(CurrencyRow, { props: rowProps({ amountText: '427,16 $' }) })
    expect(visible.find('.amount').text()).toBe('427,16 $')

    const hidden = mount(CurrencyRow, { props: rowProps({ amountText: '427,16 $', hidden: true }) })
    expect(hidden.find('.amount').text()).toBe('••••')

    const absent = mount(CurrencyRow, { props: rowProps() })
    expect(absent.find('.amount').exists()).toBe(false)
  })
})
