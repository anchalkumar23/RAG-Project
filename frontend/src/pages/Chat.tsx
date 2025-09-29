import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useMutation } from 'react-query'
import { Send, Bot, FileText, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { apiService } from '../services/api'
import { useAppStore } from '../store/appStore'
import ChatMessage from '../components/ChatMessage'
import TypingIndicator from '../components/TypingIndicator'

export default function Chat() {
  const [message, setMessage] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  const {
    chatHistory,
    addChatMessage,
    clearChatHistory,
    isTyping,
    setIsTyping,
    documents,
  } = useAppStore()

  const sendMessageMutation = useMutation(apiService.sendMessage, {
    onMutate: () => {
      setIsTyping(true)
      // Add user message immediately
      addChatMessage({
        id: Date.now().toString(),
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      })
      setMessage('')
    },
    onSuccess: (response) => {
      setIsTyping(false)
      addChatMessage({
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.answer,
        timestamp: new Date().toISOString(),
        sources: response.data.sources,
      })
    },
    onError: (error: any) => {
      setIsTyping(false)
      toast.error(error.response?.data?.message || 'Failed to send message')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || sendMessageMutation.isLoading) return
    
    if (documents.length === 0) {
      toast.error('Please upload some documents first')
      return
    }

    sendMessageMutation.mutate(message.trim())
  }

  const handleClearChat = () => {
    clearChatHistory()
    toast.success('Chat history cleared')
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [chatHistory, isTyping])

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-8rem)]">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between mb-6"
      >
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Chat Assistant</h1>
          <p className="text-secondary-400">
            Ask questions about your documents
          </p>
        </div>
        {chatHistory.length > 0 && (
          <button
            onClick={handleClearChat}
            className="btn-ghost flex items-center space-x-2"
          >
            <Trash2 className="w-4 h-4" />
            <span>Clear Chat</span>
          </button>
        )}
      </motion.div>

      <div className="flex-1 flex flex-col bg-secondary-900 rounded-xl border border-secondary-800 overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {chatHistory.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center justify-center h-full text-center py-12"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center mb-4">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-secondary-200 mb-2">
                Start a Conversation
              </h3>
              <p className="text-secondary-400 mb-6 max-w-md">
                Ask me anything about your uploaded documents. I can help you find information,
                summarize content, and answer specific questions.
              </p>
              {documents.length === 0 && (
                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
                  <p className="text-yellow-400 text-sm">
                    <FileText className="w-4 h-4 inline mr-2" />
                    Upload some documents first to start chatting
                  </p>
                </div>
              )}
            </motion.div>
          ) : (
            <AnimatePresence>
              {chatHistory.map((msg, index) => (
                <ChatMessage key={msg.id} message={msg} index={index} />
              ))}
              {isTyping && <TypingIndicator />}
            </AnimatePresence>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-secondary-800 p-4">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <input
              ref={inputRef}
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder={
                documents.length === 0
                  ? 'Upload documents to start chatting...'
                  : 'Ask a question about your documents...'
              }
              disabled={documents.length === 0 || sendMessageMutation.isLoading}
              className="flex-1 input-field"
            />
            <button
              type="submit"
              disabled={!message.trim() || documents.length === 0 || sendMessageMutation.isLoading}
              className="btn-primary px-6 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="flex items-center justify-between mt-2 text-xs text-secondary-500">
            <span>{documents.length} documents available</span>
            <span>Press Enter to send</span>
          </div>
        </div>
      </div>
    </div>
  )
}