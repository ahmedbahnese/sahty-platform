import { useEffect, useState } from 'react'
import { CloudOff, Wifi } from 'lucide-react'

export default function ConnectivityBanner() {
  const [online, setOnline] = useState(() => navigator.onLine)
  const [showRestored, setShowRestored] = useState(false)

  useEffect(() => {
    const handleOffline = () => { setOnline(false); setShowRestored(false) }
    const handleOnline = () => {
      setOnline(true)
      setShowRestored(true)
      window.setTimeout(() => setShowRestored(false), 3200)
    }
    window.addEventListener('offline', handleOffline)
    window.addEventListener('online', handleOnline)
    return () => {
      window.removeEventListener('offline', handleOffline)
      window.removeEventListener('online', handleOnline)
    }
  }, [])

  if (online && !showRestored) return null
  return <div role="status" aria-live="polite" className={`fixed inset-x-0 top-0 z-[100] flex items-center justify-center gap-2 px-4 py-2 text-center text-sm font-semibold shadow-sm ${online ? 'bg-emerald-600 text-white' : 'bg-amber-500 text-slate-950'}`}>
    {online ? <Wifi size={17} aria-hidden="true" /> : <CloudOff size={17} aria-hidden="true" />}
    <span>{online ? 'عاد الاتصال. يمكنك متابعة استخدام الخدمات.' : 'أنت الآن دون اتصال. سيتم الاحتفاظ بالواجهة المتاحة مؤقتًا.'}</span>
  </div>
}
