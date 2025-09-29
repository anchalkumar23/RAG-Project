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
    },
    multiple: true,
  })

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleUpload = () => {
    if (selectedFiles.length > 0) {
      const fileList = selectedFiles as unknown as FileList
      onUpload(fileList)
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
            className="bg-secondary-900 rounded-xl border border-secondary-800 w-full max-w-2xl max-h-[80vh] overflow-hidden"
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

            <div className="p-6 space-y-6">
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
                <p className="text-sm text-secondary-400">
                  Supports PDF, DOC, and DOCX files
                </p>
              </div>

              {selectedFiles.length > 0 && (
                <div className="space-y-3 max-h-60 overflow-y-auto">
                  <h3 className="font-medium text-secondary-200">
                    Selected Files ({selectedFiles.length})
                  </h3>
                  {selectedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between bg-secondary-800 rounded-lg p-3"
                    >
                      <div className="flex items-center space-x-3">
                        <File className="w-5 h-5 text-primary-500" />
                        <div>
                          <p className="text-sm font-medium text-secondary-200">
                            {file.name}
                          </p>
                          <p className="text-xs text-secondary-400">
                            {formatFileSize(file.size)}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        className="p-1 hover:bg-secondary-700 rounded transition-colors"
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex items-center justify-end space-x-3 p-6 border-t border-secondary-800">
              <button onClick={handleClose} className="btn-ghost">
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={selectedFiles.length === 0 || isUploading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUploading ? 'Uploading...' : `Upload ${selectedFiles.length} Files`}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}