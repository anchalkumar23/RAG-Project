import { create } from 'zustand'

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

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  sources?: Array<{
    content: string
    metadata: Record<string, any>
  }>
}

interface AppState {
  // System state
  systemStatus: 'initializing' | 'ready' | 'error'
  isLoading: boolean
  
  // Documents
  documents: Document[]
  selectedDocuments: string[]
  
  // Chat
  chatHistory: ChatMessage[]
  isTyping: boolean
  
  // Settings
  modelConfig: {
    modelType: string
    modelName: string
    embeddingModel: string
    chunkSize: number
    chunkOverlap: number
    openaiApiKey?: string
    ollamaBaseUrl?: string
  }
  
  // Actions
  setSystemStatus: (status: 'initializing' | 'ready' | 'error') => void
  setLoading: (loading: boolean) => void
  addDocument: (document: Document) => void
  removeDocument: (id: string) => void
  updateDocument: (id: string, updates: Partial<Document>) => void
  setSelectedDocuments: (ids: string[]) => void
  addChatMessage: (message: ChatMessage) => void
  clearChatHistory: () => void
  setIsTyping: (typing: boolean) => void
  updateModelConfig: (config: Partial<AppState['modelConfig']>) => void
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  systemStatus: 'initializing',
  isLoading: false,
  documents: [],
  selectedDocuments: [],
  chatHistory: [],
  isTyping: false,
  modelConfig: {
    modelType: 'HuggingFace Open Source',
    modelName: 'microsoft/DialoGPT-medium',
    embeddingModel: 'sentence-transformers/all-MiniLM-L6-v2',
    chunkSize: 1000,
    chunkOverlap: 200,
    openaiApiKey: '',
    ollamaBaseUrl: 'http://localhost:11434',
  },

  // Actions
  setSystemStatus: (status) => set({ systemStatus: status }),
  setLoading: (loading) => set({ isLoading: loading }),
  
  addDocument: (document) =>
    set((state) => ({
      documents: [...state.documents, document],
    })),
  
  removeDocument: (id) =>
    set((state) => ({
      documents: state.documents.filter((doc) => doc.id !== id),
      selectedDocuments: state.selectedDocuments.filter((docId) => docId !== id),
    })),
  
  updateDocument: (id, updates) =>
    set((state) => ({
      documents: state.documents.map((doc) =>
        doc.id === id ? { ...doc, ...updates } : doc
      ),
    })),
  
  setSelectedDocuments: (ids) => set({ selectedDocuments: ids }),
  
  addChatMessage: (message) =>
    set((state) => ({
      chatHistory: [...state.chatHistory, message],
    })),
  
  clearChatHistory: () => set({ chatHistory: [] }),
  setIsTyping: (typing) => set({ isTyping: typing }),
  
  updateModelConfig: (config) =>
    set((state) => ({
      modelConfig: { ...state.modelConfig, ...config },
    })),
}))