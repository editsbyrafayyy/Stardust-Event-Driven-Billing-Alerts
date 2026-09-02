import React from 'react'
import { Pencil, Trash2, Calendar, Tag, AlertCircle } from 'lucide-react'
import type { Subscription } from '../types'

interface SubscriptionTableProps {
  subscriptions: Subscription[] | undefined
  isLoading: boolean
  onEdit: (sub: Subscription) => void
  onDelete: (id: string, name: string) => void
}

export const SubscriptionTable: React.FC<SubscriptionTableProps> = ({
  subscriptions,
  isLoading,
  onEdit,
  onDelete,
}) => {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-[#E0D8CE] bg-[#F3EDE4] p-12 text-center">
        <span className="font-mono-numbers text-sm text-[#6B6057]">
          Loading subscription ledger...
        </span>
      </div>
    )
  }

  if (!subscriptions || subscriptions.length === 0) {
    return (
      <div className="rounded-xl border border-[#E0D8CE] bg-[#F3EDE4] p-12 text-center">
        <div className="mx-auto flex size-10 items-center justify-center rounded-full border border-[#E0D8CE] bg-[#EDE6DC] text-[#6B6057]">
          <Tag className="size-5" strokeWidth={1.5} />
        </div>
        <h3 className="mt-4 font-serif-display text-xl text-[#2A2420] italic">
          No subscriptions recorded
        </h3>
        <p className="mt-1 font-mono-numbers text-xs text-[#6B6057]">
          Use the "New Commitment" button above to add your first subscription.
        </p>
      </div>
    )
  }

  // Calculate days remaining to renewal
  const getRenewalStatus = (renewalDateStr: string) => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const renewal = new Date(renewalDateStr)
    const diffTime = renewal.getTime() - today.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays < 0) {
      return { text: 'OVERDUE', isUrgent: true, days: diffDays }
    } else if (diffDays <= 3) {
      return { text: `DUE IN ${diffDays}D`, isUrgent: true, days: diffDays }
    } else {
      return { text: `IN ${diffDays}D`, isUrgent: false, days: diffDays }
    }
  }

  return (
    <div className="overflow-hidden rounded-xl border border-[#E0D8CE] bg-[#F3EDE4] shadow-xs">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-[#E0D8CE] bg-[#EDE6DC]/70 font-mono-numbers text-[11px] uppercase tracking-wider text-[#6B6057]">
            <tr>
              <th className="px-5 py-3 font-semibold">No.</th>
              <th className="px-5 py-3 font-semibold">Service</th>
              <th className="px-5 py-3 font-semibold">Cycle</th>
              <th className="px-5 py-3 font-semibold">Cost</th>
              <th className="px-5 py-3 font-semibold">Renewal Date</th>
              <th className="px-5 py-3 font-semibold">Urgency</th>
              <th className="px-5 py-3 text-right font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#E0D8CE]">
            {subscriptions.map((sub, index) => {
              const status = getRenewalStatus(sub.renewal_date)
              const indexStr = (index + 1).toString().padStart(2, '0')

              return (
                <tr
                  key={sub.id}
                  className="group transition-colors hover:bg-[#EDE6DC]/40"
                >
                  {/* Index Number */}
                  <td className="px-5 py-4 font-mono-numbers text-xs text-[#6B6057]">
                    {indexStr}
                  </td>

                  {/* Service Name & Description */}
                  <td className="px-5 py-4">
                    <div className="font-serif-display text-lg font-medium text-[#2A2420] italic">
                      {sub.name}
                    </div>
                    {sub.description && (
                      <div className="font-mono-numbers text-xs text-[#6B6057] truncate max-w-xs">
                        {sub.description}
                      </div>
                    )}
                  </td>

                  {/* Billing Cycle Badge */}
                  <td className="px-5 py-4">
                    <span className="inline-block rounded-full border border-[#E0D8CE] bg-[#FBF4EF] px-2.5 py-0.5 font-mono-numbers text-[11px] text-[#2A2420] capitalize">
                      {sub.billing_cycle}
                    </span>
                  </td>

                  {/* Cost */}
                  <td className="px-5 py-4 font-mono-numbers text-sm font-semibold text-[#2A2420]">
                    ${sub.cost.toFixed(2)}
                  </td>

                  {/* Renewal Date */}
                  <td className="px-5 py-4 font-mono-numbers text-xs text-[#6B6057]">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="size-3 text-[#6B6057]" strokeWidth={1.75} />
                      <span>{sub.renewal_date}</span>
                    </div>
                  </td>

                  {/* Urgency Status */}
                  <td className="px-5 py-4">
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 font-mono-numbers text-[10px] font-semibold border ${
                        status.isUrgent
                          ? 'border-[#C84B31]/30 bg-[#C84B31]/10 text-[#C84B31]'
                          : 'border-[#4A7C59]/30 bg-[#4A7C59]/10 text-[#4A7C59]'
                      }`}
                    >
                      {status.isUrgent && (
                        <AlertCircle className="size-2.5" strokeWidth={2} />
                      )}
                      <span>{status.text}</span>
                    </span>
                  </td>

                  {/* Actions */}
                  <td className="px-5 py-4 text-right">
                    <div className="inline-flex items-center gap-2">
                      <button
                        onClick={() => onEdit(sub)}
                        title="Edit Subscription"
                        className="flex size-7 items-center justify-center rounded-lg border border-[#E0D8CE] bg-[#FBF4EF] text-[#6B6057] transition-colors hover:border-[#2A2420] hover:text-[#2A2420]"
                      >
                        <Pencil className="size-3.5" strokeWidth={1.75} />
                      </button>
                      <button
                        onClick={() => onDelete(sub.id, sub.name)}
                        title="Delete Subscription"
                        className="flex size-7 items-center justify-center rounded-lg border border-[#E0D8CE] bg-[#FBF4EF] text-[#6B6057] transition-colors hover:border-[#C84B31] hover:bg-[#C84B31]/10 hover:text-[#C84B31]"
                      >
                        <Trash2 className="size-3.5" strokeWidth={1.75} />
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
