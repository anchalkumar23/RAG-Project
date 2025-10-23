# 🤖 RAG Document Assistant

<div align="center">

![RAG Assistant Banner](https://img.shields.io/badge/RAG-Document%20Assistant-blue?style=for-the-badge&logo=robot&logoColor=white)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18.2+-blue?style=for-the-badge&logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?style=for-the-badge&logo=fastapi&logoColor=white)

**An intelligent document processing and question-answering system powered by Retrieval-Augmented Generation (RAG)**

[🚀 Features](#-features) • [📦 Installation](#-installation) • [🔧 Configuration](#-configuration) • [📖 Usage](#-usage) • [🔌 API](#-api) • [🤝 Contributing](#-contributing)

</div>

---

## 🌟 Overview

RAG Document Assistant is a cutting-edge application that combines the power of modern AI with document processing capabilities. Built with FastAPI backend and React frontend, it enables users to upload various document formats, process them using advanced NLP techniques, and interact with the content through an intelligent chat interface.

### 🎯 Key Capabilities

- **Multi-format Document Support**: PDF, DOCX, DOC, PPT, PPTX, images, and text files
- **Intelligent Document Processing**: OCR, table extraction, and content chunking
- **Advanced RAG Pipeline**: Context-aware question answering with source citations
- **Modern Web Interface**: Responsive, dark-themed UI with real-time interactions
- **Flexible AI Models**: Support for HuggingFace, OpenAI, and Ollama models
- **Vector Search**: ChromaDB-powered semantic search and retrieval

---

## ✨ Features

### 📄 Document Management
- **Drag & Drop Upload**: Intuitive file upload with progress tracking
- **Batch Processing**: Upload and process multiple documents simultaneously
- **Format Support**: PDF, Word, PowerPoint, images (PNG, JPG, etc.), and text files
- **Document Analytics**: View processing statistics, page counts, and chunk information
- **Export Capabilities**: Download processed documents and chat history

### 🤖 AI-Powered Chat
- **Contextual Q&A**: Ask questions about your uploaded documents
- **Source Citations**: Get references to specific document sections
- **Real-time Responses**: Streaming chat interface with typing indicators
- **Chat History**: Export conversations as PDF reports
- **Multi-document Queries**: Search across all uploaded documents simultaneously

### 🔧 Advanced Processing
- **OCR Integration**: Extract text from images and scanned documents
- **Table Extraction**: Preserve tabular data structure
- **Smart Chunking**: Intelligent text segmentation with overlap
- **Vector Embeddings**: Semantic understanding using sentence transformers
- **Language Support**: Multi-language processing capabilities

### 🎨 Modern Interface
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Dark Theme**: Eye-friendly interface with customizable colors
- **Real-time Updates**: Live progress tracking and status updates
- **Smooth Animations**: Framer Motion powered interactions
- **Accessibility**: Keyboard navigation and screen reader support

---

## 📦 Installation

### Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Git**

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rag-document-assistant.git
   cd rag-document-assistant
   ```

2. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server**
   ```bash
   python start_api.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   
   The application will be available at `http://localhost:3000`

### Docker Setup (Alternative)

```bash
# Build and run with Docker Compose
docker-compose up --build
```

---

## 🔧 Configuration

### Backend Configuration

Edit `backend/config.json` to customize your setup:

```json
{
  "model_type": "HuggingFace Open Source",
  "model_name": "microsoft/DialoGPT-medium",
  "embedding_model": "sentence-transformers/distiluse-base-multilingual-cased",
  "chunk_size": 1000,
  "chunk_overlap": 100,
  "vector_store_type": "chroma",
  "retrieval_k": 10,
  "max_file_size_mb": 100,
  "supported_formats": [".pdf", ".docx", ".doc", ".ppt", ".pptx", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".txt", ".md"],
  "enable_ocr": true,
  "enable_table_extraction": true,
  "language": "en",
  "ocr_language": "eng",
  "batch_size": 10,
  "log_level": "INFO"
}
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# Ollama Configuration (Optional)
OLLAMA_BASE_URL=http://localhost:11434

# Database Configuration
DATABASE_URL=sqlite:///./rag_assistant.db

# Logging
LOG_LEVEL=INFO
```

---

## 📖 Usage

### Getting Started

1. **Launch the Application**
   - Start both backend and frontend servers
   - Open `http://localhost:3000` in your browser

2. **Initialize the Pipeline**
   - Go to Settings page
   - Configure your preferred AI model
   - Click "Initialize Pipeline"

3. **Upload Documents**
   - Navigate to Documents page
   - Drag and drop files or click "Upload Documents"
   - Wait for processing to complete

4. **Start Chatting**
   - Go to Chat page
   - Ask questions about your documents
   - Get intelligent responses with source citations

### Supported File Formats

| Format | Extension | Processing |
|--------|-----------|------------|
| PDF | `.pdf` | Text extraction, OCR, tables |
| Word | `.docx`, `.doc` | Full text extraction |
| PowerPoint | `.pptx`, `.ppt` | Slide content extraction |
| Images | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff` | OCR processing |
| Text | `.txt`, `.md` | Direct text processing |

### Example Queries

- "What is the main topic of the uploaded document?"
- "Summarize the key points from all documents"
- "Find information about [specific topic]"
- "What are the conclusions mentioned in the research paper?"
- "Extract all the data from the tables"

---

## 🔌 API

### Core Endpoints

#### Document Management

```http
# Get all documents
GET /documents

# Upload documents
POST /documents/upload
Content-Type: multipart/form-data

# Delete document
DELETE /documents/{document_id}
```

#### Chat Interface

```http
# Send message
POST /chat
Content-Type: application/json
{
  "message": "Your question here"
}
```

#### System Management

```http
# Get system stats
GET /system/stats

# Initialize pipeline
POST /pipeline/initialize
Content-Type: application/json
{
  "modelType": "HuggingFace Open Source",
  "modelName": "microsoft/DialoGPT-medium",
  "embeddingModel": "sentence-transformers/all-MiniLM-L6-v2",
  "chunkSize": 1000,
  "chunkOverlap": 200
}
```

### API Response Examples

#### Document Upload Response
```json
{
  "data": [
    {
      "id": "uuid-here",
      "name": "document.pdf",
      "type": "pdf",
      "size": 1024000,
      "pages": 25,
      "chunks": 45,
      "status": "ready"
    }
  ]
}
```

#### Chat Response
```json
{
  "data": {
    "answer": "Based on the uploaded documents...",
    "sources": [
      {
        "content": "Relevant text excerpt...",
        "metadata": {
          "source": "document.pdf",
          "page": 5,
          "chunk_id": "chunk_123"
        }
      }
    ]
  }
}
```

---

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Models     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (HuggingFace) │
│                 │    │                 │    │                 │
│ • Document UI   │    │ • RAG Pipeline  │    │ • LLM Models    │
│ • Chat Interface│    │ • Vector Store  │    │ • Embeddings    │
│ • Analytics     │    │ • Document Proc │    │ • OCR Engine    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

**Frontend:**
- React 18.2+ with TypeScript
- Tailwind CSS for styling
- Framer Motion for animations
- React Query for state management
- Axios for API communication

**Backend:**
- FastAPI with Python 3.10+
- LangChain for AI pipeline
- ChromaDB for vector storage
- PyPDF2, python-docx for document processing
- Tesseract for OCR capabilities

**AI/ML:**
- HuggingFace Transformers
- Sentence Transformers for embeddings
- OpenAI API integration
- Ollama local model support

---

## 🚀 Performance

### Optimization Features

- **Efficient Chunking**: Smart text segmentation with configurable overlap
- **Vector Caching**: Persistent vector store for faster retrieval
- **Batch Processing**: Parallel document processing
- **Memory Management**: Optimized for large document collections
- **Lazy Loading**: On-demand model loading

### Scalability

- **Horizontal Scaling**: Stateless API design
- **Database Integration**: Ready for PostgreSQL/MySQL
- **Caching Layer**: Redis integration ready
- **Load Balancing**: Multiple worker support

---

## 🛠️ Development

### Project Structure

```
rag-document-assistant/
├── backend/
│   ├── src/
│   │   ├── document_processor.py
│   │   ├── llm_manager.py
│   │   ├── rag_pipeline.py
│   │   ├── vector_store.py
│   │   └── utils.py
│   ├── api.py
│   ├── start_api.py
│   ├── requirements.txt
│   └── config.json
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── store/
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### Building for Production

```bash
# Build frontend
cd frontend
npm run build

# Start production server
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
6. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write comprehensive tests
- Update documentation for new features
- Ensure all tests pass before submitting

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain** for the AI framework
- **HuggingFace** for pre-trained models
- **FastAPI** for the robust backend framework
- **React** team for the frontend library
- **ChromaDB** for vector storage capabilities

---

## 📞 Support

- **Documentation**: [Wiki](https://github.com/yourusername/rag-document-assistant/wiki)
- **Issues**: [GitHub Issues](https://github.com/yourusername/rag-document-assistant/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/rag-document-assistant/discussions)
- **Email**: support@ragassistant.com

---

<div align="center">

**Made with ❤️ by [Anchal Kumar Tarwey](https://github.com/yourusername)**

[⭐ Star this repo](https://github.com/yourusername/rag-document-assistant) • [🐛 Report Bug](https://github.com/yourusername/rag-document-assistant/issues) • [💡 Request Feature](https://github.com/yourusername/rag-document-assistant/issues)

</div>
