import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import {
  Stethoscope, Send, Upload, X, AlertTriangle, Clock, CheckCircle,
  Mic, MicOff, Plus, Image as ImageIcon, ChevronRight, AlertCircle
} from 'lucide-react'

const URGENCY_CONFIG = {
  'عاجل':   { color: 'bg-red-50 border-red-200 text-red-800',   icon: AlertTriangle, badge: 'bg-red-100 text-red-700' },
  'متوسط':  { color: 'bg-amber-50 border-amber-200 text-amber-800', icon: Clock, badge: 'bg-amber-100 text-amber-700' },
  'عادي':   { color: 'bg-green-50 border-green-200 text-green-800', icon: CheckCircle, badge: 'bg-green-100 text-green-700' },
}

function UrgencyBadge({ level }) {
  const cfg = URGENCY_CONFIG[level]
  if (!cfg) return null
  const Icon = cfg.icon
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold ${cfg.badge}`}>
      <Icon className="w-4 h-4" /> مستوى الإلحاح: {level}
    </span>
  )
}

export default function SymptomCheckerPage() {
  const [symptoms, setSymptoms] = useState([''])
  const [image, setImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [history, setHistory] = useState([])   // [{role, content}] for multi-turn
  const [messages, setMessages] = useState([]) // chat bubbles
  const [loading, setLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [followUpInput, setFollowUpInput] = useState('')
  const [phase, setPhase] = useState('input') // input | chat
  const fileRef = useRef(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const addSymptom = () => setSymptoms(s => [...s, ''])
  const removeSymptom = (i) => setSymptoms(s => s.filter((_, idx) => idx !== i))
  const updateSymptom = (i, v) => setSymptoms(s => s.map((x, idx) => idx === i ? v : x))

  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return
    setImage(file)
    const reader = new FileReader()
    reader.onload = (ev) => setImagePreview(ev.target.result)
    reader.readAsDataURL(file)
  }

  const handleVoice = (idx) => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert('المتصفح لا يدعم التعرف على الصوت')
      return
    }
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SR()
    recognition.lang = 'ar-SA'
    recognition.onstart = () => setIsListening(true)
    recognition.onresult = (e) => {
      updateSymptom(idx, e.results[0][0].transcript)
      setIsListening(false)
    }
    recognition.onerror = recognition.onend = () => setIsListening(false)
    recognition.start()
  }

  const callAPI = async (sympList, historyList, imgFile) => {
    const token = localStorage.getItem('token')
    const hdr = token ? { Authorization: `Bearer ${token}` } : {}

    if (imgFile) {
      const fd = new FormData()
      sympList.forEach(s => fd.append('symptoms', s))
      fd.append('symptoms', JSON.stringify(sympList))
      fd.append('history', JSON.stringify(historyList))
      if (imgFile) fd.append('image', imgFile)
      const res = await fetch('/api/ai/symptom-checker-v2', { method: 'POST', headers: hdr, body: fd })
      return res.json()
    } else {
      const res = await fetch('/api/ai/symptom-checker-v2', {
        method: 'POST',
        headers: { ...hdr, 'Content-Type': 'application/json' },
        body: JSON.stringify({ symptoms: sympList, history: historyList }),
      })
      return res.json()
    }
  }

  const startCheck = async () => {
    const valid = symptoms.filter(s => s.trim())
    if (!valid.length) return

    const userContent = `الأعراض:\n${valid.map(s => `• ${s}`).join('\n')}${image ? '\n(+ صورة مرفقة)' : ''}`
    const newMessages = [{ id: Date.now(), role: 'user', content: userContent }]
    setMessages(newMessages)
    setPhase('chat')
    setLoading(true)

    try {
      const data = await callAPI(valid, [], image)
      const botMsg = {
        id: Date.now() + 1, role: 'bot',
        content: data.analysis || data.error || 'عذراً، حدث خطأ.',
        urgency: data.urgency_assessment,
        specialty: data.recommended_specialty,
      }
      setMessages(prev => [...prev, botMsg])
      setHistory([
        { role: 'user', content: userContent },
        { role: 'assistant', content: botMsg.content },
      ])
    } catch {
      setMessages(prev => [...prev, { id: Date.now() + 2, role: 'bot', content: 'حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى.' }])
    } finally { setLoading(false) }
  }

  const sendFollowUp = async () => {
    if (!followUpInput.trim() || loading) return
    const userText = followUpInput.trim()
    setFollowUpInput('')

    const userMsg = { id: Date.now(), role: 'user', content: userText }
    setMessages(prev => [...prev, userMsg])
    setLoading(true)

    const newHistory = [...history, { role: 'user', content: userText }]

    try {
      const data = await callAPI([userText], newHistory, null)
      const botMsg = {
        id: Date.now() + 1, role: 'bot',
        content: data.analysis || data.error || 'عذراً، حدث خطأ.',
        urgency: data.urgency_assessment,
        specialty: data.recommended_specialty,
      }
      setMessages(prev => [...prev, botMsg])
      setHistory([...newHistory, { role: 'assistant', content: botMsg.content }])
    } catch {
      setMessages(prev => [...prev, { id: Date.now() + 2, role: 'bot', content: 'حدث خطأ في الاتصال.' }])
    } finally { setLoading(false) }
  }

  const reset = () => {
    setSymptoms([''])
    setImage(null)
    setImagePreview(null)
    setHistory([])
    setMessages([])
    setPhase('input')
    setFollowUpInput('')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-8" dir="rtl">
      <div className="max-w-3xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600 mb-4">
            <Stethoscope className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">فاحص الأعراض الذكي</h1>
          <p className="text-gray-500 max-w-md mx-auto">
            صف أعراضك وسيطرح المساعد أسئلة متابعة لتقييم حالتك وتوجيهك للتخصص المناسب
          </p>
        </div>

        {/* Disclaimer */}
        <div className="mb-6 bg-amber-50 border border-amber-200 rounded-2xl p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
          <p className="text-sm text-amber-700">
            <strong>تنبيه هام:</strong> هذه الأداة للتوجيه الأولي فقط ولا تُغني عن استشارة طبيب مختص.
            في حالات الطوارئ اتصل بالإسعاف فوراً.
          </p>
        </div>

        {/* Input phase */}
        {phase === 'input' && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 space-y-5">
            {/* Symptoms */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                ما الأعراض التي تشعر بها؟ *
              </label>
              <div className="space-y-2">
                {symptoms.map((s, i) => (
                  <div key={i} className="flex gap-2">
                    <div className="flex-1 flex items-center gap-2 border border-gray-200 rounded-xl px-3 py-2 bg-gray-50 focus-within:ring-2 focus-within:ring-blue-300 focus-within:border-blue-300 transition-all">
                      <ChevronRight className="w-4 h-4 text-gray-400 shrink-0" />
                      <input
                        value={s}
                        onChange={e => updateSymptom(i, e.target.value)}
                        onKeyDown={e => { if (e.key === 'Enter') { e.preventDefault(); addSymptom() } }}
                        placeholder={`العرض ${i + 1} (مثل: صداع شديد، حمى...)`}
                        className="flex-1 bg-transparent text-sm outline-none"
                      />
                      <button onClick={() => handleVoice(i)}
                        className={`p-1 rounded-lg transition-colors ${isListening ? 'text-red-500 animate-pulse' : 'text-gray-400 hover:text-gray-600'}`}>
                        {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                      </button>
                    </div>
                    {symptoms.length > 1 && (
                      <button onClick={() => removeSymptom(i)} className="p-2 text-gray-400 hover:text-red-500 transition-colors">
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
              <button onClick={addSymptom} className="mt-2 flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 transition-colors">
                <Plus className="w-4 h-4" /> إضافة عرض آخر
              </button>
            </div>

            {/* Quick symptom chips */}
            <div>
              <p className="text-xs text-gray-500 mb-2">اضغط لإضافة بسرعة:</p>
              <div className="flex flex-wrap gap-2">
                {['صداع', 'حمى', 'سعال', 'ضيق تنفس', 'آلام معدة', 'غثيان', 'دوخة', 'إرهاق', 'ألم صدر', 'طفح جلدي'].map(chip => (
                  <button key={chip} onClick={() => {
                    const empty = symptoms.findIndex(s => !s.trim())
                    if (empty >= 0) updateSymptom(empty, chip)
                    else setSymptoms(s => [...s, chip])
                  }}
                    className="text-xs bg-blue-50 text-blue-700 border border-blue-100 px-3 py-1.5 rounded-full hover:bg-blue-100 transition-colors">
                    {chip}
                  </button>
                ))}
              </div>
            </div>

            {/* Image upload */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                صورة للمنطقة المصابة (اختياري)
              </label>
              {imagePreview ? (
                <div className="relative inline-block">
                  <img src={imagePreview} alt="preview" className="h-32 rounded-xl object-cover border border-gray-200" />
                  <button onClick={() => { setImage(null); setImagePreview(null) }}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors">
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ) : (
                <button onClick={() => fileRef.current?.click()}
                  className="flex items-center gap-2 border-2 border-dashed border-gray-200 rounded-xl px-4 py-3 text-sm text-gray-500 hover:border-blue-300 hover:text-blue-600 transition-colors">
                  <ImageIcon className="w-5 h-5" />
                  رفع صورة (PNG, JPG)
                </button>
              )}
              <input ref={fileRef} type="file" accept="image/*" onChange={handleImageUpload} className="hidden" />
            </div>

            <Button
              onClick={startCheck}
              disabled={!symptoms.some(s => s.trim())}
              className="w-full bg-blue-600 hover:bg-blue-700 h-12 text-base font-semibold"
            >
              <Stethoscope className="w-5 h-5 ml-2" />
              ابدأ فحص الأعراض
            </Button>
          </div>
        )}

        {/* Chat phase */}
        {phase === 'chat' && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
            {/* Chat messages */}
            <div className="p-5 space-y-4 max-h-[500px] overflow-y-auto bg-gray-50">
              {messages.map(msg => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-start' : 'justify-end'}`}>
                  {msg.role === 'bot' && (
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0 ml-2 mt-1">
                      <Stethoscope className="w-4 h-4 text-blue-700" />
                    </div>
                  )}
                  <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-first' : ''}`}>
                    <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-line ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-sm'
                        : 'bg-white text-gray-800 shadow-sm rounded-bl-sm border border-gray-100'
                    }`}>
                      {msg.content}
                    </div>
                    {msg.role === 'bot' && (msg.urgency || msg.specialty) && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {msg.urgency && <UrgencyBadge level={msg.urgency} />}
                        {msg.specialty && (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-700 text-sm font-medium rounded-full border border-blue-100">
                            التخصص المقترح: {msg.specialty}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-end">
                  <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center shrink-0 ml-2">
                    <Stethoscope className="w-4 h-4 text-blue-700" />
                  </div>
                  <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm border border-gray-100">
                    <div className="flex gap-1">
                      {[0, 150, 300].map(d => (
                        <span key={d} className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: `${d}ms` }} />
                      ))}
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Follow-up input */}
            <div className="p-4 bg-white border-t border-gray-100">
              <div className="flex gap-2">
                <input
                  value={followUpInput}
                  onChange={e => setFollowUpInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendFollowUp() } }}
                  placeholder="أجب على أسئلة الطبيب أو أضف تفاصيل..."
                  className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300 focus:border-blue-300 transition-all bg-gray-50"
                  disabled={loading}
                />
                <Button onClick={sendFollowUp} disabled={!followUpInput.trim() || loading}
                  className="bg-blue-600 hover:bg-blue-700 px-4 rounded-xl">
                  <Send className="w-4 h-4" />
                </Button>
                <Button variant="outline" onClick={reset} className="rounded-xl text-gray-500">
                  بدء جديد
                </Button>
              </div>
              <p className="text-xs text-gray-400 text-center mt-2">
                ⚠️ هذا تقييم أولي فقط — راجع طبيبك دائماً قبل أي إجراء
              </p>
            </div>
          </div>
        )}

        {/* Education cards */}
        {phase === 'input' && (
          <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { icon: '🔍', title: 'تحليل دقيق', desc: 'يحلل الأعراض ويطرح أسئلة متابعة لتحسين التقييم' },
              { icon: '⚡', title: 'تقييم الإلحاح', desc: 'يحدد مستوى الإلحاح ومتى تحتاج رعاية طارئة' },
              { icon: '🏥', title: 'التخصص المناسب', desc: 'يوجهك لأنسب التخصصات الطبية لحالتك' },
            ].map((c, i) => (
              <div key={i} className="bg-white rounded-xl border border-gray-100 p-4 text-center shadow-sm">
                <div className="text-2xl mb-2">{c.icon}</div>
                <h3 className="font-semibold text-gray-900 text-sm mb-1">{c.title}</h3>
                <p className="text-xs text-gray-500">{c.desc}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
