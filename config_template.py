# Diagrams Creator - Configuration Example
# Copy this file to config_local.py and fill in your API keys

import os

class LocalConfig:
    """Local configuration with API keys"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = "your_openai_api_key_here"
    OPENAI_MODEL = "gpt-3.5-turbo"
    
    # Alternative AI Providers (optional)
    # GROQ_API_KEY = "your_groq_api_key_here"
    # GROQ_MODEL = "llama-3.1-70b-versatile"
    
    # HUGGINGFACE_API_KEY = "your_huggingface_api_key_here"
    # HUGGINGFACE_MODEL = "microsoft/DialoGPT-large"
    
    # Ollama Configuration (for local AI)
    # OLLAMA_URL = "http://localhost:11434"
    # OLLAMA_MODEL = "llama3.2"
    
    # Application Configuration
    SECRET_KEY = "dev-secret-key-change-in-production"
    FLASK_ENV = "development"
    LOG_LEVEL = "INFO"
    
    # AI Processing Configuration
    AI_TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    AI_PROVIDER = "openai"
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16777216
