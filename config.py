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
    
    # Configuración de OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Configuración de archivos
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'outputs')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'md', 'json'}
    
    # Configuración de librerías
    LIBS_FOLDER = os.path.join(os.getcwd(), 'Libs')
    
    # Configuración de diagramas
    DEFAULT_DIAGRAM_STYLE = 'modern'
    SUPPORTED_EXPORT_FORMATS = ['png', 'svg', 'pdf', 'xml']
    
    # Configuración de IA
    AI_TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    
    # Configuración de logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Configuración de la aplicación
    APP_NAME = 'Diagrams Creator'
    APP_VERSION = '1.0.0'
    APP_DESCRIPTION = 'Generador de diagramas de arquitectura con IA'

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
