import streamlit as st
import os
import tempfile
from pathlib import Path
import time
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules
from src.document_processor import DocumentProcessor
from src.vector_store import VectorStoreManager
from src.llm_manager import LLMManager
from src.rag_pipeline import RAGPipeline
from src.utils import setup_directories, load_config

# Page configuration
st.set_page_config(
    page_title="Advanced RAG Document Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Dark theme with light text */
    .stApp {
        background-color: #0e1117 !important;
        color: #ffffff !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #0e1117 !important;
        color: #ffffff !important;
    }
    
    /* All text elements */
    p, div, span, h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: #ffffff !important;
    }
    
    /* Input fields with dark theme */
    .stTextInput input, .stTextArea textarea {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #4a4b5c !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #1a1d23 !important;
        color: #ffffff !important;
    }
    
    /* Sidebar keeps dark theme */
    .css-1d391kg {
        background-color: #262730 !important;
        color: #ffffff !important;
    }
    
    /* Your existing custom styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff !important;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background: #1a1d23 !important;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        border-left: 4px solid #3b82f6;
        color: #ffffff !important;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #1e3a8a !important;
        border-left: 4px solid #3b82f6;
        color: #ffffff !important;
    }
    
    .assistant-message {
        background-color: #064e3b !important;
        border-left: 4px solid #10b981;
        color: #ffffff !important;
    }
    
    .document-card {
        background: #1a1d23 !important;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        margin: 0.5rem 0;
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'rag_pipeline' not in st.session_state:
        st.session_state.rag_pipeline = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processed_documents' not in st.session_state:
        st.session_state.processed_documents = []
    if 'vector_store_ready' not in st.session_state:
        st.session_state.vector_store_ready = False

def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">📚 Advanced RAG Document Assistant</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        model_type = st.selectbox(
            "Select Model Type",
            ["HuggingFace Open Source", "OpenAI", "Local Model"],
            help="Choose your preferred language model"
        )
        
        if model_type == "HuggingFace Open Source":
            model_name = st.selectbox(
                "Select Model",
                [
                    "microsoft/DialoGPT-medium",
                    "microsoft/DialoGPT-large", 
                    "facebook/blenderbot-400M-distill",
                    "google/flan-t5-large",
                    "mistralai/Mistral-7B-Instruct-v0.1"
                ]
            )
        elif model_type == "OpenAI":
            model_name = st.selectbox(
                "Select OpenAI Model",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
            )
            openai_api_key = st.text_input("OpenAI API Key", type="password")
        else:
            model_name = st.text_input("Local Model Path", value="path/to/your/model")
        
        # Embedding model selection
        embedding_model = st.selectbox(
            "Embedding Model",
            [
                "sentence-transformers/all-MiniLM-L6-v2",
                "sentence-transformers/all-mpnet-base-v2",
                "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"
            ]
        )
        
        # Vector store settings
        st.subheader("Vector Store Settings")
        chunk_size = st.slider("Chunk Size", 100, 2000, 1000)
        chunk_overlap = st.slider("Chunk Overlap", 0, 500, 200)
        
        # Initialize RAG Pipeline button
        if st.button("🚀 Initialize RAG Pipeline", type="primary"):
            with st.spinner("Initializing RAG Pipeline..."):
                try:
                    config = {
                        'model_type': model_type,
                        'model_name': model_name,
                        'embedding_model': embedding_model,
                        'chunk_size': chunk_size,
                        'chunk_overlap': chunk_overlap
                    }
                    
                    if model_type == "OpenAI" and 'openai_api_key' in locals():
                        config['openai_api_key'] = openai_api_key
                    
                    st.session_state.rag_pipeline = RAGPipeline(config)
                    st.success("✅ RAG Pipeline initialized successfully!")
                except Exception as e:
                    st.error(f"❌ Error initializing pipeline: {str(e)}")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Document Management", "💬 Chat Interface", "📊 Analytics", "⚙️ Advanced Settings"])
    
    with tab1:
        st.header("Document Management")
        
        # Document upload section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Upload Documents")
            uploaded_files = st.file_uploader(
                "Choose PDF or Word files",
                type=['pdf', 'docx', 'doc'],
                accept_multiple_files=True,
                help="Upload your documents to build the knowledge base"
            )
            
            # Folder path input for existing documents
            folder_path = st.text_input(
                "Or specify folder path with existing PDFs",
                placeholder="/path/to/your/pdf/folder",
                help="Path to folder containing your 100+ PDF documents"
            )
            
            if st.button("📂 Process Folder Documents", type="secondary"):
                if folder_path and os.path.exists(folder_path):
                    process_folder_documents(folder_path)
                else:
                    st.error("Please provide a valid folder path")
        
        with col2:
            st.subheader("Processing Status")
            if st.session_state.processed_documents:
                st.metric("Processed Documents", len(st.session_state.processed_documents))
                st.metric("Vector Store Status", "Ready" if st.session_state.vector_store_ready else "Not Ready")
            else:
                st.info("No documents processed yet")
        
        # Process uploaded files
        if uploaded_files and st.session_state.rag_pipeline:
            if st.button("🔄 Process Uploaded Documents", type="primary"):
                process_uploaded_documents(uploaded_files)
        
        # Display processed documents
        if st.session_state.processed_documents:
            st.subheader("Processed Documents")
            for i, doc in enumerate(st.session_state.processed_documents):
                with st.expander(f"📄 {doc['name']} ({doc['pages']} pages)"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Size:** {doc['size']} KB")
                    with col2:
                        st.write(f"**Type:** {doc['type']}")
                    with col3:
                        st.write(f"**Chunks:** {doc['chunks']}")
                    
                    if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                        remove_document(i)
    
    with tab2:
        st.header("Chat with Your Documents")
        
        if not st.session_state.vector_store_ready:
            st.warning("⚠️ Please process some documents first to enable chat functionality.")
            return
        
        # Chat interface
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {message["content"]}</div>', 
                               unsafe_allow_html=True)
                    
                    # Show sources if available
                    if "sources" in message:
                        with st.expander("📚 Sources"):
                            for source in message["sources"]:
                                st.write(f"• {source}")
        
        # Chat input
        user_question = st.text_input(
            "Ask a question about your documents:",
            placeholder="What are the main topics discussed in the documents?",
            key="chat_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🚀 Send", type="primary"):
                if user_question:
                    process_chat_message(user_question)
        
        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
    
    with tab3:
        st.header("Analytics & Insights")
        
        if st.session_state.processed_documents:
            # Document statistics
            col1, col2, col3, col4 = st.columns(4)
            
            total_docs = len(st.session_state.processed_documents)
            total_pages = sum(doc['pages'] for doc in st.session_state.processed_documents)
            total_chunks = sum(doc['chunks'] for doc in st.session_state.processed_documents)
            avg_pages = total_pages / total_docs if total_docs > 0 else 0
            
            with col1:
                st.metric("Total Documents", total_docs)
            with col2:
                st.metric("Total Pages", total_pages)
            with col3:
                st.metric("Total Chunks", total_chunks)
            with col4:
                st.metric("Avg Pages/Doc", f"{avg_pages:.1f}")
            
            # Document type distribution
            doc_types = {}
            for doc in st.session_state.processed_documents:
                doc_type = doc['type']
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            if doc_types:
                st.subheader("Document Type Distribution")
                st.bar_chart(doc_types)
            
            # Chat analytics
            if st.session_state.chat_history:
                st.subheader("Chat Analytics")
                user_messages = [msg for msg in st.session_state.chat_history if msg["role"] == "user"]
                st.metric("Total Questions Asked", len(user_messages))
        else:
            st.info("Process some documents to see analytics")
    
    with tab4:
        st.header("Advanced Settings")
        
        # Export/Import settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Export Data")
            if st.button("📤 Export Vector Store"):
                export_vector_store()
            
            if st.button("📤 Export Chat History"):
                export_chat_history()
        
        with col2:
            st.subheader("Import Data")
            vector_store_file = st.file_uploader("Import Vector Store", type=['pkl'])
            if vector_store_file and st.button("📥 Import Vector Store"):
                import_vector_store(vector_store_file)
        
        # System information
        st.subheader("System Information")
        if st.session_state.rag_pipeline:
            st.json({
                "Model Type": st.session_state.rag_pipeline.config.get('model_type'),
                "Model Name": st.session_state.rag_pipeline.config.get('model_name'),
                "Embedding Model": st.session_state.rag_pipeline.config.get('embedding_model'),
                "Chunk Size": st.session_state.rag_pipeline.config.get('chunk_size'),
                "Chunk Overlap": st.session_state.rag_pipeline.config.get('chunk_overlap')
            })

def process_folder_documents(folder_path: str):
    """Process all PDF documents in a folder"""
    try:
        pdf_files = list(Path(folder_path).glob("*.pdf"))
        
        if not pdf_files:
            st.warning("No PDF files found in the specified folder")
            return
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, pdf_file in enumerate(pdf_files):
            status_text.text(f"Processing {pdf_file.name}...")
            
            # Process document
            doc_info = st.session_state.rag_pipeline.process_document(str(pdf_file))
            st.session_state.processed_documents.append(doc_info)
            
            progress_bar.progress((i + 1) / len(pdf_files))
        
        st.session_state.vector_store_ready = True
        st.success(f"✅ Successfully processed {len(pdf_files)} documents!")
        
    except Exception as e:
        st.error(f"❌ Error processing folder: {str(e)}")

def process_uploaded_documents(uploaded_files):
    """Process uploaded documents"""
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # Process document
                doc_info = st.session_state.rag_pipeline.process_document(tmp_file_path)
                doc_info['name'] = uploaded_file.name
                st.session_state.processed_documents.append(doc_info)
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        st.session_state.vector_store_ready = True
        st.success(f"✅ Successfully processed {len(uploaded_files)} documents!")
        
    except Exception as e:
        st.error(f"❌ Error processing documents: {str(e)}")

def process_chat_message(question: str):
    """Process a chat message and get response"""
    try:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        # Get response from RAG pipeline
        with st.spinner("Thinking..."):
            response = st.session_state.rag_pipeline.query(question)
        
        # Add assistant response to history
        assistant_message = {
            "role": "assistant", 
            "content": response["answer"],
            "sources": response.get("sources", [])
        }
        st.session_state.chat_history.append(assistant_message)
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error processing question: {str(e)}")

def remove_document(index: int):
    """Remove a document from the processed list"""
    if 0 <= index < len(st.session_state.processed_documents):
        removed_doc = st.session_state.processed_documents.pop(index)
        st.success(f"Removed {removed_doc['name']}")
        st.rerun()

def export_vector_store():
    """Export vector store data"""
    try:
        if st.session_state.rag_pipeline:
            export_data = st.session_state.rag_pipeline.export_vector_store()
            st.download_button(
                label="📥 Download Vector Store",
                data=export_data,
                file_name="vector_store_export.pkl",
                mime="application/octet-stream"
            )
    except Exception as e:
        st.error(f"❌ Error exporting vector store: {str(e)}")

def export_chat_history():
    """Export chat history"""
    try:
        import json
        chat_data = json.dumps(st.session_state.chat_history, indent=2)
        st.download_button(
            label="📥 Download Chat History",
            data=chat_data,
            file_name="chat_history.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"❌ Error exporting chat history: {str(e)}")

def import_vector_store(file):
    """Import vector store data"""
    try:
        if st.session_state.rag_pipeline:
            st.session_state.rag_pipeline.import_vector_store(file.getvalue())
            st.success("✅ Vector store imported successfully!")
    except Exception as e:
        st.error(f"❌ Error importing vector store: {str(e)}")

if __name__ == "__main__":
    main()