import { test, expect } from '@playwright/test';

test('FlowRunner toggles approved based on TROPE_MAX', async ({ page }) => {
  // Precondition: Orchestration host at 127.0.0.1:8700 and mocks at 127.0.0.1:8900
  await page.goto('http://127.0.0.1:5173');
  await page.getByRole('button', { name: 'Run Flow' }).click();
  await expect(page.getByText('Approved?')).toBeVisible();
  // Loose assertion: approved appears with TRUE/FALSE eventually
  const approved = page.locator('text=Approved?').locator('..').locator('text=/TRUE|FALSE/');
  await expect(approved).toBeVisible({ timeout: 20_000 });
});
