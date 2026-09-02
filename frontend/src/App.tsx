import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider, useAuth } from './context/AuthContext'
import { AuthPage } from './pages/AuthPage'
import { DashboardPage } from './pages/DashboardPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30, // 30s stale time
      refetchOnWindowFocus: false,
    },
  },
})

const MainRouter: React.FC = () => {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <DashboardPage /> : <AuthPage />
}

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MainRouter />
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default App
