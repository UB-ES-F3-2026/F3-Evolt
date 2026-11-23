// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import type { CurrencyCode } from '@/models/exchange'
import SubaccountPicker from './SubaccountPicker.vue'

interface Option {
  code: CurrencyCode
  name: string
  balanceMinor: number
}

const OPTIONS: Option[] = [
  { code: 'EUR', name: 'Euro', balanceMinor: 379521 },
  { code: 'USD', name: 'Dòlar nord-americà', balanceMinor: 31755 },
]

function mountPicker(
  options: { modelValue?: string; disabledCode?: string | null; disabledTag?: string } = {},
) {
  const wrapper = mount(SubaccountPicker, {
    props: {
      id: 'origin',
      label: "Subcompte d'origen",
      modelValue: options.modelValue ?? 'USD',
      options: OPTIONS,
      disabledCode: options.disabledCode,
      disabledTag: options.disabledTag,
      'onUpdate:modelValue': (code: string) => wrapper.setProps({ modelValue: code }),
    },
  })
  return wrapper
}

describe('SubaccountPicker', () => {
  it('ties the label to the select and shows the label', () => {
    const wrapper = mountPicker()

    expect(wrapper.get('label').attributes('for')).toBe('origin')
    expect(wrapper.get('select').attributes('id')).toBe('origin')
    expect(wrapper.get('label').text()).toBe("Subcompte d'origen")
    wrapper.unmount()
  })

  it('writes each subaccount with its code, name and balance', () => {
    const wrapper = mountPicker()

    expect(wrapper.findAll('option')[0]?.text()).toMatch(/^EUR · Euro — 3\.795,21\s€$/)
    expect(wrapper.findAll('option')[1]?.text()).toMatch(/^USD · Dòlar nord-americà — 317,55\s\$$/)
    wrapper.unmount()
  })

  it('marks the other side of the exchange and keeps it unselected', () => {
    const wrapper = mountPicker({ disabledCode: 'EUR' })

    const other = wrapper.findAll('option')[0]
    expect(other?.attributes('disabled')).toBeDefined()
    expect(other?.text()).toMatch(/ · és l'origen$/)
    expect((wrapper.get('select').element as HTMLSelectElement).value).toBe('USD')
    wrapper.unmount()
  })

  it('emits the chosen code', async () => {
    const wrapper = mountPicker()

    await wrapper.get('select').setValue('EUR')

    expect(wrapper.emitted('update:modelValue')).toEqual([['EUR']])
    wrapper.unmount()
  })
})
