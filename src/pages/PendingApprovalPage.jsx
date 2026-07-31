import { Link, useLocation } from 'react-router-dom'
import { Clock, ShieldCheck, Mail, LogIn, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

const STATUS_INFO = {
  pending: {
    icon: Clock,
    iconClass: 'text-amber-500',
    bgClass: 'bg-amber-50 border-amber-200',
    title: 'طلبك قيد المراجعة',
    message:
      'تم استلام طلب تسجيلك وهو الآن قيد المراجعة من قِبَل الإدارة الطبية. سيتم مراجعة بياناتك والتواصل معك بعد اتخاذ القرار.',
  },
  rejected: {
    icon: XCircle,
    iconClass: 'text-red-500',
    bgClass: 'bg-red-50 border-red-200',
    title: 'تم رفض الطلب',
    message:
      'للأسف تم رفض طلب تسجيلك. يُرجى التواصل مع الإدارة لمعرفة السبب أو تقديم طلب جديد بمعلومات صحيحة.',
  },
  inactive: {
    icon: AlertCircle,
    iconClass: 'text-orange-500',
    bgClass: 'bg-orange-50 border-orange-200',
    title: 'الحساب غير مفعل',
    message: 'حسابك غير مفعل حالياً. يُرجى التواصل مع الإدارة لتفعيله.',
  },
}

export default function PendingApprovalPage({ reviewNote }) {
  const location = useLocation()
  const status = location.state?.status || 'pending'
  const info = STATUS_INFO[status] || STATUS_INFO.pending
  const Icon = info.icon

  const STEPS = [
    { label: 'تقديم الطلب', done: true },
    { label: 'مراجعة الإدارة', done: status === 'approved', active: status === 'pending' },
    { label: 'تفعيل الحساب', done: status === 'approved' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4 py-16" dir="rtl">
      <div className="mx-auto max-w-2xl w-full">

        <div className="rounded-2xl bg-white shadow-xl overflow-hidden">
          {/* رأس البطاقة */}
          <div className="bg-gradient-to-l from-blue-700 to-indigo-600 px-8 py-10 text-center text-white">
            <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-white/20">
              <Icon className={`h-10 w-10 ${info.iconClass} drop-shadow`} />
            </div>
            <h1 className="text-2xl font-bold">{info.title}</h1>
            <p className="mt-2 text-blue-100 text-sm">منصة صحتك في أمان</p>
          </div>

          <div className="px-8 py-8 space-y-8">
            {/* رسالة الحالة */}
            <div className={`rounded-xl border p-5 ${info.bgClass}`}>
              <p className="text-gray-800 leading-relaxed">{info.message}</p>
              {reviewNote && (
                <div className="mt-3 pt-3 border-t border-current/20">
                  <p className="text-sm font-semibold text-gray-700">ملاحظة الإدارة:</p>
                  <p className="mt-1 text-sm text-gray-600">{reviewNote}</p>
                </div>
              )}
            </div>

            {/* مراحل الطلب */}
            {status === 'pending' && (
              <div>
                <h2 className="text-sm font-semibold text-gray-500 mb-4">مراحل معالجة الطلب</h2>
                <div className="flex items-center gap-0">
                  {STEPS.map((step, i) => (
                    <div key={step.label} className="flex flex-1 items-center">
                      <div className="flex flex-col items-center flex-1">
                        <div className={`flex h-9 w-9 items-center justify-center rounded-full text-sm font-bold
                          ${step.done ? 'bg-emerald-500 text-white' : step.active ? 'bg-amber-400 text-white animate-pulse' : 'bg-gray-100 text-gray-400'}`}>
                          {step.done ? <CheckCircle className="h-5 w-5" /> : i + 1}
                        </div>
                        <p className={`mt-2 text-xs text-center ${step.active ? 'text-amber-600 font-semibold' : step.done ? 'text-emerald-600' : 'text-gray-400'}`}>
                          {step.label}
                        </p>
                      </div>
                      {i < STEPS.length - 1 && (
                        <div className={`h-0.5 flex-1 mx-1 mb-5 ${step.done ? 'bg-emerald-400' : 'bg-gray-200'}`} />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* معلومات التواصل */}
            <div className="rounded-xl bg-gray-50 p-5">
              <div className="flex items-start gap-3">
                <Mail className="h-5 w-5 text-blue-600 mt-0.5 shrink-0" />
                <div>
                  <p className="font-semibold text-gray-900">للاستفسار أو المتابعة</p>
                  <p className="mt-1 text-sm text-gray-600">
                    يُرجى التواصل مع إدارة المنصة عبر البريد الإلكتروني الرسمي مع ذكر اسمك وبريدك الإلكتروني المسجل.
                  </p>
                </div>
              </div>
            </div>

            {/* إجراءات */}
            <div className="flex flex-col gap-3 sm:flex-row">
              <Link to="/login" className="flex-1">
                <Button variant="outline" className="w-full gap-2">
                  <LogIn className="h-4 w-4" />
                  تسجيل الدخول
                </Button>
              </Link>
              <Link to="/" className="flex-1">
                <Button className="w-full gap-2">
                  <ShieldCheck className="h-4 w-4" />
                  الصفحة الرئيسية
                </Button>
              </Link>
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
