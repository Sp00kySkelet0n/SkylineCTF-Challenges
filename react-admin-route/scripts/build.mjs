import crypto from 'crypto'
import { writeFileSync } from 'fs'
import { execSync } from 'child_process'

const adminPath = '/' + crypto.randomBytes(12).toString('base64url')
writeFileSync('admin-path.json', JSON.stringify({ path: adminPath }))
execSync('pnpm exec vite build', {
  stdio: 'inherit',
  env: { ...process.env, ADMIN_PATH: adminPath },
})
execSync('node scripts/inject-padding.mjs', { stdio: 'inherit' })
