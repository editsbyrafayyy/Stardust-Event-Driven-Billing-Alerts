import { useEffect, useRef, useState, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import type { TelemetryLog } from '../types'

export type WebSocketStatus = 'connected' | 'reconnecting' | 'disconnected'

export function useWebSocket(token: string | null) {
  const [status, setStatus] = useState<WebSocketStatus>('disconnected')
  const [logs, setLogs] = useState<TelemetryLog[]>([])
  const [latestAlert, setLatestAlert] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const queryClient = useQueryClient()

  const addLog = useCallback((type: 'PUB_SUB' | 'CACHE' | 'SYSTEM', message: string) => {
    const newLog: TelemetryLog = {
      id: Math.random().toString(36).substring(2, 9),
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
      type,
      message,
    }
    setLogs((prev) => [newLog, ...prev.slice(0, 49)]) // keep last 50 entries
  }, [])

  useEffect(() => {
    if (!token) {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
      }
      setStatus('disconnected')
      return
    }

    let isMounted = true

    const connect = () => {
      if (!isMounted) return
      setStatus('reconnecting')
      addLog('SYSTEM', 'Initiating WebSocket handshake on /ws...')

      const wsUrl = `ws://localhost:8082/ws?token=${token}`
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onopen = () => {
        if (!isMounted) return
        setStatus('connected')
        addLog('SYSTEM', 'WebSocket channel open (Subscribed to Redis "alerts")')
      }

      ws.onmessage = (event) => {
        if (!isMounted) return
        const messageText = event.data
        addLog('PUB_SUB', `[INCOMING] ${messageText}`)
        setLatestAlert(messageText)

        // Invalidate cache queries so total spend and tables refresh automatically
        queryClient.invalidateQueries({ queryKey: ['subscriptions'] })
        queryClient.invalidateQueries({ queryKey: ['summary'] })
      }

      ws.onerror = () => {
        if (!isMounted) return
        addLog('SYSTEM', 'WebSocket encounter error. Reconnecting...')
      }

      ws.onclose = (e) => {
        if (!isMounted) return
        setStatus('disconnected')
        if (e.code === 1008) {
          addLog('SYSTEM', 'WebSocket rejected: Policy / Token violation (1008)')
        } else {
          addLog('SYSTEM', `WebSocket closed (code: ${e.code}). Retrying in 4s...`)
          reconnectTimeoutRef.current = window.setTimeout(connect, 4000)
        }
      }
    }

    connect()

    return () => {
      isMounted = false
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [token, addLog, queryClient])

  const clearAlert = () => setLatestAlert(null)

  return { status, logs, latestAlert, clearAlert, addLog }
}
