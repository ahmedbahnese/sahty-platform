import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { 
  Calendar, 
  Video, 
  Pill, 
  FileText, 
  Heart, 
  Phone, 
  Home,
  Shield,
  Stethoscope,
  Brain,
  Baby,
  Activity,
  Droplets,
  MapPin,
  Clock,
  CheckCircle,
  ArrowRight
} from 'lucide-react'

export default function ServicesPage() {
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [requestMessage, setRequestMessage] = useState('')
  const navigate = useNavigate()

  const serviceCategories = [
    { id: 'all', name: 'جميع الخدمات', icon: Stethoscope },
    { id: 'consultation', name: 'الاستشارات الطبية', icon: Video },
    { id: 'home_visit', name: 'الزيارة المنزلية', icon: Home },
    { id: 'emergency', name: 'خدمات الطوارئ', icon: Phone },
    { id: 'specialized', name: 'خدمات متخصصة', icon: Heart }
  ]

  const services = [
    {
      id: 1,
      category: 'consultation',
      title: 'حجز المواعيد الطبية',
      description: 'احجز موعدك مع أفضل الأطباء في مختلف التخصصات بسهولة ويسر',
      icon: Calendar,
      features: ['حجز فوري', 'تأكيد الموعد', 'تذكيرات تلقائية', 'إلغاء مجاني'],
      price: 'مجاني',
      duration: 'فوري',
      popular: true
    },
    {
      id: 2,
      category: 'consultation',
      title: 'الاستشارات الطبية عن بُعد',
      description: 'احصل على استشارة طبية فورية من خلال مكالمات الفيديو مع أطباء معتمدين',
      icon: Video,
      features: ['متاح 24/7', 'أطباء معتمدون', 'سرية تامة', 'تقرير طبي'],
      price: 'من 150 جنيه',
      duration: '30 دقيقة',
      popular: false
    },
    {
      id: 3,
      category: 'emergency',
      title: 'خدمة الطوارئ الطبية',
      description: 'خدمة طوارئ متاحة على مدار الساعة للحالات العاجلة والطارئة',
      icon: Phone,
      features: ['متاح 24/7', 'استجابة سريعة', 'فريق متخصص', 'تنسيق الإسعاف'],
      price: 'حسب الحالة',
      duration: 'فوري',
      popular: false
    },
    {
      id: 4,
      category: 'specialized',
      title: 'بنك الدم الرقمي',
      description: 'منصة لطلبات الدم وتسجيل المتبرعين والعثور على نقاط التبرع القريبة',
      icon: Droplets,
      features: ['شبكة متبرعين', 'طلبات طارئة', 'فحص الأهلية', 'تتبع التبرعات'],
      price: 'مجاني',
      duration: 'حسب الحاجة',
      popular: true
    },
    {
      id: 5,
      category: 'specialized',
      title: 'تحليل الصور الطبية بالذكاء الاصطناعي',
      description: 'تحليل متقدم للأشعة والصور الطبية باستخدام تقنيات الذكاء الاصطناعي',
      icon: Brain,
      features: ['تحليل دقيق', 'نتائج سريعة', 'تقرير مفصل', 'مراجعة طبية'],
      price: 'من 100 جنيه',
      duration: '24 ساعة',
      popular: false
    },
    {
      id: 6,
      category: 'specialized',
      title: 'برامج الصحة النفسية',
      description: 'جلسات علاج نفسي وبرامج دعم للصحة النفسية والعقلية',
      icon: Heart,
      features: ['جلسات فردية', 'برامج جماعية', 'متابعة مستمرة', 'سرية تامة'],
      price: 'من 250 جنيه',
      duration: '50 دقيقة',
      popular: false
    },
    {
      id: 7,
      category: 'specialized',
      title: 'رعاية الأمومة والطفولة',
      description: 'برامج شاملة لرعاية الحوامل والأطفال من الولادة حتى المراهقة',
      icon: Baby,
      features: ['متابعة الحمل', 'رعاية الأطفال', 'تطعيمات', 'استشارات تغذية'],
      price: 'من 180 جنيه',
      duration: 'حسب البرنامج',
      popular: true
    },
    {
      id: 8,
      category: 'specialized',
      title: 'برامج اللياقة والتغذية',
      description: 'برامج مخصصة للياقة البدنية والتغذية الصحية مع متابعة من المختصين',
      icon: Activity,
      features: ['برامج مخصصة', 'متابعة يومية', 'نصائح غذائية', 'تمارين موجهة'],
      price: 'من 120 جنيه',
      duration: 'شهري',
      popular: false
    },
    {
      id: 9,
      category: 'emergency',
      title: 'خدمة الإسعاف الذكي',
      description: 'خدمة إسعاف متطورة مع تتبع GPS وتنسيق مع أقرب المستشفيات',
      icon: MapPin,
      features: ['تتبع GPS', 'استجابة سريعة', 'تنسيق المستشفيات', 'فريق مدرب'],
      price: 'حسب المسافة',
      duration: '15-30 دقيقة',
      popular: false
    },
    {
      id: 10,
      category: 'home_visit',
      title: 'زيارة الطبيب المنزلية',
      description: 'يأتي إليك الطبيب في المنزل للكشف والتشخيص وكتابة الوصفة الطبية',
      icon: Stethoscope,
      features: ['كشف كامل في المنزل', 'وصفة طبية فورية', 'تقرير طبي موثّق', 'أطباء معتمدون'],
      price: 'من 250 جنيه',
      duration: '45-60 دقيقة',
      popular: true
    },
    {
      id: 11,
      category: 'home_visit',
      title: 'تمريض منزلي — إقامة',
      description: 'خدمة تمريض احترافية للمرضى الذين يحتاجون رعاية تمريضية مستمرة في المنزل',
      icon: Heart,
      features: ['ممرض/ة معتمد/ة', 'رعاية 12 أو 24 ساعة', 'قياس العلامات الحيوية', 'تقارير يومية'],
      price: 'من 800 جنيه / يوم',
      duration: 'حسب الحاجة',
      popular: false
    },
    {
      id: 12,
      category: 'home_visit',
      title: 'تمريض منزلي — إجراء طبي',
      description: 'إجراء تمريضي في المنزل كالحقن والتضميد وضغط الدم وقياس السكر وإعطاء الحقنة الوريدية',
      icon: Activity,
      features: ['حقن وريدية وعضلية', 'تضميد الجروح', 'قياس السكر والضغط', 'تركيب كانيولا'],
      price: 'من 120 جنيه',
      duration: '20-30 دقيقة',
      popular: false
    },
    {
      id: 13,
      category: 'home_visit',
      title: 'تحاليل مخبرية منزلية',
      description: 'طلب التحاليل من منزلك — يأتي الفني لسحب العينة وإرسال النتيجة إلكترونياً',
      icon: CheckCircle,
      features: ['سحب عينات في المنزل', 'نتائج إلكترونية', 'تحاليل شاملة', 'تحليل يوم العمل'],
      price: 'من 80 جنيه',
      duration: '24-48 ساعة',
      popular: false
    },
    {
      id: 14,
      category: 'home_visit',
      title: 'أشعة منزلية',
      description: 'وحدة أشعة متنقلة تأتي إلى منزلك لإجراء الأشعة السينية والموجات الصوتية',
      icon: MapPin,
      features: ['أشعة X متنقلة', 'موجات صوتية', 'تقرير فوري', 'تنسيق مع طبيبك'],
      price: 'من 300 جنيه',
      duration: '30-60 دقيقة',
      popular: false
    }
  ]

  const filteredServices = selectedCategory === 'all' 
    ? services 
    : services.filter(service => service.category === selectedCategory)

  const handleServiceRequest = (serviceId) => {
    const service = services.find(item => item.id === serviceId)
    if (!service) return
    if (service.title === 'حجز المواعيد الطبية') {
      navigate('/doctors')
    } else if (service.category === 'emergency') {
      navigate('/emergency')
    } else if (service.title === 'بنك الدم الرقمي') {
      navigate('/blood-bank')
    } else {
      setSelectedCategory(service.category)
      setRequestMessage(`تم استلام طلبك لخدمة «${service.title}». سيتم التواصل معك قريباً.`)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* الرأس */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            خدماتنا الطبية
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            نقدم مجموعة شاملة من الخدمات الطبية المتطورة لضمان حصولك على أفضل رعاية صحية
          </p>
        </div>

        {/* فئات الخدمات */}
        <div className="mb-8">
          <div className="flex flex-wrap justify-center gap-4">
            {serviceCategories.map((category) => {
              const IconComponent = category.icon
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`flex items-center px-6 py-3 rounded-full border transition-colors ${
                    selectedCategory === category.id
                      ? 'border-blue-500 bg-blue-50 text-blue-600'
                      : 'border-gray-200 hover:border-gray-300 text-gray-700'
                  }`}
                >
                  <IconComponent className="h-5 w-5 ml-2" />
                  <span className="font-medium">{category.name}</span>
                </button>
              )
            })}
          </div>
        </div>

        {requestMessage && (
          <div className="mb-6 rounded-lg border border-green-200 bg-green-50 p-4 text-green-800 text-center">
            {requestMessage}
          </div>
        )}

        {/* عدد الخدمات */}
        <div className="mb-6">
          <p className="text-gray-600 text-center">
            {filteredServices.length} خدمة متاحة
          </p>
        </div>

        {/* قائمة الخدمات */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredServices.map((service) => {
            const IconComponent = service.icon
            return (
              <div key={service.id} className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow overflow-hidden">
                {/* رأس البطاقة */}
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="bg-blue-100 p-3 rounded-full">
                      <IconComponent className="h-6 w-6 text-blue-600" />
                    </div>
                    {service.popular && (
                      <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full">
                        الأكثر طلباً
                      </span>
                    )}
                  </div>

                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {service.title}
                  </h3>
                  <p className="text-gray-600 text-sm leading-relaxed mb-4">
                    {service.description}
                  </p>

                  {/* الميزات */}
                  <div className="space-y-2 mb-6">
                    {service.features.map((feature, index) => (
                      <div key={index} className="flex items-center text-sm text-gray-600">
                        <CheckCircle className="h-4 w-4 text-green-500 ml-2 flex-shrink-0" />
                        <span>{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* معلومات السعر والمدة */}
                  <div className="flex items-center justify-between text-sm text-gray-600 mb-6">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 ml-1" />
                      <span>{service.duration}</span>
                    </div>
                    <div className="font-semibold text-blue-600">
                      {service.price}
                    </div>
                  </div>
                </div>

                {/* تذييل البطاقة */}
                <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
                  <Button 
                    onClick={() => handleServiceRequest(service.id)}
                    className="w-full flex items-center justify-center"
                  >
                    طلب الخدمة
                    <ArrowRight className="h-4 w-4 mr-2" />
                  </Button>
                </div>
              </div>
            )
          })}
        </div>

        {/* قسم المزايا */}
        <div className="mt-16 bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              لماذا تختار خدماتنا؟
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              نحن ملتزمون بتقديم أعلى مستويات الرعاية الصحية باستخدام أحدث التقنيات
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                أمان وخصوصية
              </h3>
              <p className="text-gray-600">
                بياناتك الطبية محمية بأعلى معايير الأمان والخصوصية
              </p>
            </div>

            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Stethoscope className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                أطباء معتمدون
              </h3>
              <p className="text-gray-600">
                جميع أطبائنا معتمدون ومرخصون من الجهات المختصة
              </p>
            </div>

            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                متاح 24/7
              </h3>
              <p className="text-gray-600">
                خدماتنا متاحة على مدار الساعة لضمان حصولك على الرعاية عند الحاجة
              </p>
            </div>
          </div>
        </div>

        {/* دعوة للعمل */}
        <div className="mt-12 bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8 rounded-xl text-center">
          <h3 className="text-2xl font-bold mb-4">
            هل تحتاج مساعدة في اختيار الخدمة المناسبة؟
          </h3>
          <p className="text-blue-100 mb-6">
            تواصل مع فريق الدعم الطبي للحصول على استشارة مجانية
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button className="bg-white text-blue-600 hover:bg-gray-100">
              تواصل معنا
            </Button>
            <Button variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600">
              دليل الخدمات
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

