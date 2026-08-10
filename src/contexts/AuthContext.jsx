import { createContext, useContext, useState, useEffect, useRef } from 'react'

const AuthContext = createContext()

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  // نستخدم ref للـ token حتى يمكن استخدامه داخل fetchUserProfile بدون closures قديمة
  const tokenRef = useRef(token)

  const API_BASE = '/api'

  useEffect(() => {
    tokenRef.current = token
  }, [token])

  // يعمل مرة واحدة عند التحميل الأولي فقط لاستعادة الجلسة
  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      fetchUserProfile(storedToken)
    } else {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchUserProfile = async (tokenToUse) => {
    const activeToken = tokenToUse || tokenRef.current
    if (!activeToken) {
      setLoading(false)
      return
    }
    try {
      const response = await fetch(`${API_BASE}/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${activeToken}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUser(data.user)
      } else if (response.status === 401) {
        // Token منتهي الصلاحية أو غير صالح — تسجيل خروج صامت
        _clearSession()
      }
      // أي خطأ آخر (500، network error) → نبقي المستخدم مسجلاً دخوله
    } catch {
      // خطأ شبكة أو الخادم غير متاح — لا نسجّل خروج المستخدم
      console.warn('تعذّر التحقق من الجلسة — الخادم غير متاح مؤقتاً')
    } finally {
      setLoading(false)
    }
  }

  const _clearSession = () => {
    setUser(null)
    setToken(null)
    tokenRef.current = null
    localStorage.removeItem('token')
  }

  const login = async (identifier, password) => {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier, password })
      })
      const data = await response.json()

      if (response.ok) {
        tokenRef.current = data.token
        setToken(data.token)
        setUser(data.user)
        localStorage.setItem('token', data.token)
        return { success: true, user: data.user }
      } else {
        return {
          success: false,
          message: data.message,
          pending_review: data.pending_review || false,
          provider_status: data.provider_status || 'pending',
        }
      }
    } catch {
      return { success: false, message: 'خطأ في الاتصال بالخادم' }
    }
  }

  const register = async (userData) => {
    try {
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      })
      const data = await response.json()

      if (response.ok) {
        if (data.token && data.user) {
          tokenRef.current = data.token
          setToken(data.token)
          setUser(data.user)
          localStorage.setItem('token', data.token)
        }
        return { success: true, message: data.message }
      } else {
        return { success: false, message: data.message }
      }
    } catch {
      return { success: false, message: 'خطأ في الاتصال بالخادم' }
    }
  }

  const switchRole = async (role) => {
    try {
      const response = await fetch(`${API_BASE}/auth/switch-role`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokenRef.current}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role })
      })
      const data = await response.json()
      if (!response.ok) return { success: false, message: data.message }
      tokenRef.current = data.token
      setToken(data.token)
      setUser(data.user)
      localStorage.setItem('token', data.token)
      return { success: true, user: data.user }
    } catch {
      return { success: false, message: 'خطأ في الاتصال بالخادم' }
    }
  }

  const logout = async () => {
    const currentToken = tokenRef.current
    _clearSession()
    try {
      if (currentToken) {
        await fetch(`${API_BASE}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${currentToken}`,
            'Content-Type': 'application/json'
          }
        })
      }
    } catch {
      // تجاهل أخطاء الشبكة عند تسجيل الخروج
    }
  }

  const changePassword = async (currentPassword, newPassword) => {
    try {
      const response = await fetch(`${API_BASE}/auth/change-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${tokenRef.current}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
      })
      const data = await response.json()
      return response.ok
        ? { success: true, message: data.message }
        : { success: false, message: data.message }
    } catch {
      return { success: false, message: 'خطأ في الاتصال بالخادم' }
    }
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    switchRole,
    logout,
    changePassword,
    isAuthenticated: !!user,
    isOwner: user?.is_owner || false,
    isAdmin: user?.user_type === 'admin' || user?.user_type === 'super_admin',
    isDoctor: user?.user_type === 'doctor',
    isPatient: user?.user_type === 'patient',
    isProvider: ['pharmacy', 'lab', 'radiology_center', 'hospital', 'nurse'].includes(user?.user_type),
    roleLabel: {
      patient: 'مستخدم',
      doctor: 'طبيب',
      pharmacy: 'صيدلية',
      lab: 'معمل',
      radiology_center: 'مركز أشعة',
      hospital: 'مستشفى',
      nurse: 'ممرض',
      admin: 'مدير',
      super_admin: 'مدير النظام',
    }[user?.user_type] || 'حساب'
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
