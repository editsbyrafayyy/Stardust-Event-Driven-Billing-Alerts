import React from 'react'
import { TrendingUp, Layers, Clock, Zap, Database } from 'lucide-react'
import type { SummaryOut, Subscription } from '../types'

interface MetricCardsProps {
  summary: SummaryOut | undefined
  subscriptions: Subscription[] | undefined
  isLoading: boolean
}

export const MetricCards: React.FC<MetricCardsProps> = ({
  summary,
  subscriptions,
  isLoading,
}) => {
  const totalSpend = summary?.total_monthly_spend ?? 0
  const isCached = summary?.cached ?? false
  const activeCount = subscriptions?.length ?? 0

  // Find most urgent renewal
  const upcomingList = summary?.upcoming_renewals ?? []
  const closestRenewal = upcomingList[0]

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      {/* 1. Total Monthly Spend */}
      <div className="rounded-xl border border-[#E0D8CE] bg-[#F3EDE4] p-5 shadow-xs transition-all hover:border-[#2A2420]/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs font-medium tracking-wider text-[#6B6057] uppercase">
            <TrendingUp className="size-3.5" strokeWidth={1.75} />
            <span>Monthly Spend</span>
          </div>
          {/* Cache Status Badge */}
          <div
            className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 font-mono-numbers text-[10px] font-medium border ${
              isCached
                ? 'border-[#4A7C59]/30 bg-[#4A7C59]/10 text-[#4A7C59]'
                : 'border-[#6B6057]/30 bg-[#EDE6DC] text-[#6B6057]'
            }`}
          >
            {isCached ? (
              <>
                <Zap className="size-2.5" strokeWidth={2} />
                <span>CACHED: REDIS</span>
              </>
            ) : (
              <>
                <Database className="size-2.5" strokeWidth={2} />
                <span>DIRECT DB</span>
              </>
            )}
          </div>
        </div>

        <div className="mt-3 flex items-baseline gap-2">
          <span className="font-serif-display text-4xl font-medium tracking-tight text-[#2A2420] italic">
            {isLoading ? '...' : `$${totalSpend.toFixed(2)}`}
          </span>
          <span className="font-mono-numbers text-xs text-[#6B6057]">/ month</span>
        </div>
        <p className="mt-2 text-xs text-[#6B6057]">
          Normalized across yearly, quarterly & weekly cycles
        </p>
      </div>

      {/* 2. Active Commitments */}
      <div className="rounded-xl border border-[#E0D8CE] bg-[#F3EDE4] p-5 shadow-xs transition-all hover:border-[#2A2420]/30">
        <div className="flex items-center gap-1.5 text-xs font-medium tracking-wider text-[#6B6057] uppercase">
          <Layers className="size-3.5" strokeWidth={1.75} />
          <span>Active Commitments</span>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="font-serif-display text-4xl font-medium tracking-tight text-[#2A2420] italic">
            {isLoading ? '...' : activeCount.toString().padStart(2, '0')}
          </span>
          <span className="font-mono-numbers text-xs text-[#6B6057]">services</span>
        </div>
        <p className="mt-2 text-xs text-[#6B6057]">
          Multi-tenant isolated PostgreSQL storage
        </p>
      </div>

      {/* 3. Imminent Renewal */}
      <div className="rounded-xl border border-[#E0D8CE] bg-[#F3EDE4] p-5 shadow-xs transition-all hover:border-[#2A2420]/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1.5 text-xs font-medium tracking-wider text-[#6B6057] uppercase">
            <Clock className="size-3.5 text-[#C84B31]" strokeWidth={1.75} />
            <span>Imminent Renewal</span>
          </div>
          {closestRenewal && (
            <span className="rounded-full border border-[#C84B31]/30 bg-[#C84B31]/10 px-2 py-0.5 font-mono-numbers text-[10px] font-semibold text-[#C84B31]">
              NEXT UP
            </span>
          )}
        </div>

        {closestRenewal ? (
          <div className="mt-3">
            <div className="font-serif-display text-2xl font-medium text-[#2A2420] italic truncate">
              {closestRenewal.name}
            </div>
            <div className="mt-1 flex items-center justify-between text-xs">
              <span className="font-mono-numbers text-[#C84B31] font-semibold">
                ${closestRenewal.cost.toFixed(2)}
              </span>
              <span className="font-mono-numbers text-[#6B6057]">
                Due: {closestRenewal.renewal_date}
              </span>
            </div>
          </div>
        ) : (
          <div className="mt-3 flex h-14 items-center">
            <span className="font-mono-numbers text-xs text-[#6B6057]">
              No renewals due in the next 7 days
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
