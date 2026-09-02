import React from 'react'
import { Radio, RefreshCw, RadioTower, LogOut, User, Bell } from 'lucide-react'
import type { WebSocketStatus } from '../hooks/useWebSocket'
import { useAuth } from '../context/AuthContext'

interface HeaderProps {
  wsStatus: WebSocketStatus
  unreadAlertsCount: number
  onToggleTelemetry: () => void
  isTelemetryOpen: boolean
}

export const Header: React.FC<HeaderProps> = ({
  wsStatus,
  unreadAlertsCount,
  onToggleTelemetry,
  isTelemetryOpen,
}) => {
  const { username, logout } = useAuth()

  return (
    <header className="sticky top-0 z-30 border-b border-[#E0D8CE] bg-[#FBF4EF]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        {/* Brand Logo & Editorial Title */}
        <div className="flex items-center gap-3">
          <span className="font-serif-display text-2xl tracking-tight text-[#2A2420] italic font-medium">
            StarDust
          </span>
          <span className="h-4 w-px bg-[#E0D8CE]" />
          <span className="font-mono-numbers text-xs tracking-wider text-[#6B6057] uppercase">
            Ledger & Telemetry
          </span>
        </div>

        {/* Status Indicators & User Controls */}
        <div className="flex items-center gap-3">
          {/* WebSocket Status Beacon */}
          <div className="inline-flex items-center gap-1.5 rounded-full border border-[#E0D8CE] bg-[#F3EDE4] px-3 py-1 text-xs font-medium text-[#2A2420]">
            {wsStatus === 'connected' && (
              <>
                <Radio className="size-3 text-[#4A7C59] animate-pulse" strokeWidth={2} />
                <span className="font-mono-numbers text-[11px] text-[#4A7C59]">WS: LIVE</span>
              </>
            )}
            {wsStatus === 'reconnecting' && (
              <>
                <RefreshCw className="size-3 text-[#C5A059] animate-spin" strokeWidth={2} />
                <span className="font-mono-numbers text-[11px] text-[#C5A059]">WS: RECONNECTING</span>
              </>
            )}
            {wsStatus === 'disconnected' && (
              <>
                <RadioTower className="size-3 text-[#C84B31]" strokeWidth={2} />
                <span className="font-mono-numbers text-[11px] text-[#C84B31]">WS: OFFLINE</span>
              </>
            )}
          </div>

          {/* Telemetry Console Toggle */}
          <button
            onClick={onToggleTelemetry}
            className={`relative inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
              isTelemetryOpen
                ? 'border-[#2A2420] bg-[#2A2420] text-[#FBF4EF]'
                : 'border-[#E0D8CE] bg-[#F3EDE4] text-[#2A2420] hover:bg-[#EDE6DC]'
            }`}
          >
            <Bell className="size-3" strokeWidth={1.75} />
            <span className="font-mono-numbers text-[11px]">FEED</span>
            {unreadAlertsCount > 0 && (
              <span className="flex size-4 items-center justify-center rounded-full bg-[#C84B31] font-mono-numbers text-[10px] font-bold text-white">
                {unreadAlertsCount}
              </span>
            )}
          </button>

          {/* User Session Pill */}
          <div className="inline-flex items-center gap-2 rounded-full border border-[#E0D8CE] bg-[#F3EDE4] pl-3 pr-1.5 py-1 text-xs text-[#2A2420]">
            <User className="size-3.5 text-[#6B6057]" strokeWidth={1.75} />
            <span className="font-medium">{username}</span>
            <button
              onClick={logout}
              title="Sign Out"
              className="flex size-6 items-center justify-center rounded-full text-[#6B6057] hover:bg-[#EDE6DC] hover:text-[#C84B31] transition-colors"
            >
              <LogOut className="size-3" strokeWidth={1.75} />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
