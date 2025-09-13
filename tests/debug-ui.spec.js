import { test, expect } from '@playwright/test';

test.describe('Debug UI', () => {
  test('Check if validation button exists and can be clicked', async ({ page }) => {
    await page.goto('http://127.0.0.1:8700/agentpm/ui/');
    
    // Check if the button exists
    const button = page.locator('#btn-validate');
    await expect(button).toBeVisible();
    
    // Check if the button has an onclick handler
    const hasOnclick = await button.evaluate(el => el.onclick !== null);
    console.log('Button has onclick:', hasOnclick);
    
    // Check if the toggleValidation function exists
    const hasToggleFunction = await page.evaluate(() => typeof toggleValidation === 'function');
    console.log('toggleValidation function exists:', hasToggleFunction);
    
    // Check for JavaScript errors
    const errors = await page.evaluate(() => {
      const errors = [];
      window.addEventListener('error', e => errors.push(e.message));
      return errors;
    });
    console.log('JavaScript errors:', errors);
    
    // Try to manually attach the event listener
    await page.evaluate(() => {
      const btn = document.getElementById('btn-validate');
      if (btn) {
        btn.onclick = toggleValidation;
        console.log('Manually attached onclick handler');
      }
    });
    
    // Click the button
    await button.click();
    
    // Wait a bit and check if panel is visible
    await page.waitForTimeout(1000);
    
    // Check if validation panel exists
    const panel = page.locator('#validation-panel');
    const isVisible = await panel.isVisible();
    console.log('Panel visible:', isVisible);
    
    // Check the computed style
    const display = await panel.evaluate(el => getComputedStyle(el).display);
    console.log('Panel display style:', display);
    
    // Try to call the function directly
    await page.evaluate(() => {
      if (typeof toggleValidation === 'function') {
        toggleValidation();
      }
    });
    
    await page.waitForTimeout(1000);
    const isVisibleAfter = await panel.isVisible();
    console.log('Panel visible after direct call:', isVisibleAfter);
  });
});