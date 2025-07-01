// File: src/components/layout/Sidebar.tsx
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import {
  HomeIcon,
  DocumentTextIcon,
  CogIcon,
  UserGroupIcon,
  SparklesIcon,
  FolderIcon,
  ArrowLeftOnRectangleIcon
} from '@heroicons/react/24/outline'

type SidebarProps = {
  isOpen: boolean
}

const Sidebar = ({ isOpen }: SidebarProps) => {
  const { user, logout } = useAuth()

  return (
    <div className={`bg-indigo-900 text-white transition-all duration-300 ${isOpen ? 'w-64' : 'w-20'}`}>
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center justify-center h-16 border-b border-indigo-800">
          <div className={`flex items-center ${isOpen ? 'justify-start pl-4' : 'justify-center'}`}>
            <SparklesIcon className="h-8 w-8 text-indigo-300" />
            {isOpen && <span className="ml-2 text-xl font-bold">StoryForge AI</span>}
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="flex-1 py-4 overflow-y-auto">
          <ul className="space-y-2 px-2">
            <li>
              <NavLink 
                to="/dashboard" 
                className={({ isActive }) => 
                  `flex items-center py-2 px-4 rounded-md ${isActive ? 'bg-indigo-700' : 'hover:bg-indigo-800'}`
                }
              >
                <HomeIcon className="h-6 w-6" />
                {isOpen && <span className="ml-3">Dashboard</span>}
              </NavLink>
            </li>
            <li>
              <NavLink 
                to="/projects" 
                className={({ isActive }) => 
                  `flex items-center py-2 px-4 rounded-md ${isActive ? 'bg-indigo-700' : 'hover:bg-indigo-800'}`
                }
              >
                <FolderIcon className="h-6 w-6" />
                {isOpen && <span className="ml-3">Projects</span>}
              </NavLink>
            </li>
            <li>
              <NavLink 
                to="/settings" 
                className={({ isActive }) => 
                  `flex items-center py-2 px-4 rounded-md ${isActive ? 'bg-indigo-700' : 'hover:bg-indigo-800'}`
                }
              >
                <CogIcon className="h-6 w-6" />
                {isOpen && <span className="ml-3">Settings</span>}
              </NavLink>
            </li>
          </ul>
        </nav>
        
        {/* User info */}
        <div className="border-t border-indigo-800 p-4">
          <div className="flex items-center">
            <div className="h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center">
              <span className="text-white font-medium">
                {user?.username ? user.username[0].toUpperCase() : '?'}
              </span>
            </div>
            {isOpen && (
              <div className="ml-3 overflow-hidden">
                <p className="text-sm font-medium truncate">{user?.username}</p>
                <p className="text-xs text-indigo-300 truncate">{user?.email}</p>
                <p className="text-xs text-indigo-300 mt-1">
                  <span className="font-medium">{user?.tokensRemaining}</span> tokens left
                </p>
              </div>
            )}
          </div>
          
          <button 
            className="mt-4 w-full flex items-center justify-center py-2 px-4 rounded-md hover:bg-indigo-800 transition-colors"
            onClick={logout}
          >
            <ArrowLeftOnRectangleIcon className="h-5 w-5" />
            {isOpen && <span className="ml-2">Logout</span>}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Sidebar