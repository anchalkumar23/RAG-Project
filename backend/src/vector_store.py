import os
import pickle
import logging
from typing import List, Dict, Any, Optional
import numpy as np

# Vector store imports
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.schema import Document

# Sentence transformers for embeddings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manages vector stores for document embeddings"""
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2", 
                 store_type: str = "faiss"):
        self.embedding_model_name = embedding_model
        self.store_type = store_type
        self.vector_store = None
        self.embeddings = None
        self.documents = []
        
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Initialize embedding model"""
        try:
            if "openai" in self.embedding_model_name.lower():
                # OpenAI embeddings
                self.embeddings = OpenAIEmbeddings(
                    model=self.embedding_model_name,
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
            else:
                # HuggingFace embeddings
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=self.embedding_model_name,
                    model_kwargs={'device': 'cpu'},  # Use 'cuda' if GPU available
                    encode_kwargs={'normalize_embeddings': True}
                )
            
            logger.info(f"Initialized embeddings with model: {self.embedding_model_name}")
            
        except Exception as e:
            logger.error(f"Error initializing embeddings: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the vector store
        
        Args:
            documents: List of document dictionaries with text content
            
        Returns:
            bool: Success status
        """
        try:
            # Prepare documents for vector store
            langchain_docs = []
            
            for doc in documents:
                text_chunks = doc.get('text_content', [])
                doc_name = doc.get('name', 'Unknown')
                
                for i, chunk in enumerate(text_chunks):
                    if chunk.strip():  # Skip empty chunks
                        metadata = {
                            'source': doc_name,
                            'chunk_id': i,
                            'doc_type': doc.get('type', 'Unknown'),
                            'page_count': doc.get('pages', 0),
                            'has_tables': len(doc.get('tables', [])) > 0,
                            'has_images': len(doc.get('images', [])) > 0
                        }
                        
                        langchain_docs.append(
                            Document(page_content=chunk, metadata=metadata)
                        )
                
                # Add table content as separate documents
                for table in doc.get('tables', []):
                    table_content = f"Table content: {table.get('content', '')}"
                    metadata = {
                        'source': doc_name,
                        'content_type': 'table',
                        'page': table.get('page', 0),
                        'doc_type': doc.get('type', 'Unknown')
                    }
                    
                    langchain_docs.append(
                        Document(page_content=table_content, metadata=metadata)
                    )
            
            if not langchain_docs:
                logger.warning("No valid documents to add to vector store")
                return False
            
            # Create or update vector store
            if self.vector_store is None:
                if self.store_type == "faiss":
                    self.vector_store = FAISS.from_documents(langchain_docs, self.embeddings)
                elif self.store_type == "chroma":
                    self.vector_store = Chroma.from_documents(langchain_docs, self.embeddings)
                else:
                    raise ValueError(f"Unsupported vector store type: {self.store_type}")
            else:
                # Add to existing vector store
                if self.store_type == "faiss":
                    new_store = FAISS.from_documents(langchain_docs, self.embeddings)
                    self.vector_store.merge_from(new_store)
                elif self.store_type == "chroma":
                    self.vector_store.add_documents(langchain_docs)
            
            self.documents.extend(documents)
            logger.info(f"Added {len(langchain_docs)} document chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            return False
    
    def similarity_search(self, query: str, k: int = 5, 
                         filter_metadata: Optional[Dict] = None) -> List[Document]:
        """
        Perform similarity search
        
        Args:
            query: Search query
            k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of similar documents
        """
        try:
            if self.vector_store is None:
                logger.warning("Vector store not initialized")
                return []
            
            if filter_metadata:
                # Use metadata filtering if supported
                if hasattr(self.vector_store, 'similarity_search'):
                    results = self.vector_store.similarity_search(
                        query, k=k, filter=filter_metadata
                    )
                else:
                    results = self.vector_store.similarity_search(query, k=k)
            else:
                results = self.vector_store.similarity_search(query, k=k)
            
            return results
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """
        Perform similarity search with relevance scores
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of (document, score) tuples
        """
        try:
            if self.vector_store is None:
                logger.warning("Vector store not initialized")
                return []
            
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
            
        except Exception as e:
            logger.error(f"Error performing similarity search with score: {str(e)}")
            return []
    
    def get_retriever(self, search_type: str = "similarity", k: int = 5):
        """
        Get a retriever for the vector store
        
        Args:
            search_type: Type of search ("similarity", "mmr", etc.)
            k: Number of documents to retrieve
            
        Returns:
            Retriever object
        """
        try:
            if self.vector_store is None:
                logger.warning("Vector store not initialized")
                return None
            
            # Use MMR (Maximal Marginal Relevance) for better diversity in results
            if search_type == "mmr" and hasattr(self.vector_store, 'as_retriever'):
                return self.vector_store.as_retriever(
                    search_type="mmr",
                    search_kwargs={
                        "k": k,
                        "fetch_k": k * 2,  # Fetch more candidates for diversity
                        "lambda_mult": 0.7  # Balance between relevance and diversity
                    }
                )
            
            return self.vector_store.as_retriever(
                search_type=search_type,
                search_kwargs={"k": k}
            )
            
        except Exception as e:
            logger.error(f"Error creating retriever: {str(e)}")
            return None
    
    def save_vector_store(self, path: str) -> bool:
        """
        Save vector store to disk
        
        Args:
            path: Path to save the vector store
            
        Returns:
            bool: Success status
        """
        try:
            if self.vector_store is None:
                logger.warning("No vector store to save")
                return False
            
            if self.store_type == "faiss":
                self.vector_store.save_local(path)
            elif self.store_type == "chroma":
                # Chroma saves automatically to specified directory
                pass
            
            # Save additional metadata
            metadata = {
                'embedding_model': self.embedding_model_name,
                'store_type': self.store_type,
                'document_count': len(self.documents),
                'documents': self.documents
            }
            
            with open(os.path.join(path, 'metadata.pkl'), 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"Vector store saved to {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
            return False
    
    def load_vector_store(self, path: str) -> bool:
        """
        Load vector store from disk
        
        Args:
            path: Path to load the vector store from
            
        Returns:
            bool: Success status
        """
        try:
            # Load metadata
            metadata_path = os.path.join(path, 'metadata.pkl')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    metadata = pickle.load(f)
                
                self.documents = metadata.get('documents', [])
                logger.info(f"Loaded metadata for {len(self.documents)} documents")
            
            # Load vector store
            if self.store_type == "faiss":
                self.vector_store = FAISS.load_local(path, self.embeddings)
            elif self.store_type == "chroma":
                self.vector_store = Chroma(
                    persist_directory=path,
                    embedding_function=self.embeddings
                )
            
            logger.info(f"Vector store loaded from {path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            stats = {
                'embedding_model': self.embedding_model_name,
                'store_type': self.store_type,
                'document_count': len(self.documents),
                'is_initialized': self.vector_store is not None
            }
            
            if self.vector_store is not None:
                if self.store_type == "faiss":
                    stats['vector_count'] = self.vector_store.index.ntotal
                    stats['dimension'] = self.vector_store.index.d
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting vector store stats: {str(e)}")
            return {}
    
    def clear_vector_store(self):
        """Clear the vector store"""
        self.vector_store = None
        self.documents = []
        logger.info("Vector store cleared")
    
    def export_embeddings(self) -> Optional[np.ndarray]:
        """Export embeddings as numpy array"""
        try:
            if self.vector_store is None or self.store_type != "faiss":
                return None
            
            # Get embeddings from FAISS index
            embeddings = self.vector_store.index.reconstruct_n(
                0, self.vector_store.index.ntotal
            )
            return embeddings
            
        except Exception as e:
            logger.error(f"Error exporting embeddings: {str(e)}")
            return None
    
    def search_by_metadata(self, metadata_filter: Dict[str, Any], k: int = 10) -> List[Document]:
        """
        Search documents by metadata criteria
        
        Args:
            metadata_filter: Dictionary of metadata key-value pairs to filter by
            k: Maximum number of results to return
            
        Returns:
            List of matching documents
        """
        try:
            if self.vector_store is None:
                return []
            
            # This is a simplified implementation
            # For more advanced filtering, consider using a database-backed vector store
            all_docs = []
            
            # Get all documents (this is not efficient for large collections)
            if hasattr(self.vector_store, 'docstore'):
                for doc_id in self.vector_store.docstore._dict:
                    doc = self.vector_store.docstore._dict[doc_id]
                    
                    # Check if document matches filter criteria
                    matches = True
                    for key, value in metadata_filter.items():
                        if key not in doc.metadata or doc.metadata[key] != value:
                            matches = False
                            break
                    
                    if matches:
                        all_docs.append(doc)
                        if len(all_docs) >= k:
                            break
            
            return all_docs
            
        except Exception as e:
            logger.error(f"Error searching by metadata: {str(e)}")
            return []