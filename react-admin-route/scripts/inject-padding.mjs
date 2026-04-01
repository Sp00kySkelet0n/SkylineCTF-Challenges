import { readFileSync, writeFileSync } from 'fs'
import { readdirSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const distDir = join(__dirname, '..', 'dist', 'assets')

const { path: adminPath } = JSON.parse(
  readFileSync(join(__dirname, '..', 'admin-path.json'), 'utf8')
)

const pathStr = JSON.stringify(adminPath)
const lazyFiles = readdirSync(distDir).filter((f) => f.startsWith('lazy-') && f.endsWith('.js'))

for (const file of lazyFiles) {
  const filePath = join(distDir, file)
  let content = readFileSync(filePath, 'utf8')
  const idx = content.indexOf(pathStr)
  if (idx === -1) continue

  const padSize = Math.max(0, 2 * idx + pathStr.length - content.length)
  if (padSize <= 0) continue

  const padding = ';var __=' + JSON.stringify('x'.repeat(padSize)) + ';'
  const insertAt = idx + pathStr.length
  content = content.slice(0, insertAt) + padding + content.slice(insertAt)
  writeFileSync(filePath, content)
}
