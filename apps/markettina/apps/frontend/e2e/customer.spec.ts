import { test, expect } from '@playwright/test';

/**
 * MARKETTINA - Customer Dashboard E2E Tests
 */

test.describe('Customer Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Set mock token for testing
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.setItem('admin_token', 'test_token_for_e2e');
      localStorage.setItem('token', 'test_token_for_e2e');
    });
  });

  test('should display dashboard with MARKETTINA branding', async ({ page }) => {
    await page.goto('/dashboard');

    // Verify MARKETTINA branding (updated from Enterprise Framework)
    await expect(page.locator('text=/MARKETTINA/i').first()).toBeVisible();
  });

  test('should display dashboard overview metrics', async ({ page }) => {
    await page.goto('/dashboard');

    // Verify metric cards exist
    await expect(page.locator('text=/utenti|users/i').first()).toBeVisible();
  });

  test('should have working sidebar navigation', async ({ page }) => {
    await page.goto('/dashboard');

    // Verify sidebar links
    await expect(page.locator('a[href="/dashboard/portfolio"], a:has-text("Portfolio")')).toBeVisible();
    await expect(page.locator('a[href="/dashboard/bookings"], a:has-text("Prenotazioni")')).toBeVisible();
    await expect(page.locator('a[href="/dashboard/support"], a:has-text("Supporto")')).toBeVisible();
  });

  test('should navigate to Portfolio', async ({ page }) => {
    await page.goto('/dashboard/portfolio');

    // Verify page loaded (might show error if API not connected - that's ok)
    await expect(page).toHaveURL(/\/dashboard\/portfolio/);
  });

  test('should navigate to Support', async ({ page }) => {
    await page.goto('/dashboard/support');

    await expect(page).toHaveURL(/\/dashboard\/support/);
  });
});
