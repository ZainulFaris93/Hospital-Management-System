import { expect, test } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';

test.describe('Role-based access control', () => {
  test('visitors who are not logged in are sent to login', async ({ page }) => {
    for (const path of ['/admin_home/', '/doctor_home/', '/patient_home/']) {
      await page.goto(path);
      await expect(page).toHaveURL(/login_page/);
    }
  });

  test('a patient cannot open admin or doctor pages', async ({ page }) => {
    await new LoginPage(page).loginAsDemo('Patient');
    for (const path of ['/admin_home/', '/admin_view_patient/', '/doctor_appointments/']) {
      await page.goto(path);
      await expect(page).toHaveURL(/\/patient_home\/$/);
    }
  });

  test('a doctor cannot open admin pages', async ({ page }) => {
    await new LoginPage(page).loginAsDemo('Doctor');
    await page.goto('/admin_view_appointments/');
    await expect(page).toHaveURL(/\/doctor_home\/$/);
  });

  test('admin APIs reject other roles with 403', async ({ page }) => {
    await new LoginPage(page).loginAsDemo('Patient');
    const response = await page.request.get('/approval-counts/');
    expect(response.status()).toBe(403);
  });
});
