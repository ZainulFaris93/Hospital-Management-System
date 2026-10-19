import { expect, test } from '@playwright/test';
import { BookingPage, isoDaysFromNow } from '../pages/BookingPage';
import { LoginPage } from '../pages/LoginPage';

/**
 * The full journey across all three roles:
 * patient books → admin approves → doctor marks consulted → patient sees it in history.
 */
test.describe.serial('Appointment lifecycle', () => {
  const date = isoDaysFromNow(14);
  const slot = '10:00 AM - 11:00 AM';

  test('patient books an appointment', async ({ page }) => {
    await new LoginPage(page).login('ananya', 'Patient@123');
    const booking = new BookingPage(page);
    await booking.goto();
    await booking.book('Neurology', 'Arjun', date, slot);
    await expect(page.getByText('Appointment booked successfully!')).toBeVisible();
  });

  test('the booked slot is disabled for the next patient', async ({ page }) => {
    await new LoginPage(page).loginAsDemo('Patient');
    const booking = new BookingPage(page);
    await booking.goto();
    await booking.choose('Neurology', 'Arjun', date);
    await expect(booking.timeSlot().locator(`option[value="${slot}"]`)).toBeDisabled();
  });

  test('admin approves the pending appointment', async ({ page }) => {
    await new LoginPage(page).loginAsDemo('Admin');
    await page.goto('/admin_view_appointments/');
    const row = page.locator('tr', { hasText: 'Ananya' }).filter({ hasText: slot });
    await expect(row).toHaveCount(1);
    page.once('dialog', (dialog) => dialog.accept()); // "Approve this appointment?"
    await row.locator('.approve-btn').click();
    await expect(row).toHaveCount(0); // leaves the pending list
  });

  test('doctor marks it as consulted', async ({ page }) => {
    await new LoginPage(page).login('dr.arjun', 'Doctor@123');
    await page.goto('/doctor_appointments/');
    const row = page.locator('#appointments-body tr', { hasText: 'Ananya' }).filter({ hasText: slot });
    await expect(row).toHaveCount(1);
    await row.locator('.consult-btn').click();
    await expect(row).toHaveCount(0);
  });

  test('patient sees the consultation in their history', async ({ page }) => {
    await new LoginPage(page).login('ananya', 'Patient@123');
    await page.goto('/patient_appointment_history/');
    const row = page.locator('tr', { hasText: slot }).filter({ hasText: 'Arjun' });
    await expect(row.locator('.status-badge')).toHaveText('Consulted');
  });
});

test.describe('Booking rules', () => {
  test('warns when the patient already has an appointment that day', async ({ page }) => {
    // seeded data: rahul already sees Dr. Meera (Cardiology) today
    await new LoginPage(page).loginAsDemo('Patient');
    const booking = new BookingPage(page);
    await booking.goto();
    await booking.choose('Cardiology', 'Meera', isoDaysFromNow(0));
    await expect(booking.dateMessage()).toBeVisible();
    await expect(booking.dateMessage()).toContainText('You already booked for this date');
  });

  test('past dates cannot be picked', async ({ page }) => {
    await new LoginPage(page).loginAsDemo('Patient');
    const booking = new BookingPage(page);
    await booking.goto();
    await expect(booking.date()).toHaveAttribute('min', isoDaysFromNow(0));
  });
});
