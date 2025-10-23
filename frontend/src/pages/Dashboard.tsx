import { motion } from 'framer-motion'
import { useQuery } from 'react-query'
import { FileText, MessageSquare, Activity } from 'lucide-react'
import { apiService } from '../services/api'
import { useAppStore } from '../store/appStore'
import StatsCard from '../components/StatsCard.tsx'
import RecentActivity from '../components/RecentActivity'
import QuickActions from '../components/QuickActions'

export default function Dashboard() {
  const { documents, chatHistory } = useAppStore()
  
  const { data: systemStats } = useQuery(
    'systemStats',
    apiService.getSystemStats,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  )

  const stats = [
    {
      title: 'Total Documents',
      value: documents.length.toString(),
      change: 'Active',
      changeType: 'neutral' as const,
      icon: FileText,
    },
    {
      title: 'Chat Messages',
      value: chatHistory.length.toString(),
      change: 'Recent',
      changeType: 'neutral' as const,
      icon: MessageSquare,
    },
    {
      title: 'System Status',
      value: systemStats?.data.pipeline_status === 'initialized' ? 'Ready' : 'Not Ready',
      change: systemStats?.data.pipeline_status === 'initialized' ? 'Healthy' : 'Initializing',
      changeType: 'neutral' as const,
      icon: Activity,
    },
  ]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold gradient-text mb-2">
          Welcome to RAG Assistant
        </h1>
        <p className="text-secondary-400">
          Intelligent document processing and question answering system
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {stats.map((stat, index) => (
          <StatsCard key={stat.title} {...stat} index={index} />
        ))}
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="lg:col-span-2"
        >
          <RecentActivity />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <QuickActions />
        </motion.div>
      </div>

      {systemStats && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-primary-500" />
            System Overview
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-secondary-800 rounded-lg p-4">
              <h4 className="font-medium text-secondary-200 mb-2">Model Configuration</h4>
              <p className="text-sm text-secondary-400">
                {systemStats.data.llm?.model_type} - {systemStats.data.llm?.model_name}
              </p>
            </div>
            <div className="bg-secondary-800 rounded-lg p-4">
              <h4 className="font-medium text-secondary-200 mb-2">Vector Store</h4>
              <p className="text-sm text-secondary-400">
                {systemStats.data.vector_store?.document_count} documents indexed
              </p>
            </div>
            <div className="bg-secondary-800 rounded-lg p-4">
              <h4 className="font-medium text-secondary-200 mb-2">Processing</h4>
              <p className="text-sm text-secondary-400">
                Chunk size: {systemStats.data.document_processor?.chunk_size}
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}