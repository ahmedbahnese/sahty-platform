import { useState, useRef, useEffect, useCallback } from 'react'
import { Bot, Send, X, Minus, Maximize2, Mic, MicOff, MessageCircle } from 'lucide-react'

export default function FloatingAIChat() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'مرحباً! أنا مساعدك الطبي الذكي 🩺\nكيف يمكنني مساعدتك اليوم؟',
      time: new Date().toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' })
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [position, setPosition] = useState({ x: null, y: null })
  const [dragging, setDragging] = useState(false)
  const dragOffset = useRef({ x: 0, y: 0 })
  const chatRef = useRef(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (isOpen && !isMinimized) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isOpen, isMinimized])

  // Drag functionality
  const handleMouseDown = useCallback((e) => {
    if (e.target.closest('button') || e.target.closest('input') || e.target.closest('textarea')) return
    setDragging(true)
    const rect = chatRef.current.getBoundingClientRect()
    dragOffset.current = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    }
    e.preventDefault()
  }, [])

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!dragging) return
      const newX = e.clientX - dragOffset.current.x
      const newY = e.clientY - dragOffset.current.y
      const maxX = window.innerWidth - (chatRef.current?.offsetWidth || 380)
      const maxY = window.innerHeight - (chatRef.current?.offsetHeight || 500)
      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      })
    }
    const handleMouseUp = () => setDragging(false)
    if (dragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [dragging])

  // Touch drag
  const handleTouchStart = useCallback((e) => {
    if (e.target.closest('button') || e.target.closest('input') || e.target.closest('textarea')) return
    const touch = e.touches[0]
    setDragging(true)
    const rect = chatRef.current.getBoundingClientRect()
    dragOffset.current = {
      x: touch.clientX - rect.left,
      y: touch.clientY - rect.top
    }
  }, [])

  useEffect(() => {
    const handleTouchMove = (e) => {
      if (!dragging) return
      const touch = e.touches[0]
      const newX = touch.clientX - dragOffset.current.x
      const newY = touch.clientY - dragOffset.current.y
      const maxX = window.innerWidth - (chatRef.current?.offsetWidth || 340)
      const maxY = window.innerHeight - (chatRef.current?.offsetHeight || 500)
      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      })
    }
    const handleTouchEnd = () => setDragging(false)
    if (dragging) {
      document.addEventListener('touchmove', handleTouchMove, { passive: false })
      document.addEventListener('touchend', handleTouchEnd)
    }
    return () => {
      document.removeEventListener('touchmove', handleTouchMove)
      document.removeEventListener('touchend', handleTouchEnd)
    }
  }, [dragging])

  const sendMessage = async () => {
    if (!input.trim() || loading) return
    const userMsg = {
      id: Date.now(),
      type: 'user',
      content: input.trim(),
      time: new Date().toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' })
    }
    setMessages(prev => [...prev, userMsg])
    const userInput = input.trim()
    setInput('')
    setLoading(true)

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/ai/voice-assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ message: userInput })
      })
      const data = await response.json()
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        content: data.response || 'عذراً، لم أتمكن من معالجة طلبك. يرجى المحاولة مرة أخرى.',
        urgency: data.urgency_level,
        time: new Date().toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' })
      }])
    } catch {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'bot',
        content: 'عذراً، حدث خطأ في الاتصال. يرجى التحقق من اتصالك والمحاولة مرة أخرى.',
        time: new Date().toLocaleTimeString('ar-SA', { hour: '2-digit', minute: '2-digit' })
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleVoice = () => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      alert('المتصفح لا يدعم التعرف على الصوت')
      return
    }
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    recognition.lang = 'ar-SA'
    recognition.onstart = () => setIsListening(true)
    recognition.onresult = (e) => {
      setInput(e.results[0][0].transcript)
      setIsListening(false)
    }
    recognition.onerror = () => setIsListening(false)
    recognition.onend = () => setIsListening(false)
    recognition.start()
  }

  const chatStyle = position.x !== null ? {
    position: 'fixed',
    left: `${position.x}px`,
    top: `${position.y}px`,
    bottom: 'auto',
    right: 'auto',
    zIndex: 9999
  } : {
    position: 'fixed',
    bottom: '24px',
    left: '24px',
    zIndex: 9999
  }

  const urgencyColor = (urgency) => {
    if (!urgency) return ''
    if (urgency === 'high' || urgency === 'عالي') return 'border-r-4 border-red-500'
    if (urgency === 'medium' || urgency === 'متوسط') return 'border-r-4 border-yellow-500'
    return 'border-r-4 border-green-500'
  }

  if (!isOpen) {
    return (
      <div style={chatStyle}>
        <button
          onClick={() => setIsOpen(true)}
          className="group flex items-center gap-2 bg-navy-700 hover:bg-navy-800 text-white rounded-full shadow-2xl transition-all duration-300 hover:scale-105 px-4 py-3"
          style={{ background: 'linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)' }}
          title="المساعد الطبي الذكي"
        >
          <Bot className="h-6 w-6" />
          <span className="text-sm font-medium hidden sm:block">المساعد الذكي</span>
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></span>
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"></span>
        </button>
      </div>
    )
  }

  return (
    <div style={chatStyle} ref={chatRef}>
      <div
        className={`bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-gray-200 transition-all duration-300 ${isMinimized ? 'h-auto' : 'h-[520px]'}`}
        style={{ width: '360px', maxWidth: '95vw' }}
      >
        {/* Header */}
        <div
          className="flex items-center justify-between px-4 py-3 cursor-grab active:cursor-grabbing select-none"
          style={{ background: 'linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)' }}
          onMouseDown={handleMouseDown}
          onTouchStart={handleTouchStart}
        >
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-400 rounded-full border-2 border-white"></span>
            </div>
            <div>
              <p className="text-white font-semibold text-sm">المساعد الطبي الذكي</p>
              <p className="text-blue-200 text-xs">متاح دائماً · جاهز للمساعدة</p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="text-white/70 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition-colors"
              title={isMinimized ? 'تكبير' : 'تصغير'}
            >
              {isMinimized ? <Maximize2 className="h-4 w-4" /> : <Minus className="h-4 w-4" />}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white/70 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition-colors"
              title="إغلاق"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-start' : 'justify-end'}`}>
                  {msg.type === 'bot' && (
                    <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 ml-2 mt-1">
                      <Bot className="h-4 w-4 text-blue-700" />
                    </div>
                  )}
                  <div className={`max-w-[78%] ${msg.type === 'user' ? 'order-first' : ''}`}>
                    <div
                      className={`rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-line ${
                        msg.type === 'user'
                          ? 'bg-blue-600 text-white rounded-br-sm'
                          : `bg-white text-gray-800 shadow-sm rounded-bl-sm ${urgencyColor(msg.urgency)}`
                      }`}
                    >
                      {msg.content}
                    </div>
                    <p className={`text-xs text-gray-400 mt-1 ${msg.type === 'user' ? 'text-right' : 'text-left'}`}>
                      {msg.time}
                    </p>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-end">
                  <div className="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 ml-2">
                    <Bot className="h-4 w-4 text-blue-700" />
                  </div>
                  <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                    <div className="flex gap-1 items-center">
                      <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                      <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                      <span className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick suggestions */}
            {messages.length <= 2 && (
              <div className="px-3 py-2 bg-white border-t border-gray-100 flex gap-2 overflow-x-auto">
                {['ما هي أعراض الإنفلونزا؟', 'كيف أتحكم في ضغط الدم؟', 'نصائح للنوم الصحي'].map(s => (
                  <button
                    key={s}
                    onClick={() => setInput(s)}
                    className="text-xs bg-blue-50 text-blue-700 px-3 py-1.5 rounded-full whitespace-nowrap hover:bg-blue-100 transition-colors border border-blue-100 flex-shrink-0"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}

            {/* Input */}
            <div className="p-3 bg-white border-t border-gray-200">
              <div className="flex items-end gap-2">
                <button
                  onClick={handleVoice}
                  className={`p-2 rounded-xl transition-colors flex-shrink-0 ${
                    isListening ? 'bg-red-100 text-red-600 animate-pulse' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                  }`}
                  title="إدخال صوتي"
                >
                  {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                </button>
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="اكتب سؤالك الطبي..."
                  className="flex-1 resize-none border border-gray-200 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-200 transition-all bg-gray-50"
                  rows={1}
                  style={{ maxHeight: '80px', direction: 'rtl' }}
                  onInput={(e) => {
                    e.target.style.height = 'auto'
                    e.target.style.height = Math.min(e.target.scrollHeight, 80) + 'px'
                  }}
                />
                <button
                  onClick={sendMessage}
                  disabled={!input.trim() || loading}
                  className="p-2 rounded-xl text-white transition-all flex-shrink-0 disabled:opacity-40"
                  style={{ background: 'linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%)' }}
                  title="إرسال"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
              <p className="text-xs text-gray-400 text-center mt-2">
                ⚠️ للاستشارة الأولية فقط — راجع طبيبك دائماً
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
