import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

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
      // تجاهل ملفات السجلات وملفات النظام المتغيرة باستمرار لمنع إعادة التحميل المتكررة
      ignored: [
        '**/.local/**',
        '**/.cache/**',
        '**/node_modules/**',
        '**/*.log',
        '**/*.pyc',
        '**/app.db',
        '**/__pycache__/**',
      ]
    },
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
