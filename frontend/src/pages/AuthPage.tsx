import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { KeyRound, User as UserIcon, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react'

export const AuthPage: React.FC = () => {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { login, register } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      if (isRegister) {
        await register(username.trim(), password)
      } else {
        await login(username.trim(), password)
      }
    } catch (err: any) {
      if (err.response?.status === 429) {
        setError('Rate limit exceeded (5 attempts/min). Please try again in 60s.')
      } else {
        setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center p-6">
      {/* Folio Container */}
      <div className="relative z-10 w-full max-w-md overflow-hidden rounded-2xl border border-[#E0D8CE] bg-[#FBF4EF] p-8 shadow-2xl">
        {/* Folio Header */}
        <div className="text-center">
          <span className="font-mono-numbers text-xs tracking-widest text-[#6B6057] uppercase">
            Access Verification Folio
          </span>
          <h1 className="mt-1 font-serif-display text-4xl font-medium tracking-tight text-[#2A2420] italic">
            StarDust
          </h1>
          <p className="mt-2 text-xs text-[#6B6057] leading-relaxed">
            Event-driven subscription ledger & real-time telemetry console
          </p>
        </div>

        {/* Tab Selector */}
        <div className="mt-6 flex rounded-lg border border-[#E0D8CE] bg-[#F3EDE4] p-1 font-mono-numbers text-xs">
          <button
            type="button"
            onClick={() => {
              setIsRegister(false)
              setError(null)
            }}
            className={`flex-1 rounded-md py-1.5 font-medium transition-all ${
              !isRegister
                ? 'bg-[#2A2420] text-[#FBF4EF] shadow-xs'
                : 'text-[#6B6057] hover:text-[#2A2420]'
            }`}
          >
            Authenticate
          </button>
          <button
            type="button"
            onClick={() => {
              setIsRegister(true)
              setError(null)
            }}
            className={`flex-1 rounded-md py-1.5 font-medium transition-all ${
              isRegister
                ? 'bg-[#2A2420] text-[#FBF4EF] shadow-xs'
                : 'text-[#6B6057] hover:text-[#2A2420]'
            }`}
          >
            Register Folio
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-[#C84B31]/30 bg-[#C84B31]/10 px-3 py-2.5 font-mono-numbers text-xs text-[#C84B31]">
              <AlertCircle className="size-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Username */}
          <div>
            <label className="block font-mono-numbers text-xs uppercase tracking-wider text-[#6B6057] mb-1">
              Account Identifier
            </label>
            <div className="relative">
              <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 size-3.5 text-[#6B6057]" />
              <input
                type="text"
                required
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded-lg border border-[#E0D8CE] bg-[#F3EDE4] py-2 pl-9 pr-3 text-sm text-[#2A2420] placeholder-[#6B6057]/60 focus:border-[#2A2420] focus:outline-hidden"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block font-mono-numbers text-xs uppercase tracking-wider text-[#6B6057] mb-1">
              Passphrase
            </label>
            <div className="relative">
              <KeyRound className="absolute left-3 top-1/2 -translate-y-1/2 size-3.5 text-[#6B6057]" />
              <input
                type="password"
                required
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-[#E0D8CE] bg-[#F3EDE4] py-2 pl-9 pr-3 text-sm text-[#2A2420] placeholder-[#6B6057]/60 focus:border-[#2A2420] focus:outline-hidden"
              />
            </div>
          </div>

          {/* Submit Action */}
          <button
            type="submit"
            disabled={isLoading}
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-[#2A2420] py-2.5 font-medium text-xs text-[#FBF4EF] hover:bg-[#1A1614] transition-colors disabled:opacity-50"
          >
            <span>{isLoading ? 'Verifying...' : isRegister ? 'Create Account' : 'Authenticate & Enter'}</span>
            <ArrowRight className="size-3.5" />
          </button>
        </form>

        {/* Security Telemetry Footnote */}
        <div className="mt-6 border-t border-[#E0D8CE] pt-4 text-center font-mono-numbers text-[10px] text-[#6B6057]">
          <div className="flex items-center justify-center gap-1.5">
            <ShieldCheck className="size-3 text-[#4A7C59]" strokeWidth={2} />
            <span>BCRYPT 12-ROUNDS · JWT HS256 · RATE-LIMITED (REDIS)</span>
          </div>
        </div>
      </div>
    </div>
  )
}
