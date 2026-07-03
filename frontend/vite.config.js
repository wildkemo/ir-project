import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const root = path.dirname(fileURLToPath(import.meta.url))

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
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
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
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
    watch: {
      usePolling: true,
      interval: 1000,
      ignored: watchIgnored,
    },
  },
})
