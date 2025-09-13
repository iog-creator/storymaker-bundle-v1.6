import { test, expect } from '@playwright/test';

test.describe('Debug UI Tests', () => {
  test('Basic UI load with full URL', async ({ page }) => {
    await page.goto('http://127.0.0.1:5173/ui/index.html');
    await expect(page.locator('body')).toBeVisible();
  });
});
