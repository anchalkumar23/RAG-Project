import { motion } from 'framer-motion'
import { useQuery } from 'react-query'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts'
import { FileText, MessageSquare, Clock, TrendingUp } from 'lucide-react'
import { apiService } from '@/services/api'
import { useAppStore } from '@/store/appStore'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export default function Analytics() {
  const { documents, chatHistory } = useAppStore()
  
  useQuery(
    'analytics',
    apiService.getAnalytics
  )

  // Prepare chart data
  const documentTypeData = documents.reduce((acc, doc) => {
    const type = doc.type
    acc[type] = (acc[type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const pieData = Object.entries(documentTypeData).map(([name, value]) => ({
    name,
    value,
  }))

  const documentSizeData = documents.map((doc) => ({
    name: doc.name.substring(0, 20) + '...',
    size: Math.round(doc.size / 1024), // Convert to MB
    pages: doc.pages,
    chunks: doc.chunks,
  }))

  const chatActivityData = chatHistory
    .filter((msg) => msg.role === 'user')
    .reduce((acc, msg) => {
      const date = new Date(msg.timestamp).toLocaleDateString()
      acc[date] = (acc[date] || 0) + 1
      return acc
    }, {} as Record<string, number>)

  const lineData = Object.entries(chatActivityData).map(([date, count]) => ({
    date,
    messages: count,
  }))

  const stats = [
    {
      title: 'Total Documents',
      value: documents.length,
      icon: FileText,
      color: 'text-blue-500',
    },
    {
      title: 'Total Messages',
      value: chatHistory.length,
      icon: MessageSquare,
      color: 'text-green-500',
    },
    {
      title: 'Avg Processing Time',
      value: '2.3s',
      icon: Clock,
      color: 'text-yellow-500',
    },
    {
      title: 'Success Rate',
      value: '98.5%',
      icon: TrendingUp,
      color: 'text-purple-500',
    },
  ]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold gradient-text mb-2">Analytics</h1>
        <p className="text-secondary-400">
          Insights and statistics about your RAG system
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {stats.map((stat) => (
          <div key={stat.title} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-secondary-400 text-sm">{stat.title}</p>
                <p className="text-2xl font-bold text-secondary-100">
                  {stat.value}
                </p>
              </div>
              <stat.icon className={`w-8 h-8 ${stat.color}`} />
            </div>
          </div>
        ))}
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-4">Document Types</h3>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((_, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-secondary-400">
              No documents to display
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-4">Chat Activity</h3>
          {lineData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={lineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="date" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="messages"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-secondary-400">
              No chat activity to display
            </div>
          )}
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="card"
      >
        <h3 className="text-lg font-semibold mb-4">Document Overview</h3>
        {documentSizeData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={documentSizeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="size" fill="#3b82f6" name="Size (MB)" />
              <Bar dataKey="pages" fill="#10b981" name="Pages" />
              <Bar dataKey="chunks" fill="#f59e0b" name="Chunks" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-64 text-secondary-400">
            No documents to display
          </div>
        )}
      </motion.div>
    </div>
  )
}