import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5000,
    allowedHosts: true,
    watch: {
      ignored: [
        '**/node_modules/**',
        '**/*.log',
        '**/*.pyc',
        '**/__pycache__/**',
        '**/src/database/*.db',
      ]
    },
    proxy: {
      '/api': {
        target: process.env.API_URL || 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
