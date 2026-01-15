'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import { useRouter } from 'next/navigation'

interface User {
  id: number
  username: string
  email: string
  full_name?: string
  is_admin: boolean
}

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [err, setErr] = useState(null)

  useEffect(() => {
    // Check for stored token on mount
    // TODO: switch to httpOnly cookies for better security?
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
      fetchCurrentUser(storedToken)
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchCurrentUser = async (authToken) => {
    try {
      const response = await apiClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${authToken}` }
      })
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      localStorage.removeItem('token')
      setToken(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await apiClient.post('/auth/login', formData)
    const { access_token } = response.data

    setToken(access_token)
    localStorage.setItem('token', access_token)
    await fetchCurrentUser(access_token)
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        login,
        logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
