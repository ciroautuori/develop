import { test, expect, Page } from '@playwright/test';

/**
 * MARKETTINA - Admin Backoffice E2E Tests
 */

// Helper: Login as admin
async function adminLogin(page: Page, email = 'admin@markettina.it', password = 'admin123') {
  await page.goto('/admin/login');
  await page.fill('input[type="email"], input[name="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');

  // Wait for redirect to admin dashboard
  await page.waitForURL(/\/admin(?!\/login)/);
}

test.describe('Admin Login', () => {
  test('should display login form', async ({ page }) => {
    await page.goto('/admin/login');

    await expect(page.locator('input[type="email"], input[name="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show error on invalid credentials', async ({ page }) => {
    await page.goto('/admin/login');

    await page.fill('input[type="email"], input[name="email"]', 'wrong@email.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    // Expect error message or toast
    await expect(page.locator('text=/errore|error|invalid|credenziali/i')).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Admin Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Set mock token for testing (skip real auth)
    await page.goto('/admin/login');
    await page.evaluate(() => {
      localStorage.setItem('admin_token', 'test_token_for_e2e');
    });
  });

  test('should display dashboard after login', async ({ page }) => {
    await page.goto('/admin');

    // Verify dashboard elements
    await expect(page.locator('h1, h2').first()).toBeVisible();
  });

  test('should navigate to AI Marketing', async ({ page }) => {
    await page.goto('/admin/ai-marketing');

    // Verify AI Marketing page loaded
    await expect(page.locator('text=/marketing|content|ai|brand/i').first()).toBeVisible();
  });

  test('should navigate to Settings Hub', async ({ page }) => {
    await page.goto('/admin/settings');

    // Verify Settings Hub tabs exist
    await expect(page.locator('button:has-text("Utenti"), button:has-text("Users")')).toBeVisible();
    await expect(page.locator('button:has-text("Profilo"), button:has-text("Profile")')).toBeVisible();
    await expect(page.locator('button:has-text("Integrazioni"), button:has-text("Integrations")')).toBeVisible();
    await expect(page.locator('button:has-text("Sistema"), button:has-text("System")')).toBeVisible();
    await expect(page.locator('button:has-text("Sito"), button:has-text("Site")')).toBeVisible();
    await expect(page.locator('button:has-text("Database")')).toBeVisible();
    await expect(page.locator('button:has-text("Email")')).toBeVisible();
  });

  test('should switch tabs in Settings Hub', async ({ page }) => {
    await page.goto('/admin/settings');

    // Click on Profile tab
    await page.click('button:has-text("Profilo"), button:has-text("Profile")');
    await expect(page.locator('text=/informazioni personali|personal info/i')).toBeVisible();

    // Click on Site tab
    await page.click('button:has-text("Sito"), button:has-text("Site")');
    await expect(page.locator('text=/nome sito|site name/i')).toBeVisible();

    // Click on Email tab
    await page.click('button:has-text("Email")');
    await expect(page.locator('text=/smtp|email|configurazione/i')).toBeVisible();
  });

  test('should navigate to Finance Hub', async ({ page }) => {
    await page.goto('/admin/finance-hub');

    // Verify Finance elements
    await expect(page.locator('text=/finance|fatturato|revenue|token/i').first()).toBeVisible();
  });

  test('should navigate to Business Hub (CRM)', async ({ page }) => {
    await page.goto('/admin/business');

    // Verify CRM elements
    await expect(page.locator('text=/business|clienti|customer|crm/i').first()).toBeVisible();
  });

  test('should navigate to Editorial Calendar', async ({ page }) => {
    await page.goto('/admin/calendario-editoriale');

    // Verify Calendar elements
    await expect(page.locator('text=/calendario|calendar|post/i').first()).toBeVisible();
  });

  test('should navigate to User Management', async ({ page }) => {
    await page.goto('/admin/utenti');

    // Verify User Management elements
    await expect(page.locator('text=/utenti|users|gestione/i').first()).toBeVisible();
  });
});
