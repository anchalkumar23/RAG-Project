import { motion } from 'framer-motion'
import { Bot } from 'lucide-react'

export default function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="flex justify-start mb-4"
    >
      <div className="flex">
        <div className="w-8 h-8 rounded-full bg-secondary-700 flex items-center justify-center flex-shrink-0 mr-3">
          <Bot className="w-4 h-4 text-secondary-200" />
        </div>
        
        <div className="bg-secondary-800 rounded-2xl px-4 py-3">
          <div className="flex space-x-1">
            <motion.div
              className="w-2 h-2 bg-secondary-400 rounded-full"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1, repeat: Infinity, delay: 0 }}
            />
            <motion.div
              className="w-2 h-2 bg-secondary-400 rounded-full"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
            />
            <motion.div
              className="w-2 h-2 bg-secondary-400 rounded-full"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
            />
          </div>
        </div>
      </div>
    </motion.div>
  )
}