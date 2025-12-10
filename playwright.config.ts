import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './scripts',
  testMatch: '**/*.ts',
  fullyParallel: false, // Run sequentially to avoid rate limiting
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Single worker to avoid rate limiting
  timeout: 120000, // 2 minutes per test
  reporter: 'list',
  use: {
    baseURL: 'https://militaria.pl',
    trace: 'on-first-retry',
    headless: false, // Show browser for debugging
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})

