// File: src/components/layout/Layout.tsx
import { Outlet } from 'react-router-dom'
import { useState } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'

const Layout = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }
  
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar isOpen={isSidebarOpen} />
      
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header toggleSidebar={toggleSidebar} />
        
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout