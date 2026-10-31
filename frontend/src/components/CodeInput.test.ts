// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { nextTick } from 'vue'
import CodeInput from './CodeInput.vue'

function mountInput(initial = '') {
  const wrapper = mount(CodeInput, {
    attachTo: document.body,
    props: {
      length: 6,
      label: 'Codi',
      modelValue: initial,
      'onUpdate:modelValue': (code: string) => wrapper.setProps({ modelValue: code }),
    },
  })
  return wrapper
}

function boxes(wrapper: ReturnType<typeof mountInput>) {
  return wrapper.findAll('input')
}

function typed(wrapper: ReturnType<typeof mountInput>) {
  return wrapper.props('modelValue')
}

describe('CodeInput', () => {
  it('shows one box per digit, with the first one ready to type', () => {
    const wrapper = mountInput()

    expect(boxes(wrapper)).toHaveLength(6)
    expect(document.activeElement).toBe(boxes(wrapper)[0]?.element)
    wrapper.unmount()
  })

  it('moves to the next box after each digit', async () => {
    const wrapper = mountInput()

    await boxes(wrapper)[0]?.setValue('4')

    expect(typed(wrapper)).toBe('4')
    expect(document.activeElement).toBe(boxes(wrapper)[1]?.element)
    wrapper.unmount()
  })

  it('fills all the boxes with a pasted code', async () => {
    const wrapper = mountInput()

    await boxes(wrapper)[0]?.setValue('048213')

    expect(typed(wrapper)).toBe('048213')
    expect(boxes(wrapper).map((box) => (box.element as HTMLInputElement).value)).toEqual([
      '0', '4', '8', '2', '1', '3',
    ])
    wrapper.unmount()
  })

  it('ignores anything that is not a digit', async () => {
    const wrapper = mountInput('12')

    await boxes(wrapper)[2]?.setValue('a')

    expect(typed(wrapper)).toBe('12')
    expect((boxes(wrapper)[2]?.element as HTMLInputElement).value).toBe('')
    wrapper.unmount()
  })

  it('replaces a digit in the middle without losing the others', async () => {
    const wrapper = mountInput('123456')

    await boxes(wrapper)[2]?.setValue('9')

    expect(typed(wrapper)).toBe('129456')
    wrapper.unmount()
  })

  it('backspace on an empty box deletes the previous digit', async () => {
    const wrapper = mountInput('12')

    await boxes(wrapper)[2]?.trigger('keydown', { key: 'Backspace' })

    expect(typed(wrapper)).toBe('1')
    expect(document.activeElement).toBe(boxes(wrapper)[1]?.element)
    wrapper.unmount()
  })

  it('goes back to the first box when the code is emptied', async () => {
    const wrapper = mountInput('12')
    boxes(wrapper)[2]?.element.focus()

    await wrapper.setProps({ modelValue: '' })
    await nextTick()

    expect(document.activeElement).toBe(boxes(wrapper)[0]?.element)
    wrapper.unmount()
  })

  it('locks every box and marks them red', () => {
    const wrapper = mountInput()
    wrapper.unmount()

    const locked = mount(CodeInput, {
      props: { length: 6, label: 'Codi', modelValue: '', invalid: true, disabled: true },
    })

    expect(locked.findAll('input').every((box) => (box.element as HTMLInputElement).disabled)).toBe(true)
    expect(locked.findAll('input.invalid')).toHaveLength(6)
    locked.unmount()
  })
})
