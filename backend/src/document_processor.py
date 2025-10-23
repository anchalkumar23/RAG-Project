import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import tempfile

# PDF processing
import PyPDF2
import pdfplumber
from pypdf import PdfReader

# Document processing
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.document_loaders import UnstructuredPowerPointLoader, UnstructuredImageLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Image and table processing
import cv2
import numpy as np
from PIL import Image
import pytesseract
import pandas as pd

# Unstructured for advanced document parsing
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Advanced document processor for PDFs and Word documents with image and table extraction"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a document and extract text, images, and tables
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing processed document information
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                return self._process_pdf(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._process_word(file_path)
            elif file_extension in ['.ppt', '.pptx']:
                return self._process_powerpoint(file_path)
            elif file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
                return self._process_image(file_path)
            elif file_extension in ['.txt', '.md']:
                return self._process_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            raise
    
    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process PDF document with advanced extraction"""
        logger.info(f"Processing PDF: {file_path}")
        
        # Basic document info
        doc_info = {
            'name': Path(file_path).name,
            'type': 'PDF',
            'size': os.path.getsize(file_path) // 1024,  # Size in KB
            'pages': 0,
            'chunks': 0,
            'text_content': [],
            'images': [],
            'tables': [],
            'metadata': {}
        }
        
        try:
            # Method 1: Use unstructured for comprehensive extraction
            elements = partition_pdf(
                filename=file_path,
                extract_images_in_pdf=False,  # Disable to improve performance for bulk uploads
                infer_table_structure=True,
                chunking_strategy="by_title",
                max_characters=self.chunk_size,
                combine_text_under_n_chars=100,
                languages=["eng", "deu"]  # Support both English and German
            )
            
            # Process elements
            text_chunks = []
            tables = []
            images = []
            
            for element in elements:
                if hasattr(element, 'text') and element.text.strip():
                    if element.category == "Table":
                        tables.append({
                            'content': element.text,
                            'page': getattr(element, 'metadata', {}).get('page_number', 0),
                            'type': 'table'
                        })
                    else:
                        text_chunks.append(element.text)
            
            # Fallback to pdfplumber for additional table extraction
            with pdfplumber.open(file_path) as pdf:
                doc_info['pages'] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    # Extract tables
                    page_tables = page.extract_tables()
                    for table in page_tables:
                        if table:
                            # Convert table to text format
                            table_text = self._table_to_text(table)
                            tables.append({
                                'content': table_text,
                                'page': page_num + 1,
                                'type': 'table'
                            })
                    
                    # Extract images (basic info)
                    if hasattr(page, 'images'):
                        for img in page.images:
                            images.append({
                                'page': page_num + 1,
                                'bbox': img.get('bbox', []),
                                'type': 'image'
                            })
            
            # Combine all text
            all_text = ' '.join(text_chunks)
            
            # Split into chunks
            documents = [Document(page_content=all_text, metadata={'source': file_path})]
            chunks = self.text_splitter.split_documents(documents)
            
            doc_info.update({
                'text_content': [chunk.page_content for chunk in chunks],
                'chunks': len(chunks),
                'tables': tables,
                'images': images,
                'metadata': {
                    'total_tables': len(tables),
                    'total_images': len(images),
                    'extraction_method': 'unstructured + pdfplumber'
                }
            })
            
        except Exception as e:
            logger.warning(f"Advanced extraction failed, falling back to basic PDF processing: {str(e)}")
            # Fallback to basic PyPDF processing
            doc_info = self._process_pdf_basic(file_path)
        
        return doc_info
    
    def _process_pdf_basic(self, file_path: str) -> Dict[str, Any]:
        """Basic PDF processing fallback"""
        logger.info(f"Using basic PDF processing for: {file_path}")
        
        doc_info = {
            'name': Path(file_path).name,
            'type': 'PDF',
            'size': os.path.getsize(file_path) // 1024,
            'pages': 0,
            'chunks': 0,
            'text_content': [],
            'images': [],
            'tables': [],
            'metadata': {}
        }
        
        # Use PyPDF2 for basic text extraction
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            doc_info['pages'] = len(pdf_reader.pages)
            
            text_content = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    text_content.append(text)
            
            # Combine and split text
            all_text = '\n\n'.join(text_content)
            documents = [Document(page_content=all_text, metadata={'source': file_path})]
            chunks = self.text_splitter.split_documents(documents)
            
            doc_info.update({
                'text_content': [chunk.page_content for chunk in chunks],
                'chunks': len(chunks),
                'metadata': {'extraction_method': 'basic_pypdf2'}
            })
        
        return doc_info
    
    def _process_word(self, file_path: str) -> Dict[str, Any]:
        """Process Word document"""
        logger.info(f"Processing Word document: {file_path}")
        
        doc_info = {
            'name': Path(file_path).name,
            'type': 'Word',
            'size': os.path.getsize(file_path) // 1024,
            'pages': 1,  # Word doesn't have fixed pages
            'chunks': 0,
            'text_content': [],
            'images': [],
            'tables': [],
            'metadata': {}
        }
        
        try:
            # Use unstructured for comprehensive extraction
            elements = partition_docx(filename=file_path)
            
            text_chunks = []
            tables = []
            
            for element in elements:
                if hasattr(element, 'text') and element.text.strip():
                    if element.category == "Table":
                        tables.append({
                            'content': element.text,
                            'type': 'table'
                        })
                    else:
                        text_chunks.append(element.text)
            
            # Combine all text
            all_text = ' '.join(text_chunks)
            
            # Split into chunks
            documents = [Document(page_content=all_text, metadata={'source': file_path})]
            chunks = self.text_splitter.split_documents(documents)
            
            doc_info.update({
                'text_content': [chunk.page_content for chunk in chunks],
                'chunks': len(chunks),
                'tables': tables,
                'metadata': {
                    'total_tables': len(tables),
                    'extraction_method': 'unstructured'
                }
            })
            
        except Exception as e:
            logger.warning(f"Advanced Word processing failed, using basic method: {str(e)}")
            # Fallback to basic processing
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            chunks = self.text_splitter.split_documents(documents)
            
            doc_info.update({
                'text_content': [chunk.page_content for chunk in chunks],
                'chunks': len(chunks),
                'metadata': {'extraction_method': 'basic_docx2txt'}
            })
        
        return doc_info
    
    def _process_powerpoint(self, file_path: str) -> Dict[str, Any]:
        """Process PowerPoint document"""
        logger.info(f"Processing PowerPoint: {file_path}")
        
        doc_info = {
            'name': Path(file_path).name,
            'type': 'PowerPoint',
            'size': os.path.getsize(file_path) // 1024,
            'pages': 0,
            'chunks': 0,
            'text_content': [],
            'images': [],
            'tables': [],
            'metadata': {}
        }
        
        try:
            loader = UnstructuredPowerPointLoader(file_path)
            documents = loader.load()
            
            # Combine all text
            all_text = '\n\n'.join([doc.page_content for doc in documents])
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([Document(page_content=all_text, metadata={'source': file_path})])
            
            doc_info.update({
                'text_content': [chunk.page_content for chunk in chunks],
                'chunks': len(chunks),
                'pages': len(documents),  # Approximate slide count
                'metadata': {'extraction_method': 'unstructured_ppt'}
            })
            
        except Exception as e:
            logger.error(f"Error processing PowerPoint: {str(e)}")
            # Fallback to basic text extraction
            doc_info.update({
                'text_content': ["Could not extract text from PowerPoint file"],
                'chunks': 1,
                'metadata': {'extraction_method': 'failed', 'error': str(e)}
            })
        
        return doc_info
    
    def _process_image(self, file_path: str) -> Dict[str, Any]:
        """Process image with OCR"""
        logger.info(f"Processing image: {file_path}")
        
        doc_info = {
            'name': Path(file_path).name,
            'type': 'Image',
            'size': os.path.getsize(file_path) // 1024,
            'pages': 1,
            'chunks': 0,
            'text_content': [],
            'images': [],
            'tables': [],
            'metadata': {}
        }
        
        try:
            # Extract text using OCR
            extracted_text = self.process_image_with_ocr(file_path)
            
            if extracted_text.strip():
                # Split into chunks
                documents = [Document(page_content=extracted_text, metadata={'source': file_path})]
                chunks = self.text_splitter.split_documents(documents)
                
                doc_info.update({
                    'text_content': [chunk.page_content for chunk in chunks],
                    'chunks': len(chunks),
                    'metadata': {'extraction_method': 'ocr', 'has_text': True}
                })
            else:
                doc_info.update({
                    'text_content': ["No text could be extracted from this image"],
                    'chunks': 1,
                    'metadata': {'extraction_method': 'ocr', 'has_text': False}
                })
                
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            doc_info.update({
                'text_content': ["Could not process image file"],
                'chunks': 1,
                'metadata': {'extraction_method': 'failed', 'error': str(e)}
            })
        
        return doc_info
    
    def _process_text(self, file_path: str) -> Dict[str, Any]:
        """Process plain text files"""
        logger.info(f"Processing text file: {file_path}")
        
        doc_info = {
            'name': Path(file_path).name,
            'type': 'Text',
            'size': os.path.getsize(file_path) // 1024,
            'pages': 1,
            'chunks': 0,
            'text_content': [],
            'images': [],
            'tables': [],
            'metadata': {}
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Split into chunks
            documents = [Document(page_content=text_content, metadata={'source': file_path})]
            chunks = self.text_splitter.split_documents(documents)
            
            doc_info.update({
                'text_content': [chunk.page_content for chunk in chunks],
                'chunks': len(chunks),
                'metadata': {'extraction_method': 'direct_read'}
            })
            
        except Exception as e:
            logger.error(f"Error processing text file: {str(e)}")
            doc_info.update({
                'text_content': ["Could not read text file"],
                'chunks': 1,
                'metadata': {'extraction_method': 'failed', 'error': str(e)}
            })
        
        return doc_info
    
    def _table_to_text(self, table: List[List[str]]) -> str:
        """Convert table data to readable text format"""
        if not table:
            return ""
        
        # Create a formatted table string
        table_text = []
        for row in table:
            if row:  # Skip empty rows
                # Clean and join cells
                clean_row = [str(cell).strip() if cell else "" for cell in row]
                table_text.append(" | ".join(clean_row))
        
        return "\n".join(table_text)
    
    def extract_images_from_pdf(self, file_path: str, output_dir: str = None) -> List[str]:
        """Extract images from PDF and save them"""
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        image_paths = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    if hasattr(page, 'images'):
                        for img_num, img in enumerate(page.images):
                            try:
                                # Extract image
                                image_obj = page.crop(img['bbox']).to_image()
                                image_path = os.path.join(
                                    output_dir, 
                                    f"page_{page_num+1}_img_{img_num+1}.png"
                                )
                                image_obj.save(image_path)
                                image_paths.append(image_path)
                            except Exception as e:
                                logger.warning(f"Failed to extract image: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error extracting images from PDF: {str(e)}")
        
        return image_paths
    
    def process_image_with_ocr(self, image_path: str) -> str:
        """Process image with OCR to extract text"""
        try:
            # Load image
            image = cv2.imread(image_path)
            
            # Preprocess image for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get better results
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text using pytesseract with German language
            text = pytesseract.image_to_string(thresh, lang='deu')
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error processing image with OCR: {str(e)}")
            return ""
    
    def get_document_stats(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed documents"""
        if not documents:
            return {}
        
        total_docs = len(documents)
        total_pages = sum(doc.get('pages', 0) for doc in documents)
        total_chunks = sum(doc.get('chunks', 0) for doc in documents)
        total_tables = sum(len(doc.get('tables', [])) for doc in documents)
        total_images = sum(len(doc.get('images', [])) for doc in documents)
        
        doc_types = {}
        for doc in documents:
            doc_type = doc.get('type', 'Unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        return {
            'total_documents': total_docs,
            'total_pages': total_pages,
            'total_chunks': total_chunks,
            'total_tables': total_tables,
            'total_images': total_images,
            'average_pages_per_doc': total_pages / total_docs if total_docs > 0 else 0,
            'average_chunks_per_doc': total_chunks / total_docs if total_docs > 0 else 0,
            'document_types': doc_types
        }