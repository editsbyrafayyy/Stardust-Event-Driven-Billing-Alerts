import { apiClient } from './client'
import type { Subscription, SubscriptionCreate, SubscriptionUpdate, SummaryOut } from '../types'

export async function getSubscriptionsApi(): Promise<Subscription[]> {
  const response = await apiClient.get<Subscription[]>('/subscriptions')
  return response.data
}

export async function getSummaryApi(): Promise<SummaryOut> {
  const response = await apiClient.get<SummaryOut>('/subscriptions/summary')
  return response.data
}

export async function createSubscriptionApi(payload: SubscriptionCreate): Promise<Subscription> {
  const response = await apiClient.post<Subscription>('/subscriptions', payload)
  return response.data
}

export async function patchSubscriptionApi(id: string, payload: SubscriptionUpdate): Promise<Subscription> {
  const response = await apiClient.patch<Subscription>(`/subscriptions/${id}`, payload)
  return response.data
}

export async function deleteSubscriptionApi(id: string): Promise<{ message: string; id: string }> {
  const response = await apiClient.delete<{ message: string; id: string }>(`/subscriptions/${id}`)
  return response.data
}
