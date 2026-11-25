/** A query value as text, or undefined when it is missing or repeated. */
export function queryText(value: unknown): string | undefined {
  return typeof value === 'string' ? value : undefined
}
