import express from 'express'
import { readFileSync } from 'fs'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const __dirname = dirname(fileURLToPath(import.meta.url))

const app = express()
const FLAG = process.env.FLAG || 'HIT{r34ct_r0ut3_0bfusc4t10n}'

let adminPath = '/'
try {
  const { path } = JSON.parse(readFileSync(join(__dirname, 'admin-path.json'), 'utf8'))
  adminPath = path
} catch {
  console.warn('admin-path.json not found, using default')
}

app.get(`${adminPath}`, (req, res) => {
  if (req.accepts('json')) return res.json({ coucou: FLAG })
  res.sendFile(join(__dirname, 'dist', 'index.html'))
})

app.use(express.static(join(__dirname, 'dist')))

app.get('/{*splat}', (_req, res) => {
  res.sendFile(join(__dirname, 'dist', 'index.html'))
})

const port = process.env.PORT || 3000
app.listen(port, '0.0.0.0', () => {
  console.log(`Server on port ${port}`)
})
