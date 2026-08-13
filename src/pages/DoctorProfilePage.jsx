import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import {
  Star, MapPin, Clock, Calendar, Phone, Award, CheckCircle,
  Video, Stethoscope, ChevronLeft, ChevronRight, User, X,
  AlertCircle, Loader2
} from 'lucide-react'

const DAYS_AR = ['الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']

export default function DoctorProfilePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isAuthenticated, token } = useAuth()

  const [doctor, setDoctor] = useState(null)
  const [slots, setSlots] = useState([])
  const [loading, setLoading] = useState(true)
  const [slotsLoading, setSlotsLoading] = useState(false)
  const [selectedSlot, setSelectedSlot] = useState(null)
  const [bookingOpen, setBookingOpen] = useState(false)
  const [bookingLoading, setBookingLoading] = useState(false)
  const [bookingForm, setBookingForm] = useState({ reason: '', symptoms: '', appointment_type: 'in_person' })
  const [bookingSuccess, setBookingSuccess] = useState(false)
  const [confirmedAppointment, setConfirmedAppointment] = useState(null)
  const [error, setError] = useState(null)
  const [slotDays, setSlotDays] = useState(7)
  const [selectedDate, setSelectedDate] = useState('')

  const authHeaders = () => ({
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  })

  useEffect(() => {
    fetchDoctor()
  }, [id])

  useEffect(() => {
    if (doctor) {
      setSelectedDate('')
      fetchSlots()
    }
  }, [doctor, slotDays])

  async function fetchDoctor() {
    setLoading(true)
    try {
      const res = await fetch(`/api/doctors/${id}`)
      if (!res.ok) throw new Error('الطبيب غير موجود')
      const data = await res.json()
      setDoctor(data.doctor)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function fetchSlots() {
    setSlotsLoading(true)
    try {
      const res = await fetch(`/api/doctors/${id}/available-slots?days=${slotDays}`)
      if (res.ok) {
        const data = await res.json()
        setSlots(data.slots || [])
        setSelectedDate(current => current || data.slots?.[0]?.date || '')
      }
    } finally {
      setSlotsLoading(false)
    }
  }

  async function handleBook() {
    if (!isAuthenticated) { navigate('/login'); return }
    if (!selectedSlot) return
    setBookingLoading(true)
    try {
      const res = await fetch('/api/appointments', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({
          doctor_id: doctor.id,
          appointment_date: selectedSlot.datetime,
          appointment_type: bookingForm.appointment_type,
          reason: bookingForm.reason,
          symptoms: bookingForm.symptoms,
        }),
      })
      const data = await res.json()
      if (res.ok) {
        setConfirmedAppointment(data.appointment)
        setBookingSuccess(true)
        setBookingOpen(false)
        fetchSlots()
      } else {
        setError(data.message || 'فشل الحجز')
      }
    } catch {
      setError('خطأ في الاتصال بالخادم')
    } finally {
      setBookingLoading(false)
    }
  }

  // Group slots by date
  const slotsByDate = slots.reduce((acc, slot) => {
    if (!acc[slot.date]) acc[slot.date] = []
    acc[slot.date].push(slot)
    return acc
  }, {})
  const availableDates = Object.keys(slotsByDate)
  const visibleSlots = slotsByDate[selectedDate] || []

  const formatDate = (iso) => {
    const d = new Date(iso)
    return d.toLocaleDateString('ar-EG', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
  }

  const formatDateShort = (iso) => new Date(`${iso}T00:00:00`).toLocaleDateString('ar-EG', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
    </div>
  )

  if (error && !doctor) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-3" />
        <p className="text-gray-600">{error}</p>
        <button onClick={() => navigate('/doctors')} className="mt-4 text-blue-600 hover:underline">
          العودة لقائمة الأطباء
        </button>
      </div>
    </div>
  )

  if (!doctor) return null

  const stars = Array.from({ length: 5 }, (_, i) => i < Math.round(doctor.rating || 0))

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">

        {/* Back */}
        <button onClick={() => navigate('/doctors')}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 transition-colors">
          <ChevronRight className="h-4 w-4" />
          العودة للأطباء
        </button>

        {/* Doctor Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <div className="flex flex-col sm:flex-row gap-5">
            {/* Avatar */}
            <div className="w-24 h-24 rounded-2xl flex items-center justify-center text-white text-3xl font-bold flex-shrink-0"
              style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}>
              {doctor.first_name?.charAt(0)}
            </div>
            {/* Info */}
            <div className="flex-1">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <h1 className="text-xl font-bold text-gray-900">د. {doctor.first_name} {doctor.last_name}</h1>
                    {doctor.is_verified && (
                      <span className="flex items-center gap-1 px-2 py-0.5 bg-green-50 text-green-700 text-xs rounded-full font-medium">
                        <CheckCircle className="h-3 w-3" /> موثق
                      </span>
                    )}
                    {doctor.available_for_telemedicine && (
                      <span className="flex items-center gap-1 px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">
                        <Video className="h-3 w-3" /> عيادة افتراضية
                      </span>
                    )}
                  </div>
                  <p className="text-blue-600 font-medium mt-1">{doctor.specialization}</p>
                  {doctor.sub_specialization && (
                    <p className="text-gray-500 text-sm">{doctor.sub_specialization}</p>
                  )}
                </div>
                {/* Fee */}
                {doctor.consultation_fee && (
                  <div className="text-right">
                    <p className="text-2xl font-bold text-gray-900">{doctor.consultation_fee} ج.م</p>
                    <p className="text-xs text-gray-400">رسوم الكشف</p>
                  </div>
                )}
              </div>

              {/* Meta */}
              <div className="flex flex-wrap gap-4 mt-4 text-sm text-gray-600">
                {doctor.years_of_experience && (
                  <span className="flex items-center gap-1.5">
                    <Award className="h-4 w-4 text-yellow-500" />
                    {doctor.years_of_experience} سنة خبرة
                  </span>
                )}
                {doctor.clinic_name && (
                  <span className="flex items-center gap-1.5">
                    <Stethoscope className="h-4 w-4 text-blue-400" />
                    {doctor.clinic_name}
                  </span>
                )}
                {doctor.clinic_address && (
                  <span className="flex items-center gap-1.5">
                    <MapPin className="h-4 w-4 text-red-400" />
                    {doctor.clinic_address}
                  </span>
                )}
                {doctor.consultation_duration && (
                  <span className="flex items-center gap-1.5">
                    <Clock className="h-4 w-4 text-purple-400" />
                    {doctor.consultation_duration} دقيقة
                  </span>
                )}
              </div>

              {/* Rating */}
              <div className="flex items-center gap-2 mt-3">
                <div className="flex gap-0.5">
                  {stars.map((filled, i) => (
                    <Star key={i} className={`h-4 w-4 ${filled ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`} />
                  ))}
                </div>
                <span className="text-sm font-semibold text-gray-700">{(doctor.rating || 0).toFixed(1)}</span>
                <span className="text-sm text-gray-400">({doctor.total_reviews || 0} تقييم)</span>
                {doctor.appointments_count > 0 && (
                  <span className="text-sm text-gray-400">• {doctor.appointments_count} حالة منجزة</span>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Slots panel */}
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-blue-500" />
                  الأوقات المتاحة
                </h2>
                <select
                  value={slotDays}
                  onChange={e => setSlotDays(Number(e.target.value))}
                  className="text-sm border border-gray-200 rounded-lg px-2 py-1 text-gray-700 focus:outline-none"
                >
                  <option value={7}>أسبوع</option>
                  <option value={14}>أسبوعان</option>
                  <option value={30}>شهر</option>
                </select>
              </div>

              {slotsLoading ? (
                <div className="flex justify-center py-10">
                  <Loader2 className="h-6 w-6 animate-spin text-blue-400" />
                </div>
              ) : Object.keys(slotsByDate).length === 0 ? (
                <div className="text-center py-10 text-gray-400">
                  <Calendar className="h-10 w-10 opacity-30 mx-auto mb-2" />
                  <p className="text-sm">لا توجد أوقات متاحة خلال هذه الفترة</p>
                </div>
              ) : (
                <div className="space-y-5">
                  <div className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1" role="tablist" aria-label="اختر تاريخ الموعد">
                    {availableDates.map(date => (
                      <button
                        key={date}
                        type="button"
                        role="tab"
                        aria-selected={selectedDate === date}
                        onClick={() => { setSelectedDate(date); setSelectedSlot(null) }}
                        className={`min-w-[92px] rounded-xl border px-3 py-2 text-center text-xs font-semibold transition ${
                          selectedDate === date
                            ? 'border-blue-600 bg-blue-600 text-white shadow-sm'
                            : 'border-slate-200 bg-white text-slate-600 hover:border-blue-300 hover:bg-blue-50'
                        }`}
                      >
                        <span className="block">{formatDateShort(date)}</span>
                      </button>
                    ))}
                  </div>
                  <div>
                    <p className="mb-2 text-sm font-bold text-slate-800">{selectedDate && formatDate(selectedDate)}</p>
                    <div className="flex flex-wrap gap-2">
                      {visibleSlots.map(slot => (
                        <button
                          key={slot.datetime}
                          type="button"
                          disabled={!slot.available}
                          onClick={() => { setSelectedSlot(slot); setBookingOpen(true) }}
                          aria-label={`${slot.time}${slot.available ? '' : ' غير متاح'}`}
                          className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition-all ${
                            !slot.available
                              ? 'cursor-not-allowed border-slate-100 bg-slate-100 text-slate-400 line-through'
                              : selectedSlot?.datetime === slot.datetime
                                ? 'border-blue-600 text-white'
                                : 'border-slate-200 text-slate-700 hover:border-blue-400 hover:bg-blue-50'
                          }`}
                          style={selectedSlot?.datetime === slot.datetime && slot.available
                            ? { background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }
                            : {}}
                        >
                          {slot.time}
                        </button>
                      ))}
                    </div>
                    <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-500">
                      <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-blue-600" /> متاح للحجز</span>
                      <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-full bg-slate-300" /> محجوز</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Reviews */}
            {doctor.reviews?.length > 0 && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                <h2 className="text-base font-bold text-gray-900 mb-4">آراء المرضى</h2>
                <div className="space-y-4">
                  {doctor.reviews.map(r => (
                    <div key={r.id} className="border-b border-gray-50 pb-4 last:border-0 last:pb-0">
                      <div className="flex items-center gap-2 mb-1.5">
                        <div className="flex gap-0.5">
                          {Array.from({ length: 5 }, (_, i) => (
                            <Star key={i} className={`h-3.5 w-3.5 ${i < r.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-200'}`} />
                          ))}
                        </div>
                        <span className="text-xs font-medium text-gray-700">{r.patient_name}</span>
                        <span className="text-xs text-gray-400 mr-auto">
                          {r.created_at ? new Date(r.created_at).toLocaleDateString('ar-EG') : ''}
                        </span>
                      </div>
                      {r.review && <p className="text-sm text-gray-600 leading-relaxed">{r.review}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Availability summary */}
            {doctor.availability?.length > 0 && (
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
                <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-500" />
                  أوقات العمل
                </h3>
                <div className="space-y-2">
                  {doctor.availability.map((a, i) => (
                    <div key={i} className="flex justify-between text-sm">
                      <span className="text-gray-600">{a.day}</span>
                      <span className="text-gray-500 font-medium">{a.start} – {a.end}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Book CTA */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
              <h3 className="text-sm font-bold text-gray-900 mb-3">حجز موعد</h3>
              {bookingSuccess ? (
                <div className="text-center py-3">
                  <CheckCircle className="h-10 w-10 text-green-500 mx-auto mb-2" />
                  <p className="text-sm font-semibold text-green-700">تم الحجز بنجاح!</p>
                  {confirmedAppointment && (
                    <div className="mt-3 rounded-xl bg-emerald-50 p-3 text-right text-xs text-emerald-800">
                      <p className="font-bold">د. {doctor.first_name} {doctor.last_name}</p>
                      <p className="mt-1">{doctor.specialization}</p>
                      <p className="mt-1">{formatDate(confirmedAppointment.appointment_date)} — {new Date(confirmedAppointment.appointment_date).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })}</p>
                      <p className="mt-1">الحالة: بانتظار تأكيد الطبيب</p>
                    </div>
                  )}
                  <p className="text-xs text-gray-500 mt-2">تم إرسال إشعار إلى الطبيب</p>
                  <button onClick={() => navigate('/appointments')}
                    className="mt-3 w-full py-2 text-sm text-blue-600 border border-blue-200 rounded-xl hover:bg-blue-50 transition-colors">
                    عرض مواعيدي
                  </button>
                </div>
              ) : (
                <p className="text-sm text-gray-500">
                  اختر وقتاً من التقويم لبدء الحجز
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Booking Modal */}
      {bookingOpen && selectedSlot && !bookingSuccess && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md" dir="rtl">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <h3 className="font-bold text-gray-900">تأكيد الحجز</h3>
              <button onClick={() => setBookingOpen(false)} className="p-1 text-gray-400 hover:text-gray-600">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="px-6 py-5 space-y-4">
              <div className="p-3 rounded-xl bg-blue-50 text-sm text-blue-800">
                <p className="font-semibold">د. {doctor.first_name} {doctor.last_name}</p>
                <p className="mt-0.5">{formatDate(selectedSlot.date)} — {selectedSlot.time}</p>
                {doctor.consultation_fee && (
                  <p className="mt-0.5">رسوم الكشف: {doctor.consultation_fee} ج.م</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">نوع الزيارة</label>
                <select
                  value={bookingForm.appointment_type}
                  onChange={e => setBookingForm(f => ({ ...f, appointment_type: e.target.value }))}
                  className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                >
                  <option value="in_person">حضوري</option>
                  {doctor.available_for_telemedicine && <option value="telemedicine">عبر الإنترنت</option>}
                  <option value="home_visit">زيارة منزلية</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">سبب الزيارة</label>
                <input
                  type="text"
                  placeholder="مثال: فحص دوري، متابعة علاج..."
                  value={bookingForm.reason}
                  onChange={e => setBookingForm(f => ({ ...f, reason: e.target.value }))}
                  className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">الأعراض (اختياري)</label>
                <textarea
                  rows={2}
                  placeholder="صف الأعراض التي تعاني منها..."
                  value={bookingForm.symptoms}
                  onChange={e => setBookingForm(f => ({ ...f, symptoms: e.target.value }))}
                  className="w-full border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none"
                />
              </div>

              {error && (
                <p className="text-sm text-red-600 flex items-center gap-1.5">
                  <AlertCircle className="h-4 w-4" /> {error}
                </p>
              )}

              {!isAuthenticated && (
                <p className="text-sm text-amber-700 bg-amber-50 rounded-xl p-3">
                  يجب تسجيل الدخول أولاً لحجز موعد
                </p>
              )}
            </div>
            <div className="px-6 pb-5 flex gap-3">
              <button
                onClick={() => setBookingOpen(false)}
                className="flex-1 py-2.5 text-sm font-medium text-gray-700 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                إلغاء
              </button>
              <button
                onClick={isAuthenticated ? handleBook : () => navigate('/login')}
                disabled={bookingLoading}
                className="flex-1 py-2.5 text-sm font-semibold text-white rounded-xl transition-all hover:opacity-90 disabled:opacity-60 flex items-center justify-center gap-2"
                style={{ background: 'linear-gradient(135deg, #0f2444 0%, #2563eb 100%)' }}
              >
                {bookingLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Calendar className="h-4 w-4" />}
                {isAuthenticated ? 'تأكيد الحجز' : 'تسجيل الدخول للحجز'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
