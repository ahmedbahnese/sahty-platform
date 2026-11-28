/* Sahty service worker: offline app shell + emergency push notifications. */
const CACHE = 'sahty-v1'
const APP_SHELL = ['/', '/index.html', '/icons/icon.svg', '/icons/emergency.svg', '/manifest.webmanifest']

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
  )
})

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  )
})

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url)
  if (event.request.method !== 'GET' || url.origin !== self.location.origin) return

  // API data: network first, cache fallback when offline.
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const copy = response.clone()
          caches.open(CACHE).then(cache => cache.put(event.request, copy))
          return response
        })
        .catch(() => caches.match(event.request))
    )
    return
  }

  // Navigation: network first, offline falls back to the cached app shell.
  if (event.request.mode === 'navigate') {
    event.respondWith(fetch(event.request).catch(() => caches.match('/index.html')))
    return
  }

  // Static assets: cache first.
  event.respondWith(
    caches.match(event.request).then(hit => {
      if (hit) return hit
      return fetch(event.request).then(response => {
        const copy = response.clone()
        caches.open(CACHE).then(cache => cache.put(event.request, copy))
        return response
      })
    })
  )
})

// Emergency push notification from the server.
self.addEventListener('push', event => {
  let data = {}
  try {
    data = event.data ? event.data.json() : {}
  } catch (_) {
    data = { body: event.data ? event.data.text() : '' }
  }
  const title = data.title || 'تنبيه طوارئ — صحتي'
  const options = {
    body: data.body || 'يوجد تنبيه طوارئ جديد. اضغط لفتح صفحة الطوارئ.',
    icon: '/icons/emergency.svg',
    badge: '/icons/emergency.svg',
    tag: data.tag || 'sahty-emergency',
    data: { url: data.url || '/emergency' },
  }
  event.waitUntil(self.registration.showNotification(title, options))
})

self.addEventListener('notificationclick', event => {
  event.notification.close()
  const url = (event.notification.data && event.notification.data.url) || '/emergency'
  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(list => {
      for (const client of list) {
        if ('focus' in client) {
          client.navigate(url)
          return client.focus()
        }
      }
      if (clients.openWindow) return clients.openWindow(url)
    })
  )
})
