// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import AmountKeypad from './AmountKeypad.vue'

function mountKeypad(
  options: { amount?: string; decimals?: 0 | 2; error?: string | null; disabled?: boolean } = {},
) {
  const wrapper = mount(AmountKeypad, {
    props: {
      amount: options.amount ?? '',
      decimals: options.decimals,
      error: options.error,
      disabled: options.disabled,
      'onUpdate:amount': (amount: string) => wrapper.setProps({ amount }),
    },
  })
  return wrapper
}

function typed(wrapper: ReturnType<typeof mountKeypad>): string {
  return wrapper.props('amount') as string
}

async function press(wrapper: ReturnType<typeof mountKeypad>, text: string): Promise<void> {
  const key = wrapper.findAll('button.key').find((button) => button.text() === text)
  expect(key).toBeDefined()
  await key?.trigger('click')
}

describe('AmountKeypad', () => {
  it('associates the label with the input and asks for a numeric keyboard', () => {
    const wrapper = mountKeypad()

    expect(wrapper.get('label').attributes('for')).toBe(wrapper.get('input').attributes('id'))
    expect(wrapper.get('input').attributes('inputmode')).toBe('numeric')
    wrapper.unmount()
  })

  it('builds the amount key by key', async () => {
    const wrapper = mountKeypad()

    await press(wrapper, '1')
    await press(wrapper, '2')
    expect(typed(wrapper)).toBe('12')

    await press(wrapper, ',')
    await press(wrapper, '5')
    expect(typed(wrapper)).toBe('12,5')

    wrapper.unmount()
  })

  it('ignores a second comma and a third decimal', async () => {
    const wrapper = mountKeypad()

    await press(wrapper, '1')
    await press(wrapper, '2')
    await press(wrapper, ',')
    await press(wrapper, '5')
    expect(typed(wrapper)).toBe('12,5')

    await press(wrapper, ',')
    expect(typed(wrapper)).toBe('12,5')

    await press(wrapper, '9')
    expect(typed(wrapper)).toBe('12,59')

    await press(wrapper, '9')
    expect(typed(wrapper)).toBe('12,59')

    wrapper.unmount()
  })

  it('erases one character at a time', async () => {
    const wrapper = mountKeypad({ amount: '12,59' })

    await press(wrapper, '⌫')

    expect(typed(wrapper)).toBe('12,5')
    wrapper.unmount()
  })

  it('hides the comma and cuts the amount at it when the currency has no decimals', async () => {
    const wrapper = mountKeypad({ decimals: 0 })

    expect(wrapper.findAll('button.key').map((key) => key.text())).not.toContain(',')

    await wrapper.get('input').setValue('5,5')

    // The fraction is dropped, not merged into the integer ('55' would be ×10).
    expect(typed(wrapper)).toBe('5')
    wrapper.unmount()
  })

  it('renders the hint slot between the amount field and the keypad', () => {
    const wrapper = mount(AmountKeypad, {
      props: { amount: '' },
      slots: { hint: '<p class="my-hint">Ajuda</p>' },
    })

    const hint = wrapper.get('.hint')
    expect(hint.text()).toBe('Ajuda')
    // Between the field and the keypad, so the view can drop a note there.
    expect(hint.element.compareDocumentPosition(wrapper.get('.keypad').element)).toBe(
      Node.DOCUMENT_POSITION_FOLLOWING,
    )
    expect(hint.element.compareDocumentPosition(wrapper.get('.field').element)).toBe(
      Node.DOCUMENT_POSITION_PRECEDING,
    )
    wrapper.unmount()
  })

  it('renders no hint when the slot is not filled', () => {
    const wrapper = mountKeypad()

    expect(wrapper.find('.hint').exists()).toBe(false)
    wrapper.unmount()
  })

  it('cleans what is typed into the input and does not re-emit the same amount', async () => {
    const wrapper = mountKeypad()

    await wrapper.get('input').setValue('1a2.5')

    expect(typed(wrapper)).toBe('12,5')
    expect((wrapper.get('input').element as HTMLInputElement).value).toBe('12,5')

    const emitted = wrapper.emitted('update:amount')?.length ?? 0
    await wrapper.get('input').setValue('12,5')

    expect(wrapper.emitted('update:amount')?.length ?? 0).toBe(emitted)
    wrapper.unmount()
  })

  it('shows the error and marks the input invalid', () => {
    const wrapper = mountKeypad({ error: "L'import és massa petit per canviar." })

    const alert = wrapper.get('p[role="alert"]')
    expect(alert.text()).toBe("L'import és massa petit per canviar.")
    expect(wrapper.get('input').attributes('aria-invalid')).toBe('true')
    expect(wrapper.get('input').attributes('aria-describedby')).toBe(alert.attributes('id'))
    wrapper.unmount()
  })

  it('locks the input and every key when disabled', () => {
    const wrapper = mountKeypad({ disabled: true })

    expect((wrapper.get('input').element as HTMLInputElement).disabled).toBe(true)
    expect(wrapper.findAll('button.key').every((key) => (key.element as HTMLButtonElement).disabled)).toBe(
      true,
    )
    wrapper.unmount()
  })
})
