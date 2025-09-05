#!/usr/bin/env python3
"""
Configuración de la aplicación Diagrams Creator
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    
    # Configuración de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Configuración de OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Alternative AI Providers
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    GROQ_MODEL = os.environ.get('GROQ_MODEL', 'llama-3.1-70b-versatile')
    
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    HUGGINGFACE_MODEL = os.environ.get('HUGGINGFACE_MODEL', 'microsoft/DialoGPT-large')
    
    # Ollama Configuration
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2')
    
    # Configuración de archivos
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'outputs')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'txt,pdf,docx,doc,md,json').split(','))
    
    # Configuración de librerías
    LIBS_FOLDER = os.path.join(os.getcwd(), 'Libs')
    
    # Configuración de diagramas
    DEFAULT_DIAGRAM_TYPE = os.environ.get('DEFAULT_DIAGRAM_TYPE', 'auto')
    DEFAULT_DIAGRAM_STYLE = os.environ.get('DEFAULT_DIAGRAM_STYLE', 'modern')
    SUPPORTED_EXPORT_FORMATS = os.environ.get('ENABLED_EXPORT_FORMATS', 'png,svg,pdf,xml').split(',')
    
    # Configuración de IA
    AI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', 0.7))
    MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 2000))
    AI_TIMEOUT = int(os.environ.get('AI_TIMEOUT', 30))
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Icon library settings
    ICON_CACHE_SIZE = int(os.environ.get('ICON_CACHE_SIZE', 1000))
    ICON_SEARCH_LIMIT = int(os.environ.get('ICON_SEARCH_LIMIT', 50))
    
    # Security settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 60))
    
    # Export settings
    PNG_QUALITY = int(os.environ.get('PNG_QUALITY', 95))
    PDF_DPI = int(os.environ.get('PDF_DPI', 300))
    
    # Development settings
    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'True').lower() == 'true'
    VERBOSE_LOGGING = os.environ.get('VERBOSE_LOGGING', 'True').lower() == 'true'
    TEST_MODE = os.environ.get('TEST_MODE', 'False').lower() == 'true'
    
    # Configuración de la aplicación
    APP_NAME = 'Diagrams Creator'
    APP_VERSION = '1.0.0'
    APP_DESCRIPTION = 'AI-Powered Architecture Diagrams'

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    FLASK_ENV = 'production'
    
class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
