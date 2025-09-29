import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string
  change: string
  changeType: 'positive' | 'negative' | 'neutral'
  icon: LucideIcon
  index: number
}

export default function StatsCard({
  title,
  value,
  change,
  changeType,
  icon: Icon,
  index,
}: StatsCardProps) {
  const changeColor = {
    positive: 'text-green-500',
    negative: 'text-red-500',
    neutral: 'text-secondary-400',
  }[changeType]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="card hover:bg-secondary-800 transition-colors duration-200"
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-secondary-400 text-sm font-medium">{title}</p>
          <p className="text-2xl font-bold text-secondary-100 mt-1">{value}</p>
          <p className={`text-sm mt-1 ${changeColor}`}>{change}</p>
        </div>
        <div className="w-12 h-12 bg-primary-500/10 rounded-lg flex items-center justify-center">
          <Icon className="w-6 h-6 text-primary-500" />
        </div>
      </div>
    </motion.div>
  )
}