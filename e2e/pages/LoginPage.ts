import { expect, type Page } from '@playwright/test';

export type Role = 'Admin' | 'Doctor' | 'Patient';

export const HOME_FOR: Record<Role, RegExp> = {
  Admin: /\/admin_home\/$/,
  Doctor: /\/doctor_home\/$/,
  Patient: /\/patient_home\/$/,
};

export class LoginPage {
  constructor(private readonly page: Page) {}

  readonly username = () => this.page.locator('input[name="uname"]');
  readonly password = () => this.page.locator('input[name="pass"]');
  readonly submit = () => this.page.locator('.login-btn');
  readonly demoRole = (role: Role) => this.page.locator('.demo-role', { hasText: role });

  async goto() {
    await this.page.goto('/login_page');
  }

  async login(username: string, password: string) {
    await this.goto();
    await this.username().fill(username);
    await this.password().fill(password);
    await this.submit().click();
  }

  /** Uses the one-click demo buttons, the same way a visitor would. */
  async loginAsDemo(role: Role) {
    await this.goto();
    await this.demoRole(role).click();
    await this.submit().click();
    await expect(this.page).toHaveURL(HOME_FOR[role]);
  }
}
