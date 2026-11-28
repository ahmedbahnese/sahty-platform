import { useEffect, useState } from 'react'
import { Download, Share, X } from 'lucide-react'
import { getInstallPromptEvent, isIOS, isStandalone } from '../lib/push'

// "Install Sahty as an app" banner: shows when the browser offers installation
// (beforeinstallprompt) and the app is not installed yet. On iOS it shows the
// manual "Add to Home Screen" instructions instead.
export default function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null)
  const [visible, setVisible] = useState(false)
  const [installed, setInstalled] = useState(isStandalone())
  const [dismissed, setDismissed] = useState(
    () => sessionStorage.getItem('sahty-install-dismissed') === '1'
  )

  useEffect(() => {
    const onPrompt = event => {
      event.preventDefault()
      window.__sahtyInstallPrompt = event
      setDeferredPrompt(event)
      if (!isStandalone() && sessionStorage.getItem('sahty-install-dismissed') !== '1') {
        setVisible(true)
      }
    }
    const onInstalled = () => {
      setInstalled(true)
      setVisible(false)
      window.__sahtyInstallPrompt = null
      setDeferredPrompt(null)
    }
    window.addEventListener('beforeinstallprompt', onPrompt)
    window.addEventListener('appinstalled', onInstalled)
    const existing = getInstallPromptEvent()
    if (existing) {
      setDeferredPrompt(existing)
      if (!isStandalone() && sessionStorage.getItem('sahty-install-dismissed') !== '1') {
        setVisible(true)
      }
    }
    return () => {
      window.removeEventListener('beforeinstallprompt', onPrompt)
      window.removeEventListener('appinstalled', onInstalled)
    }
  }, [])

  if (installed || dismissed) return null

  const dismiss = () => {
    sessionStorage.setItem('sahty-install-dismissed', '1')
    setDismissed(true)
  }

  const install = async () => {
    const promptEvent = deferredPrompt || getInstallPromptEvent()
    if (!promptEvent) return
    promptEvent.prompt()
    const choice = await promptEvent.userChoice.catch(() => null)
    if (choice && choice.outcome === 'accepted') {
      setVisible(false)
    }
    window.__sahtyInstallPrompt = null
    setDeferredPrompt(null)
  }

  // iOS Safari has no beforeinstallprompt: show manual instructions.
  if (!deferredPrompt && isIOS() && !isStandalone()) {
    return (
      <div className="fixed bottom-4 right-4 left-4 z-50 mx-auto max-w-md rounded-2xl border border-blue-100 bg-white p-4 shadow-xl" dir="rtl">
        <div className="flex items-start gap-3">
          <div className="rounded-xl bg-blue-50 p-2 text-blue-600"><Download className="h-5 w-5" /></div>
          <div className="flex-1 text-sm">
            <p className="font-bold text-gray-900">ثبّت تطبيق صحتي على جهازك</p>
            <p className="mt-1 text-gray-600">من زر المشاركة <Share className="inline h-4 w-4" /> اختر «إضافة إلى الشاشة الرئيسية» ليظهر التطبيق على شاشتك ويعمل بدون إنترنت.</p>
          </div>
          <button onClick={dismiss} aria-label="إغلاق"><X className="h-4 w-4 text-gray-400" /></button>
        </div>
      </div>
    )
  }

  if (!visible || !deferredPrompt) return null

  return (
    <div className="fixed bottom-4 right-4 left-4 z-50 mx-auto max-w-md rounded-2xl border border-blue-100 bg-white p-4 shadow-xl" dir="rtl">
      <div className="flex items-start gap-3">
        <div className="rounded-xl bg-blue-50 p-2 text-blue-600"><Download className="h-5 w-5" /></div>
        <div className="flex-1 text-sm">
          <p className="font-bold text-gray-900">ثبّت تطبيق صحتي على جهازك</p>
          <p className="mt-1 text-gray-600">يظهر على شاشتك الرئيسية ويعمل بدون إنترنت، مع وصول سريع للطوارئ والدليل الطبي.</p>
          <div className="mt-3 flex gap-2">
            <button onClick={install} className="rounded-xl bg-blue-600 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-700">تثبيت التطبيق</button>
            <button onClick={dismiss} className="rounded-xl border border-gray-200 px-4 py-2 text-xs text-gray-600 hover:bg-gray-50">لاحقاً</button>
          </div>
        </div>
        <button onClick={dismiss} aria-label="إغلاق"><X className="h-4 w-4 text-gray-400" /></button>
      </div>
    </div>
  )
}
