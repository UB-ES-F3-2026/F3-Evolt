/** Saving a file on the device. */

// The browser reads the file after the click, and a phone can take a while: it is freed later.
const FREE_AFTER_MS = 60_000

export function saveFile(file: Blob, fileName: string): void {
  const url = URL.createObjectURL(file)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), FREE_AFTER_MS)
}
