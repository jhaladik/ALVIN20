// File: src/components/ui/LoadingSpinner.tsx
type SpinnerSize = 'sm' | 'md' | 'lg'

type LoadingSpinnerProps = {
  size?: SpinnerSize
  className?: string
}

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
}

const LoadingSpinner = ({ size = 'md', className = '' }: LoadingSpinnerProps) => {
  return (
    <div className="flex justify-center items-center">
      <div
        className={`${sizeClasses[size]} ${className} animate-spin rounded-full border-4 border-gray-200 border-t-indigo-600`}
      ></div>
    </div>
  )
}

export default LoadingSpinner