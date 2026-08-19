import { test, expect } from '@playwright/test'

async function openHome(page) {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'صحتك في أمان' })).toBeVisible()
}

async function expectNoHorizontalOverflow(page) {
  const hasOverflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)
  expect(hasOverflow, `horizontal overflow at ${await page.evaluate(() => window.innerWidth)}px`).toBe(false)
}

test.describe('Sehaty responsive shell', () => {
  test('renders without horizontal overflow at every target viewport', async ({ page }) => {
    await openHome(page)
    await expectNoHorizontalOverflow(page)

    for (const width of [375, 768, 1024, 1440]) {
      await page.setViewportSize({ width, height: 900 })
      await expectNoHorizontalOverflow(page)
    }
  })

  test('shows public desktop navigation on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await openHome(page)

    await expect(page.locator('nav a:visible', { hasText: 'الأطباء' }).first()).toBeVisible()
    await expect(page.getByRole('button', { name: 'الخدمات الطبية' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'فتح القائمة' })).toBeHidden()
  })

  test('opens and closes the mobile navigation drawer', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await openHome(page)

    const menuButton = page.getByRole('button', { name: 'فتح القائمة' })
    await expect(menuButton).toBeVisible()
    await menuButton.click()
    await expect(page.getByRole('button', { name: 'إغلاق القائمة' })).toBeVisible()
    await expect(page.locator('nav a:visible', { hasText: 'الأطباء' }).first()).toBeVisible()

    await page.getByRole('button', { name: 'إغلاق القائمة' }).first().click()
    await expect(page.getByRole('button', { name: 'فتح القائمة' })).toBeVisible()
  })

  test('keeps the contact form usable on a narrow phone viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await openHome(page)

    const form = page.locator('form').last()
    await expect(form).toBeVisible()
    const formBox = await form.boundingBox()
    expect(formBox).not.toBeNull()
    expect(formBox.x).toBeGreaterThanOrEqual(0)
    expect(formBox.x + formBox.width).toBeLessThanOrEqual(375)

    for (const field of await form.locator('input, textarea').all()) {
      const box = await field.boundingBox()
      expect(box).not.toBeNull()
      expect(box.x).toBeGreaterThanOrEqual(0)
      expect(box.x + box.width).toBeLessThanOrEqual(375)
    }
  })

  test('routes the primary CTA to registration', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 900 })
    await openHome(page)

    await page.getByRole('link', { name: 'ابدأ مجاناً الآن' }).first().click()
    await expect(page).toHaveURL(/\/register$/)
    await expect(page.getByRole('heading', { name: /إنشاء حساب|حساب جديد/ })).toBeVisible()
  })
})
