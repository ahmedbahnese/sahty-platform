import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './ui-tests',
  testMatch: 'ai-widget-responsive.spec.js',
  timeout: 30_000,
  fullyParallel: false,
  reporter: [['list']],
  use: {
    baseURL: process.env.BASE_URL || 'http://127.0.0.1:5173',
    headless: true,
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
})
