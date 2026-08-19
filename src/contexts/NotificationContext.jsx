import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { CheckCircle2, CircleAlert, Info, LoaderCircle, X } from 'lucide-react'

const NotificationContext = createContext(null)

const styles = {
  success: {
    icon: CheckCircle2,
    label: 'تم التنفيذ',
    container: 'border-emerald-200 bg-emerald-50 text-emerald-950',
    iconClass: 'text-emerald-600',
    bar: 'bg-emerald-500',
  },
  error: {
    icon: CircleAlert,
    label: 'تعذر التنفيذ',
    container: 'border-red-200 bg-red-50 text-red-950',
    iconClass: 'text-red-600',
    bar: 'bg-red-500',
  },
  info: {
    icon: Info,
    label: 'تنبيه',
    container: 'border-blue-200 bg-blue-50 text-blue-950',
    iconClass: 'text-blue-600',
    bar: 'bg-blue-500',
  },
  loading: {
    icon: LoaderCircle,
    label: 'جارٍ التنفيذ',
    container: 'border-amber-200 bg-amber-50 text-amber-950',
    iconClass: 'text-amber-600',
    bar: 'bg-amber-500',
  },
}

function NotificationItem({ notification, onDismiss }) {
  const appearance = styles[notification.type] || styles.info
  const Icon = appearance.icon

  return (
    <div
      role={notification.type === 'error' ? 'alert' : 'status'}
      className={`relative w-[calc(100vw-2rem)] max-w-sm overflow-hidden rounded-2xl border p-4 shadow-lg backdrop-blur-sm ${appearance.container}`}
      dir="rtl"
    >
      <div className="flex items-start gap-3">
        <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${appearance.iconClass} ${notification.type === 'loading' ? 'animate-spin' : ''}`} aria-hidden="true" />
        <div className="min-w-0 flex-1">
          <p className="text-sm font-bold">{notification.title || appearance.label}</p>
          {notification.message && <p className="mt-1 text-xs leading-5 opacity-80">{notification.message}</p>}
        </div>
        <button
          type="button"
          onClick={() => onDismiss(notification.id)}
          className="rounded-lg p-1 opacity-60 transition-opacity hover:opacity-100"
          aria-label="إغلاق الإشعار"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      {notification.duration > 0 && (
        <div
          className={`absolute inset-x-0 bottom-0 h-0.5 origin-right ${appearance.bar}`}
          style={{ animation: `notification-progress ${notification.duration}ms linear forwards` }}
        />
      )}
    </div>
  )
}

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([])

  const dismiss = useCallback((id) => {
    setNotifications(current => current.filter(notification => notification.id !== id))
  }, [])

  const notify = useCallback(({ type = 'info', title, message, duration = 5000 }) => {
    const id = `${Date.now()}-${Math.random()}`
    setNotifications(current => [...current, { id, type, title, message, duration }].slice(-3))
    if (duration > 0) {
      window.setTimeout(() => dismiss(id), duration)
    }
    return id
  }, [dismiss])

  const value = useMemo(() => ({
    notify,
    success: (message, title = 'تم التنفيذ') => notify({ type: 'success', title, message }),
    error: (message, title = 'تعذر التنفيذ') => notify({ type: 'error', title, message, duration: 7000 }),
    info: (message, title = 'تنبيه') => notify({ type: 'info', title, message }),
    loading: (message, title = 'جارٍ التنفيذ') => notify({ type: 'loading', title, message, duration: 0 }),
    dismiss,
  }), [dismiss, notify])

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed inset-x-0 top-4 z-[100] flex justify-center px-4 sm:justify-start sm:px-6" aria-live="polite">
        <div className="pointer-events-auto flex w-full max-w-md flex-col gap-3">
          {notifications.map(notification => (
            <NotificationItem key={notification.id} notification={notification} onDismiss={dismiss} />
          ))}
        </div>
      </div>
    </NotificationContext.Provider>
  )
}

export function useNotifications() {
  const context = useContext(NotificationContext)
  if (!context) throw new Error('useNotifications must be used within a NotificationProvider')
  return context
}