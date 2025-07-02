// ===== FIXED Button.tsx =====
import { ReactNode } from 'react'
import LoadingSpinner from './LoadingSpinner' // ✅ ADD THIS IMPORT

type ButtonVariant = 'primary' | 'secondary' | 'success' | 'danger' | 'ghost'
type ButtonSize = 'sm' | 'md' | 'lg'

type ButtonProps = {
  children: ReactNode
  variant?: ButtonVariant
  size?: ButtonSize
  isLoading?: boolean
  disabled?: boolean
  className?: string
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
}

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled = false,
  className = '',
  onClick,
  type = 'button',
}: ButtonProps) => {
  const variantClasses = {
    primary: 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-500',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
  }

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  }

  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center rounded-md font-medium transition-colors 
                 focus:outline-none focus:ring-2 focus:ring-offset-2
                 ${variantClasses[variant]} 
                 ${sizeClasses[size]}
                 ${disabled || isLoading ? 'opacity-60 cursor-not-allowed' : ''}
                 ${className}`}
      onClick={onClick}
      disabled={disabled || isLoading}
    >
      {isLoading ? <LoadingSpinner size="sm" className="mr-2" /> : null}
      {children}
    </button>
  )
}

export default Button