import { expect, type Page } from '@playwright/test';

export class BookingPage {
  constructor(private readonly page: Page) {}

  readonly department = () => this.page.locator('#department');
  readonly doctor = () => this.page.locator('#doctor');
  readonly date = () => this.page.locator('#datePicker');
  readonly timeSlot = () => this.page.locator('#timeSlot');
  readonly description = () => this.page.locator('textarea[name="desc"]');
  readonly dateMessage = () => this.page.locator('#dateMessage');
  readonly confirm = () => this.page.getByRole('button', { name: 'Confirm Appointment' });

  async goto() {
    await this.page.goto('/patient_book_appointment/');
  }

  async choose(department: string, doctor: string, isoDate: string) {
    await this.department().selectOption({ label: department });
    // doctors load over AJAX once a department is picked
    await expect(this.doctor().locator('option', { hasText: doctor })).toHaveCount(1);
    await this.doctor().selectOption({ label: doctor });
    await this.date().fill(isoDate);
    await this.date().dispatchEvent('change');
  }

  async book(department: string, doctor: string, isoDate: string, slot: string, note = 'Booked by Playwright') {
    await this.choose(department, doctor, isoDate);
    await this.timeSlot().selectOption(slot);
    await this.description().fill(note);
    await this.confirm().click();
  }
}

/** yyyy-mm-dd for today + n days, in local time (matches the date input). */
export function isoDaysFromNow(n: number): string {
  const d = new Date();
  d.setDate(d.getDate() + n);
  const local = new Date(d.getTime() - d.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 10);
}
