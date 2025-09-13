import { devices, defineConfig } from '@playwright/test';

export default defineConfig({
  use: {
    baseURL: 'http://127.0.0.1:5173',
    launchOptions: { headless: true }
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: 'npm run server',
    url: 'http://127.0.0.1:5173/ui/index.html',
    reuseExistingServer: !process.env.CI
  }
});
