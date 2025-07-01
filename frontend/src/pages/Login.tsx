// File: src/pages/Login.tsx
import { useState, FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import { SparklesIcon } from '@heroicons/react/24/outline'

const Login = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { login } = useAuth()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      await login(email, password)
      // Successful login will redirect via the App component
    } catch (err) {
      setError('Invalid email or password')
      setIsSubmitting(false)
    }
  }

  const handleDemoLogin = async () => {
    setEmail('demo@storyforge.ai')
    setPassword('demo123')
    setError('')
    setIsSubmitting(true)

    try {
      await login('demo@storyforge.ai', 'demo123')
      // Successful login will redirect via the App component
    } catch (err) {
      setError('Demo login failed. Please try again.')
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="card max-w-md w-full space-y-8">
        <div>
          <div className="flex justify-center">
            <SparklesIcon className="h-12 w-12 text-indigo-600" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-bold text-gray-900">
            Sign in to StoryForge AI
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Unleash your creative potential
          </p>
        </div>
        
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-standard mt-1"
                placeholder="your@email.com"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-standard mt-1"
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                Remember me
              </label>
            </div>

            <div className="text-sm">
              <a href="#" className="font-medium text-indigo-600 hover:text-indigo-500">
                Forgot your password?
              </a>
            </div>
          </div>

          <div className="space-y-3">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full btn-primary flex justify-center items-center"
            >
              {isSubmitting ? <LoadingSpinner size="sm" /> : 'Sign in'}
            </button>
            
            <button
              type="button"
              onClick={handleDemoLogin}
              disabled={isSubmitting}
              className="w-full btn-secondary flex justify-center"
            >
              Use demo account
            </button>
          </div>
        </form>
        
        <div className="text-center">
          <span className="text-gray-600 text-sm">
            Don't have an account?{' '}
            <Link to="/register" className="text-indigo-600 hover:text-indigo-500 font-medium">
              Register
            </Link>
          </span>
        </div>
      </div>
    </div>
  )
}

export default Login