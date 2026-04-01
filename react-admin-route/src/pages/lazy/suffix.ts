const ERRORS: Record<string, string> = {}
for (let i = 0; i < 500; i++) {
  ERRORS[`E${String(i).padStart(4, '0')}`] = `Error code ${i} description for debugging purposes`
}

for (let i = 0; i < 300; i++) {
  ERRORS[`W${String(i).padStart(4, '0')}`] = `Warning code ${i} message`
}

export function formatError(code: string, msg?: string): string {
  const base = ERRORS[code] ?? code
  return msg ? `${base}: ${msg}` : base
}

export const DEFAULTS = {
  theme: 'dark',
  locale: 'fr-FR',
  timezone: 'Europe/Paris',
  currency: 'EUR',
  pageSize: 25,
  sortOrder: 'asc' as const,
}

export function mergeOptions<T extends object>(a: T, b: Partial<T>): T {
  return { ...a, ...b }
}

export function delay(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms))
}

const LOREM = 'Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua'.split(' ')

export function lorem(length: number): string {
  return Array.from({ length }, (_, i) => LOREM[i % LOREM.length]).join(' ')
}

export const SCHEMA = {
  version: 1,
  fields: Array.from({ length: 100 }, (_, i) => ({
    name: `field_${i}`,
    type: (['string', 'number', 'boolean'] as const)[i % 3],
    required: i % 2 === 0,
  })),
}

const LARGE_DATA = Array.from({ length: 800 }, (_, i) => ({
  id: i,
  name: `item_${i}`,
  value: Math.random() * 1000,
  timestamp: Date.now() - i * 1000,
}))

export function getDataSlice(offset: number, limit: number) {
  return LARGE_DATA.slice(offset, offset + limit)
}
