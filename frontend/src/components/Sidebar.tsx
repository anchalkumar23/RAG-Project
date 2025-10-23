import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useState } from 'react'
import { LayoutDashboard, FileText, MessageSquare, ChartBar as BarChart3, Settings, BookOpen, ChevronLeft, ChevronRight } from 'lucide-react'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)

  return (
    <motion.div
      initial={{ x: -250 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.3 }}
      className={`${isCollapsed ? 'w-16' : 'w-64'} bg-secondary-900 border-r border-secondary-800 flex flex-col transition-all duration-300 relative`}
    >
      {/* Header */}
      <div className="p-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
            <BookOpen className="w-6 h-6 text-white" />
          </div>
          {!isCollapsed && (
            <div>
              <h1 className="text-xl font-bold gradient-text">RAG Assistant</h1>
              <p className="text-xs text-secondary-400">Document Intelligence</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 space-y-2">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center ${isCollapsed ? 'justify-center px-2' : 'space-x-3 px-4'} py-3 rounded-lg transition-all duration-200 group ${
                isActive
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'text-secondary-300 hover:text-white hover:bg-secondary-800'
              }`
            }
            title={isCollapsed ? item.name : ''}
          >
            {({ isActive }) => (
              <>
                <item.icon
                  className={`w-5 h-5 transition-transform duration-200 ${
                    isActive ? 'scale-110' : 'group-hover:scale-105'
                  }`}
                />
                {!isCollapsed && <span className="font-medium">{item.name}</span>}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className={`p-4 border-t border-secondary-800 ${isCollapsed ? 'text-center' : ''}`}>
        <div className="text-xs text-secondary-500">
          {isCollapsed ? 'v1.0' : 'v1.0.0 • Production Ready'}
        </div>
      </div>

      {/* Toggle Button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-20 w-6 h-6 bg-secondary-800 border border-secondary-700 rounded-full flex items-center justify-center hover:bg-secondary-700 transition-colors duration-200 shadow-lg"
      >
        {isCollapsed ? (
          <ChevronRight className="w-3 h-3 text-secondary-300" />
        ) : (
          <ChevronLeft className="w-3 h-3 text-secondary-300" />
        )}
      </button>
    </motion.div>
  )
}