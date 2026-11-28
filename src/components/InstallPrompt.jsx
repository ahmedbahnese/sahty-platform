import { useState } from 'react'
import { Download, Share, X } from 'lucide-react'
import { usePwaInstall, promptInstall } from '../lib/pwaInstall'

// "Install Sahty as an app" banner: a first-visit nudge only. Dismissing it
// hides the banner for the session — the header install button stays
// available, so the user can retry any time. Install state comes from the
// shared hook in lib/pwaInstall (single beforeinstallprompt capture).
export default function InstallPrompt() {
  const { installed, canPrompt, isIOS } = usePwaInstall()
  const [dismissed, setDismissed] = useState(
    () => sessionStorage.getItem('sahty-install-dismissed') === '1'
  )
  const [declined, setDeclined] = useState(false)

  if (installed || dismissed) return null

  const dismiss = () => {
    sessionStorage.setItem('sahty-install-dismissed', '1')
    setDismissed(true)
  }

  const install = async () => {
    const outcome = await promptInstall()
    if (outcome === 'accepted') return // installed=true hides the banner
    if (outcome === 'dismissed') setDeclined(true)
  }

  // The user declined from this banner: the native prompt is gone, so show
  // the retry note (the header button stays available for a later retry).
  if (declined && !canPrompt) {
    return (
      <div className="fixed bottom-4 right-4 left-4 z-50 mx-auto max-w-md rounded-2xl border border-amber-100 bg-white p-4 shadow-xl" dir="rtl">
        <div className="flex items-start gap-3">
          <div className="rounded-xl bg-amber-50 p-2 text-amber-600"><Download className="h-5 w-5" /></div>
          <div className="flex-1 text-sm">
            <p className="font-bold text-gray-900">رفضت التثبيت — لا مشكلة</p>
            <p className="mt-1 text-gray-600">يمكنك إعادة المحاولة في أي وقت من زر التثبيت في الأعلى.</p>
          </div>
          <button onClick={dismiss} aria-label="إغلاق"><X className="h-4 w-4 text-gray-400" /></button>
        </div>
      </div>
    )
  }

  // iOS Safari has no beforeinstallprompt: show manual instructions.
  if (!canPrompt && isIOS) {
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

  if (!canPrompt) return null

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
