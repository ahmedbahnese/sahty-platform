import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
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
  ArrowLeft
} from 'lucide-react'

export default function HomePage() {
  const features = [
    {
      icon: Calendar,
      title: 'حجز المواعيد',
      description: 'احجز موعدك مع أفضل الأطباء بسهولة ويسر'
    },
    {
      icon: Stethoscope,
      title: 'استشارات طبية',
      description: 'احصل على استشارة طبية فورية عن بُعد'
    },
    {
      icon: Droplets,
      title: 'بنك الدم',
      description: 'تبرع بالدم أو ابحث عن متبرعين في حالات الطوارئ'
    },
    {
      icon: Shield,
      title: 'أمان البيانات',
      description: 'بياناتك الطبية محمية بأعلى معايير الأمان'
    },
    {
      icon: Phone,
      title: 'خدمة الطوارئ',
      description: 'خدمة طوارئ متاحة 24/7 للحالات العاجلة'
    },
    {
      icon: Users,
      title: 'فريق طبي متميز',
      description: 'أطباء معتمدون وذوو خبرة عالية'
    }
  ]

  const stats = [
    { number: '1000+', label: 'طبيب معتمد' },
    { number: '50000+', label: 'مريض راضٍ' },
    { number: '100+', label: 'مستشفى شريك' },
    { number: '24/7', label: 'خدمة متواصلة' }
  ]

  return (
    <div className="min-h-screen">
      {/* القسم الرئيسي */}
      <section className="bg-gradient-to-br from-blue-600 to-blue-800 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <h1 className="text-4xl md:text-6xl font-bold leading-tight">
                صحتك في أمان
              </h1>
              <p className="text-xl md:text-2xl text-blue-100">
                منصة طبية شاملة تجمع بين أفضل الأطباء والخدمات الصحية المتطورة
              </p>
              <p className="text-lg text-blue-200">
                احجز مواعيدك الطبية، احصل على استشارات فورية، وتابع صحتك بكل سهولة من مكان واحد
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/register">
                  <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 w-full sm:w-auto">
                    ابدأ الآن مجاناً
                    <ArrowLeft className="mr-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link to="/doctors">
                  <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600 w-full sm:w-auto">
                    تصفح الأطباء
                  </Button>
                </Link>
              </div>
            </div>
            <div className="relative">
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 border border-white/20">
                <Heart className="h-32 w-32 text-white/80 mx-auto mb-4" />
                <div className="text-center">
                  <h3 className="text-2xl font-bold mb-2">رعاية صحية متكاملة</h3>
                  <p className="text-blue-100">
                    نوفر لك جميع الخدمات الطبية التي تحتاجها في مكان واحد
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* الإحصائيات */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* الميزات */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              لماذا تختار صحتك في أمان؟
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              نقدم لك مجموعة شاملة من الخدمات الطبية المتطورة لضمان حصولك على أفضل رعاية صحية
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon
              return (
                <div key={index} className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
                  <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mb-6">
                    <IconComponent className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-4">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* دعوة للعمل */}
      <section className="py-20 bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            ابدأ رحلتك الصحية اليوم
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            انضم إلى آلاف المرضى والأطباء الذين يثقون في منصة صحتك في أمان
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
                إنشاء حساب مجاني
                <CheckCircle className="mr-2 h-5 w-5" />
              </Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
                تسجيل الدخول
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

