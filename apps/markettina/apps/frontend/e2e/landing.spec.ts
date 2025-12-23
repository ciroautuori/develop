import { test, expect } from '@playwright/test';

/**
 * MARKETTINA - Landing Page E2E Tests
 */
test.describe('Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display hero section with MARKETTINA branding', async ({ page }) => {
    // Verify main heading
    await expect(page.locator('h1')).toContainText(/MARKETTINA|Marketing|AI/i);

    // Verify CTA buttons exist
    await expect(page.getByRole('link', { name: /inizia|prova|scopri/i })).toBeVisible();
  });

  test('should display Token Calculator', async ({ page }) => {
    // Scroll to Token Calculator section
    const calculator = page.locator('text=Calcola i tuoi Token').first();
    await calculator.scrollIntoViewIfNeeded();

    // Verify sliders exist
    await expect(page.locator('input[type="range"]').first()).toBeVisible();
  });

  test('should navigate to admin login', async ({ page }) => {
    // Click on login/admin link
    await page.goto('/admin/login');

    // Verify login form
    await expect(page.locator('input[type="email"], input[type="text"]').first()).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('should load legal pages', async ({ page }) => {
    // Privacy Policy
    await page.goto('/privacy');
    await expect(page.locator('h1')).toContainText(/privacy|policy/i);

    // Terms of Service
    await page.goto('/terms');
    await expect(page.locator('h1')).toContainText(/terms|condizioni|servizio/i);
  });
});
