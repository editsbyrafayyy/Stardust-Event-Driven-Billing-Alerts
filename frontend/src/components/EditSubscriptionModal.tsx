import React, { useState, useEffect } from 'react'
import { X, Check, Calendar, DollarSign, Tag, FileText } from 'lucide-react'
import type { Subscription, SubscriptionUpdate } from '../types'

interface EditSubscriptionModalProps {
  isOpen: boolean
  onClose: () => void
  subscription: Subscription | null
  onSubmit: (id: string, data: SubscriptionUpdate) => Promise<void>
  isSubmitting: boolean
}

export const EditSubscriptionModal: React.FC<EditSubscriptionModalProps> = ({
  isOpen,
  onClose,
  subscription,
  onSubmit,
  isSubmitting,
}) => {
  const [name, setName] = useState('')
  const [cost, setCost] = useState('')
  const [billingCycle, setBillingCycle] = useState('monthly')
  const [description, setDescription] = useState('')
  const [renewalDate, setRenewalDate] = useState('')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (subscription) {
      setName(subscription.name)
      setCost(subscription.cost.toString())
      setBillingCycle(subscription.billing_cycle)
      setDescription(subscription.description || '')
      setRenewalDate(subscription.renewal_date)
    }
  }, [subscription])

  if (!isOpen || !subscription) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    const costNum = parseFloat(cost)
    if (isNaN(costNum) || costNum <= 0) {
      setError('Please enter a valid positive cost amount.')
      return
    }

    try {
      await onSubmit(subscription.id, {
        name: name.trim(),
        cost: costNum,
        billing_cycle: billingCycle,
        description: description.trim(),
        renewal_date: renewalDate,
      })
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update subscription.')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#2A2420]/40 backdrop-blur-xs p-4">
      <div className="w-full max-w-md overflow-hidden rounded-2xl border border-[#E0D8CE] bg-[#FBF4EF] p-6 shadow-2xl">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-[#E0D8CE] pb-4">
          <div>
            <h2 className="font-serif-display text-2xl font-medium text-[#2A2420] italic">
              Amend Commitment
            </h2>
            <p className="font-mono-numbers text-xs text-[#6B6057]">
              Update subscription terms and renewal dates
            </p>
          </div>
          <button
            onClick={onClose}
            className="flex size-7 items-center justify-center rounded-full text-[#6B6057] hover:bg-[#EDE6DC] hover:text-[#2A2420] transition-colors"
          >
            <X className="size-4" strokeWidth={1.75} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          {error && (
            <div className="rounded-lg border border-[#C84B31]/30 bg-[#C84B31]/10 px-3 py-2 font-mono-numbers text-xs text-[#C84B31]">
              {error}
            </div>
          )}

          {/* Service Name */}
          <div>
            <label className="block font-mono-numbers text-xs uppercase tracking-wider text-[#6B6057] mb-1">
              Service Name
            </label>
            <div className="relative">
              <Tag className="absolute left-3 top-1/2 -translate-y-1/2 size-3.5 text-[#6B6057]" />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-lg border border-[#E0D8CE] bg-[#F3EDE4] py-2 pl-9 pr-3 text-sm text-[#2A2420] focus:border-[#2A2420] focus:outline-hidden"
              />
            </div>
          </div>

          {/* Cost & Cycle Row */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-mono-numbers text-xs uppercase tracking-wider text-[#6B6057] mb-1">
                Cost ($)
              </label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 size-3.5 text-[#6B6057]" />
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  value={cost}
                  onChange={(e) => setCost(e.target.value)}
                  className="w-full rounded-lg border border-[#E0D8CE] bg-[#F3EDE4] py-2 pl-9 pr-3 font-mono-numbers text-sm text-[#2A2420] focus:border-[#2A2420] focus:outline-hidden"
                />
              </div>
            </div>

            <div>
              <label className="block font-mono-numbers text-xs uppercase tracking-wider text-[#6B6057] mb-1">
                Billing Cycle
              </label>
              <select
                value={billingCycle}
                onChange={(e) => setBillingCycle(e.target.value)}
                className="w-full rounded-lg border border-[#E0D8CE] bg-[#F3EDE4] py-2 px-3 text-sm text-[#2A2420] focus:border-[#2A2420] focus:outline-hidden"
              >
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
                <option value="quarterly">Quarterly</option>
                <option value="weekly">Weekly</option>
                <option value="daily">Daily</option>
              </select>
            </div>
          </div>

          {/* Renewal Date */}
          <div>
            <label className="block font-mono-numbers text-xs uppercase tracking-wider text-[#6B6057] mb-1">
              Renewal Date
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 size-3.5 text-[#6B6057]" />
              <input
                type="date"
                required
                value={renewalDate}
                onChange={(e) => setRenewalDate(e.target.value)}
                className="w-full rounded-lg border border-[#E0D8CE] bg-[#F3EDE4] py-2 pl-9 pr-3 font-mono-numbers text-sm text-[#2A2420] focus:border-[#2A2420] focus:outline-hidden"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block font-mono-numbers text-xs uppercase tracking-wider text-[#6B6057] mb-1">
              Description / Notes
            </label>
            <div className="relative">
              <FileText className="absolute left-3 top-2.5 size-3.5 text-[#6B6057]" />
              <textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full rounded-lg border border-[#E0D8CE] bg-[#F3EDE4] py-2 pl-9 pr-3 text-sm text-[#2A2420] focus:border-[#2A2420] focus:outline-hidden resize-none"
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-6 flex items-center justify-end gap-2 border-t border-[#E0D8CE] pt-4">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-[#E0D8CE] px-4 py-2 text-xs font-medium text-[#6B6057] hover:bg-[#EDE6DC] hover:text-[#2A2420] transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center gap-1.5 rounded-lg bg-[#2A2420] px-4 py-2 text-xs font-medium text-[#FBF4EF] hover:bg-[#1A1614] transition-colors disabled:opacity-50"
            >
              <Check className="size-3.5" />
              <span>{isSubmitting ? 'Saving...' : 'Save Amendments'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
