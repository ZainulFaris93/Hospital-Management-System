import { defineConfig, devices } from '@playwright/test';

/**
 * Starts the Django app on a fresh SQLite database with demo data, then runs
 * the end-to-end suite against it. Run from this folder: `npx playwright test`.
 */
const PORT = 8000;
const python = process.env.PYTHON ?? 'python';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false,
  workers: 1, // tests share one database, so run them in order
  retries: process.env.CI ? 1 : 0,
  forbidOnly: !!process.env.CI,
  timeout: 30_000,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'desktop-chrome', use: { ...devices['Desktop Chrome'] } },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 7'] },
      testMatch: /(public|auth|access)\.spec\.ts/, // read-only checks on a phone screen
    },
  ],
  webServer: {
    command: [
      `${python} manage.py migrate --no-input`,
      `${python} manage.py seed_demo`,
      `${python} manage.py runserver 127.0.0.1:${PORT} --noreload`,
    ].join(' && '),
    cwd: '../hospital_project',
    url: `http://127.0.0.1:${PORT}/login_page`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      USE_SQLITE: 'True',
      SQLITE_PATH: 'e2e.sqlite3',
      DEMO_MODE: 'True',
      DEBUG: 'True',
    },
  },
});
