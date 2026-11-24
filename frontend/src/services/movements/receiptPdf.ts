/**
 * Makes a movement's PDF receipt in the browser (docs/api.md §10.5).
 * jsPDF and the font are heavy, so they load only when someone asks for a receipt.
 */

import type { ReceiptContent } from '@/models/receipt'

const TITLE = 'Justificant del moviment'
const FONT = 'DejaVuSans'
const FONT_FILE = `${FONT}.ttf`
const MARGIN_PT = 56
const LINE_HEIGHT = 1.3

// The colours of the detail screen (frontend/src/style.css): a PDF cannot read CSS variables.
const TEXT_COLOR = '#1a2233'
const MUTED_COLOR = '#6c7a96'
const INCOME_COLOR = '#16a34a'
const EXPENSE_COLOR = '#dc2626'

export async function makeReceiptPdf(content: ReceiptContent): Promise<Blob> {
  const [{ jsPDF }, font] = await Promise.all([
    import('jspdf'),
    // PDF's basic fonts garble «−» and much of what people type, so the font goes inside the file.
    import('dejavu-fonts-ttf/ttf/DejaVuSans.ttf?inline'),
  ])

  const doc = new jsPDF({ unit: 'pt', format: 'a4', compress: true })
  doc.setProperties({ title: TITLE, author: 'Evolt' })
  doc.addFileToVFS(FONT_FILE, font.default.split(',')[1])
  doc.addFont(FONT_FILE, FONT, 'normal')
  doc.setFont(FONT)

  const width = doc.internal.pageSize.getWidth() - 2 * MARGIN_PT
  const bottom = doc.internal.pageSize.getHeight() - MARGIN_PT
  let y = MARGIN_PT

  function write(text: string, size: number, color: string, spaceAfter = 0): void {
    doc.setFontSize(size).setTextColor(color)
    const lineHeight = size * LINE_HEIGHT
    // Wraps at the margins, long words too, and flows to a new page: a long concept is never cut.
    for (const line of doc.splitTextToSize(text, width) as string[]) {
      if (y + lineHeight > bottom) {
        doc.addPage()
        y = MARGIN_PT
      }
      doc.text(line, MARGIN_PT, y, { baseline: 'top' })
      y += lineHeight
    }
    y += spaceAfter
  }

  write('Evolt', 12, MUTED_COLOR)
  write(TITLE, 20, TEXT_COLOR, 24)
  write(content.amount, 28, content.isIncome ? INCOME_COLOR : EXPENSE_COLOR)
  write(content.concept, 14, TEXT_COLOR, 24)
  for (const { label, value } of content.rows) {
    write(label, 10, MUTED_COLOR)
    write(value, 12, TEXT_COLOR, 10)
  }

  return doc.output('blob')
}
