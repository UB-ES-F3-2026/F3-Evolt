// @vitest-environment jsdom
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import ConfirmDialog from './ConfirmDialog.vue'

describe('ConfirmDialog', () => {
  it('is a modal dialog named by its title, with the message under it', () => {
    const dialog = mount(ConfirmDialog, {
      props: { title: 'Segur?', message: 'No es pot desfer.', confirmLabel: 'Eliminar', cancelLabel: 'Cancel·lar' },
    })

    const window = dialog.get('[role="dialog"]')
    expect(window.attributes('aria-modal')).toBe('true')
    expect(dialog.get(`#${window.attributes('aria-labelledby')}`).text()).toBe('Segur?')
    expect(dialog.get(`#${window.attributes('aria-describedby')}`).text()).toBe('No es pot desfer.')
    expect(dialog.findAll('button').map((button) => button.text())).toEqual(['Cancel·lar', 'Eliminar'])
  })

  it('emits confirm and cancel from their buttons', async () => {
    const dialog = mount(ConfirmDialog, {
      props: { title: 'Segur?', confirmLabel: 'Eliminar', cancelLabel: 'Cancel·lar', danger: true },
    })

    expect(dialog.get('.confirm').classes()).toContain('danger')
    await dialog.get('.cancel').trigger('click')
    await dialog.get('.confirm').trigger('click')

    expect(dialog.emitted('cancel')).toHaveLength(1)
    expect(dialog.emitted('confirm')).toHaveLength(1)
  })

  it('Esc and a click on the backdrop cancel a question', async () => {
    const dialog = mount(ConfirmDialog, { props: { title: 'Segur?', confirmLabel: 'Sí', cancelLabel: 'No' } })

    await dialog.get('.backdrop').trigger('keydown', { key: 'Escape' })
    await dialog.get('.backdrop').trigger('click')
    // A click inside the window is not a click on the backdrop.
    await dialog.get('.dialog').trigger('click')

    expect(dialog.emitted('cancel')).toHaveLength(2)
    expect(dialog.emitted('confirm')).toBeUndefined()
  })

  it('a notice has a single button, and every way out confirms it', async () => {
    const dialog = mount(ConfirmDialog, { props: { title: 'Atenció', confirmLabel: "D'acord" } })

    expect(dialog.findAll('button').map((button) => button.text())).toEqual(["D'acord"])
    expect(dialog.find('[role="dialog"]').attributes('aria-describedby')).toBeUndefined()
    await dialog.get('.backdrop').trigger('keydown', { key: 'Escape' })
    await dialog.get('.backdrop').trigger('click')

    expect(dialog.emitted('confirm')).toHaveLength(2)
  })

  it('while busy both buttons are disabled and nothing closes it', async () => {
    const dialog = mount(ConfirmDialog, {
      props: { title: 'Segur?', confirmLabel: 'Eliminar', cancelLabel: 'Cancel·lar', busy: true },
    })

    expect(dialog.findAll('button').every((button) => button.attributes('disabled') !== undefined)).toBe(true)
    await dialog.get('.backdrop').trigger('keydown', { key: 'Escape' })
    await dialog.get('.backdrop').trigger('click')

    expect(dialog.emitted('cancel')).toBeUndefined()
  })

  it('moves the focus to the confirm button when it opens', async () => {
    const dialog = mount(ConfirmDialog, {
      props: { title: 'Segur?', confirmLabel: 'Eliminar', cancelLabel: 'Cancel·lar' },
      attachTo: document.body,
    })
    await new Promise((resolve) => setTimeout(resolve, 0))

    expect(document.activeElement).toBe(dialog.get('.confirm').element)
    dialog.unmount()
  })
})
