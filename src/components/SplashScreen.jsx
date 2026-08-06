import { useEffect, useState } from 'react'
import { Heart } from 'lucide-react'

export default function SplashScreen({ onDone }) {
  const [phase, setPhase] = useState('in') // in | hold | out

  useEffect(() => {
    const t1 = setTimeout(() => setPhase('out'), 1400)
    const t2 = setTimeout(() => onDone(), 1900)
    return () => { clearTimeout(t1); clearTimeout(t2) }
  }, [onDone])

  return (
    <div
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-center"
      style={{
        background: 'linear-gradient(135deg, #0f2444 0%, #1e40af 100%)',
        opacity: phase === 'out' ? 0 : 1,
        transition: 'opacity 0.5s ease-in-out'
      }}
    >
      {/* Pulse rings */}
      <div className="relative flex items-center justify-center mb-6">
        <div className="absolute w-28 h-28 rounded-full bg-white/10 animate-ping" style={{ animationDuration: '1.2s' }} />
        <div className="absolute w-20 h-20 rounded-full bg-white/15" />
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center shadow-2xl"
          style={{ background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(8px)' }}
        >
          <Heart className="h-8 w-8 text-white fill-white" />
        </div>
      </div>

      {/* Brand name */}
      <h1
        className="text-5xl font-black text-white tracking-wide"
        style={{
          opacity: phase === 'in' ? 1 : phase === 'out' ? 0 : 1,
          transform: phase === 'in' ? 'translateY(0)' : 'translateY(-4px)',
          transition: 'all 0.4s ease',
          textShadow: '0 2px 20px rgba(0,0,0,0.3)'
        }}
      >
        صحتي
      </h1>
      <p className="text-blue-200 text-sm mt-2 tracking-widest font-medium">منصة طبية شاملة</p>

      {/* Loading dots */}
      <div className="flex gap-1.5 mt-8">
        {[0, 1, 2].map(i => (
          <span
            key={i}
            className="w-2 h-2 bg-blue-300 rounded-full animate-bounce"
            style={{ animationDelay: `${i * 150}ms` }}
          />
        ))}
      </div>
    </div>
  )
}
