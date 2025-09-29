from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
import json
import logging
from pathlib import Path

# Import your existing modules
from src.rag_pipeline import RAGPipeline
from src.utils import setup_directories, load_config, validate_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Document Assistant API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
rag_pipeline = None
processed_documents = []

# Pydantic models
class ChatMessage(BaseModel):
    message: str

class PipelineConfig(BaseModel):
    modelType: str
    modelName: str
    embeddingModel: str
    chunkSize: int
    chunkOverlap: int
    openaiApiKey: Optional[str] = None

class DocumentResponse(BaseModel):
    id: str
    name: str
    type: str
    size: int
    pages: int
    chunks: int
    status: str

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    setup_directories()
    logger.info("RAG Document Assistant API started")

@app.get("/")
async def root():
    return {"message": "RAG Document Assistant API", "status": "running"}

@app.get("/system/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        if rag_pipeline:
            stats = rag_pipeline.get_pipeline_stats()
            return {"data": stats}
        else:
            return {
                "data": {
                    "pipeline_status": "not_initialized",
                    "llm": {"model_type": "None", "model_name": "None"},
                    "vector_store": {"document_count": 0},
                    "document_processor": {"chunk_size": 1000}
                }
            }
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pipeline/initialize")
async def initialize_pipeline(config: PipelineConfig):
    """Initialize the RAG pipeline"""
    global rag_pipeline
    
    try:
        # Convert frontend config to backend format
        backend_config = {
            'model_type': config.modelType,
            'model_name': config.modelName,
            'embedding_model': config.embeddingModel,
            'chunk_size': config.chunkSize,
            'chunk_overlap': config.chunkOverlap
        }
        
        if config.openaiApiKey:
            backend_config['openai_api_key'] = config.openaiApiKey
        
        logger.info(f"Received configuration from frontend: {backend_config}")
        
        rag_pipeline = RAGPipeline(backend_config)
        logger.info("RAG pipeline initialized successfully")
        
        return {"message": "Pipeline initialized successfully", "status": "success"}
        
    except Exception as e:
        logger.error(f"Error initializing pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def get_documents():
    """Get all processed documents"""
    try:
        documents = []
        for i, doc in enumerate(processed_documents):
            documents.append({
                "id": str(i),
                "name": doc.get('name', 'Unknown'),
                "type": doc.get('type', 'Unknown'),
                "size": doc.get('size', 0),
                "pages": doc.get('pages', 0),
                "chunks": doc.get('chunks', 0),
                "uploadedAt": doc.get('uploadedAt', ''),
                "status": "ready"
            })
        
        return {"data": documents}
        
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process documents"""
    global processed_documents
    
    if not rag_pipeline:
        raise HTTPException(status_code=400, detail="Pipeline not initialized. Please initialize the pipeline first.")
    
    try:
        uploaded_docs = []
        
        for file in files:
            # Validate file
            if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
                continue
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            try:
                # Process document
                doc_info = rag_pipeline.process_document(tmp_file_path)
                doc_info['name'] = file.filename
                doc_info['uploadedAt'] = '2024-01-01T00:00:00Z'  # You can use actual timestamp
                
                processed_documents.append(doc_info)
                
                uploaded_docs.append({
                    "id": str(len(processed_documents) - 1),
                    "name": file.filename,
                    "type": doc_info.get('type', 'Unknown'),
                    "size": doc_info.get('size', 0),
                    "pages": doc_info.get('pages', 0),
                    "chunks": doc_info.get('chunks', 0),
                    "status": "ready"
                })
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
        
        return {"data": uploaded_docs}
        
    except Exception as e:
        logger.error(f"Error uploading documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    global processed_documents
    
    try:
        doc_index = int(document_id)
        if 0 <= doc_index < len(processed_documents):
            removed_doc = processed_documents.pop(doc_index)
            logger.info(f"Deleted document: {removed_doc.get('name', 'Unknown')}")
            return {"message": "Document deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid document ID")
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def send_message(message: ChatMessage):
    """Send a chat message and get response"""
    if not rag_pipeline:
        raise HTTPException(status_code=400, detail="Pipeline not initialized. Please initialize the pipeline first.")
    
    if not processed_documents:
        raise HTTPException(status_code=400, detail="No documents available. Please upload some documents first.")
    
    try:
        response = rag_pipeline.query(message.message)
        
        return {
            "data": {
                "answer": response.get("answer", "I couldn't generate an answer."),
                "sources": response.get("sources", [])
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics")
async def get_analytics():
    """Get analytics data"""
    try:
        # Basic analytics based on processed documents
        total_docs = len(processed_documents)
        total_pages = sum(doc.get('pages', 0) for doc in processed_documents)
        total_chunks = sum(doc.get('chunks', 0) for doc in processed_documents)
        
        doc_types = {}
        for doc in processed_documents:
            doc_type = doc.get('type', 'Unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        return {
            "data": {
                "total_documents": total_docs,
                "total_pages": total_pages,
                "total_chunks": total_chunks,
                "document_types": doc_types,
                "processing_stats": {
                    "average_pages_per_doc": total_pages / total_docs if total_docs > 0 else 0,
                    "average_chunks_per_doc": total_chunks / total_docs if total_docs > 0 else 0
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vector-store/export")
async def export_vector_store():
    """Export vector store"""
    if not rag_pipeline:
        raise HTTPException(status_code=400, detail="Pipeline not initialized")
    
    try:
        export_data = rag_pipeline.export_vector_store()
        
        # Create a temporary file for download
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            tmp_file.write(export_data)
            tmp_file_path = tmp_file.name
        
        return FileResponse(
            tmp_file_path,
            media_type='application/octet-stream',
            filename='vector_store_export.pkl'
        )
        
    except Exception as e:
        logger.error(f"Error exporting vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vector-store/import")
async def import_vector_store(file: UploadFile = File(...)):
    """Import vector store"""
    if not rag_pipeline:
        raise HTTPException(status_code=400, detail="Pipeline not initialized")
    
    try:
        content = await file.read()
        rag_pipeline.import_vector_store(content)
        
        return {"message": "Vector store imported successfully"}
        
    except Exception as e:
        logger.error(f"Error importing vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)