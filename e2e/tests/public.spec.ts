import { expect, test } from '@playwright/test';

test.describe('Public pages', () => {
  test('home page loads with navigation', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Welcome to StarCare', level: 1 })).toBeVisible();
    await expect(page.locator('a.navbar-brand')).toContainText('StarCare');
  });

  for (const path of ['/about', '/contact', '/patient_signup', '/doctor_signup']) {
    test(`${path} responds without errors`, async ({ page }) => {
      const response = await page.goto(path);
      expect(response?.status()).toBe(200);
    });
  }

  test('static assets are served', async ({ request }) => {
    const response = await request.get('/static/images/hospital_logo.svg');
    expect(response.status()).toBe(200);
  });
});
