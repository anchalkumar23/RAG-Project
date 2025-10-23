import { motion } from 'framer-motion'
import { User, Bot, ExternalLink } from 'lucide-react'

interface ChatMessageProps {
  message: {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    sources?: Array<{
      content: string
      metadata: Record<string, any>
    }>
  }
  index: number
}

export default function ChatMessage({ message, index }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
            isUser
              ? 'bg-primary-600 ml-3'
              : 'bg-secondary-700 mr-3'
          }`}
        >
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <Bot className="w-4 h-4 text-secondary-200" />
          )}
        </div>
        
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? 'bg-primary-600 text-white'
              : 'bg-secondary-800 text-secondary-100'
          }`}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
          
          <p className="text-xs text-secondary-400 mt-2">
            {new Date(message.timestamp).toLocaleTimeString()}
          </p>
        </div>
      </div>
    </motion.div>
  )
}