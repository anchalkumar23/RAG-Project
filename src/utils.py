import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import tempfile
import shutil

logger = logging.getLogger(__name__)

def setup_directories():
    """Setup necessary directories for the application"""
    directories = [
        "data",
        "data/documents",
        "data/vector_stores",
        "data/exports",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logger.info("Directories setup completed")

def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    default_config = {
        "model_type": "HuggingFace Open Source",
        "model_name": "microsoft/DialoGPT-medium",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "vector_store_type": "faiss",
        "retrieval_k": 5,
        "max_file_size_mb": 100,
        "supported_formats": [".pdf", ".docx", ".doc"],
        "enable_ocr": True,
        "enable_table_extraction": True
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults
            default_config.update(config)
            logger.info(f"Configuration loaded from {config_path}")
        else:
            logger.info("Using default configuration")
        
        return default_config
        
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return default_config

def save_config(config: Dict[str, Any], config_path: str = "config.json"):
    """Save configuration to JSON file"""
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Configuration saved to {config_path}")
        
    except Exception as e:
        logger.error(f"Error saving configuration: {str(e)}")

def validate_file(file_path: str, max_size_mb: int = 100, 
                 supported_formats: List[str] = None) -> Dict[str, Any]:
    """Validate uploaded file"""
    if supported_formats is None:
        supported_formats = [".pdf", ".docx", ".doc"]
    
    result = {
        "valid": False,
        "error": None,
        "file_info": {}
    }
    
    try:
        if not os.path.exists(file_path):
            result["error"] = "File does not exist"
            return result
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            result["error"] = f"File size ({file_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
            return result
        
        # Check file format
        file_extension = Path(file_path).suffix.lower()
        if file_extension not in supported_formats:
            result["error"] = f"Unsupported file format: {file_extension}. Supported formats: {supported_formats}"
            return result
        
        # File info
        result["file_info"] = {
            "name": Path(file_path).name,
            "size_mb": file_size_mb,
            "extension": file_extension,
            "path": file_path
        }
        
        result["valid"] = True
        return result
        
    except Exception as e:
        result["error"] = f"Error validating file: {str(e)}"
        return result

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove special characters that might cause issues
    text = text.replace('\x00', '')  # Remove null bytes
    text = text.replace('\ufffd', '')  # Remove replacement characters
    
    return text.strip()

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def create_temp_file(content: bytes, suffix: str = "") -> str:
    """Create a temporary file with given content"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(content)
            return tmp_file.name
    except Exception as e:
        logger.error(f"Error creating temporary file: {str(e)}")
        raise

def cleanup_temp_file(file_path: str):
    """Clean up temporary file"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.error(f"Error cleaning up temporary file {file_path}: {str(e)}")

def get_file_hash(file_path: str) -> str:
    """Get MD5 hash of file for deduplication"""
    import hashlib
    
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash: {str(e)}")
        return ""

def setup_logging(log_level: str = "INFO", log_file: str = "logs/rag_app.log"):
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Logging setup completed")

def export_data(data: Dict[str, Any], filename: str, format: str = "json") -> str:
    """Export data to file"""
    try:
        export_dir = Path("data/exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = export_dir / filename
        
        if format.lower() == "json":
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Data exported to {file_path}")
        return str(file_path)
        
    except Exception as e:
        logger.error(f"Error exporting data: {str(e)}")
        raise

def import_data(file_path: str, format: str = "json") -> Dict[str, Any]:
    """Import data from file"""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if format.lower() == "json":
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported import format: {format}")
        
        logger.info(f"Data imported from {file_path}")
        return data
        
    except Exception as e:
        logger.error(f"Error importing data: {str(e)}")
        raise

def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    import platform
    import psutil
    import torch
    
    try:
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_free_gb": round(psutil.disk_usage('.').free / (1024**3), 2),
            "cuda_available": torch.cuda.is_available(),
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
        
        if torch.cuda.is_available():
            info["cuda_device_name"] = torch.cuda.get_device_name(0)
            info["cuda_memory_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return {"error": str(e)}

def monitor_memory_usage():
    """Monitor and log memory usage"""
    import psutil
    
    try:
        memory = psutil.virtual_memory()
        logger.info(f"Memory usage: {memory.percent}% ({memory.used / (1024**3):.2f}GB / {memory.total / (1024**3):.2f}GB)")
        
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.memory_allocated() / (1024**3)
            gpu_memory_cached = torch.cuda.memory_reserved() / (1024**3)
            logger.info(f"GPU memory: {gpu_memory:.2f}GB allocated, {gpu_memory_cached:.2f}GB cached")
        
    except Exception as e:
        logger.error(f"Error monitoring memory: {str(e)}")

def batch_process_files(file_paths: List[str], batch_size: int = 10, 
                       process_func: callable = None) -> List[Any]:
    """Process files in batches to manage memory"""
    if not process_func:
        raise ValueError("Process function is required")
    
    results = []
    
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(file_paths) + batch_size - 1)//batch_size}")
        
        batch_results = []
        for file_path in batch:
            try:
                result = process_func(file_path)
                batch_results.append(result)
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                continue
        
        results.extend(batch_results)
        
        # Monitor memory after each batch
        monitor_memory_usage()
    
    return results