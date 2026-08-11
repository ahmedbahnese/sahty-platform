import { useState, useEffect, useRef, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Bell, BellRing, Check, Trash2, Calendar, Droplets, Activity, AlertCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

const TYPE_ICON = {
  appointment: Calendar,
  blood_bank:  Droplets,
  system:      Activity,
}
const TYPE_COLOR = {
  appointment: 'text-blue-500',
  blood_bank:  'text-red-500',
  system:      'text-gray-500',
}

export default function NotificationBell() {
  const { isAuthenticated, token } = useAuth()
  const [unread, setUnread]           = useState(0)
  const [notifications, setNotifs]    = useState([])
  const [open, setOpen]               = useState(false)
  const [loading, setLoading]         = useState(false)
  const dropdownRef = useRef(null)
  const pollRef     = useRef(null)

  const authHeaders = useCallback(() => ({
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }), [token])

  // Poll unread count every 30 seconds
  const fetchUnread = useCallback(async () => {
    if (!isAuthenticated || !token) return
    try {
      const res = await fetch('/api/notifications/unread-count', { headers: authHeaders() })
      if (res.ok) {
        const data = await res.json()
        setUnread(data.unread_count || 0)
      }
    } catch { /* silent */ }
  }, [isAuthenticated, token, authHeaders])

  useEffect(() => {
    fetchUnread()
    pollRef.current = setInterval(fetchUnread, 30_000)
    return () => clearInterval(pollRef.current)
  }, [fetchUnread])

  const enableBrowserNotifications = async () => {
    if (!('Notification' in window)) return
    const permission = await Notification.requestPermission()
    if (permission === 'granted') {
      new Notification('صحتي', { body: 'سيتم عرض تنبيهاتك المهمة هنا.' })
    }
  }

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const openDropdown = async () => {
    setOpen(o => !o)
    if (!open) {
      setLoading(true)
      try {
        const res = await fetch('/api/notifications?per_page=15', { headers: authHeaders() })
        if (res.ok) {
          const data = await res.json()
          setNotifs(data.notifications || [])
          setUnread(data.unread_count || 0)
        }
      } catch { /* silent */ }
      setLoading(false)
    }
  }

  const markAllRead = async () => {
    try {
      await fetch('/api/notifications/mark-read', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({}),
      })
      setNotifs(prev => prev.map(n => ({ ...n, is_read: true })))
      setUnread(0)
    } catch { /* silent */ }
  }

  const markOne = async (id) => {
    try {
      await fetch('/api/notifications/mark-read', {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ ids: [id] }),
      })
      setNotifs(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
      setUnread(prev => Math.max(0, prev - 1))
    } catch { /* silent */ }
  }

  const deleteNotif = async (e, id) => {
    e.stopPropagation()
    try {
      await fetch(`/api/notifications/${id}`, { method: 'DELETE', headers: authHeaders() })
      setNotifs(prev => prev.filter(n => n.id !== id))
    } catch { /* silent */ }
  }

  const timeAgo = (iso) => {
    if (!iso) return ''
    const diff = (Date.now() - new Date(iso).getTime()) / 1000
    if (diff < 60)   return 'الآن'
    if (diff < 3600) return `منذ ${Math.floor(diff / 60)} د`
    if (diff < 86400) return `منذ ${Math.floor(diff / 3600)} س`
    return `منذ ${Math.floor(diff / 86400)} ي`
  }

  if (!isAuthenticated) return null

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell button */}
      <button
        onClick={openDropdown}
        className="relative p-2 rounded-xl text-gray-600 hover:bg-gray-100 transition-colors"
        aria-label="الإشعارات"
      >
        {unread > 0 ? (
          <BellRing className="h-5 w-5 text-blue-600" />
        ) : (
          <Bell className="h-5 w-5" />
        )}
        {unread > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center rounded-full text-white text-[10px] font-bold px-1"
            style={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' }}>
            {unread > 99 ? '99+' : unread}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {open && (
        <div className="absolute left-0 rtl:right-0 rtl:left-auto mt-2 w-80 bg-white rounded-2xl shadow-2xl border border-gray-100 z-50 overflow-hidden"
          style={{ maxHeight: '480px', display: 'flex', flexDirection: 'column' }}>

          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-gray-900">الإشعارات</h3>
              {'Notification' in window && Notification.permission !== 'granted' && (
                <button onClick={enableBrowserNotifications} className="text-xs text-blue-600 hover:underline">
                  تفعيل المتصفح
                </button>
              )}
            </div>
            {unread > 0 && (
              <button onClick={markAllRead}
                className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 transition-colors">
                <Check className="h-3.5 w-3.5" />
                تعيين الكل كمقروء
              </button>
            )}
          </div>

          {/* List */}
          <div className="overflow-y-auto flex-1">
            {loading ? (
              <div className="flex items-center justify-center py-10">
                <div className="w-6 h-6 border-2 border-blue-300 border-t-blue-600 rounded-full animate-spin" />
              </div>
            ) : notifications.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-gray-400 gap-2">
                <Bell className="h-8 w-8 opacity-30" />
                <p className="text-sm">لا توجد إشعارات</p>
              </div>
            ) : (
              notifications.map(n => {
                const Icon = TYPE_ICON[n.type] || AlertCircle
                const color = TYPE_COLOR[n.type] || 'text-gray-500'
                return (
                  <div
                    key={n.id}
                    onClick={() => markOne(n.id)}
                    className={`flex items-start gap-3 px-4 py-3 cursor-pointer transition-colors border-b border-gray-50 group hover:bg-gray-50 ${
                      !n.is_read ? 'bg-blue-50/60' : ''
                    }`}
                  >
                    <div className={`mt-0.5 flex-shrink-0 ${color}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-xs font-semibold leading-tight truncate ${!n.is_read ? 'text-gray-900' : 'text-gray-700'}`}>
                        {n.title}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5 line-clamp-2 leading-relaxed">
                        {n.message}
                      </p>
                      <p className="text-[10px] text-gray-400 mt-1">{timeAgo(n.created_at)}</p>
                    </div>
                    <div className="flex flex-col items-center gap-1 flex-shrink-0">
                      {!n.is_read && (
                        <span className="w-2 h-2 rounded-full bg-blue-500 mt-1" />
                      )}
                      <button
                        onClick={(e) => deleteNotif(e, n.id)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 text-gray-300 hover:text-red-500"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  </div>
                )
              })
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="border-t border-gray-100 px-4 py-2 text-center">
              <Link to="/dashboard"
                className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                onClick={() => setOpen(false)}>
                عرض جميع الإشعارات
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
