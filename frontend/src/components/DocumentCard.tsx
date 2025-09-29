import { motion } from 'framer-motion'
import { FileText, Trash2, Calendar, HardDrive, FileImage } from 'lucide-react'

interface Document {
  id: string
  name: string
  type: string
  size: number
  pages: number
  chunks: number
  uploadedAt: string
  status: 'processing' | 'ready' | 'error'
}

interface DocumentCardProps {
  document: Document
  index: number
  onDelete: (id: string) => void
  isDeleting: boolean
}

export default function DocumentCard({
  document,
  index,
  onDelete,
  isDeleting,
}: DocumentCardProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'bg-green-500'
      case 'processing':
        return 'bg-yellow-500'
      case 'error':
        return 'bg-red-500'
      default:
        return 'bg-secondary-500'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return FileText
      case 'word':
        return FileImage
      default:
        return FileText
    }
  }

  const TypeIcon = getTypeIcon(document.type)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.1 }}
      className="card hover:bg-secondary-800 transition-all duration-200 group"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-500/10 rounded-lg flex items-center justify-center">
            <TypeIcon className="w-5 h-5 text-primary-500" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-secondary-100 truncate" title={document.name}>
              {document.name}
            </h3>
            <div className="flex items-center space-x-2 mt-1">
              <div className={`w-2 h-2 rounded-full ${getStatusColor(document.status)}`} />
              <span className="text-xs text-secondary-400 capitalize">
                {document.status}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={() => onDelete(document.id)}
          disabled={isDeleting}
          className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-2 hover:bg-red-500/10 rounded-lg"
        >
          <Trash2 className="w-4 h-4 text-red-500" />
        </button>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-secondary-400 flex items-center">
            <HardDrive className="w-4 h-4 mr-1" />
            Size
          </span>
          <span className="text-secondary-200">{formatFileSize(document.size * 1024)}</span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-secondary-400">Pages</span>
          <span className="text-secondary-200">{document.pages}</span>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-secondary-400">Chunks</span>
          <span className="text-secondary-200">{document.chunks}</span>
        </div>
        
        <div className="flex items-center justify-between text-sm pt-2 border-t border-secondary-800">
          <span className="text-secondary-400 flex items-center">
            <Calendar className="w-4 h-4 mr-1" />
            Uploaded
          </span>
          <span className="text-secondary-200">{formatDate(document.uploadedAt)}</span>
        </div>
      </div>
    </motion.div>
  )
}