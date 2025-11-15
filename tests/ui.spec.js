import { test, expect } from '@playwright/test';

test.describe('PR-000 UI Tests', () => {
  test('Basic UI load', async ({ page }) => {
    await page.goto('/ui/index.html');
    await expect(page.locator('body')).toBeVisible();
  });

  test('Keybar functionality', async ({ page }) => {
    await page.goto('/ui/index.html');
    await page.keyboard.press('H');
    await expect(page.locator('#help-panel')).toBeVisible();
  });

  test('H guidance display', async ({ page }) => {
    await page.goto('/ui/index.html');
    await page.keyboard.press('H');
    await expect(page.locator('#help-panel')).toContainText('guidance');
  });

  test('AJV green→red mutation', async ({ page }) => {
    await page.goto('/ui/index.html');
    await page.keyboard.press('E');  // Loads sample
    await expect(page.locator('#ajv-badge')).toHaveClass(/green/);

    await page.evaluate(() => {
      const envText = document.querySelector('#envelope-inspector').textContent;
      const env = JSON.parse(envText);
      env.status = 'oops';  // Mutate
      document.querySelector('#envelope-inspector').textContent = JSON.stringify(env, null, 2);
      // Trigger re-validate (add 'input' event listener in UI JS for real)
      document.querySelector('#envelope-inspector').dispatchEvent(new Event('input'));
    });
    await expect(page.locator('#ajv-badge')).toHaveClass(/red/);
  });
});
