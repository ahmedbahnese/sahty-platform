import { useState } from 'react'
import { X, Download, Check, Share } from 'lucide-react'
import { usePwaInstall, promptInstall, getBrowserFamily } from '../lib/pwaInstall'

// Install modal, opened from the persistent header install button.
// Capability detection decides the branch first; the browser family is used
// only to pick the right manual-instructions text. The modal never claims
// the site was installed when it wasn't, and it never links to an App Store
// listing (no official iOS app exists).
export default function PwaInstallModal({ open, onClose }) {
  const { installed, canPrompt, isIOS } = usePwaInstall()
  const [declined, setDeclined] = useState(false)
  const [busy, setBusy] = useState(false)

  if (!open) return null

  const family = getBrowserFamily()

  const handleInstall = async () => {
    setBusy(true)
    const outcome = await promptInstall()
    setBusy(false)
    if (outcome === 'accepted') {
      onClose()
    } else if (outcome === 'dismissed') {
      setDeclined(true)
    }
    // 'unavailable': the prompt event is gone, so the modal re-renders into
    // the manual-instructions branch below.
  }

  const iosSteps = [
    'افتح موقع صحتي في متصفح سفاري على الآيفون.',
    'اضغط زر المشاركة (مربع به سهم لأعلى) أسفل الشاشة.',
    'اختر «إضافة إلى الشاشة الرئيسية» من القائمة.',
    'اضغط «إضافة» في أعلى الشاشة — ستظهر أيقونة صحتي على شاشتك الرئيسية.',
  ]

  let body

  if (installed) {
    body = (
      <>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-emerald-50 text-emerald-600">
          <Check className="h-7 w-7" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">التطبيق مثبّت على جهازك</h2>
        <p className="mt-2 text-sm leading-relaxed text-gray-600">
          أنت تستخدم صحتي كتطبيق مثبّت — يمكنك فتحه من شاشتك الرئيسية في أي وقت، ويعمل بدون إنترنت.
        </p>
        <button onClick={onClose} className="mt-6 w-full rounded-xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white hover:bg-emerald-700">
          إغلاق
        </button>
      </>
    )
  } else if (canPrompt) {
    body = (
      <>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-blue-50 text-blue-600">
          <Download className="h-7 w-7" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">تثبيت تطبيق صحتي</h2>
        <p className="mt-2 text-sm leading-relaxed text-gray-600">
          سيظهر التطبيق على شاشتك الرئيسية ويعمل بدون إنترنت، مع وصول سريع للطوارئ والدليل الطبي.
        </p>
        {declined && (
          <p className="mt-4 rounded-xl bg-amber-50 p-3 text-sm text-amber-800">
            رفضت التثبيت — لا مشكلة، يمكنك إعادة المحاولة في أي وقت من زر التثبيت في الأعلى.
          </p>
        )}
        <button
          onClick={handleInstall}
          disabled={busy}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-sm font-bold text-white hover:bg-blue-700 disabled:opacity-60"
        >
          <Download className="h-4 w-4" />
          {busy ? 'جارٍ التثبيت…' : 'تثبيت التطبيق'}
        </button>
        <button onClick={onClose} className="mt-2 w-full rounded-xl px-4 py-2 text-sm text-gray-500 hover:bg-gray-50">
          لاحقاً
        </button>
      </>
    )
  } else if (isIOS) {
    body = (
      <>
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-blue-50 text-blue-600">
          <Share className="h-7 w-7" />
        </div>
        <h2 className="text-lg font-bold text-gray-900">التثبيت على الآيفون</h2>
        <p className="mt-2 text-sm leading-relaxed text-gray-600">
          متصفح سفاري لا يعرض زر تثبيت مباشر — أضف صحتي إلى شاشتك الرئيسية بالخطوات التالية:
        </p>
        <ol className="mt-4 space-y-2 text-right text-sm leading-relaxed text-gray-700">
          {iosSteps.map((step, i) => (
            <li key={i} className="flex gap-2">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">{i + 1}</span>
              <span>{step}</span>
            </li>
          ))}
        </ol>
        <p className="mt-4 rounded-xl bg-slate-50 p-3 text-xs leading-relaxed text-gray-500">
          ملاحظة: لا يمكن للموقع إنشاء الأيقونة تلقائياً على الآيفون — الخطوات أعلاه يدوية في سفاري.
        </p>
        <button onClick={onClose} className="mt-6 w-full rounded-xl bg-blue-600 px-4 py-3 text-sm font-bold text-white hover:bg-blue-700">
          فهمت
        </button>
      </>
    )
  } else if (family === 'firefox') {
    body = (
      <>
        <h2 className="text-lg font-bold text-gray-900">التثبيت غير مدعوم في فايرفوكس</h2>
        <p className="mt-2 text-sm leading-relaxed text-gray-600">
          متصفح فايرفوكس لا يدعم تثبيت التطبيق مباشرة. جرّب متصفح كروم أو إيدج على جهازك لتثبيت صحتي، أو احفظ الموقع في المفضلة للوصول السريع إليه.
        </p>
        <button onClick={onClose} className="mt-6 w-full rounded-xl bg-blue-600 px-4 py-3 text-sm font-bold text-white hover:bg-blue-700">
          إغلاق
        </button>
      </>
    )
  } else if (family === 'safari') {
    body = (
      <>
        <h2 className="text-lg font-bold text-gray-900">التثبيت في سفاري على ماك</h2>
        <p className="mt-2 text-sm leading-relaxed text-gray-600">
          من قائمة «ملف» في سفاري اختر «إضافة إلى Dock» (متاح في macOS Sonoma أو أحدث) لتثبيت صحتي كتطبيق، أو احفظ الموقع في المفضلة للوصول السريع إليه.
        </p>
        <button onClick={onClose} className="mt-6 w-full rounded-xl bg-blue-600 px-4 py-3 text-sm font-bold text-white hover:bg-blue-700">
          إغلاق
        </button>
      </>
    )
  } else {
    body = (
      <>
        <h2 className="text-lg font-bold text-gray-900">تثبيت تطبيق صحتي</h2>
        <p className="mt-2 text-sm leading-relaxed text-gray-600">
          من قائمة المتصفح (النقاط الثلاث أعلى الشاشة) اختر «تثبيت صحتي» أو «إضافة إلى الشاشة الرئيسية». إذا لم يظهر الخيار، حدّث الصفحة وحاول مجدداً — أو جرّب متصفح كروم أو إيدج.
        </p>
        {declined && (
          <p className="mt-4 rounded-xl bg-amber-50 p-3 text-sm text-amber-800">
            رفضت التثبيت — لا مشكلة، يمكنك إعادة المحاولة في أي وقت من زر التثبيت في الأعلى.
          </p>
        )}
        <button onClick={onClose} className="mt-6 w-full rounded-xl bg-blue-600 px-4 py-3 text-sm font-bold text-white hover:bg-blue-700">
          إغلاق
        </button>
      </>
    )
  }

  return (
    <div className="fixed inset-0 z-[80] flex items-end justify-center bg-slate-950/40 sm:items-center sm:p-4" dir="rtl" role="dialog" aria-modal="true">
      <div className="w-full max-w-md rounded-t-3xl bg-white p-6 text-center shadow-2xl sm:rounded-3xl">
        <div className="mb-4 flex justify-end">
          <button type="button" onClick={onClose} aria-label="إغلاق" className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-700">
            <X className="h-5 w-5" />
          </button>
        </div>
        {body}
      </div>
    </div>
  )
}
