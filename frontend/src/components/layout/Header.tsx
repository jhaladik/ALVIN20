// src/components/layout/Header.tsx - COMPLETE FIXED VERSION
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
  const { activeUsers } = useSocket() // ✅ FIXED: Use activeUsers instead of onlineUsers
  const [searchQuery, setSearchQuery] = useState('')
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      navigate(`/projects?search=${encodeURIComponent(searchQuery)}`)
    }
  }
  
  const getPageTitle = () => {
    const path = location.pathname
    if (path.includes('/dashboard')) return 'Dashboard'
    if (path.includes('/projects') && !path.includes('/scenes') && !path.includes('/story') && !path.includes('/objects') && !path.includes('/ai')) return 'Projects'
    if (path.includes('/scenes')) return 'Scene Editor'
    if (path.includes('/story')) return 'Story Editor'
    if (path.includes('/objects')) return 'Story Objects'
    if (path.includes('/ai')) return 'AI Workshop'
    if (path.includes('/settings')) return 'Settings'
    return 'ALVIN'
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
            <Bars3Icon className="w-6 h-6" />
          </button>
          
          <div className="ml-4">
            <h1 className="text-xl font-semibold text-gray-900">{getPageTitle()}</h1>
          </div>
        </div>

        {/* Search Bar */}
        <div className="flex-1 max-w-lg mx-4">
          <form onSubmit={handleSearch} className="relative">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Search projects, scenes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </form>
        </div>

        {/* Right side icons */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <div className="relative">
            <button
              className="text-gray-500 hover:text-gray-700 focus:outline-none focus:text-gray-700"
              onClick={() => setNotificationsOpen(!notificationsOpen)}
            >
              <BellIcon className="w-6 h-6" />
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                3
              </span>
            </button>
            
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
          
          {/* Online users indicator - WITH NULL CHECKS */}
          <div className="flex items-center">
            <div className="relative flex -space-x-2">
              {activeUsers && activeUsers.length > 0 ? (
                activeUsers.slice(0, 3).map((user, index) => (
                  <div
                    key={user.id || index}
                    className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center border-2 border-white"
                    title={user.username || 'User'}
                  >
                    <span className="text-white text-xs font-medium">
                      {(user.username || 'U')[0]?.toUpperCase()}
                    </span>
                  </div>
                ))
              ) : null}
              
              {activeUsers && activeUsers.length > 3 && (
                <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center border-2 border-white">
                  <span className="text-gray-600 text-xs font-medium">+{activeUsers.length - 3}</span>
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