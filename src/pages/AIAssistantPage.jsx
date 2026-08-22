import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Bot, 
  Send, 
  Mic, 
  MicOff, 
  Upload, 
  Image as ImageIcon,
  FileText,
  Heart,
  Brain,
  Stethoscope,
  Pill,
  Activity,
  User,
  Clock,
  CheckCircle,
  AlertCircle,
  Camera,
  X
} from 'lucide-react'

export default function AIAssistantPage() {
  const [activeTab, setActiveTab] = useState('chat')
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [symptoms, setSymptoms] = useState([''])
  const [analysisResult, setAnalysisResult] = useState(null)
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)

  // رسائل ترحيبية
  const welcomeMessages = [
    {
      id: 1,
      type: 'bot',
      content: 'مرحباً بك في المساعد الطبي الذكي! أنا هنا لمساعدتك في الاستشارات الطبية الأولية.',
      timestamp: new Date().toISOString()
    },
    {
      id: 2,
      type: 'bot',
      content: 'يمكنني مساعدتك في:\n• الإجابة على الأسئلة الطبية\n• تحليل الأعراض\n• فحص الصور الطبية\n• تقديم نصائح صحية\n• فحص تفاعل الأدوية',
      timestamp: new Date().toISOString()
    }
  ]

  useEffect(() => {
    setMessages(welcomeMessages)
  // welcomeMessages is an immutable initial value for this component.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // إرسال سياق المحادثة الكاملة للحصول على ردود أكثر دقة
      const conversationHistory = messages
        .filter(m => m.type === 'user' || m.type === 'bot')
        .slice(-10)  // آخر 10 رسائل
        .map(m => ({
          role: m.type === 'user' ? 'user' : 'assistant',
          content: m.content,
        }))

      const response = await fetch('/api/ai/voice-assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          message: inputMessage,
          history: conversationHistory,
        })
      })

      const data = await response.json()

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.response || 'عذراً، لم أتمكن من فهم سؤالك. يرجى المحاولة مرة أخرى.',
        urgency: data.urgency_level,
        specialty: data.recommended_specialty,
        timestamp: new Date().toISOString()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('خطأ في إرسال الرسالة:', error)
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'عذراً، حدث خطأ في النظام. يرجى المحاولة مرة أخرى.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('المتصفح لا يدعم التعرف على الصوت')
      return
    }

    const recognition = new window.webkitSpeechRecognition()
    recognition.lang = 'ar-SA'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => {
      setIsListening(true)
    }

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      setInputMessage(transcript)
      setIsListening(false)
    }

    recognition.onerror = () => {
      setIsListening(false)
      alert('حدث خطأ في التعرف على الصوت')
    }

    recognition.onend = () => {
      setIsListening(false)
    }

    recognition.start()
  }

  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      setSelectedImage(file)
      const reader = new FileReader()
      reader.onload = (e) => {
        setImagePreview(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleImageAnalysis = async () => {
    if (!selectedImage) return

    setIsLoading(true)
    const formData = new FormData()
    formData.append('image', selectedImage)
    formData.append('image_type', 'general')

    try {
      const response = await fetch('/api/ai/analyze-image', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      })

      const data = await response.json()
      setAnalysisResult(data)
    } catch (error) {
      console.error('خطأ في تحليل الصورة:', error)
      alert('حدث خطأ في تحليل الصورة')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSymptomChange = (index, value) => {
    const newSymptoms = [...symptoms]
    newSymptoms[index] = value
    setSymptoms(newSymptoms)
  }

  const addSymptom = () => {
    setSymptoms([...symptoms, ''])
  }

  const removeSymptom = (index) => {
    if (symptoms.length > 1) {
      const newSymptoms = symptoms.filter((_, i) => i !== index)
      setSymptoms(newSymptoms)
    }
  }

  const handleSymptomCheck = async () => {
    const validSymptoms = symptoms.filter(s => s.trim())
    if (validSymptoms.length === 0) return

    setIsLoading(true)

    try {
      const response = await fetch('/api/ai/symptom-checker', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          symptoms: validSymptoms
        })
      })

      const data = await response.json()
      setAnalysisResult(data)
    } catch (error) {
      console.error('خطأ في فحص الأعراض:', error)
      alert('حدث خطأ في فحص الأعراض')
    } finally {
      setIsLoading(false)
    }
  }

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'عاجل': return 'text-red-600 bg-red-100'
      case 'متوسط': return 'text-yellow-600 bg-yellow-100'
      default: return 'text-green-600 bg-green-100'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* الرأس */}
        <div className="text-center mb-12">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-100 p-4 rounded-full">
              <Bot className="h-12 w-12 text-blue-600" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            المساعد الطبي الذكي
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            مساعد ذكي متطور لتقديم الاستشارات الطبية الأولية وتحليل الصور الطبية
          </p>
        </div>

        {/* التبويبات */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 rtl:space-x-reverse px-6">
              <button
                onClick={() => setActiveTab('chat')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'chat'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Bot className="h-4 w-4 inline ml-2" />
                المحادثة الذكية
              </button>
              <button
                onClick={() => setActiveTab('image')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'image'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <ImageIcon className="h-4 w-4 inline ml-2" />
                تحليل الصور
              </button>
              <button
                onClick={() => setActiveTab('symptoms')}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === 'symptoms'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Stethoscope className="h-4 w-4 inline ml-2" />
                فحص الأعراض
              </button>
            </nav>
          </div>

          <div className="p-6">
            {/* تبويب المحادثة */}
            {activeTab === 'chat' && (
              <div className="space-y-6">
                {/* منطقة الرسائل */}
                <div className="bg-gray-50 rounded-lg p-4 h-96 overflow-y-auto">
                  <div className="space-y-4">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                            message.type === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-white text-gray-800 border border-gray-200'
                          }`}
                        >
                          <div className="whitespace-pre-wrap">{message.content}</div>
                          {message.urgency && (
                            <div className={`mt-2 px-2 py-1 text-xs rounded-full inline-block ${getUrgencyColor(message.urgency)}`}>
                              {message.urgency}
                            </div>
                          )}
                          {message.specialty && (
                            <div className="mt-1 text-xs text-gray-500">
                              التخصص المقترح: {message.specialty}
                            </div>
                          )}
                          <div className="text-xs opacity-70 mt-1">
                            {new Date(message.timestamp).toLocaleTimeString('ar-SA')}
                          </div>
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex justify-start">
                        <div className="bg-white text-gray-800 border border-gray-200 px-4 py-2 rounded-lg">
                          <div className="flex items-center space-x-2 rtl:space-x-reverse">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                            <span>جاري الكتابة...</span>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                </div>

                {/* منطقة الإدخال */}
                <div className="flex space-x-2 rtl:space-x-reverse">
                  <div className="flex-1">
                    <Input
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="اكتب سؤالك الطبي هنا..."
                      disabled={isLoading}
                    />
                  </div>
                  <Button
                    onClick={handleVoiceInput}
                    variant="outline"
                    disabled={isLoading}
                    className={isListening ? 'bg-red-100 text-red-600' : ''}
                  >
                    {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  </Button>
                  <Button
                    onClick={handleSendMessage}
                    disabled={isLoading || !inputMessage.trim()}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>

                {/* نصائح سريعة */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {[
                    'ما هي أعراض الإنفلونزا؟',
                    'نصائح للنوم الصحي',
                    'كيف أتعامل مع الصداع؟',
                    'أطعمة مفيدة للقلب'
                  ].map((tip, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(tip)}
                      className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg transition-colors"
                    >
                      {tip}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* تبويب تحليل الصور */}
            {activeTab === 'image' && (
              <div className="space-y-6">
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    تحليل الصور الطبية بالذكاء الاصطناعي
                  </h3>
                  <p className="text-gray-600 mb-6">
                    ارفع صورة طبية (أشعة، تحاليل، إلخ) للحصول على تحليل أولي
                  </p>
                </div>

                {/* منطقة رفع الصورة */}
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  {imagePreview ? (
                    <div className="space-y-4">
                      <img
                        src={imagePreview}
                        alt="معاينة الصورة"
                        className="max-w-full max-h-64 mx-auto rounded-lg"
                      />
                      <div className="flex justify-center space-x-2 rtl:space-x-reverse">
                        <Button
                          onClick={handleImageAnalysis}
                          disabled={isLoading}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          {isLoading ? 'جاري التحليل...' : 'تحليل الصورة'}
                        </Button>
                        <Button
                          onClick={() => {
                            setSelectedImage(null)
                            setImagePreview(null)
                            setAnalysisResult(null)
                          }}
                          variant="outline"
                        >
                          <X className="h-4 w-4 ml-1" />
                          إزالة
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <Camera className="h-16 w-16 text-gray-400 mx-auto" />
                      <div>
                        <Button
                          onClick={() => fileInputRef.current?.click()}
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          <Upload className="h-4 w-4 ml-2" />
                          اختر صورة
                        </Button>
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="image/*"
                          onChange={handleImageUpload}
                          className="hidden"
                        />
                      </div>
                      <p className="text-sm text-gray-500">
                        PNG, JPG, GIF حتى 16MB
                      </p>
                    </div>
                  )}
                </div>

                {/* نتائج التحليل */}
                {analysisResult && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h4 className="font-semibold text-blue-800 mb-4 flex items-center">
                      <Brain className="h-5 w-5 ml-2" />
                      نتائج التحليل
                    </h4>
                    <div className="space-y-4">
                      {analysisResult.success ? (
                        <>
                          <div className="bg-white p-4 rounded-lg">
                            <h5 className="font-medium mb-2">التحليل:</h5>
                            <p className="text-gray-700 whitespace-pre-wrap">
                              {analysisResult.analysis}
                            </p>
                          </div>
                          {analysisResult.urgency_level && (
                            <div className={`px-3 py-2 rounded-lg ${getUrgencyColor(analysisResult.urgency_level)}`}>
                              مستوى الإلحاح: {analysisResult.urgency_level}
                            </div>
                          )}
                          {analysisResult.recommendations && (
                            <div className="bg-white p-4 rounded-lg">
                              <h5 className="font-medium mb-2">التوصيات:</h5>
                              <ul className="list-disc list-inside space-y-1">
                                {analysisResult.recommendations.map((rec, index) => (
                                  <li key={index} className="text-gray-700">{rec}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="text-red-600">
                          خطأ في التحليل: {analysisResult.error}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <Alert className="border-yellow-200 bg-yellow-50">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-yellow-700">
                    هذا التحليل للمساعدة فقط ولا يغني عن استشارة طبيب مختص.
                  </AlertDescription>
                </Alert>
              </div>
            )}

            {/* تبويب فحص الأعراض */}
            {activeTab === 'symptoms' && (
              <div className="space-y-6">
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    فحص الأعراض الذكي
                  </h3>
                  <p className="text-gray-600 mb-6">
                    أدخل الأعراض التي تشعر بها للحصول على تقييم أولي
                  </p>
                </div>

                {/* إدخال الأعراض */}
                <div className="space-y-4">
                  <Label>الأعراض:</Label>
                  {symptoms.map((symptom, index) => (
                    <div key={index} className="flex space-x-2 rtl:space-x-reverse">
                      <Input
                        value={symptom}
                        onChange={(e) => handleSymptomChange(index, e.target.value)}
                        placeholder={`العرض ${index + 1}`}
                        className="flex-1"
                      />
                      {symptoms.length > 1 && (
                        <Button
                          onClick={() => removeSymptom(index)}
                          variant="outline"
                          size="sm"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  ))}
                  
                  <div className="flex space-x-2 rtl:space-x-reverse">
                    <Button onClick={addSymptom} variant="outline">
                      إضافة عرض
                    </Button>
                    <Button
                      onClick={handleSymptomCheck}
                      disabled={isLoading || symptoms.every(s => !s.trim())}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {isLoading ? 'جاري الفحص...' : 'فحص الأعراض'}
                    </Button>
                  </div>
                </div>

                {/* نتائج فحص الأعراض */}
                {analysisResult && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <h4 className="font-semibold text-green-800 mb-4 flex items-center">
                      <Activity className="h-5 w-5 ml-2" />
                      نتائج فحص الأعراض
                    </h4>
                    <div className="space-y-4">
                      {analysisResult.success ? (
                        <>
                          <div className="bg-white p-4 rounded-lg">
                            <h5 className="font-medium mb-2">التحليل:</h5>
                            <p className="text-gray-700 whitespace-pre-wrap">
                              {analysisResult.analysis}
                            </p>
                          </div>
                          {analysisResult.urgency_assessment && (
                            <div className={`px-3 py-2 rounded-lg ${getUrgencyColor(analysisResult.urgency_assessment)}`}>
                              تقييم الإلحاح: {analysisResult.urgency_assessment}
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="text-red-600">
                          خطأ في الفحص: {analysisResult.error}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <Alert className="border-blue-200 bg-blue-50">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription className="text-blue-700">
                    هذا الفحص للتوجيه الأولي فقط. في حالة الأعراض الشديدة، يرجى مراجعة الطبيب فوراً.
                  </AlertDescription>
                </Alert>
              </div>
            )}
          </div>
        </div>

        {/* ميزات إضافية */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center mb-4">
              <Heart className="h-8 w-8 text-red-500 ml-3" />
              <h3 className="text-lg font-semibold">نصائح صحية</h3>
            </div>
            <p className="text-gray-600 mb-4">
              احصل على نصائح صحية مخصصة بناءً على حالتك الصحية
            </p>
            <Button variant="outline" className="w-full">
              احصل على نصائح
            </Button>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center mb-4">
              <Pill className="h-8 w-8 text-blue-500 ml-3" />
              <h3 className="text-lg font-semibold">فحص الأدوية</h3>
            </div>
            <p className="text-gray-600 mb-4">
              تحقق من التفاعلات بين الأدوية والآثار الجانبية
            </p>
            <Button variant="outline" className="w-full">
              فحص الأدوية
            </Button>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center mb-4">
              <FileText className="h-8 w-8 text-green-500 ml-3" />
              <h3 className="text-lg font-semibold">تقارير طبية</h3>
            </div>
            <p className="text-gray-600 mb-4">
              إنتاج تقارير طبية شاملة بناءً على الفحوصات
            </p>
            <Button variant="outline" className="w-full">
              إنشاء تقرير
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

