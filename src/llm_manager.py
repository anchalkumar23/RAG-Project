import os
import logging
from typing import Dict, Any, List, Optional
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    pipeline, BitsAndBytesConfig
)

# LangChain LLM imports
from langchain_community.llms import HuggingFacePipeline, OpenAI
from langchain_openai import ChatOpenAI
from langchain.callbacks.manager import CallbackManagerForLLMRun

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages different types of language models for RAG"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_type = config.get('model_type', 'HuggingFace Open Source')
        self.model_name = config.get('model_name', 'microsoft/DialoGPT-medium')
        self.llm = None
        self.tokenizer = None
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the language model based on configuration"""
        try:
            if self.model_type == "OpenAI":
                self._initialize_openai_model()
            elif self.model_type == "HuggingFace Open Source":
                self._initialize_huggingface_model()
            elif self.model_type == "Local Model":
                self._initialize_local_model()
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
                
            logger.info(f"Successfully initialized {self.model_type} model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            raise
    
    def _initialize_openai_model(self):
        """Initialize OpenAI model"""
        api_key = self.config.get('openai_api_key') or os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        if "gpt-3.5" in self.model_name or "gpt-4" in self.model_name:
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                openai_api_key=api_key,
                temperature=0.1,
                max_tokens=1000
            )
        else:
            self.llm = OpenAI(
                model_name=self.model_name,
                openai_api_key=api_key,
                temperature=0.1,
                max_tokens=1000
            )
    
    def _initialize_huggingface_model(self):
        """Initialize HuggingFace model"""
        try:
            # Check if CUDA is available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            # Configure model loading based on model size and available resources
            model_config = self._get_model_config()
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                padding_side="left"
            )
            
            # Add pad token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with appropriate configuration
            if model_config['use_quantization'] and device == "cuda":
                # Use 4-bit quantization for large models
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
                
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=quantization_config,
                    device_map="auto",
                    trust_remote_code=True,
                    torch_dtype=torch.float16
                )
            else:
                # Standard loading
                model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    device_map="auto" if device == "cuda" else None,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if device == "cuda" else torch.float32
                )
                
                if device == "cpu":
                    model = model.to(device)
            
            # Create text generation pipeline
            text_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=self.tokenizer,
                max_new_tokens=model_config['max_new_tokens'],
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                device=0 if device == "cuda" else -1
            )
            
            # Wrap in LangChain HuggingFacePipeline
            self.llm = HuggingFacePipeline(
                pipeline=text_pipeline,
                model_kwargs={
                    "temperature": 0.1,
                    "max_new_tokens": model_config['max_new_tokens']
                }
            )
            
        except Exception as e:
            logger.error(f"Error initializing HuggingFace model: {str(e)}")
            # Fallback to a smaller, more reliable model
            self._initialize_fallback_model()
    
    def _initialize_fallback_model(self):
        """Initialize a smaller fallback model"""
        logger.info("Initializing fallback model...")
        
        fallback_model = "microsoft/DialoGPT-small"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            model = AutoModelForCausalLM.from_pretrained(fallback_model)
            
            text_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=self.tokenizer,
                max_new_tokens=256,
                temperature=0.1,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            self.llm = HuggingFacePipeline(pipeline=text_pipeline)
            self.model_name = fallback_model
            
            logger.info(f"Successfully initialized fallback model: {fallback_model}")
            
        except Exception as e:
            logger.error(f"Error initializing fallback model: {str(e)}")
            raise
    
    def _initialize_local_model(self):
        """Initialize local model"""
        model_path = self.config.get('model_name', '')
        
        if not os.path.exists(model_path):
            raise ValueError(f"Local model path does not exist: {model_path}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path)
            
            text_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=self.tokenizer,
                max_new_tokens=512,
                temperature=0.1
            )
            
            self.llm = HuggingFacePipeline(pipeline=text_pipeline)
            
        except Exception as e:
            logger.error(f"Error initializing local model: {str(e)}")
            raise
    
    def _get_model_config(self) -> Dict[str, Any]:
        """Get model-specific configuration"""
        config = {
            'max_new_tokens': 512,
            'use_quantization': False
        }
        
        # Model-specific configurations
        if "mistral" in self.model_name.lower():
            config.update({
                'max_new_tokens': 1024,
                'use_quantization': True
            })
        elif "llama" in self.model_name.lower():
            config.update({
                'max_new_tokens': 1024,
                'use_quantization': True
            })
        elif "flan-t5" in self.model_name.lower():
            config.update({
                'max_new_tokens': 512,
                'use_quantization': False
            })
        elif "dialogpt" in self.model_name.lower():
            config.update({
                'max_new_tokens': 256,
                'use_quantization': False
            })
        
        return config
    
    def generate_response(self, prompt: str, max_length: int = 512) -> str:
        """
        Generate response from the model
        
        Args:
            prompt: Input prompt
            max_length: Maximum response length
            
        Returns:
            Generated response
        """
        try:
            if self.llm is None:
                raise ValueError("Model not initialized")
            
            # Format prompt for better responses
            formatted_prompt = self._format_prompt(prompt)
            
            # Generate response
            response = self.llm(formatted_prompt)
            
            # Clean up response
            cleaned_response = self._clean_response(response, prompt)
            
            return cleaned_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    def _format_prompt(self, prompt: str) -> str:
        """Format prompt for better model performance"""
        if self.model_type == "OpenAI":
            return prompt
        
        # For HuggingFace models, add instruction formatting
        if "mistral" in self.model_name.lower():
            return f"<s>[INST] {prompt} [/INST]"
        elif "llama" in self.model_name.lower():
            return f"### Human: {prompt}\n### Assistant:"
        elif "flan-t5" in self.model_name.lower():
            return f"Answer the following question: {prompt}"
        else:
            return f"Human: {prompt}\nAssistant:"
    
    def _clean_response(self, response: str, original_prompt: str) -> str:
        """Clean and format the model response"""
        try:
            # Remove the original prompt if it's repeated
            if original_prompt in response:
                response = response.replace(original_prompt, "").strip()
            
            # Remove common prefixes
            prefixes_to_remove = [
                "Human:", "Assistant:", "AI:", "Bot:", 
                "### Human:", "### Assistant:", "[INST]", "[/INST]",
                "<s>", "</s>"
            ]
            
            for prefix in prefixes_to_remove:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()
            
            # Remove repetitive patterns
            lines = response.split('\n')
            cleaned_lines = []
            
            for line in lines:
                line = line.strip()
                if line and line not in cleaned_lines[-3:]:  # Avoid recent repetitions
                    cleaned_lines.append(line)
            
            response = '\n'.join(cleaned_lines)
            
            # Limit response length
            if len(response) > 1000:
                response = response[:1000] + "..."
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning response: {str(e)}")
            return response
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model_type': self.model_type,
            'model_name': self.model_name,
            'is_initialized': self.llm is not None,
            'has_tokenizer': self.tokenizer is not None,
            'device': 'cuda' if torch.cuda.is_available() else 'cpu'
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        try:
            if self.tokenizer:
                tokens = self.tokenizer.encode(text)
                return len(tokens)
            else:
                # Rough estimation: ~4 characters per token
                return len(text) // 4
        except Exception as e:
            logger.error(f"Error estimating tokens: {str(e)}")
            return len(text) // 4