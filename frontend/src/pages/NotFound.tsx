// File: src/pages/NotFound.tsx
import { Link } from 'react-router-dom'
import { FaceFrownIcon } from '@heroicons/react/24/outline'

const NotFound = () => {
  return (
    <div className="min-h-screen flex flex-col justify-center items-center px-4">
      <FaceFrownIcon className="h-16 w-16 text-indigo-600 mb-4" />
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Page not found</h1>
      <p className="text-lg text-gray-600 mb-8 text-center max-w-md">
        Sorry, we couldn't find the page you're looking for.
      </p>
      <Link to="/" className="btn-primary">
        Go back home
      </Link>
    </div>
  )
}

export default NotFound