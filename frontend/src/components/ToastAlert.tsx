import React from 'react'
import { ShieldAlert, X } from 'lucide-react'

interface ToastAlertProps {
  message: string | null
  onDismiss: () => void
}

export const ToastAlert: React.FC<ToastAlertProps> = ({ message, onDismiss }) => {
  if (!message) return null

  return (
    <div className="fixed top-20 right-6 z-50 flex max-w-md items-start gap-3 rounded-xl border border-[#C84B31]/30 bg-[#FBF4EF] p-4 shadow-2xl transition-all animate-in slide-in-from-top-3">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-lg border border-[#C84B31]/30 bg-[#C84B31]/10 text-[#C84B31]">
        <ShieldAlert className="size-4.5" strokeWidth={1.75} />
      </div>

      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-mono-numbers text-[10px] font-bold text-[#C84B31] uppercase tracking-wider">
            Live Server Push
          </span>
          <span className="h-1.5 w-1.5 rounded-full bg-[#C84B31] animate-ping" />
        </div>
        <p className="mt-1 font-serif-display text-base font-medium text-[#2A2420] italic leading-tight">
          {message}
        </p>
      </div>

      <button
        onClick={onDismiss}
        className="flex size-6 shrink-0 items-center justify-center rounded-full text-[#6B6057] hover:bg-[#EDE6DC] hover:text-[#2A2420] transition-colors"
      >
        <X className="size-3.5" strokeWidth={1.75} />
      </button>
    </div>
  )
}
