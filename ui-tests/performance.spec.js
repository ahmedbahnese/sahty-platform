import { test, expect } from '@playwright/test'

const ROUTES = ['/', '/doctors', '/hospitals', '/blood-bank']

async function collectPerformance(page) {
  return page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0]
    const paints = Object.fromEntries(
      performance.getEntriesByType('paint').map(entry => [entry.name, entry.startTime]),
    )
    const resources = performance.getEntriesByType('resource').map(resource => ({
      name: resource.name,
      initiatorType: resource.initiatorType,
      transferSize: resource.transferSize || 0,
      encodedBodySize: resource.encodedBodySize || 0,
      duration: resource.duration || 0,
    }))

    return {
      domContentLoaded: navigation?.domContentLoadedEventEnd || 0,
      load: navigation?.loadEventEnd || 0,
      response: navigation?.responseStart || 0,
      firstContentfulPaint: paints['first-contentful-paint'] || 0,
      resources,
      totalTransferSize: resources.reduce((sum, resource) => sum + resource.transferSize, 0),
      totalEncodedSize: resources.reduce((sum, resource) => sum + resource.encodedBodySize, 0),
      javascriptBytes: resources
        .filter(resource => resource.initiatorType === 'script' || /\.js(?:\?|$)/.test(resource.name))
        .reduce((sum, resource) => sum + resource.encodedBodySize, 0),
      stylesheetBytes: resources
        .filter(resource => resource.initiatorType === 'link' || /\.css(?:\?|$)/.test(resource.name))
        .reduce((sum, resource) => sum + resource.encodedBodySize, 0),
    }
  })
}

async function loadAndMeasure(page, route) {
  await page.goto(route, { waitUntil: 'load' })
  await expect(page.locator('#root')).toBeVisible()
  await page.waitForTimeout(250)
  return collectPerformance(page)
}

test.describe('Sehaty performance budget', () => {
  test('loads key public routes within the navigation budget', async ({ page }) => {
    for (const route of ROUTES) {
      const metrics = await loadAndMeasure(page, route)
      expect(metrics.response, `${route}: server response`).toBeLessThan(1500)
      expect(metrics.domContentLoaded, `${route}: DOMContentLoaded`).toBeLessThan(3500)
      expect(metrics.load, `${route}: load event`).toBeLessThan(5000)
      expect(metrics.firstContentfulPaint, `${route}: FCP`).toBeGreaterThan(0)
      expect(metrics.firstContentfulPaint, `${route}: FCP`).toBeLessThan(3000)
    }
  })

  test('stays within the frontend resource budget', async ({ page }) => {
    const metrics = await loadAndMeasure(page, '/')
    expect(metrics.javascriptBytes, 'compressed JavaScript payload').toBeLessThan(1_900_000)
    expect(metrics.stylesheetBytes, 'compressed stylesheet payload').toBeLessThan(400_000)
    expect(metrics.totalEncodedSize, 'total encoded resource payload').toBeLessThan(2_500_000)
  })

  test('responds quickly to mobile menu interaction', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto('/', { waitUntil: 'load' })
    await expect(page.getByRole('heading', { name: 'صحتك في أمان' })).toBeVisible()

    const menuButton = page.getByRole('button', { name: 'فتح القائمة' })
    const start = Date.now()
    await menuButton.click()
    await expect(page.getByRole('button', { name: 'إغلاق القائمة' })).toBeVisible()
    const interactionTime = Date.now() - start

    expect(interactionTime, 'mobile menu response time').toBeLessThan(500)
  })

  test('does not report failed document resources on the public home route', async ({ page }) => {
    const failedRequests = []
    page.on('requestfailed', request => {
      if (request.resourceType() !== 'fetch' && request.resourceType() !== 'xhr') {
        failedRequests.push(`${request.method()} ${request.url()}`)
      }
    })

    await loadAndMeasure(page, '/')
    expect(failedRequests, failedRequests.join('\n')).toEqual([])
  })
})
