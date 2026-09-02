import { apiClient } from './client'
import type { AuthResponse, User } from '../types'

export async function loginApi(formData: URLSearchParams): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
  return response.data
}

export async function registerApi(username: string, password: string): Promise<User> {
  const response = await apiClient.post<User>('/register', {
    username,
    password,
  })
  return response.data
}
