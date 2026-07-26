import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { 
  Calendar, 
  Users, 
  Heart, 
  Activity, 
  Clock, 
  Bell,
  Settings,
  User,
  Stethoscope,
  Shield,
  Crown,
  BarChart3,
  FileText,
  Pill,
  MapPin
} from 'lucide-react'

export default function DashboardPage() {
  const { user, isAdmin, isDoctor, isPatient } = useAuth()
  const [stats, setStats] = useState({
    appointments: 0,
    patients: 0,
    doctors: 0,
    notifications: 0
  })

  useEffect(() => {
    // محاكاة جلب الإحصائيات
    setStats({
      appointments: 25,
      patients: 150,
      doctors: 45,
      notifications: 8
    })
  }, [])

  const PatientDashboard = () => (
    <div className="space-y-6">
      {/* بطاقات الإحصائيات */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-blue-100 p-3 rounded-full">
              <Calendar className="h-6 w-6 text-blue-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">المواعيد القادمة</p>
              <p className="text-2xl font-bold text-gray-900">3</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-green-100 p-3 rounded-full">
              <Pill className="h-6 w-6 text-green-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">الأدوية النشطة</p>
              <p className="text-2xl font-bold text-gray-900">5</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-purple-100 p-3 rounded-full">
              <FileText className="h-6 w-6 text-purple-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">التقارير الطبية</p>
              <p className="text-2xl font-bold text-gray-900">12</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-red-100 p-3 rounded-full">
              <Bell className="h-6 w-6 text-red-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">التنبيهات</p>
              <p className="text-2xl font-bold text-gray-900">2</p>
            </div>
          </div>
        </div>
      </div>

      {/* الأقسام الرئيسية */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* المواعيد القادمة */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">المواعيد القادمة</h3>
          <div className="space-y-4">
            <div className="flex items-center p-4 bg-blue-50 rounded-lg">
              <div className="bg-blue-100 p-2 rounded-full">
                <Stethoscope className="h-5 w-5 text-blue-600" />
              </div>
              <div className="mr-3 flex-1">
                <p className="font-medium text-gray-900">د. أحمد محمد</p>
                <p className="text-sm text-gray-600">طب القلب</p>
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900">غداً</p>
                <p className="text-sm text-gray-600">10:00 ص</p>
              </div>
            </div>
            
            <div className="flex items-center p-4 bg-green-50 rounded-lg">
              <div className="bg-green-100 p-2 rounded-full">
                <Stethoscope className="h-5 w-5 text-green-600" />
              </div>
              <div className="mr-3 flex-1">
                <p className="font-medium text-gray-900">د. فاطمة علي</p>
                <p className="text-sm text-gray-600">طب الأطفال</p>
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900">الأحد</p>
                <p className="text-sm text-gray-600">2:00 م</p>
              </div>
            </div>
          </div>
          <Button className="w-full mt-4" variant="outline">
            عرض جميع المواعيد
          </Button>
        </div>

        {/* الأدوية والتذكيرات */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">تذكيرات الأدوية</h3>
          <div className="space-y-4">
            <div className="flex items-center p-4 bg-yellow-50 rounded-lg">
              <div className="bg-yellow-100 p-2 rounded-full">
                <Pill className="h-5 w-5 text-yellow-600" />
              </div>
              <div className="mr-3 flex-1">
                <p className="font-medium text-gray-900">أسبرين 100 مجم</p>
                <p className="text-sm text-gray-600">مرة واحدة يومياً</p>
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900">8:00 ص</p>
                <p className="text-sm text-gray-600">بعد الإفطار</p>
              </div>
            </div>
            
            <div className="flex items-center p-4 bg-purple-50 rounded-lg">
              <div className="bg-purple-100 p-2 rounded-full">
                <Pill className="h-5 w-5 text-purple-600" />
              </div>
              <div className="mr-3 flex-1">
                <p className="font-medium text-gray-900">فيتامين د</p>
                <p className="text-sm text-gray-600">مرة واحدة أسبوعياً</p>
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900">الجمعة</p>
                <p className="text-sm text-gray-600">مع الطعام</p>
              </div>
            </div>
          </div>
          <Button className="w-full mt-4" variant="outline">
            إدارة الأدوية
          </Button>
        </div>
      </div>
    </div>
  )

  const DoctorDashboard = () => (
    <div className="space-y-6">
      {/* بطاقات الإحصائيات */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-blue-100 p-3 rounded-full">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">المرضى اليوم</p>
              <p className="text-2xl font-bold text-gray-900">12</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-green-100 p-3 rounded-full">
              <Calendar className="h-6 w-6 text-green-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">المواعيد هذا الأسبوع</p>
              <p className="text-2xl font-bold text-gray-900">45</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-purple-100 p-3 rounded-full">
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">التقييم</p>
              <p className="text-2xl font-bold text-gray-900">4.8</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-yellow-100 p-3 rounded-full">
              <Clock className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">ساعات العمل</p>
              <p className="text-2xl font-bold text-gray-900">8</p>
            </div>
          </div>
        </div>
      </div>

      {/* جدول المواعيد */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">مواعيد اليوم</h3>
        <div className="space-y-4">
          {[
            { time: '9:00 ص', patient: 'أحمد محمد', type: 'كشف دوري', status: 'مؤكد' },
            { time: '10:00 ص', patient: 'فاطمة علي', type: 'استشارة', status: 'في الانتظار' },
            { time: '11:00 ص', patient: 'محمد أحمد', type: 'متابعة', status: 'مكتمل' }
          ].map((appointment, index) => (
            <div key={index} className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{appointment.patient}</p>
                    <p className="text-sm text-gray-600">{appointment.type}</p>
                  </div>
                  <div className="text-left">
                    <p className="text-sm font-medium text-gray-900">{appointment.time}</p>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      appointment.status === 'مؤكد' ? 'bg-blue-100 text-blue-800' :
                      appointment.status === 'في الانتظار' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {appointment.status}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )

  const AdminDashboard = () => (
    <div className="space-y-6">
      {/* بطاقات الإحصائيات */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-blue-100 p-3 rounded-full">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">إجمالي المستخدمين</p>
              <p className="text-2xl font-bold text-gray-900">{stats.patients + stats.doctors}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-green-100 p-3 rounded-full">
              <Stethoscope className="h-6 w-6 text-green-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">الأطباء</p>
              <p className="text-2xl font-bold text-gray-900">{stats.doctors}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-purple-100 p-3 rounded-full">
              <Heart className="h-6 w-6 text-purple-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">المرضى</p>
              <p className="text-2xl font-bold text-gray-900">{stats.patients}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center">
            <div className="bg-yellow-100 p-3 rounded-full">
              <Calendar className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="mr-4">
              <p className="text-sm font-medium text-gray-600">المواعيد اليوم</p>
              <p className="text-2xl font-bold text-gray-900">{stats.appointments}</p>
            </div>
          </div>
        </div>
      </div>

      {/* أدوات الإدارة */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center mb-4">
            <Users className="h-6 w-6 text-blue-600 ml-2" />
            <h3 className="text-lg font-semibold text-gray-900">إدارة المستخدمين</h3>
          </div>
          <p className="text-gray-600 mb-4">إدارة حسابات المرضى والأطباء</p>
          <Button className="w-full">عرض المستخدمين</Button>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center mb-4">
            <BarChart3 className="h-6 w-6 text-green-600 ml-2" />
            <h3 className="text-lg font-semibold text-gray-900">التقارير والإحصائيات</h3>
          </div>
          <p className="text-gray-600 mb-4">عرض تقارير النظام والإحصائيات</p>
          <Button className="w-full" variant="outline">عرض التقارير</Button>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center mb-4">
            <Settings className="h-6 w-6 text-purple-600 ml-2" />
            <h3 className="text-lg font-semibold text-gray-900">إعدادات النظام</h3>
          </div>
          <p className="text-gray-600 mb-4">تكوين إعدادات المنصة</p>
          <Button className="w-full" variant="outline">الإعدادات</Button>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* الرأس */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                مرحباً، {user?.profile?.first_name || user?.email}
              </h1>
              <p className="text-gray-600 mt-1">
                 {isAdmin ? 'مدير النظام' :
                 isDoctor ? 'طبيب معتمد' :
                 'مريض'}
              </p>
            </div>
            <div className="flex items-center space-x-4 rtl:space-x-reverse">
              <Button variant="outline" size="sm">
                <Bell className="h-4 w-4 ml-1" />
                التنبيهات
                {stats.notifications > 0 && (
                  <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1 mr-2">
                    {stats.notifications}
                  </span>
                )}
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 ml-1" />
                الإعدادات
              </Button>
            </div>
          </div>
        </div>

        {/* المحتوى حسب نوع المستخدم */}
        {isPatient && <PatientDashboard />}
        {isDoctor && <DoctorDashboard />}
        {isAdmin && <AdminDashboard />}
      </div>
    </div>
  )
}

