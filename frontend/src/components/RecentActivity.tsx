import { motion } from 'framer-motion'
import { Clock, FileText, MessageSquare, Upload } from 'lucide-react'
import { useAppStore } from '@/store/appStore'

export default function RecentActivity() {
  const { documents, chatHistory } = useAppStore()

  // Combine and sort recent activities
  const activities = [
    ...documents.slice(-5).map((doc) => ({
      id: doc.id,
      type: 'document',
      title: `Uploaded ${doc.name}`,
      timestamp: doc.uploadedAt,
      icon: Upload,
    })),
    ...chatHistory.slice(-5).filter(msg => msg.role === 'user').map((msg) => ({
      id: msg.id,
      type: 'chat',
      title: msg.content.substring(0, 50) + (msg.content.length > 50 ? '...' : ''),
      timestamp: msg.timestamp,
      icon: MessageSquare,
    })),
  ]
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 8)

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60))

    if (diffInMinutes < 1) return 'Just now'
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`
    return `${Math.floor(diffInMinutes / 1440)}d ago`
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <Clock className="w-5 h-5 mr-2 text-primary-500" />
        Recent Activity
      </h3>
      
      {activities.length === 0 ? (
        <div className="text-center py-8 text-secondary-400">
          <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No recent activity</p>
          <p className="text-sm">Upload documents or start chatting to see activity</p>
        </div>
      ) : (
        <div className="space-y-3">
          {activities.map((activity, index) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="flex items-center space-x-3 p-3 rounded-lg hover:bg-secondary-800 transition-colors"
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                activity.type === 'document' 
                  ? 'bg-blue-500/10 text-blue-500' 
                  : 'bg-green-500/10 text-green-500'
              }`}>
                <activity.icon className="w-4 h-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-secondary-200 truncate">
                  {activity.title}
                </p>
                <p className="text-xs text-secondary-400">
                  {formatTimeAgo(activity.timestamp)}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}