import React, { createContext, useContext, useState, useEffect } from 'react'
import { loginApi, registerApi } from '../api/auth'

interface AuthContextType {
  token: string | null
  username: string | null
  isAuthenticated: boolean
  login: (u: string, p: string) => Promise<void>
  register: (u: string, p: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('stardust_token'))
  const [username, setUsername] = useState<string | null>(() => localStorage.getItem('stardust_user'))

  useEffect(() => {
    const handleLogout = () => {
      setToken(null)
      setUsername(null)
    }
    window.addEventListener('auth_logout', handleLogout)
    return () => window.removeEventListener('auth_logout', handleLogout)
  }, [])

  const login = async (u: string, p: string) => {
    const params = new URLSearchParams()
    params.append('username', u)
    params.append('password', p)
    const data = await loginApi(params)
    localStorage.setItem('stardust_token', data.access_token)
    localStorage.setItem('stardust_user', u)
    setToken(data.access_token)
    setUsername(u)
  }

  const register = async (u: string, p: string) => {
    await registerApi(u, p)
    await login(u, p)
  }

  const logout = () => {
    localStorage.removeItem('stardust_token')
    localStorage.removeItem('stardust_user')
    setToken(null)
    setUsername(null)
  }

  return (
    <AuthContext.Provider
      value={{
        token,
        username,
        isAuthenticated: !!token,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
