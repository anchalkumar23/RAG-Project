import { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import {
  Upload,
  Search,
  Plus,
} from 'lucide-react'
import { useDropzone } from 'react-dropzone'
import toast from 'react-hot-toast'
import { apiService } from '../services/api'
import { useAppStore } from '../store/appStore'
import DocumentCard from '../components/DocumentCard'
import UploadModal from '../components/UploadModal'

export default function Documents() {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [showUploadModal, setShowUploadModal] = useState(false)
  const { documents, addDocument, removeDocument } = useAppStore()
  const queryClient = useQueryClient()

  useQuery(
    'documents',
    apiService.getDocuments
  )

  const uploadMutation = useMutation(apiService.uploadDocuments, {
    onSuccess: (response) => {
      response.data.forEach((doc) => {
        addDocument({
          id: doc.id,
          name: doc.name,
          type: doc.type,
          size: doc.size,
          pages: doc.pages,
          chunks: doc.chunks,
          uploadedAt: new Date().toISOString(),
          status: 'ready',
        })
      })
      toast.success(`Successfully uploaded ${response.data.length} documents`)
      queryClient.invalidateQueries('documents')
      setShowUploadModal(false)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Upload failed')
    },
  })

  const deleteMutation = useMutation(apiService.deleteDocument, {
    onSuccess: (_, documentId) => {
      removeDocument(documentId)
      toast.success('Document deleted successfully')
      queryClient.invalidateQueries('documents')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Delete failed')
    },
  })

  const onDrop = (acceptedFiles: File[]) => {
    const fileList = acceptedFiles as unknown as FileList
    uploadMutation.mutate(fileList)
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    multiple: true,
  })

  const filteredDocuments = documents.filter((doc) => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterType === 'all' || doc.type.toLowerCase() === filterType
    return matchesSearch && matchesFilter
  })

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Documents</h1>
          <p className="text-secondary-400">
            Manage your document collection and processing
          </p>
        </div>
        <button
          onClick={() => setShowUploadModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-4 h-4" />
          <span>Upload Documents</span>
        </button>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-4"
      >
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input-field pl-10 w-full"
          />
        </div>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="input-field"
        >
          <option value="all">All Types</option>
          <option value="pdf">PDF</option>
          <option value="word">Word</option>
        </select>
      </motion.div>

      {documents.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className={`card border-2 border-dashed cursor-pointer transition-colors duration-200 ${
            isDragActive
              ? 'border-primary-500 bg-primary-500/10'
              : 'border-secondary-700 hover:border-secondary-600'
          }`}
          {...getRootProps()}
        >
          <input {...getInputProps()} />
          <div className="text-center py-12">
            <Upload className="w-16 h-16 text-secondary-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-secondary-200 mb-2">
              Upload Your First Documents
            </h3>
            <p className="text-secondary-400 mb-4">
              Drag and drop PDF or Word files here, or click to browse
            </p>
            <button className="btn-primary">
              Choose Files
            </button>
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {filteredDocuments.map((document, index) => (
            <DocumentCard
              key={document.id}
              document={document}
              index={index}
              onDelete={(id) => deleteMutation.mutate(id)}
              isDeleting={deleteMutation.isLoading}
            />
          ))}
        </motion.div>
      )}

      <UploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUpload={(files) => uploadMutation.mutate(files)}
        isUploading={uploadMutation.isLoading}
      />
    </div>
  )
}