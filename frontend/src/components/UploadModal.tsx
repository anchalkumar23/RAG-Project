import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { X, Upload, File, Trash2 } from 'lucide-react'

interface UploadModalProps {
  isOpen: boolean
  onClose: () => void
  onUpload: (files: FileList) => void
  isUploading: boolean
}

export default function UploadModal({
  isOpen,
  onClose,
  onUpload,
  isUploading,
}: UploadModalProps) {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const onDrop = (acceptedFiles: File[]) => {
    setSelectedFiles((prev) => [...prev, ...acceptedFiles])
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'application/vnd.ms-powerpoint': ['.ppt'],
      'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/gif': ['.gif'],
      'image/bmp': ['.bmp'],
      'image/tiff': ['.tiff'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    multiple: true,
  })

  const removeFile = (indexToRemove: number) => {
    setSelectedFiles((prev) => prev.filter((_, index) => index !== indexToRemove))
  }

  const handleUpload = () => {
    if (selectedFiles.length > 0) {
      // Create a proper FileList-like object
      const dt = new DataTransfer()
      selectedFiles.forEach(file => dt.items.add(file))
      onUpload(dt.files)
    }
  }

  const handleClose = () => {
    setSelectedFiles([])
    onClose()
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getUploadButtonText = () => {
    const count = selectedFiles.length
    if (count === 0) return 'Select Files'
    if (count === 1) return 'Upload 1 File'
    return `Upload ${count} Files`
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
          onClick={handleClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            className="bg-secondary-900 rounded-xl border border-secondary-800 w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between p-6 border-b border-secondary-800">
              <h2 className="text-xl font-semibold text-secondary-100">
                Upload Documents
              </h2>
              <button
                onClick={handleClose}
                className="p-2 hover:bg-secondary-800 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-secondary-400" />
              </button>
            </div>

            <div className="p-6 space-y-6 flex-1 overflow-hidden flex flex-col">
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-primary-500 bg-primary-500/10'
                    : 'border-secondary-700 hover:border-secondary-600'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="w-12 h-12 text-secondary-500 mx-auto mb-4" />
                <p className="text-secondary-200 mb-2">
                  Drag and drop files here, or click to browse
                </p>
                <p className="text-sm text-secondary-400 mb-2">
                  Supports PDF, DOC, DOCX, PPT, PPTX, PNG, JPG, TXT, MD files
                </p>
                <p className="text-xs text-secondary-500">
                  You can upload up to 6000 files at once
                </p>
              </div>

              {selectedFiles.length > 0 && (
                <div className="flex-1 flex flex-col min-h-0">
                  <h3 className="font-medium text-secondary-200 mb-3">
                    Selected Files ({selectedFiles.length})
                  </h3>
                  <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                    {selectedFiles.map((file, index) => (
                      <div
                        key={`${file.name}-${file.size}-${index}`}
                        className="flex items-center justify-between bg-secondary-800 rounded-lg p-3 flex-shrink-0"
                      >
                        <div className="flex items-center space-x-3 min-w-0 flex-1">
                          <File className="w-5 h-5 text-primary-500 flex-shrink-0" />
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium text-secondary-200 truncate">
                              {file.name}
                            </p>
                            <p className="text-xs text-secondary-400">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => removeFile(index)}
                          className="p-1 hover:bg-secondary-700 rounded transition-colors flex-shrink-0 ml-2"
                          disabled={isUploading}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center justify-end space-x-3 p-6 border-t border-secondary-800 flex-shrink-0">
              <button onClick={handleClose} className="btn-ghost" disabled={isUploading}>
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={selectedFiles.length === 0 || isUploading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUploading ? 'Uploading...' : getUploadButtonText()}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}