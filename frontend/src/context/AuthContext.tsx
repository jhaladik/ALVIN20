// storyforge-ai/src/context/AuthContext.tsx - UPDATED with JWT support
import { createContext, useState, useEffect, ReactNode } from 'react'
import { api } from '../services/api'

type User = {
  id: string
  email: string
  username: string
  plan: string
  tokensRemaining: number
  createdAt: string
}

type AuthContextType = {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  login: async () => {},
  register: async () => {},
  logout: async () => {},
})

type AuthProviderProps = {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Set up axios interceptor for JWT tokens
  useEffect(() => {
    // Add request interceptor to include JWT token
    const requestInterceptor = api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Add response interceptor to handle token expiration
    const responseInterceptor = api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('authToken')
          setUser(null)
          // Optionally redirect to login page
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )

    // Cleanup interceptors on unmount
    return () => {
      api.interceptors.request.eject(requestInterceptor)
      api.interceptors.response.eject(responseInterceptor)
    }
  }, [])

  useEffect(() => {
    // Check if user is already logged in
    const checkAuthStatus = async () => {
      try {
        const token = localStorage.getItem('authToken')
        if (!token) {
          setIsLoading(false)
          return
        }

        // Try to get current user with stored token
        const { data } = await api.get('/api/auth/me')
        setUser(data.user)
      } catch (error) {
        console.log('Auth check failed:', error)
        // Remove invalid token
        localStorage.removeItem('authToken')
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }
    
    checkAuthStatus()
  }, [])

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const { data } = await api.post('/api/auth/login', { email, password })
      
      // Store token if provided (JWT mode)
      if (data.token) {
        localStorage.setItem('authToken', data.token)
      }
      
      setUser(data.user)
    } catch (error: any) {
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error)
      }
      throw new Error('Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (username: string, email: string, password: string) => {
    setIsLoading(true)
    try {
      const { data } = await api.post('/api/auth/register', { username, email, password })
      
      // Store token if provided (JWT mode)
      if (data.token) {
        localStorage.setItem('authToken', data.token)
      }
      
      setUser(data.user)
    } catch (error: any) {
      if (error.response?.data?.error) {
        throw new Error(error.response.data.error)
      }
      throw new Error('Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      await api.post('/api/auth/logout')
    } catch (error) {
      console.error('Logout failed', error)
    } finally {
      // Always clear local state
      localStorage.removeItem('authToken')
      setUser(null)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}