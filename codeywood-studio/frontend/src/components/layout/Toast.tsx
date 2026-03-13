import { useEffect, useState } from 'react'

interface ToastMessage {
  id: number
  text: string
  type: 'success' | 'error' | 'info'
}

let toastId = 0
let addToastFn: ((msg: Omit<ToastMessage, 'id'>) => void) | null = null

export function toast(text: string, type: 'success' | 'error' | 'info' = 'success') {
  addToastFn?.({ text, type })
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  useEffect(() => {
    addToastFn = (msg) => {
      const id = ++toastId
      setToasts(prev => [...prev, { ...msg, id }])
      setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3000)
    }
    return () => { addToastFn = null }
  }, [])

  const borderColor = {
    success: 'border-accent-green',
    error: 'border-accent-red',
    info: 'border-accent-blue',
  }

  const textColor = {
    success: 'text-accent-green',
    error: 'text-accent-red',
    info: 'text-accent-blue',
  }

  return (
    <div className="fixed bottom-6 right-6 z-[300] flex flex-col gap-2">
      {toasts.map(t => (
        <div
          key={t.id}
          className={`pixel-border ${borderColor[t.type]} ${textColor[t.type]} bg-bg-card px-5 py-3 text-sm animate-[slideUp_0.3s_ease]`}
        >
          {t.text}
        </div>
      ))}
    </div>
  )
}
