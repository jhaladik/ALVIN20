// File: src/components/layout/Header.tsx
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Bars3Icon, BellIcon, MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { useAuth } from '../../hooks/useAuth'
import { useSocket } from '../../hooks/useSocket'

type HeaderProps = {
  toggleSidebar: () => void
}

const Header = ({ toggleSidebar }: HeaderProps) => {
  const location = useLocation()
  const navigate = useNavigate()
  const { onlineUsers } = useSocket()
  const [searchQuery, setSearchQuery] = useState('')
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // Implement search functionality
    if (searchQuery.trim()) {
      navigate(`/projects?search=${encodeURIComponent(searchQuery)}`)
    }
  }
  
  // Get page title based on current route
  const getPageTitle = () => {
    const path = location.pathname
    if (path.includes('/dashboard')) return 'Dashboard'
    if (path.includes('/projects') && !path.includes('/scenes') && !path.includes('/story') && !path.includes('/objects') && !path.includes('/ai')) return 'Projects'
    if (path.includes('/scenes')) return 'Scene Editor'
    if (path.includes('/story')) return 'Story Editor'
    if (path.includes('/objects')) return 'Story Objects'
    if (path.includes('/ai')) return 'AI Workshop'
    if (path.includes('/settings')) return 'Settings'
    return 'StoryForge AI'
  }
  
  return (
    <header className="bg-white shadow-sm z-10">
      <div className="flex items-center justify-between h-16 px-4 md:px-6">
        <div className="flex items-center">
          <button
            type="button"
            className="text-gray-500 hover:text-gray-700 focus:outline-none"
            onClick={toggleSidebar}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
          <h1 className="ml-4 text-lg font-medium text-gray-800">
            {getPageTitle()}
          </h1>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Search bar - only show on certain pages */}
          {(location.pathname === '/projects' || location.pathname === '/dashboard') && (
            <form onSubmit={handleSearch} className="hidden md:block">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="search"
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white 
                  placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:border-indigo-500 
                  focus:ring-1 focus:ring-indigo-500"
                  placeholder="Search projects..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </form>
          )}
          
          {/* Notification bell */}
          <div className="relative">
            <button
              type="button"
              className="flex items-center text-gray-500 hover:text-gray-700 focus:outline-none"
              onClick={() => setNotificationsOpen(!notificationsOpen)}
            >
              <BellIcon className="h-6 w-6" />
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full flex items-center justify-center text-xs text-white">
                2
              </span>
            </button>
            
            {/* Dropdown menu */}
            {notificationsOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg overflow-hidden z-20">
                <div className="py-2 px-4 bg-gray-50 text-sm font-medium text-gray-700 border-b border-gray-200 flex justify-between items-center">
                  <span>Notifications</span>
                  <button 
                    onClick={() => setNotificationsOpen(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
                <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                  <div className="px-4 py-3 hover:bg-gray-50">
                    <p className="text-sm font-medium text-gray-900">New comment on "Chapter 1"</p>
                    <p className="text-xs text-gray-500 mt-1">5 minutes ago</p>
                  </div>
                  <div className="px-4 py-3 hover:bg-gray-50">
                    <p className="text-sm font-medium text-gray-900">AI analysis completed</p>
                    <p className="text-xs text-gray-500 mt-1">1 hour ago</p>
                  </div>
                </div>
                <a
                  href="#"
                  className="block text-center py-2 text-sm text-indigo-600 bg-gray-50 hover:bg-gray-100 border-t border-gray-200"
                >
                  View all notifications
                </a>
              </div>
            )}
          </div>
          
          {/* Online users indicator */}
          <div className="flex items-center">
            <div className="relative flex -space-x-2">
              {onlineUsers.length > 0 ? (
                onlineUsers.slice(0, 3).map((user, index) => (
                  <div
                    key={index}
                    className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center border-2 border-white"
                    title={user}
                  >
                    <span className="text-white text-xs font-medium">{user[0]?.toUpperCase()}</span>
                  </div>
                ))
              ) : null}
              
              {onlineUsers.length > 3 && (
                <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center border-2 border-white">
                  <span className="text-gray-600 text-xs font-medium">+{onlineUsers.length - 3}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header