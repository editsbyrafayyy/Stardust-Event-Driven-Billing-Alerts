export type BillingCycle = 'monthly' | 'yearly' | 'quarterly' | 'weekly' | 'daily'

export interface User {
  id: string
  username: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface Subscription {
  id: string
  name: string
  cost: number
  billing_cycle: BillingCycle | string
  description: string | null
  renewal_date: string
}

export interface SubscriptionCreate {
  name: string
  cost: number
  billing_cycle: string
  description: string
  renewal_date?: string
}

export interface SubscriptionUpdate {
  name?: string
  cost?: number
  billing_cycle?: string
  description?: string
  renewal_date?: string
}

export interface UpcomingRenewal {
  id: string
  name: string
  cost: number
  renewal_date: string
}

export interface SummaryOut {
  total_monthly_spend: number
  upcoming_renewals: UpcomingRenewal[]
  cached: boolean
}

export interface TelemetryLog {
  id: string
  timestamp: string
  type: 'PUB_SUB' | 'CACHE' | 'SYSTEM'
  message: string
}
