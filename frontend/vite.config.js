import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const root = path.dirname(fileURLToPath(import.meta.url))

// EMFILE on external/USB drives: avoid watching node_modules and use polling.
const watchIgnored = [
  path.join(root, 'node_modules'),
  path.join(root, 'dist'),
  path.join(root, '.git'),
  '**/node_modules/**',
  '**/dist/**',
  '**/.git/**',
  '**/.vite/**',
]

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
    watch: {
      usePolling: true,
      interval: 1000,
      ignored: watchIgnored,
    },
  },
  preview: {
    watch: {
      usePolling: true,
      interval: 1000,
      ignored: watchIgnored,
    },
  },
})
