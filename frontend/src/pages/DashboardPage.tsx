import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getSubscriptionsApi, getSummaryApi, createSubscriptionApi, patchSubscriptionApi, deleteSubscriptionApi } from '../api/subscriptions'
import { useAuth } from '../context/AuthContext'
import { useWebSocket } from '../hooks/useWebSocket'
import { Header } from '../components/Header'
import { MetricCards } from '../components/MetricCards'
import { SubscriptionTable } from '../components/SubscriptionTable'
import { TelemetryDrawer } from '../components/TelemetryDrawer'
import { AddSubscriptionModal } from '../components/AddSubscriptionModal'
import { EditSubscriptionModal } from '../components/EditSubscriptionModal'
import { ToastAlert } from '../components/ToastAlert'
import { Plus, Filter } from 'lucide-react'
import type { Subscription, SubscriptionCreate, SubscriptionUpdate } from '../types'

export const DashboardPage: React.FC = () => {
  const { token } = useAuth()
  const queryClient = useQueryClient()
  const { status: wsStatus, logs, latestAlert, clearAlert, addLog } = useWebSocket(token)

  const [isTelemetryOpen, setIsTelemetryOpen] = useState(false)
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [editingSub, setEditingSub] = useState<Subscription | null>(null)
  const [cycleFilter, setCycleFilter] = useState<string>('all')

  // 1. Fetch Subscriptions List
  const { data: subscriptions, isLoading: isSubsLoading } = useQuery({
    queryKey: ['subscriptions'],
    queryFn: getSubscriptionsApi,
  })

  // 2. Fetch Aggregated Summary
  const { data: summary, isLoading: isSummaryLoading } = useQuery({
    queryKey: ['summary'],
    queryFn: getSummaryApi,
  })

  // 3. Create Mutation
  const createMutation = useMutation({
    mutationFn: createSubscriptionApi,
    onSuccess: (newSub) => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] })
      queryClient.invalidateQueries({ queryKey: ['summary'] })
      addLog('CACHE', `Mutation: created '${newSub.name}' -> Evicted summary cache`)
    },
  })

  // 4. Patch Mutation
  const patchMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: SubscriptionUpdate }) =>
      patchSubscriptionApi(id, data),
    onSuccess: (updatedSub) => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] })
      queryClient.invalidateQueries({ queryKey: ['summary'] })
      addLog('CACHE', `Mutation: updated '${updatedSub.name}' -> Evicted summary cache`)
    },
  })

  // 5. Delete Mutation
  const deleteMutation = useMutation({
    mutationFn: deleteSubscriptionApi,
    onSuccess: (res) => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] })
      queryClient.invalidateQueries({ queryKey: ['summary'] })
      addLog('CACHE', `Mutation: deleted sub id=${res.id} -> Evicted summary cache`)
    },
  })

  const handleDelete = (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to remove commitment '${name}'?`)) {
      deleteMutation.mutate(id)
    }
  }

  // Filter subscriptions
  const filteredSubs = subscriptions?.filter((sub) => {
    if (cycleFilter === 'all') return true
    return sub.billing_cycle.toLowerCase() === cycleFilter
  })

  return (
    <div className="min-h-screen bg-[#FBF4EF] text-[#2A2420]">
      {/* Header */}
      <Header
        wsStatus={wsStatus}
        unreadAlertsCount={logs.filter((l) => l.type === 'PUB_SUB').length}
        onToggleTelemetry={() => setIsTelemetryOpen((prev) => !prev)}
        isTelemetryOpen={isTelemetryOpen}
      />

      {/* Main Content Body */}
      <main className="mx-auto max-w-6xl px-6 py-8 space-y-8">
        {/* Metric Cards Row */}
        <section>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-mono-numbers text-xs uppercase tracking-widest text-[#6B6057]">
              Executive Overview
            </h2>
            <span className="font-mono-numbers text-[11px] text-[#6B6057]">
              TTL Window: 300s
            </span>
          </div>
          <MetricCards
            summary={summary}
            subscriptions={subscriptions}
            isLoading={isSubsLoading || isSummaryLoading}
          />
        </section>

        {/* Subscriptions Ledger Section */}
        <section className="space-y-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="font-serif-display text-2xl font-medium text-[#2A2420] italic">
                Recurring Commitments
              </h2>
              <p className="font-mono-numbers text-xs text-[#6B6057]">
                Master ledger of active services and renewal schedules
              </p>
            </div>

            {/* Action Bar */}
            <div className="flex items-center gap-2">
              {/* Cycle Filter */}
              <div className="flex items-center gap-1 rounded-lg border border-[#E0D8CE] bg-[#F3EDE4] p-1 text-xs font-mono-numbers">
                <Filter className="size-3 text-[#6B6057] ml-1" />
                {['all', 'monthly', 'yearly', 'quarterly'].map((cycle) => (
                  <button
                    key={cycle}
                    onClick={() => setCycleFilter(cycle)}
                    className={`rounded-md px-2.5 py-1 capitalize transition-all ${
                      cycleFilter === cycle
                        ? 'bg-[#2A2420] text-[#FBF4EF] font-medium shadow-xs'
                        : 'text-[#6B6057] hover:text-[#2A2420]'
                    }`}
                  >
                    {cycle}
                  </button>
                ))}
              </div>

              {/* Add Commitment Button */}
              <button
                onClick={() => setIsAddModalOpen(true)}
                className="inline-flex items-center gap-1.5 rounded-lg bg-[#2A2420] px-4 py-2 text-xs font-medium text-[#FBF4EF] hover:bg-[#1A1614] transition-colors shadow-xs"
              >
                <Plus className="size-3.5" />
                <span>New Commitment</span>
              </button>
            </div>
          </div>

          {/* Ledger Table */}
          <SubscriptionTable
            subscriptions={filteredSubs}
            isLoading={isSubsLoading}
            onEdit={(sub) => setEditingSub(sub)}
            onDelete={handleDelete}
          />
        </section>
      </main>

      {/* Real-time Server Push Toast Alert */}
      <ToastAlert message={latestAlert} onDismiss={clearAlert} />

      {/* Cyber-Physical Terminal Drawer */}
      <TelemetryDrawer
        isOpen={isTelemetryOpen}
        onClose={() => setIsTelemetryOpen(false)}
        logs={logs}
        onClearLogs={() => {}}
      />

      {/* Add Subscription Modal */}
      <AddSubscriptionModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSubmit={async (data: SubscriptionCreate) => {
          await createMutation.mutateAsync(data)
        }}
        isSubmitting={createMutation.isPending}
      />

      {/* Edit Subscription Modal */}
      <EditSubscriptionModal
        isOpen={!!editingSub}
        onClose={() => setEditingSub(null)}
        subscription={editingSub}
        onSubmit={async (id: string, data: SubscriptionUpdate) => {
          await patchMutation.mutateAsync({ id, data })
        }}
        isSubmitting={patchMutation.isPending}
      />
    </div>
  )
}
