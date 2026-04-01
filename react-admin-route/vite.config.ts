import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import crypto from 'crypto'

const ADMIN_PATH = process.env.ADMIN_PATH || '/' + crypto.randomBytes(12).toString('base64url')

export default defineConfig({
  plugins: [react()],
  define: {
    __ADMIN_PATH__: JSON.stringify(ADMIN_PATH),
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) =>
          id.includes('AdminRoute') || id.includes('pages/Admin') || id.includes('pages/lazy') ? 'lazy' : undefined,
      },
    },
  },
})
