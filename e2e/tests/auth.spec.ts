import { expect, test } from '@playwright/test';
import { HOME_FOR, LoginPage, type Role } from '../pages/LoginPage';

test.describe('Login', () => {
  for (const role of ['Admin', 'Doctor', 'Patient'] as Role[]) {
    test(`${role} can log in with the demo button and lands on their dashboard`, async ({ page }) => {
      const login = new LoginPage(page);
      await login.loginAsDemo(role);
      await expect(page).toHaveURL(HOME_FOR[role]);
    });
  }

  test('demo button fills in the credentials', async ({ page }) => {
    const login = new LoginPage(page);
    await login.goto();
    await login.demoRole('Doctor').click();
    await expect(login.username()).toHaveValue('dr.meera');
    await expect(login.password()).toHaveValue('Doctor@123');
  });

  test('wrong password shows an error and stays on login', async ({ page }) => {
    const login = new LoginPage(page);
    await login.login('rahul', 'wrong-password');
    await expect(page.getByText('Invalid username or password')).toBeVisible();
    await expect(page).toHaveURL(/login_page/);
  });

  test('logging out blocks the dashboard again', async ({ page }) => {
    const login = new LoginPage(page);
    await login.loginAsDemo('Patient');
    await page.goto('/logout_function');
    await page.goto('/patient_home/');
    await expect(page).toHaveURL(/login_page/);
  });
});
