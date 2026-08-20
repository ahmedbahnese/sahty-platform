import { test, expect } from '@playwright/test'

const viewports = [
  { name: 'phone', width: 390, height: 844 },
  { name: 'small-phone', width: 320, height: 568 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'desktop', width: 1440, height: 900 },
]

test.describe('المساعد الذكي العائم', () => {
  for (const viewport of viewports) {
    test(`${viewport.name}: يظهر مغلقاً داخل حدود الشاشة ويفتح دون تجاوز العرض`, async ({ browser }) => {
      const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, isMobile: viewport.width < 600, hasTouch: viewport.width < 800 })
      const page = await context.newPage()
      await page.goto('/', { waitUntil: 'networkidle' })
      const closed = page.getByTitle('المساعد الطبي الذكي')
      await expect(closed).toBeVisible()
      const closedBox = await closed.boundingBox()
      expect(closedBox).not.toBeNull()
      expect(closedBox.x).toBeGreaterThanOrEqual(0)
      expect(closedBox.y).toBeGreaterThanOrEqual(0)
      expect(closedBox.x + closedBox.width).toBeLessThanOrEqual(viewport.width)
      expect(closedBox.y + closedBox.height).toBeLessThanOrEqual(viewport.height)

      await closed.click()
      const panel = page.locator('div[style*="width: min(370px"]').first()
      await expect(panel).toBeVisible()
      const panelBox = await panel.boundingBox()
      expect(panelBox).not.toBeNull()
      expect(panelBox.width).toBeLessThanOrEqual(viewport.width * 0.96)
      expect(panelBox.x).toBeGreaterThanOrEqual(0)
      expect(panelBox.x + panelBox.width).toBeLessThanOrEqual(viewport.width)
      await context.close()
    })

    test(`${viewport.name}: يمكن سحب الأيقونة المغلقة دون فتحها`, async ({ browser }) => {
      const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, isMobile: viewport.width < 600, hasTouch: viewport.width < 800 })
      const page = await context.newPage()
      await page.goto('/', { waitUntil: 'networkidle' })
      const closed = page.getByTitle('المساعد الطبي الذكي')
      const before = await closed.boundingBox()
      expect(before).not.toBeNull()
      const startX = before.x + before.width / 2
      const startY = before.y + before.height / 2
      await page.mouse.move(startX, startY)
      await page.mouse.down()
      await page.mouse.move(Math.max(8, viewport.width / 2), Math.max(8, viewport.height / 2), { steps: 8 })
      await page.mouse.up()
      await page.waitForTimeout(100)
      const after = await closed.boundingBox()
      expect(after).not.toBeNull()
      expect(after.x).toBeGreaterThanOrEqual(0)
      expect(after.y).toBeGreaterThanOrEqual(0)
      expect(after.x + after.width).toBeLessThanOrEqual(viewport.width)
      expect(after.y + after.height).toBeLessThanOrEqual(viewport.height)
      await expect(page.getByTitle('المساعد الطبي الذكي')).toBeVisible()
      await context.close()
    })
  }
})
