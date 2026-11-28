// Shared PWA / Web Push helpers for Sahty.

// VAPID public key (public by design — it is sent to every browser that
// subscribes). The matching private key lives ONLY in the Vercel env var
// VAPID_PRIVATE_KEY; it is never committed to the repo.
export const VAPID_PUBLIC_KEY =
  'BCofZyG3KQggHe6r-VUk9jmhjm8zNB3dPpO-TpvCQ8qATnAbBTXIjewQP8rYy1wo4atF1SSpOi_cxJfqB4Ja_7M'

export function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) outputArray[i] = rawData.charCodeAt(i)
  return outputArray
}

export function isStandalone() {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true
  )
}

export function isIOS() {
  return /iphone|ipad|ipod/i.test(window.navigator.userAgent)
}

export function getInstallPromptEvent() {
  return window.__sahtyInstallPrompt || null
}

export async function getServiceWorkerRegistration() {
  if (!('serviceWorker' in navigator)) return null
  try {
    return await navigator.serviceWorker.ready
  } catch (_) {
    return null
  }
}

// Subscribe this device for emergency push notifications and store the
// subscription on the server. Returns { ok, reason }.
export async function subscribeEmergencyPush() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    return { ok: false, reason: 'المتصفح لا يدعم إشعارات الدفع' }
  }
  if (Notification.permission !== 'granted') {
    return { ok: false, reason: 'لم يتم منح إذن الإشعارات' }
  }
  const registration = await getServiceWorkerRegistration()
  if (!registration) return { ok: false, reason: 'تعذر تسجيل خدمة التطبيق' }
  try {
    let subscription = await registration.pushManager.getSubscription()
    if (!subscription) {
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      })
    }
    const token = localStorage.getItem('token')
    const response = await fetch('/api/notifications/push-subscribe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ subscription }),
    })
    if (!response.ok) return { ok: false, reason: 'تعذر حفظ الاشتراك على الخادم' }
    return { ok: true }
  } catch (error) {
    return { ok: false, reason: 'تعذر تفعيل إشعارات الدفع على هذا الجهاز' }
  }
}
