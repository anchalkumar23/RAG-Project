import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { Upload, MessageSquare, BarChart3, Settings } from 'lucide-react'

export default function QuickActions() {
  const navigate = useNavigate()

  const actions = [
    {
      title: 'Upload Documents',
      description: 'Add new documents to your knowledge base',
      icon: Upload,
      color: 'bg-blue-500',
      onClick: () => navigate('/documents'),
    },
    {
      title: 'Start Chat',
      description: 'Ask questions about your documents',
      icon: MessageSquare,
      color: 'bg-green-500',
      onClick: () => navigate('/chat'),
    },
    {
      title: 'View Analytics',
      description: 'See insights and statistics',
      icon: BarChart3,
      color: 'bg-purple-500',
      onClick: () => navigate('/analytics'),
    },
    {
      title: 'Configure Settings',
      description: 'Adjust system parameters',
      icon: Settings,
      color: 'bg-orange-500',
      onClick: () => navigate('/settings'),
    },
  ]

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
      <div className="space-y-3">
        {actions.map((action, index) => (
          <motion.button
            key={action.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            onClick={action.onClick}
            className="w-full flex items-center space-x-3 p-3 rounded-lg hover:bg-secondary-800 transition-colors text-left group"
          >
            <div className={`w-10 h-10 ${action.color} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform`}>
              <action.icon className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-medium text-secondary-200 group-hover:text-white transition-colors">
                {action.title}
              </p>
              <p className="text-xs text-secondary-400">
                {action.description}
              </p>
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  )
}