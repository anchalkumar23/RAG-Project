#!/usr/bin/env python3
"""
Start script for the RAG Document Assistant API
"""
import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    # Set environment variables
    os.environ.setdefault("PYTHONPATH", str(backend_dir))
    
    # Start the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )