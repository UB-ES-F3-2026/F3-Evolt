import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs'
import { describe, expect, it } from 'vitest'
import { formatSignedCents } from '@/models/money'
import type { ReceiptContent } from '@/models/receipt'
import { makeReceiptPdf } from './receiptPdf'

const content: ReceiptContent = {
  amount: formatSignedCents(1000, 'negative'),
  isIncome: false,
  concept: 'Bizum enviat',
  rows: [
    { label: 'Data i hora', value: '1/11/2026, 18:42' },
    { label: 'Estat', value: 'Completat' },
    { label: 'Contrapart', value: 'Núria Soler' },
    { label: 'Referència', value: 'EVT-000029' },
  ],
}

const withoutSpaces = (text: string) => text.replace(/\s/g, '')

/** Reads the text back from the real file, as a person would see it. Line breaks do not count. */
async function readPdf(pdf: Blob): Promise<{ pages: number; text: string }> {
  const document = await getDocument({ data: new Uint8Array(await pdf.arrayBuffer()), verbosity: 0 }).promise
  let text = ''
  for (let number = 1; number <= document.numPages; number++) {
    const page = await document.getPage(number)
    const { items } = await page.getTextContent()
    text += items.map((item) => ('str' in item ? item.str : '')).join('')
  }
  return { pages: document.numPages, text: withoutSpaces(text) }
}

describe('makeReceiptPdf (DP-04, DP-08)', () => {
  it('makes a one-page PDF with every piece of data, the «−» sign included', async () => {
    const pdf = await makeReceiptPdf(content)
    const { pages, text } = await readPdf(pdf)

    expect(pdf.type).toBe('application/pdf')
    expect(pages).toBe(1)
    expect(text).toContain(withoutSpaces(content.amount))
    expect(text).toContain('Bizumenviat')
    for (const { label, value } of content.rows) {
      expect(text).toContain(withoutSpaces(label))
      expect(text).toContain(withoutSpaces(value))
    }
  })

  it('does not cut a long concept: it wraps, to another page if needed', async () => {
    const concept = Array.from({ length: 900 }, (_, index) => `paraula${index}`).join(' ')
    const { pages, text } = await readPdf(await makeReceiptPdf({ ...content, concept }))

    expect(text).toContain(withoutSpaces(concept))
    expect(text).toContain('EVT-000029')
    expect(pages).toBeGreaterThan(1)
  })

  it('does not cut a long word with no spaces', async () => {
    const concept = 'x'.repeat(400)
    const { text } = await readPdf(await makeReceiptPdf({ ...content, concept }))

    expect(text).toContain(concept)
  })

  it('still makes the receipt when a text has characters the font lacks', async () => {
    const { text } = await readPdf(await makeReceiptPdf({ ...content, concept: 'Aportació a Viatge 🎉 旅行' }))

    expect(text).toContain('Aportació')
    expect(text).toContain('EVT-000029')
  })
})
