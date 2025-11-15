import { test, expect } from '@playwright/test';

test.describe('PR-002 UI Gate Tests', () => {
  test('Valid envelope shows green badge (AJV)', async ({ page }) => {
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
      const serverBtn = document.getElementById('btn-validate-server');
      if (serverBtn) {
        serverBtn.onclick = validateServer;
      }
    });
    
    // Open validation panel
    await page.click('#btn-validate');
    await expect(page.locator('#validation-panel')).toBeVisible();
    
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
    await page.click('#btn-validate-ajv');
    
    // Check badge is green
    await expect(page.locator('#validation-badge')).toHaveClass(/valid/);
    await expect(page.locator('#validation-badge')).toContainText('Valid');
  });

  test('Invalid envelope shows red badge (AJV)', async ({ page }) => {
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
      const serverBtn = document.getElementById('btn-validate-server');
      if (serverBtn) {
        serverBtn.onclick = validateServer;
      }
    });
    
    // Open validation panel
    await page.click('#btn-validate');
    await expect(page.locator('#validation-panel')).toBeVisible();
    
    // Paste invalid envelope with extra property
    const invalidEnvelope = JSON.stringify({
      "status": "ok",
      "data": {"test": "data"},
      "error": null,
      "extra": "not allowed",
      "meta": {
        "run_id": "20250913T120000Z-test02",
        "timestamp": "2025-09-13T12:00:00.000Z",
        "source": "test",
        "schema_version": "1.1.0-pr000"
      }
    });
    
    await page.fill('#validation-input', invalidEnvelope);
    await page.click('#btn-validate-ajv');
    
    // Check badge is red
    await expect(page.locator('#validation-badge')).toHaveClass(/invalid/);
    await expect(page.locator('#validation-badge')).toContainText('Invalid');
  });

  test('Server validation archives invalid payload', async ({ page }) => {
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
      const serverBtn = document.getElementById('btn-validate-server');
      if (serverBtn) {
        serverBtn.onclick = validateServer;
      }
    });
    
    // Open validation panel
    await page.click('#btn-validate');
    await expect(page.locator('#validation-panel')).toBeVisible();
    
    // Paste invalid envelope
    const invalidEnvelope = JSON.stringify({
      "status": "ok",
      "data": {"test": "data"},
      "error": null,
      "extra": "not allowed",
      "meta": {
        "run_id": "20250913T120000Z-test03",
        "timestamp": "2025-09-13T12:00:00.000Z",
        "source": "test",
        "schema_version": "1.1.0-pr000"
      }
    });
    
    await page.fill('#validation-input', invalidEnvelope);
    await page.click('#btn-validate-server');
    
    // Check badge is red
    await expect(page.locator('#validation-badge')).toHaveClass(/invalid/);
    await expect(page.locator('#validation-badge')).toContainText('Invalid');
    
    // Check result shows run_id
    await expect(page.locator('#validation-result')).toContainText('run_id:');
  });

  test('Error status with data field shows red badge', async ({ page }) => {
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
      const serverBtn = document.getElementById('btn-validate-server');
      if (serverBtn) {
        serverBtn.onclick = validateServer;
      }
    });
    
    // Open validation panel
    await page.click('#btn-validate');
    await expect(page.locator('#validation-panel')).toBeVisible();
    
    // Paste invalid envelope (error status with data field)
    const invalidEnvelope = JSON.stringify({
      "status": "error",
      "data": {"should": "be null"},
      "error": {"code": "TEST", "message": "test"},
      "meta": {
        "run_id": "20250913T120000Z-test04",
        "timestamp": "2025-09-13T12:00:00.000Z",
        "source": "test",
        "schema_version": "1.1.0-pr000"
      }
    });
    
    await page.fill('#validation-input', invalidEnvelope);
    await page.click('#btn-validate-ajv');
    
    // Check badge is red
    await expect(page.locator('#validation-badge')).toHaveClass(/invalid/);
    await expect(page.locator('#validation-badge')).toContainText('Invalid');
  });

  test('Invalid JSON shows error', async ({ page }) => {
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
      const serverBtn = document.getElementById('btn-validate-server');
      if (serverBtn) {
        serverBtn.onclick = validateServer;
      }
    });
    
    // Open validation panel
    await page.click('#btn-validate');
    await expect(page.locator('#validation-panel')).toBeVisible();
    
    // Paste invalid JSON
    await page.fill('#validation-input', '{ invalid json }');
    await page.click('#btn-validate-ajv');
    
    // Check badge is red
    await expect(page.locator('#validation-badge')).toHaveClass(/invalid/);
    await expect(page.locator('#validation-badge')).toContainText('Invalid');
    
    // Check result shows JSON error
    await expect(page.locator('#validation-result')).toContainText('Invalid JSON');
  });
});
