# Advanced RAG Document Assistant

A comprehensive Retrieval-Augmented Generation (RAG) application built with Streamlit and LangChain for processing and querying large collections of PDF and Word documents.

## Features

### 🚀 Core Capabilities
- **Multi-format Support**: Process PDF and Word documents with images and tables
- **Advanced Text Extraction**: Uses multiple extraction methods for optimal results
- **Table & Image Processing**: Extracts and processes tables and images from documents
- **Scalable Architecture**: Designed to handle 100-6000+ documents efficiently
- **Multiple LLM Support**: OpenAI, HuggingFace Open Source, and Local models

### 📊 Document Processing
- **Intelligent Chunking**: Optimized text splitting with configurable overlap
- **Metadata Extraction**: Comprehensive document metadata and statistics
- **Batch Processing**: Efficient processing of large document collections
- **Progress Tracking**: Real-time processing status and progress indicators

### 🔍 Advanced Search & Retrieval
- **Vector Similarity Search**: FAISS-based vector storage for fast retrieval
- **Semantic Search**: Context-aware document retrieval
- **Source Attribution**: Detailed source references for all answers
- **Metadata Filtering**: Search by document type, content type, etc.

### 💬 Interactive Chat Interface
- **Natural Language Queries**: Ask questions in plain English
- **Context-Aware Responses**: Maintains conversation context
- **Source Citations**: Shows relevant document excerpts
- **Chat History**: Persistent conversation history

### 📈 Analytics & Monitoring
- **Document Statistics**: Comprehensive analytics dashboard
- **Processing Metrics**: Track document processing performance
- **System Monitoring**: Memory usage and performance metrics
- **Export/Import**: Backup and restore functionality

## Installation

### Prerequisites
- Python 3.8 or higher
- CUDA-compatible GPU (optional, for faster processing)
- Sufficient RAM (8GB+ recommended for large document collections)

### Setup Instructions

1. **Clone or download the application files**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install additional system dependencies** (for OCR and image processing):

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils
```

**macOS**:
```bash
brew install tesseract
brew install poppler
```

**Windows**:
- Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Add Tesseract to your PATH

4. **Set up environment variables** (optional):
```bash
# For OpenAI models
export OPENAI_API_KEY="your-openai-api-key"

# For HuggingFace models (optional)
export HUGGINGFACE_API_TOKEN="your-hf-token"
```

## Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will open in your web browser at `http://localhost:8501`

### Processing Your Documents

#### Method 1: Upload Files
1. Go to the "Document Management" tab
2. Use the file uploader to select PDF or Word files
3. Click "Process Uploaded Documents"

#### Method 2: Process Folder (Recommended for large collections)
1. Place your PDF files in a folder
2. Enter the folder path in the "folder path" input
3. Click "Process Folder Documents"

### Configuration

#### Model Selection
- **HuggingFace Open Source**: Free models like DialoGPT, Mistral, Flan-T5
- **OpenAI**: GPT-3.5-turbo, GPT-4 (requires API key)
- **Local Model**: Use your own fine-tuned models

#### Embedding Models
- `sentence-transformers/all-MiniLM-L6-v2` (default, fast)
- `sentence-transformers/all-mpnet-base-v2` (better quality)
- `sentence-transformers/multi-qa-MiniLM-L6-cos-v1` (optimized for Q&A)

#### Processing Parameters
- **Chunk Size**: Text chunk size for processing (default: 1000)
- **Chunk Overlap**: Overlap between chunks (default: 200)

### Querying Your Documents

1. Process your documents first
2. Go to the "Chat Interface" tab
3. Ask questions about your documents
4. View answers with source citations

#### Example Queries
- "What are the main topics discussed in these documents?"
- "Summarize the key findings from the research papers"
- "What information is available about [specific topic]?"
- "Compare the methodologies used in different studies"

## Advanced Features

### Batch Processing
For large document collections (100-6000+ PDFs):

1. Organize documents in folders
2. Use the folder processing feature
3. Monitor progress in real-time
4. Process in batches to manage memory

### Analytics Dashboard
- View document statistics
- Monitor processing performance
- Track chat interactions
- Export analytics data

### Data Management
- Export vector stores for backup
- Import previously processed data
- Clear and reset data
- System information monitoring

## Configuration Options

Edit `config.json` to customize:

```json
{
  "model_type": "HuggingFace Open Source",
  "model_name": "microsoft/DialoGPT-medium",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "vector_store_type": "faiss",
  "retrieval_k": 5,
  "max_file_size_mb": 100,
  "batch_size": 10
}
```

## Performance Optimization

### For Large Document Collections
1. **Use GPU acceleration**: Install CUDA-compatible PyTorch
2. **Increase batch size**: Process more documents simultaneously
3. **Optimize chunk size**: Balance between context and performance
4. **Use efficient models**: Choose models based on your hardware

### Memory Management
- Monitor memory usage in the Analytics tab
- Process documents in smaller batches if needed
- Clear unused data regularly
- Use quantized models for large language models

## Troubleshooting

### Common Issues

**1. Out of Memory Errors**
- Reduce batch size
- Use smaller models
- Process fewer documents at once
- Clear browser cache and restart

**2. Slow Processing**
- Enable GPU acceleration
- Use smaller embedding models
- Reduce chunk size
- Process documents in smaller batches

**3. Model Loading Issues**
- Check internet connection
- Verify model names
- Try fallback models
- Check available disk space

**4. PDF Processing Errors**
- Ensure PDFs are not corrupted
- Check file permissions
- Try different extraction methods
- Update dependencies

### Getting Help

1. Check the logs in the `logs/` directory
2. Monitor system resources in the Analytics tab
3. Try with smaller document sets first
4. Verify all dependencies are installed correctly

## Technical Architecture

### Components
- **Document Processor**: Handles PDF/Word extraction with OCR and table processing
- **Vector Store Manager**: Manages FAISS/Chroma vector databases
- **LLM Manager**: Handles multiple language model types
- **RAG Pipeline**: Orchestrates the complete RAG workflow

### Data Flow
1. Documents → Text Extraction → Chunking
2. Chunks → Embeddings → Vector Store
3. Query → Retrieval → Context + LLM → Response

### Supported Models

#### Language Models
- Microsoft DialoGPT (Small, Medium, Large)
- Google Flan-T5 (Base, Large)
- Mistral 7B Instruct
- OpenAI GPT-3.5/GPT-4
- Custom local models

#### Embedding Models
- Sentence Transformers (various sizes)
- OpenAI text-embedding-ada-002
- Custom embedding models

## Changelog

### Version 1.0.0
- Initial release with full RAG functionality
- Support for PDF and Word documents
- Multiple LLM and embedding model support
- Advanced document processing with OCR and table extraction
- Interactive Streamlit interface
- Comprehensive analytics and monitoring