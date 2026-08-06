import { Link } from 'react-router-dom'
import { Heart, Phone, Mail, MapPin, Facebook, Twitter, Instagram } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* معلومات الشركة */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2 rtl:space-x-reverse">
              <Heart className="h-8 w-8 text-blue-400" />
              <span className="text-xl font-bold">صحتي</span>
            </div>
            <p className="text-gray-300 text-sm leading-relaxed">
              منصة طبية شاملة تهدف إلى تقديم أفضل الخدمات الصحية والطبية للمرضى والأطباء في جميع أنحاء مصر والوطن العربي.
            </p>
            <div className="flex space-x-4 rtl:space-x-reverse">
              <a 
                href="https://www.facebook.com/share/1Ei7ZKXFi6/?mibextid=wwXIfr" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-blue-400 transition-colors"
              >
                <Facebook className="h-5 w-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-blue-400 transition-colors">
                <Twitter className="h-5 w-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-blue-400 transition-colors">
                <Instagram className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* روابط سريعة */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">روابط سريعة</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/" className="text-gray-300 hover:text-white transition-colors">
                  الرئيسية
                </Link>
              </li>
              <li>
                <Link to="/doctors" className="text-gray-300 hover:text-white transition-colors">
                  الأطباء
                </Link>
              </li>
              <li>
                <Link to="/services" className="text-gray-300 hover:text-white transition-colors">
                  الخدمات
                </Link>
              </li>
              <li>
                <Link to="/blood-bank" className="text-gray-300 hover:text-white transition-colors">
                  بنك الدم
                </Link>
              </li>
              <li>
                <Link to="/emergency" className="text-gray-300 hover:text-white transition-colors">
                  الطوارئ
                </Link>
              </li>
            </ul>
          </div>

          {/* الخدمات */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">خدماتنا</h3>
            <ul className="space-y-2 text-gray-300">
              <li>حجز المواعيد الطبية</li>
              <li>الاستشارات الطبية عن بُعد</li>
              <li>إدارة الأدوية والتذكيرات</li>
              <li>بنك الدم الرقمي</li>
              <li>خدمات الطوارئ</li>
              <li>المتابعة المنزلية</li>
            </ul>
          </div>

          {/* معلومات الاتصال */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">تواصل معنا</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 rtl:space-x-reverse">
                <Phone className="h-5 w-5 text-blue-400" />
                <span className="text-gray-300">01063299450</span>
              </div>
              <div className="flex items-center space-x-3 rtl:space-x-reverse">
                <Mail className="h-5 w-5 text-blue-400" />
                <span className="text-gray-300">Ahmedbahnese@yahoo.com</span>
              </div>
              <div className="flex items-center space-x-3 rtl:space-x-reverse">
                <MapPin className="h-5 w-5 text-blue-400" />
                <span className="text-gray-300">الإسكندرية، مصر</span>
              </div>
            </div>
          </div>
        </div>

        {/* خط الفصل */}
        <div className="border-t border-gray-800 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-gray-400 text-sm">
              © 2024 صحتي. جميع الحقوق محفوظة.
            </div>
            <div className="flex space-x-6 rtl:space-x-reverse mt-4 md:mt-0">
              <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
                سياسة الخصوصية
              </a>
              <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
                شروط الاستخدام
              </a>
              <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">
                اتفاقية الخدمة
              </a>
            </div>
          </div>
          
          {/* معلومات المطور */}
          <div className="text-center mt-4 pt-4 border-t border-gray-800">
            <p className="text-gray-500 text-xs">
              تم التطوير بواسطة: أحمد حامد أحمد بهنسي | 
              <a 
                href="https://www.facebook.com/share/1Ei7ZKXFi6/?mibextid=wwXIfr" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-400 hover:text-blue-300 mr-1"
              >
                تواصل مع المطور
              </a>
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}

