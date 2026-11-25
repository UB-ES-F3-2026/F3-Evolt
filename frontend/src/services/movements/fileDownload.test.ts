// @vitest-environment jsdom
import { afterEach, describe, expect, it, vi } from 'vitest'
import { saveFile } from './fileDownload'

afterEach(() => {
  vi.useRealTimers()
  vi.restoreAllMocks()
  vi.unstubAllGlobals()
})

describe('saveFile', () => {
  it('downloads the file with its name, and frees it only later', () => {
    vi.useFakeTimers()
    const createObjectURL = vi.fn(() => 'blob:receipt')
    const revokeObjectURL = vi.fn()
    vi.stubGlobal('URL', Object.assign(URL, { createObjectURL, revokeObjectURL }))
    let clicked: { href: string; download: string } | null = null
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (this: HTMLAnchorElement) {
      clicked = { href: this.href, download: this.download }
    })
    const file = new Blob(['%PDF-'])

    saveFile(file, 'justificant-EVT-000029.pdf')

    expect(createObjectURL).toHaveBeenCalledWith(file)
    expect(clicked).toEqual({ href: 'blob:receipt', download: 'justificant-EVT-000029.pdf' })
    expect(revokeObjectURL).not.toHaveBeenCalled()

    vi.runAllTimers()
    expect(revokeObjectURL).toHaveBeenCalledWith('blob:receipt')
  })
})
