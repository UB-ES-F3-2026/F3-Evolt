import { describe, expect, it, vi } from 'vitest'
import { messageForCode } from '@/models/errorMessages'
import type { UserSummary } from '@/models/user'
import { useSendPaymentViewModel } from './useSendPaymentViewModel'

const huabin: UserSummary = { id: 'usr-04', name: 'Huabin', username: '123huabin123' }

describe('useSendPaymentViewModel', () => {
  it('CUP-08, CUP-09: asks the API for the recipient of `?to=`, so a reload keeps it', async () => {
    const getUser = vi.fn(() => Promise.resolve(huabin))
    const viewModel = useSendPaymentViewModel('usr-04', { getUser })

    await viewModel.load()

    expect(getUser).toHaveBeenCalledWith('usr-04')
    expect(viewModel.recipient.value).toEqual(huabin)
    expect(viewModel.error.value).toBeNull()
  })

  it('CUP-10: an id that is not a user shows «No hem trobat aquest destinatari.» and offers to choose again', async () => {
    const getUser = vi.fn(() => Promise.reject({ code: 'RECIPIENT_NOT_FOUND', message: 'x' }))
    const viewModel = useSendPaymentViewModel('usr-99', { getUser })

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('RECIPIENT_NOT_FOUND'))
    expect(viewModel.isRecipientMissing.value).toBe(true)
  })

  it('without `?to=` there is nobody to send to, without asking the API', async () => {
    const getUser = vi.fn(() => Promise.resolve(huabin))
    const viewModel = useSendPaymentViewModel(undefined, { getUser })

    await viewModel.load()

    expect(getUser).not.toHaveBeenCalled()
    expect(viewModel.isRecipientMissing.value).toBe(true)
  })

  it('a network error can be tried again: it is not a missing recipient', async () => {
    const getUser = vi.fn(() => Promise.reject({ code: 'NETWORK_ERROR', message: 'x' }))
    const viewModel = useSendPaymentViewModel('usr-04', { getUser })

    await viewModel.load()

    expect(viewModel.error.value).toBe(messageForCode('NETWORK_ERROR'))
    expect(viewModel.isRecipientMissing.value).toBe(false)
  })
})
