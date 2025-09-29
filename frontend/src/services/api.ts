import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log error for debugging
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export interface Document {
  id: string
  name: string
  type: string
  size: number
  pages: number
  chunks: number
  uploadedAt: string
  status: 'processing' | 'ready' | 'error'
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: Array<{
    content: string
    metadata: Record<string, any>
  }>
}

export interface SystemStats {
  data: {
    pipeline_status: string
    llm: {
      model_type: string
      model_name: string
    }
    vector_store: {
      document_count: number
    }
    document_processor: {
      chunk_size: number
    }
  }
}

export interface UploadResponse {
  data: Document[]
}

export interface ChatResponse {
  data: {
    answer: string
    sources: Array<{
      content: string
      metadata: Record<string, any>
    }>
  }
}

export const apiService = {
  // System endpoints
  getSystemStats: async (): Promise<SystemStats> => {
    const response = await api.get('/system/stats')
    return response.data
  },

  // Document endpoints
  getDocuments: async (): Promise<{ data: Document[] }> => {
    const response = await api.get('/documents')
    return response.data
  },

  uploadDocuments: async (files: FileList): Promise<UploadResponse> => {
    const formData = new FormData()
    Array.from(files).forEach((file) => {
      formData.append('files', file)
    })
    
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  deleteDocument: async (documentId: string): Promise<void> => {
    await api.delete(`/documents/${documentId}`)
  },

  // Chat endpoints
  sendMessage: async (message: string): Promise<ChatResponse> => {
    const response = await api.post('/chat', { message })
    return response.data
  },

  // Settings endpoints
  initializePipeline: async (config: any): Promise<void> => {
    const response = await api.post('/pipeline/initialize', config)
    return response.data
  },

  // Analytics endpoints
  getAnalytics: async (): Promise<any> => {
    const response = await api.get('/analytics')
    return response.data
  },

  // Vector store endpoints
  exportVectorStore: async (): Promise<Blob> => {
    const response = await api.get('/vector-store/export', {
      responseType: 'blob',
    })
    return response.data
  },

  importVectorStore: async (file: File): Promise<void> => {
    const formData = new FormData()
    formData.append('file', file)
    await api.post('/vector-store/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

export default api