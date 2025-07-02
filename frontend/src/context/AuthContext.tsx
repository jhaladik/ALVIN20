// frontend/src/context/AuthContext.tsx - FIXED VERSION with Token Compatibility
import { createContext, useState, useEffect, ReactNode } from 'react'
import { api } from '../services/api'

type User = {
  id: string
  email: string
  username: string
  full_name?: string
  plan: string
  tokens_remaining?: number
  tokens_limit?: number
  created_at: string
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
        if (error.response?.status === 401 && !error.config.url?.includes('/api/auth/me')) {
          // Token expired or invalid (but not during initial auth check)
          localStorage.removeItem('authToken')
          setUser(null)
          // Only redirect if we're not already on a public page
          if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
            window.location.href = '/login'
          }
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
      
      // ✅ FIXED: Handle both token field variations
      const token = data.access_token || data.token
      if (token) {
        localStorage.setItem('authToken', token)
      } else {
        throw new Error('No authentication token received')
      }
      
      setUser(data.user)
    } catch (error: any) {
      console.error('Login error:', error)
      if (error.response?.data?.message) {
        throw new Error(error.response.data.message)
      } else if (error.response?.data?.error) {
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
      const { data } = await api.post('/api/auth/register', { 
        username, 
        email, 
        password 
      })
      
      // ✅ FIXED: Handle both token field variations
      const token = data.access_token || data.token
      if (token) {
        localStorage.setItem('authToken', token)
      } else {
        throw new Error('No authentication token received')
      }
      
      setUser(data.user)
    } catch (error: any) {
      console.error('Registration error:', error)
      if (error.response?.data?.message) {
        throw new Error(error.response.data.message)
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error)
      }
      throw new Error('Registration failed')
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      // Try to logout on server (but don't fail if it doesn't work)
      await api.post('/api/auth/logout')
    } catch (error) {
      console.error('Server logout failed', error)
      // Continue with local logout even if server logout fails
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