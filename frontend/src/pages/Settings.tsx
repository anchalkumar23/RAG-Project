import { useState } from 'react'
import { motion } from 'framer-motion'
import { useMutation } from 'react-query'
import { Save, Download, Upload, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import { apiService } from '@/services/api'
import { useAppStore } from '@/store/appStore'

export default function Settings() {
  const { modelConfig, updateModelConfig } = useAppStore()
  const [config, setConfig] = useState(modelConfig)

  const initializeMutation = useMutation(apiService.initializePipeline, {
    onSuccess: () => {
      toast.success('Pipeline initialized successfully')
      updateModelConfig(config)
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Initialization failed')
    },
  })

  const handleSave = () => {
    // Validate OpenAI API key if OpenAI model is selected
    if (config.modelType === 'OpenAI' && !config.openaiApiKey) {
      toast.error('OpenAI API key is required for OpenAI models')
      return
    }
    
    initializeMutation.mutate(config)
  }

  const handleExport = async () => {
    try {
      const blob = await apiService.exportVectorStore()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `vector_store_backup_${new Date().toISOString().split('T')[0]}.pkl`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success('Vector store backup created successfully')
    } catch (error) {
      toast.error('Export failed')
    }
  }

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      apiService.importVectorStore(file)
        .then(() => {
          toast.success('Vector store imported successfully')
        })
        .catch(() => {
          toast.error('Import failed')
        })
    }
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold gradient-text mb-2">Settings</h1>
        <p className="text-secondary-400">
          Configure your RAG system parameters
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-4">Model Configuration</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Model Type
              </label>
              <select
                value={config.modelType}
                onChange={(e) => setConfig({ ...config, modelType: e.target.value })}
                className="input-field w-full"
              >
                <option value="HuggingFace Open Source">HuggingFace Open Source</option>
                <option value="OpenAI">OpenAI</option>
                <option value="Ollama">Ollama</option>
                <option value="Local Model">Local Model</option>
              </select>
            </div>

            {config.modelType === 'OpenAI' && (
              <div>
                <label className="block text-sm font-medium text-secondary-200 mb-2">
                  OpenAI API Key
                </label>
                <input
                  type="password"
                  value={config.openaiApiKey || ''}
                  onChange={(e) => setConfig({ ...config, openaiApiKey: e.target.value })}
                  placeholder="Enter your OpenAI API key"
                  className="input-field w-full"
                />
              </div>
            )}

            {config.modelType === 'Ollama' && (
              <div>
                <label className="block text-sm font-medium text-secondary-200 mb-2">
                  Ollama Base URL
                </label>
                <input
                  type="text"
                  value={config.ollamaBaseUrl || 'http://localhost:11434'}
                  onChange={(e) => setConfig({ ...config, ollamaBaseUrl: e.target.value })}
                  placeholder="http://localhost:11434"
                  className="input-field w-full"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Model Name
              </label>
              {config.modelType === 'HuggingFace Open Source' ? (
                <select
                  value={config.modelName}
                  onChange={(e) => setConfig({ ...config, modelName: e.target.value })}
                  className="input-field w-full"
                >
                  <option value="microsoft/DialoGPT-medium">DialoGPT Medium</option>
                  <option value="microsoft/DialoGPT-large">DialoGPT Large</option>
                  <option value="facebook/blenderbot-400M-distill">BlenderBot 400M</option>
                  <option value="google/flan-t5-large">Flan-T5 Large</option>
                  <option value="mistralai/Mistral-7B-Instruct-v0.1">Mistral 7B</option>
                </select>
              ) : config.modelType === 'OpenAI' ? (
                <select
                  value={config.modelName}
                  onChange={(e) => setConfig({ ...config, modelName: e.target.value })}
                  className="input-field w-full"
                >
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-turbo-preview">GPT-4 Turbo</option>
                </select>
              ) : config.modelType === 'Ollama' ? (
                <input
                  type="text"
                  value={config.modelName}
                  onChange={(e) => setConfig({ ...config, modelName: e.target.value })}
                  placeholder="llama2, mistral, codellama, etc."
                  className="input-field w-full"
                />
              ) : (
                <input
                  type="text"
                  value={config.modelName}
                  onChange={(e) => setConfig({ ...config, modelName: e.target.value })}
                  placeholder="Path to local model"
                  className="input-field w-full"
                />
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Embedding Model
              </label>
              <select
                value={config.embeddingModel}
                onChange={(e) => setConfig({ ...config, embeddingModel: e.target.value })}
                className="input-field w-full"
              >
                <option value="sentence-transformers/all-MiniLM-L6-v2">
                  all-MiniLM-L6-v2 (Fast)
                </option>
                <option value="sentence-transformers/all-mpnet-base-v2">
                  all-mpnet-base-v2 (Better Quality)
                </option>
                <option value="sentence-transformers/multi-qa-MiniLM-L6-cos-v1">
                  multi-qa-MiniLM-L6-cos-v1 (Q&A Optimized)
                </option>
              </select>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="card"
        >
          <h3 className="text-lg font-semibold mb-4">Processing Parameters</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Chunk Size: {config.chunkSize}
              </label>
              <input
                type="range"
                min="100"
                max="2000"
                step="100"
                value={config.chunkSize}
                onChange={(e) => setConfig({ ...config, chunkSize: parseInt(e.target.value) })}
                className="w-full h-2 bg-secondary-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-secondary-400 mt-1">
                <span>100</span>
                <span>2000</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-secondary-200 mb-2">
                Chunk Overlap: {config.chunkOverlap}
              </label>
              <input
                type="range"
                min="0"
                max="500"
                step="50"
                value={config.chunkOverlap}
                onChange={(e) => setConfig({ ...config, chunkOverlap: parseInt(e.target.value) })}
                className="w-full h-2 bg-secondary-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-secondary-400 mt-1">
                <span>0</span>
                <span>500</span>
              </div>
            </div>

            <div className="pt-4">
              <button
                onClick={handleSave}
                disabled={initializeMutation.isLoading}
                className="btn-primary w-full flex items-center justify-center space-x-2"
              >
                {initializeMutation.isLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                <span>
                  {initializeMutation.isLoading ? 'Initializing...' : 'Save & Initialize'}
                </span>
              </button>
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="card"
      >
        <h3 className="text-lg font-semibold mb-4">Data Management</h3>
        <div className="mb-4 p-4 bg-secondary-800 rounded-lg">
          <h4 className="font-medium text-secondary-200 mb-2">About Vector Store Backup</h4>
          <p className="text-sm text-secondary-400 mb-2">
            <strong>Export:</strong> Creates a backup file containing all processed document embeddings and metadata. 
            This allows you to save your work and restore it later without reprocessing documents.
          </p>
          <p className="text-sm text-secondary-400">
            <strong>Import:</strong> Restores a previously exported backup, instantly loading all processed documents 
            and their embeddings. Useful for transferring data between systems or restoring previous states.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={handleExport}
            className="btn-secondary flex items-center justify-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Create Backup</span>
          </button>
          
          <label className="btn-secondary flex items-center justify-center space-x-2 cursor-pointer">
            <Upload className="w-4 h-4" />
            <span>Restore Backup</span>
            <input
              type="file"
              accept=".pkl"
              onChange={handleImport}
              className="hidden"
            />
          </label>
        </div>
      </motion.div>
    </div>
  )
}