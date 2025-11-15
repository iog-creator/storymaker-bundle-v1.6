import { test, expect } from '@playwright/test';

test.describe('Debug AJV', () => {
  test('Test AJV validation', async ({ page }) => {
    await page.goto('http://127.0.0.1:8700/agentpm/ui/');
    
    // Manually attach event listeners
    await page.evaluate(() => {
      const btn = document.getElementById('btn-validate');
      if (btn) {
        btn.onclick = toggleValidation;
      }
      const ajvBtn = document.getElementById('btn-validate-ajv');
      if (ajvBtn) {
        ajvBtn.onclick = validateAJV;
      }
    });
    
    // Open validation panel
    await page.click('#btn-validate');
    await expect(page.locator('#validation-panel')).toBeVisible();
    
    // Check if AJV is loaded
    const ajvLoaded = await page.evaluate(() => {
      try {
        return typeof Ajv !== 'undefined';
      } catch (e) {
        return false;
      }
    });
    console.log('AJV loaded:', ajvLoaded);
    
    // Check if schema is loaded
    const schemaLoaded = await page.evaluate(() => typeof schema !== 'undefined' && schema !== null);
    console.log('Schema loaded:', schemaLoaded);
    
    // Paste valid envelope
    const validEnvelope = JSON.stringify({
      "status": "ok",
      "data": {"test": "data"},
      "error": null,
      "meta": {
        "run_id": "20250913T120000Z-test01",
        "timestamp": "2025-09-13T12:00:00.000Z",
        "source": "test",
        "schema_version": "1.1.0-pr000"
      }
    });
    
    await page.fill('#validation-input', validEnvelope);
    
    // Click AJV validation
    await page.click('#btn-validate-ajv');
    
    // Wait a bit
    await page.waitForTimeout(1000);
    
    // Check badge state
    const badgeClass = await page.locator('#validation-badge').getAttribute('class');
    const badgeText = await page.locator('#validation-badge').textContent();
    console.log('Badge class:', badgeClass);
    console.log('Badge text:', badgeText);
    
    // Check result
    const resultText = await page.locator('#validation-result').textContent();
    console.log('Result text:', resultText);
  });
});
