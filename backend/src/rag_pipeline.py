import logging
from typing import Dict, Any, List, Optional
import time

from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from .document_processor import DocumentProcessor
from .vector_store import VectorStoreManager
from .llm_manager import LLMManager

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Complete RAG pipeline for document question answering"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.document_processor = None
        self.vector_store = None
        self.llm_manager = None
        self.qa_chain = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all RAG components"""
        try:
            logger.info("Initializing RAG pipeline components...")
            logger.info(f"Configuration: {self.config}")
            
            # Initialize document processor
            self.document_processor = DocumentProcessor(
                chunk_size=self.config.get('chunk_size', 1000),
                chunk_overlap=self.config.get('chunk_overlap', 200)
            )
            
            # Initialize vector store
            self.vector_store = VectorStoreManager(
                embedding_model=self.config.get('embedding_model', 'sentence-transformers/all-MiniLM-L6-v2'),
                store_type=self.config.get('vector_store_type', 'faiss')
            )
            
            # Initialize LLM
            logger.info(f"Initializing LLM with model_type: {self.config.get('model_type')}, model_name: {self.config.get('model_name')}")
            self.llm_manager = LLMManager(self.config)
            
            # Create QA chain
            self._create_qa_chain()
            
            logger.info("RAG pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG pipeline: {str(e)}")
            raise
    
    def _create_qa_chain(self):
        """Create the question-answering chain"""
        try:
            # Custom prompt template for better responses
            prompt_template = """You are a helpful AI assistant. Use the following pieces of context to answer the question at the end. 
            
            IMPORTANT INSTRUCTIONS:
            - Answer based on the provided context below
            - If you cannot find a direct answer in the context, try to provide relevant information from the context that might help
            - Only say "I don't have enough information" if the context is completely unrelated to the question
            - Be specific and detailed when the context supports it
            - If the question is in German, answer in German
            - If the question is in English, answer in English
            - Provide a comprehensive answer using all relevant information from the context
            
            Context:
            {context}
            
            Question: {question}
            
            Helpful Answer:
            """
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Get retriever from vector store
            retriever = self.vector_store.get_retriever(
                search_type="similarity",
                k=self.config.get('retrieval_k', 10)  # Increased to 10 for better context
            )
            
            if retriever is None:
                logger.warning("Retriever not available, QA chain not created")
                return
            
            # Create RetrievalQA chain
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm_manager.llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
            
            logger.info("QA chain created successfully")
            
        except Exception as e:
            logger.error(f"Error creating QA chain: {str(e)}")
            self.qa_chain = None
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single document and add to vector store
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Document processing information
        """
        try:
            logger.info(f"Processing document: {file_path}")
            
            # Process document
            doc_info = self.document_processor.process_document(file_path)
            
            # Add to vector store
            success = self.vector_store.add_documents([doc_info])
            
            if success:
                # Recreate QA chain with updated vector store
                self._create_qa_chain()
                logger.info(f"Successfully processed and indexed: {file_path}")
            else:
                logger.error(f"Failed to add document to vector store: {file_path}")
            
            return doc_info
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise
    
    def process_documents_batch(self, file_paths: List[str], 
                               progress_callback: Optional[callable] = None) -> List[Dict[str, Any]]:
        """
        Process multiple documents in batch
        
        Args:
            file_paths: List of document file paths
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of document processing information
        """
        processed_docs = []
        batch_size = 50  # Process in smaller batches for better memory management
        
        try:
            logger.info(f"Processing {len(file_paths)} documents in batch")
            
            # Process in batches
            for batch_start in range(0, len(file_paths), batch_size):
                batch_end = min(batch_start + batch_size, len(file_paths))
                batch_files = file_paths[batch_start:batch_end]
                
                logger.info(f"Processing batch {batch_start//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
                
                batch_docs = []
                for i, file_path in enumerate(batch_files):
                    try:
                        doc_info = self.document_processor.process_document(file_path)
                        batch_docs.append(doc_info)
                        processed_docs.append(doc_info)
                        
                        if progress_callback:
                            progress_callback(batch_start + i + 1, len(file_paths), file_path)
                            
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {str(e)}")
                        continue
                
                # Add batch to vector store
                if batch_docs:
                    success = self.vector_store.add_documents(batch_docs)
                    if not success:
                        logger.error(f"Failed to add batch {batch_start//batch_size + 1} to vector store")
            
            # Recreate QA chain after all batches
            if processed_docs:
                self._create_qa_chain()
                logger.info(f"Successfully processed and indexed {len(processed_docs)} documents")
            
            return processed_docs
            
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            return processed_docs
    
    def query(self, question: str, include_sources: bool = True) -> Dict[str, Any]:
        """
        Query the RAG system
        
        Args:
            question: User question
            include_sources: Whether to include source documents
            
        Returns:
            Dictionary with answer and optional sources
        """
        try:
            if self.qa_chain is None:
                return {
                    "answer": "I'm sorry, but the system is not ready to answer questions yet. Please process some documents first.",
                    "sources": [],
                    "error": "QA chain not initialized"
                }
            
            logger.info(f"Processing query: {question}")
            start_time = time.time()
            
            # Get response from QA chain
            result = self.qa_chain.invoke({"query": question})
            
            processing_time = time.time() - start_time
            
            # Extract answer and sources
            answer = result.get("result", "I couldn't generate an answer.")
            source_docs = result.get("source_documents", []) if include_sources else []
            
            # Format sources
            sources = []
            if source_docs:
                for doc in source_docs:
                    source_info = {
                        "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                        "metadata": doc.metadata
                    }
                    sources.append(source_info)
            
            response = {
                "answer": answer,
                "sources": sources,
                "processing_time": processing_time,
                "timestamp": time.time()
            }
            
            logger.info(f"Query processed in {processing_time:.2f} seconds")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def get_similar_documents(self, query: str, k: int = 5) -> List[Document]:
        """
        Get similar documents without generating an answer
        
        Args:
            query: Search query
            k: Number of documents to return
            
        Returns:
            List of similar documents
        """
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Error getting similar documents: {str(e)}")
            return []
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics"""
        try:
            stats = {
                "pipeline_status": "initialized" if self.qa_chain else "not_ready",
                "timestamp": time.time()
            }
            
            # Document processor stats
            if self.document_processor:
                stats["document_processor"] = {
                    "chunk_size": self.document_processor.chunk_size,
                    "chunk_overlap": self.document_processor.chunk_overlap
                }
            
            # Vector store stats
            if self.vector_store:
                stats["vector_store"] = self.vector_store.get_stats()
            
            # LLM stats
            if self.llm_manager:
                stats["llm"] = self.llm_manager.get_model_info()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting pipeline stats: {str(e)}")
            return {"error": str(e)}
    
    def export_vector_store(self) -> bytes:
        """Export vector store data"""
        try:
            import pickle
            import tempfile
            import os
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save vector store
                self.vector_store.save_vector_store(temp_dir)
                
                # Create archive
                import shutil
                archive_path = shutil.make_archive(temp_dir + "_export", 'zip', temp_dir)
                
                # Read archive data
                with open(archive_path, 'rb') as f:
                    data = f.read()
                
                # Clean up
                os.unlink(archive_path)
                
                return data
                
        except Exception as e:
            logger.error(f"Error exporting vector store: {str(e)}")
            raise
    
    def import_vector_store(self, data: bytes):
        """Import vector store data"""
        try:
            import tempfile
            import zipfile
            import os
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save uploaded data
                zip_path = os.path.join(temp_dir, "import.zip")
                with open(zip_path, 'wb') as f:
                    f.write(data)
                
                # Extract archive
                extract_dir = os.path.join(temp_dir, "extracted")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Load vector store
                self.vector_store.load_vector_store(extract_dir)
                
                # Recreate QA chain
                self._create_qa_chain()
                
                logger.info("Vector store imported successfully")
                
        except Exception as e:
            logger.error(f"Error importing vector store: {str(e)}")
            raise
    
    def clear_all_data(self):
        """Clear all processed data"""
        try:
            if self.vector_store:
                self.vector_store.clear_vector_store()
            
            self.qa_chain = None
            logger.info("All data cleared")
            
        except Exception as e:
            logger.error(f"Error clearing data: {str(e)}")
            raise
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update pipeline configuration"""
        try:
            self.config.update(new_config)
            
            # Reinitialize components if necessary
            if any(key in new_config for key in ['model_type', 'model_name', 'embedding_model']):
                logger.info("Reinitializing pipeline with new configuration")
                self._initialize_components()
            
        except Exception as e:
            logger.error(f"Error updating configuration: {str(e)}")
            raise