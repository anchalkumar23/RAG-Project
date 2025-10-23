import { motion } from 'framer-motion'
import { Bell, User } from 'lucide-react'
import { useAppStore } from '@/store/appStore'

export default function Header() {
  const { systemStatus } = useAppStore()

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-secondary-900 border-b border-secondary-800 px-6 py-4"
    >
      <div className="flex items-center justify-between">
        <div></div>

        <div className="flex items-center space-x-4">
          <button className="btn-ghost p-2">
            <Bell className="w-5 h-5" />
          </button>

          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
        </div>
      </div>
    </motion.header>
  )
}