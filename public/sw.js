const CACHE_NAME = 'sahty-shell-v2'
const OFFLINE_URL = '/offline.html'
const CORE_ASSETS = ['/', OFFLINE_URL]

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(CORE_ASSETS)))
  self.skipWaiting()
})

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))))
  )
  self.clients.claim()
})

self.addEventListener('fetch', event => {
  const request = event.request
  if (request.method !== 'GET' || !request.url.startsWith(self.location.origin)) return

  const isNavigation = request.mode === 'navigate'
  const isStaticAsset = ['script', 'style', 'image', 'font'].includes(request.destination)

  if (isNavigation) {
    event.respondWith(
      fetch(request)
        .then(response => {
          const copy = response.clone()
          caches.open(CACHE_NAME).then(cache => cache.put(request, copy))
          return response
        })
        .catch(() => caches.match(request).then(cached => cached || caches.match('/') || caches.match(OFFLINE_URL)))
    )
    return
  }

  if (isStaticAsset) {
    event.respondWith(
      caches.match(request).then(cached => {
        const network = fetch(request).then(response => {
          if (response.ok) caches.open(CACHE_NAME).then(cache => cache.put(request, response.clone()))
          return response
        })
        return cached || network
      })
    )
  }
})
