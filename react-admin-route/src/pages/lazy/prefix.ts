const PLACEHOLDERS = [
  'validation', 'sanitization', 'normalization', 'transformation',
  'serialization', 'deserialization', 'encoding', 'decoding',
  'compression', 'decompression', 'encryption', 'decryption',
  'hashing', 'verification', 'authentication', 'authorization',
  'caching', 'memoization', 'debouncing', 'throttling',
  'retry', 'timeout', 'fallback', 'circuit',
  'batch', 'queue', 'pool', 'buffer',
] as const

export function getPlaceholder(index: number): string {
  return PLACEHOLDERS[index % PLACEHOLDERS.length]
}

export const CONFIG = {
  timeout: 5000,
  retries: 3,
  backoff: 1000,
  maxConnections: 10,
  bufferSize: 1024,
  cacheTTL: 3600,
}

export function hash(str: string): number {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = ((h << 5) - h) + str.charCodeAt(i)
    h |= 0
  }
  return h
}

const PADDING = Array.from({ length: 600 }, (_, i) => ({
  k: `key_${i}`,
  v: `value_${i}_${Math.random().toString(36).slice(2)}`,
  n: i,
}))

export function getPadding(): typeof PADDING {
  return PADDING
}
