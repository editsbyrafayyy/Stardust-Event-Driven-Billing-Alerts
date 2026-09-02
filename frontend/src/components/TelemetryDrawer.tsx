import React from 'react'
import { Terminal, X, Trash2, ArrowDownCircle } from 'lucide-react'
import type { TelemetryLog } from '../types'

interface TelemetryDrawerProps {
  isOpen: boolean
  onClose: () => void
  logs: TelemetryLog[]
  onClearLogs: () => void
}

export const TelemetryDrawer: React.FC<TelemetryDrawerProps> = ({
  isOpen,
  onClose,
  logs,
  onClearLogs,
}) => {
  if (!isOpen) return null

  return (
    <div className="fixed bottom-4 right-4 z-40 w-full max-w-lg overflow-hidden rounded-xl border border-[#2A4A35] bg-[#0F1A13] text-[#4A7C59] shadow-2xl font-mono-numbers">
      {/* Terminal Header Bar */}
      <div className="flex items-center justify-between border-b border-[#2A4A35] bg-[#0A120D] px-4 py-2.5">
        <div className="flex items-center gap-2">
          <Terminal className="size-3.5 text-[#4A7C59]" strokeWidth={2} />
          <span className="text-xs font-medium tracking-wider text-[#A8D5BA] uppercase">
            Redis Pub/Sub & WebSocket Telemetry
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onClearLogs}
            title="Clear Feed"
            className="flex size-5 items-center justify-center rounded text-[#4A7C59] hover:bg-[#1B3324] hover:text-[#A8D5BA] transition-colors"
          >
            <Trash2 className="size-3" strokeWidth={1.75} />
          </button>
          <button
            onClick={onClose}
            title="Close Console"
            className="flex size-5 items-center justify-center rounded text-[#4A7C59] hover:bg-[#1B3324] hover:text-[#A8D5BA] transition-colors"
          >
            <X className="size-3.5" strokeWidth={1.75} />
          </button>
        </div>
      </div>

      {/* Terminal Feed Body */}
      <div className="h-60 overflow-y-auto p-3 text-xs leading-relaxed divide-y divide-[#1B3324]/40">
        {logs.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center text-center text-[#4A7C59]/60">
            <ArrowDownCircle className="size-5 mb-2 opacity-50" />
            <span>Telemetry buffer idle. Awaiting Celery / Redis events...</span>
          </div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="py-1.5 flex items-start gap-2">
              <span className="text-[#689F7B] shrink-0 font-medium">[{log.timestamp}]</span>
              <span
                className={`font-semibold shrink-0 ${
                  log.type === 'PUB_SUB'
                    ? 'text-[#EAA846]'
                    : log.type === 'CACHE'
                    ? 'text-[#58B4D1]'
                    : 'text-[#4A7C59]'
                }`}
              >
                [{log.type}]
              </span>
              <span className="text-[#E0EAE2] break-all">{log.message}</span>
            </div>
          ))
        )}
      </div>

      {/* Terminal Footer Status */}
      <div className="border-t border-[#2A4A35] bg-[#0A120D] px-4 py-1.5 text-[10px] text-[#4A7C59]/80 flex items-center justify-between">
        <span>Channel: "alerts" · Redis v7.0</span>
        <span>Events buffered: {logs.length}</span>
      </div>
    </div>
  )
}
