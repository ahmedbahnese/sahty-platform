import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { 
  Heart, 
  Stethoscope, 
  Shield, 
  Phone, 
  Droplets, 
  Calendar, 
  Users, 
  Clock,
  CheckCircle,
  ArrowLeft,
  Bot,
  Activity,
  ChevronLeft,
  FlaskConical,
  Scan,
  Pill,
  FileText,
  MessageSquare,
  Lightbulb,
  HelpCircle,
  Send,
  AlertCircle
} from 'lucide-react'

export default function HomePage() {
  const { isAuthenticated } = useAuth()

  const features = [
    {
      icon: Calendar,
      title: 'حجز المواعيد',
      description: 'احجز موعدك مع أفضل الأطباء بسهولة ويسر في ثوانٍ معدودة',
      color: 'bg-blue-50 text-blue-700',
      link: '/doctors'
    },
    {
      icon: Stethoscope,
      title: 'استشارات طبية',
      description: 'احصل على استشارة طبية فورية عن بُعد من أخصائيين معتمدين',
      color: 'bg-indigo-50 text-indigo-700',
      link: '/doctors'
    },
    {
      icon: Droplets,
      title: 'بنك الدم',
      description: 'تبرع بالدم أو ابحث عن متبرعين في حالات الطوارئ',
      color: 'bg-red-50 text-red-600',
      link: '/blood-bank'
    },
    {
      icon: Bot,
      title: 'المساعد الذكي',
      description: 'مساعد طبي ذكي متاح 24/7 للإجابة على استفساراتك الصحية',
      color: 'bg-cyan-50 text-cyan-700',
      link: '/ai-assistant'
    },
    {
      icon: Shield,
      title: 'أمان البيانات',
      description: 'بياناتك الطبية محمية بأعلى معايير التشفير والأمان',
      color: 'bg-green-50 text-green-700',
      link: null
    },
    {
      icon: Phone,
      title: 'خدمة الطوارئ',
      description: 'خدمة طوارئ متاحة على مدار الساعة للحالات العاجلة',
      color: 'bg-orange-50 text-orange-600',
      link: '/emergency'
    }
  ]

  const stats = [
    { number: '1,000+', label: 'طبيب معتمد', icon: Stethoscope },
    { number: '50,000+', label: 'مريض راضٍ', icon: Users },
    { number: '100+', label: 'مستشفى شريك', icon: Heart },
    { number: '24/7', label: 'خدمة متواصلة', icon: Clock }
  ]

  const services = [
    { icon: FlaskConical, title: 'التحاليل المخبرية', desc: 'طلب التحاليل وعرض النتائج', link: '/lab-requests' },
    { icon: Scan, title: 'الأشعة والتصوير', desc: 'طلبات الأشعة ومتابعة النتائج', link: '/radiology' },
    { icon: Pill, title: 'متابعة الأدوية', desc: 'جدولة الأدوية والتذكير', link: '/dashboard' },
    { icon: FileText, title: 'الوصفات الطبية', desc: 'عرض وإدارة وصفاتك الطبية', link: '/dashboard' },
    { icon: Activity, title: 'الملف الطبي', desc: 'سجلاتك الطبية كاملةً في مكان واحد', link: '/dashboard' },
    { icon: Users, title: 'صحة الأسرة', desc: 'متابعة الصحة لجميع أفراد العائلة', link: '/dashboard' },
  ]

  const [feedbackForm, setFeedbackForm] = useState({ name: '', email: '', phone: '', type: 'inquiry', subject: '', message: '' })
  const [feedbackLoading, setFeedbackLoading] = useState(false)
  const [feedbackResult, setFeedbackResult] = useState(null)

  const handleFeedbackChange = (e) => {
    setFeedbackForm(prev => ({ ...prev, [e.target.name]: e.target.value }))
    setFeedbackResult(null)
  }

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault()
    setFeedbackLoading(true)
    try {
      const token = localStorage.getItem('token')
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(feedbackForm)
      })
      const data = await res.json()
      if (res.ok) {
        setFeedbackResult({ success: true, message: data.message })
        setFeedbackForm({ name: '', email: '', phone: '', type: 'inquiry', subject: '', message: '' })
      } else {
        setFeedbackResult({ success: false, message: data.message })
      }
    } catch {
      setFeedbackResult({ success: false, message: 'حدث خطأ في الاتصال' })
    } finally {
      setFeedbackLoading(false)
    }
  }

  return (
    <div className="min-h-screen" dir="rtl">
      {/* Hero */}
      <section className="relative overflow-hidden py-24 lg:py-32"
        style={{ background: 'linear-gradient(135deg, #0f2444 0%, #1a3a6b 40%, #1e4d8c 100%)' }}>
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-20 w-64 h-64 rounded-full bg-blue-400 blur-3xl"></div>
          <div className="absolute bottom-10 right-10 w-96 h-96 rounded-full bg-indigo-300 blur-3xl"></div>
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 bg-white/10 text-blue-200 rounded-full px-4 py-2 text-sm font-medium backdrop-blur-sm border border-white/20">
                <Activity className="h-4 w-4" />
                <span>منصة الرعاية الصحية الشاملة رقم #1</span>
              </div>
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold text-white leading-tight">
                صحتك<br />
                <span style={{ color: '#60a5fa' }}>في أمان</span>
              </h1>
              <p className="text-lg md:text-xl text-blue-100 leading-relaxed max-w-lg">
                منصة طبية شاملة تجمع بين أفضل الأطباء والخدمات الصحية المتطورة — احجز مواعيدك واحصل على استشاراتك فورياً
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                {isAuthenticated ? (
                  <Link to="/dashboard">
                    <button className="group flex items-center gap-3 bg-white text-blue-900 font-bold px-8 py-4 rounded-2xl hover:bg-blue-50 transition-all shadow-xl hover:shadow-2xl hover:-translate-y-0.5 text-base">
                      <span>لوحة التحكم</span>
                      <ChevronLeft className="h-5 w-5 group-hover:-translate-x-1 transition-transform" />
                    </button>
                  </Link>
                ) : (
                  <Link to="/register">
                    <button className="group flex items-center gap-3 bg-white text-blue-900 font-bold px-8 py-4 rounded-2xl hover:bg-blue-50 transition-all shadow-xl hover:shadow-2xl hover:-translate-y-0.5 text-base">
                      <span>ابدأ مجاناً الآن</span>
                      <ChevronLeft className="h-5 w-5 group-hover:-translate-x-1 transition-transform" />
                    </button>
                  </Link>
                )}
                <Link to="/doctors">
                  <button className="flex items-center gap-3 border-2 border-white/30 text-white font-semibold px-8 py-4 rounded-2xl hover:bg-white/10 transition-all backdrop-blur-sm text-base">
                    <Stethoscope className="h-5 w-5" />
                    <span>تصفح الأطباء</span>
                  </button>
                </Link>
              </div>
            </div>

            {/* Stats cards */}
            <div className="grid grid-cols-2 gap-4">
              {stats.map((stat, i) => {
                const Icon = stat.icon
                return (
                  <div key={i} className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-colors">
                    <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center mb-3">
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div className="text-3xl font-bold text-white mb-1">{stat.number}</div>
                    <div className="text-blue-200 text-sm">{stat.label}</div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 rounded-full px-4 py-2 text-sm font-medium mb-4">
              <CheckCircle className="h-4 w-4" />
              <span>ميزاتنا المتميزة</span>
            </div>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">لماذا تختار صحتي؟</h2>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto">
              نقدم مجموعة شاملة من الخدمات الطبية المتطورة لضمان حصولك على أفضل رعاية صحية
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => {
              const Icon = f.icon
              const card = (
                <div key={i} className="group bg-white rounded-2xl p-8 border border-gray-100 hover:border-blue-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-1 cursor-pointer">
                  <div className={`w-14 h-14 rounded-2xl ${f.color} bg-opacity-20 flex items-center justify-center mb-5`}
                    style={{ background: f.color.includes('blue') ? '#eff6ff' : f.color.includes('indigo') ? '#eef2ff' : f.color.includes('red') ? '#fef2f2' : f.color.includes('cyan') ? '#ecfeff' : f.color.includes('green') ? '#f0fdf4' : '#fff7ed' }}>
                    <Icon className={`h-7 w-7 ${f.color.split(' ')[1]}`} />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3">{f.title}</h3>
                  <p className="text-gray-500 leading-relaxed text-sm">{f.description}</p>
                  {f.link && (
                    <div className="mt-4 flex items-center gap-2 text-blue-600 text-sm font-medium group-hover:gap-3 transition-all">
                      <span>تعرف أكثر</span>
                      <ArrowLeft className="h-4 w-4" />
                    </div>
                  )}
                </div>
              )
              return f.link ? <Link to={f.link} key={i}>{card}</Link> : <div key={i}>{card}</div>
            })}
          </div>
        </div>
      </section>

      {/* Services */}
      <section className="py-24" style={{ background: '#f8fafc' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">خدماتنا الطبية</h2>
            <p className="text-lg text-gray-500">كل ما تحتاجه في مكان واحد</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {services.map((s, i) => {
              const Icon = s.icon
              return (
                <Link to={s.link} key={i}>
                  <div className="group flex flex-col items-center text-center p-6 bg-white rounded-2xl border border-gray-100 hover:border-blue-200 hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                    <div className="w-12 h-12 rounded-2xl bg-blue-50 flex items-center justify-center mb-3 group-hover:bg-blue-100 transition-colors">
                      <Icon className="h-6 w-6 text-blue-700" />
                    </div>
                    <h3 className="text-sm font-semibold text-gray-800 mb-1">{s.title}</h3>
                    <p className="text-xs text-gray-400 leading-relaxed">{s.desc}</p>
                  </div>
                </Link>
              )
            })}
          </div>
        </div>
      </section>

      {/* Feedback / Customer Service */}
      <section className="py-24 bg-white" id="contact">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 rounded-full px-4 py-2 text-sm font-medium mb-4">
              <MessageSquare className="h-4 w-4" />
              <span>تواصل معنا</span>
            </div>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">خدمة العملاء والشكاوى والاقتراحات</h2>
            <p className="text-lg text-gray-500 max-w-2xl mx-auto">
              رأيك يهمنا — نتابع جميع الرسائل ونرد عليها في أقرب وقت
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Type cards */}
            <div className="space-y-4">
              {[
                { icon: AlertCircle, type: 'complaint', label: 'شكوى', desc: 'للإبلاغ عن أي مشكلة أو تجربة سيئة', color: 'bg-red-50 text-red-600 border-red-100' },
                { icon: Lightbulb, type: 'suggestion', label: 'اقتراح', desc: 'شارك أفكارك لتحسين خدماتنا', color: 'bg-yellow-50 text-yellow-600 border-yellow-100' },
                { icon: HelpCircle, type: 'inquiry', label: 'استفسار', desc: 'لأي سؤال أو طلب معلومات', color: 'bg-blue-50 text-blue-600 border-blue-100' },
              ].map(item => {
                const Icon = item.icon
                return (
                  <button
                    key={item.type}
                    onClick={() => setFeedbackForm(prev => ({ ...prev, type: item.type }))}
                    className={`w-full flex items-start gap-4 p-4 rounded-2xl border-2 transition-all text-right ${
                      feedbackForm.type === item.type
                        ? `${item.color} border-current shadow-sm`
                        : 'bg-white border-gray-100 hover:border-gray-200'
                    }`}
                  >
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${feedbackForm.type === item.type ? '' : 'bg-gray-50'}`}>
                      <Icon className={`h-5 w-5 ${feedbackForm.type === item.type ? '' : 'text-gray-400'}`} />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{item.label}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{item.desc}</p>
                    </div>
                  </button>
                )
              })}

              <div className="p-4 rounded-2xl border border-gray-100 bg-gray-50 text-sm text-gray-500 leading-relaxed">
                <p className="font-medium text-gray-700 mb-1">🔒 خصوصية تامة</p>
                جميع الرسائل تصل مباشرة للمسؤولين فقط ولا تُنشر علناً.
              </div>
            </div>

            {/* Form */}
            <div className="lg:col-span-2">
              {feedbackResult?.success ? (
                <div className="flex flex-col items-center justify-center h-full text-center py-16 bg-green-50 rounded-2xl border border-green-200">
                  <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mb-4">
                    <CheckCircle className="h-8 w-8 text-green-600" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">تم الإرسال بنجاح!</h3>
                  <p className="text-gray-600 max-w-sm">{feedbackResult.message}</p>
                  <button
                    onClick={() => setFeedbackResult(null)}
                    className="mt-6 px-6 py-2.5 rounded-xl text-sm font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 transition-colors"
                  >
                    إرسال رسالة أخرى
                  </button>
                </div>
              ) : (
                <form onSubmit={handleFeedbackSubmit} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">الاسم *</label>
                      <input
                        name="name" value={feedbackForm.name} onChange={handleFeedbackChange} required
                        placeholder="أدخل اسمك الكامل"
                        className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100"
                        style={{ direction: 'rtl' }}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">البريد الإلكتروني</label>
                      <input
                        name="email" value={feedbackForm.email} onChange={handleFeedbackChange} type="email"
                        placeholder="للرد عليك (اختياري)"
                        className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100"
                        style={{ direction: 'rtl' }}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">رقم الهاتف</label>
                      <input
                        name="phone" value={feedbackForm.phone} onChange={handleFeedbackChange}
                        placeholder="للتواصل السريع (اختياري)"
                        className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100"
                        style={{ direction: 'rtl' }}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">الموضوع *</label>
                      <input
                        name="subject" value={feedbackForm.subject} onChange={handleFeedbackChange} required
                        placeholder="عنوان مختصر لرسالتك"
                        className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100"
                        style={{ direction: 'rtl' }}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">الرسالة *</label>
                    <textarea
                      name="message" value={feedbackForm.message} onChange={handleFeedbackChange} required
                      placeholder="اكتب رسالتك بالتفصيل..."
                      rows={5}
                      className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-100 resize-none"
                      style={{ direction: 'rtl' }}
                    />
                  </div>
                  {feedbackResult?.success === false && (
                    <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-700">
                      {feedbackResult.message}
                    </div>
                  )}
                  <button
                    type="submit" disabled={feedbackLoading}
                    className="w-full flex items-center justify-center gap-2 py-3 rounded-xl text-white font-semibold text-sm transition-all hover:opacity-90 disabled:opacity-50"
                    style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}
                  >
                    {feedbackLoading ? (
                      <span className="flex items-center gap-2">
                        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                        جاري الإرسال...
                      </span>
                    ) : (
                      <>
                        <Send className="h-4 w-4" />
                        إرسال الرسالة
                      </>
                    )}
                  </button>
                </form>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24" style={{ background: 'linear-gradient(135deg, #0f2444 0%, #1a3a6b 100%)' }}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="w-16 h-16 rounded-2xl bg-white/10 flex items-center justify-center mx-auto mb-6">
            <Heart className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-4xl font-bold text-white mb-4">ابدأ رحلتك الصحية اليوم</h2>
          <p className="text-xl text-blue-200 mb-10 max-w-2xl mx-auto leading-relaxed">
            انضم إلى آلاف المرضى والأطباء الذين يثقون في منصة صحتي
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {!isAuthenticated && (
              <Link to="/register">
                <button className="flex items-center gap-3 bg-white text-blue-900 font-bold px-8 py-4 rounded-2xl hover:bg-blue-50 transition-all shadow-xl text-base">
                  <CheckCircle className="h-5 w-5" />
                  <span>إنشاء حساب مجاني</span>
                </button>
              </Link>
            )}
            <Link to="/login">
              <button className="flex items-center gap-3 border-2 border-white/30 text-white font-semibold px-8 py-4 rounded-2xl hover:bg-white/10 transition-all text-base">
                <span>{isAuthenticated ? 'الذهاب للوحة التحكم' : 'تسجيل الدخول'}</span>
              </button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
