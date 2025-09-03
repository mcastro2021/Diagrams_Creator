"""
Configuración centralizada para Diagramas Creator
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base de la aplicación"""
    
    # Versión de la aplicación
    APP_VERSION = '1.0.0'
    
    # Configuración básica
    SECRET_KEY = os.getenv('SECRET_KEY', 'eraser-clone-secret-key-2024')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    ENV = os.getenv('FLASK_ENV', 'development')
    
    # Configuración del servidor
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB por defecto
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'doc', 'docx'}
    
    # Configuración de OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', 2000))
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', 0.7))
    
    # Configuración de iconos
    ICONS_BASE_PATH = 'icons'
    ICONS_PER_PAGE = 50
    MAX_SEARCH_RESULTS = 200
    
    # Configuración de diagramas
    MAX_DIAGRAMS_PER_USER = 100
    DIAGRAM_AUTO_SAVE_INTERVAL = 30  # segundos
    
    # Configuración de caché
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Configuración de seguridad
    SESSION_COOKIE_SECURE = False  # Cambiar a True en producción con HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuración de logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Configuración de base de datos (para futuras implementaciones)
    DATABASE_URL = os.getenv('DATABASE_URL', None)
    
    # Configuración de Redis (para futuras implementaciones)
    REDIS_URL = os.getenv('REDIS_URL', None)
    
    # Configuración de email (para futuras implementaciones)
    MAIL_SERVER = os.getenv('MAIL_SERVER', None)
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', None)
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', None)
    
    # Configuración de Azure (para futuras implementaciones)
    AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', None)
    AZURE_STORAGE_CONTAINER = os.getenv('AZURE_STORAGE_CONTAINER', 'diagrams')
    
    # Configuración de AWS (para futuras implementaciones)
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', None)
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', None)
    AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', None)
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # Configuración de iconos específica
    ICONS_BASE_DIR = 'icons'
    ICONS_AWS_DIR = 'AWS'
    ICONS_AZURE_DIR = 'Azure'
    
    # Configuración de categorías populares de iconos
    POPULAR_ICON_CATEGORIES = ['compute', 'database', 'networking', 'storage', 'security', 'monitoring']
    
    # Configuración de tipos de diagramas
    DIAGRAM_TYPE_KEYWORDS = {
        'flowchart': ['flujo', 'proceso', 'workflow', 'pasos', 'secuencia'],
        'sequence': ['secuencia', 'interacción', 'usuario', 'sistema'],
        'class': ['clase', 'objeto', 'uml', 'herencia'],
        'er': ['entidad', 'relación', 'base de datos', 'tabla'],
        'network': ['red', 'redes', 'router', 'switch', 'conexión'],
        'mindmap': ['mapa mental', 'ideas', 'conceptos', 'organización'],
        'architecture': ['arquitectura', 'componentes', 'servicios']
    }
    DEFAULT_DIAGRAM_TYPE = 'flowchart'
    
    # Configuración de Azure
    AZURE_VNET_MANAGER_FEATURES = ['Network Groups', 'Security Admin Rules', 'Connectivity Configuration']
    AZURE_FIREWALL_FEATURES = ['Threat Intelligence', 'TLS Inspection', 'Web Categories']
    
    # Configuración de palabras clave de Azure
    AZURE_VM_KEYWORDS = ['vm', 'virtual machine', 'máquina virtual', 'servidor']
    AZURE_APP_SERVICE_KEYWORDS = ['app service', 'web app', 'aplicación web', 'web service']
    AZURE_DATABASE_KEYWORDS = ['database', 'sql', 'cosmos', 'base de datos', 'db']
    AZURE_STORAGE_KEYWORDS = ['storage', 'blob', 'file', 'almacenamiento']
    AZURE_NETWORK_KEYWORDS = ['network', 'vnet', 'red', 'subnet']
    AZURE_SECURITY_KEYWORDS = ['security', 'firewall', 'seguridad', 'waf']
    AZURE_MONITORING_KEYWORDS = ['monitoring', 'log analytics', 'monitoreo', 'logs']
    AZURE_CDN_KEYWORDS = ['cdn', 'content delivery', 'distribución de contenido']
    AZURE_LOAD_BALANCER_KEYWORDS = ['load balancer', 'balanceador', 'carga']
    AZURE_API_MANAGEMENT_KEYWORDS = ['api', 'api management', 'gateway', 'puerta de enlace']
    AZURE_HUB_SPOKE_KEYWORDS = ['hub and spoke', 'hub-spoke', 'hub & spoke', 'topología hub', 'hub spoke']
    AZURE_SUBSCRIPTION_KEYWORDS = ['múltiples suscripciones', '4 suscripciones', 'varias suscripciones', 'subscriptions', 'suscripciones']
    AZURE_ENTERPRISE_KEYWORDS = ['empresarial', 'enterprise', 'corporativo', 'corporation']
    
    # Configuración de prompts del sistema
    SYSTEM_PROMPTS = {
        'flowchart': """Eres un experto en diagramas de flujo. 
        Genera un diagrama de flujo lógico y bien estructurado con la siguiente estructura JSON:
        {
            "type": "flowchart",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "start|process|decision|end",
                    "text": "texto descriptivo",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 120,
                    "height": 60
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "texto de la conexión (opcional)"
                }
            ]
        }
        
        Usa tipos de nodos apropiados:
        - start: para el inicio del proceso
        - process: para pasos o acciones
        - decision: para decisiones o condiciones
        - end: para el final del proceso
        
        Organiza los nodos en un flujo lógico de arriba hacia abajo o de izquierda a derecha.""",
        
        'sequence': """Eres un experto en diagramas de secuencia UML.
        Genera un diagrama de secuencia con la siguiente estructura JSON:
        {
            "type": "sequence",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "actor|system|database|external",
                    "text": "nombre del componente",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 100,
                    "height": 120
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "acción o mensaje"
                }
            ]
        }
        
        Usa tipos de nodos apropiados:
        - actor: para usuarios o sistemas externos
        - system: para componentes del sistema
        - database: para bases de datos
        - external: para servicios externos""",
        
        'class': """Eres un experto en diagramas de clases UML.
        Genera un diagrama de clases con la siguiente estructura JSON:
        {
            "type": "class",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "class|interface|abstract",
                    "text": "NombreClase\\n+atributo1: tipo\\n+atributo2: tipo\\n\\n+metodo1()\\n+metodo2()",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 150,
                    "height": 100
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "herencia|implementa|asociación"
                }
            ]
        }
        
        Usa tipos de nodos apropiados:
        - class: para clases regulares
        - interface: para interfaces
        - abstract: para clases abstractas""",
        
        'er': """Eres un experto en diagramas entidad-relación.
        Genera un diagrama ER con la siguiente estructura JSON:
        {
            "type": "er",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "entity|relationship|attribute",
                    "text": "NombreEntidad\\n+atributo1\\n+atributo2\\n+atributo3",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 140,
                    "height": 80
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "1:N|N:M|1:1"
                }
            ]
        }
        
        Usa tipos de nodos apropiados:
        - entity: para entidades principales
        - relationship: para relaciones
        - attribute: para atributos clave""",
        
        'network': """Eres un experto en diagramas de red.
        Genera un diagrama de red con la siguiente estructura JSON:
        {
            "type": "network",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "router|switch|pc|server",
                    "text": "nombre del dispositivo",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 80,
                    "height": 60
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "tipo de conexión"
                }
            ]
        }""",
        
        'mindmap': """Eres un experto en mapas mentales.
        Genera un mapa mental con la siguiente estructura JSON:
        {
            "type": "mindmap",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "circle|rectangle",
                    "text": "concepto o idea",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 100,
                    "height": 100
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "relación"
                }
            ]
        }""",
        
        'architecture': """Eres un experto en diagramas de arquitectura.
        Genera un diagrama de arquitectura con la siguiente estructura JSON:
        {
            "type": "architecture",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "rectangle|component|service",
                    "text": "nombre del componente",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 120,
                    "height": 60
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "tipo de conexión"
                }
            ]
        }"""
    }
    
    @staticmethod
    def init_app(app):
        """Inicializar configuración en la aplicación Flask"""
        pass

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    ENV = 'development'
    
    # Configuraciones específicas de desarrollo
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    
    # Logging más detallado en desarrollo
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    ENV = 'production'
    
    # Configuraciones de seguridad para producción
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Logging menos detallado en producción
    LOG_LEVEL = 'WARNING'
    
    # Configuraciones de rendimiento
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 año

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DEBUG = True
    ENV = 'testing'
    
    # Configuraciones específicas para testing
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Base de datos de prueba
    DATABASE_URL = 'sqlite:///:memory:'

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtener configuración basada en variables de entorno"""
    config_name = os.getenv('FLASK_CONFIG', 'default')
    return config.get(config_name, config['default'])

def validate_config():
    """Validar configuración requerida"""
    errors = []
    
    # Validar directorios requeridos
    required_dirs = [Config.UPLOAD_FOLDER, Config.OUTPUT_FOLDER, Config.ICONS_BASE_PATH]
    for directory in required_dirs:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ Directorio creado: {directory}")
            except Exception as e:
                errors.append(f"No se pudo crear el directorio {directory}: {e}")
    
    # Validar configuración de OpenAI
    if Config.OPENAI_API_KEY == 'your-openai-api-key-here':
        print("⚠️  OpenAI API Key no configurada. La funcionalidad de IA estará limitada.")
    
    # Validar configuración de archivos
    if Config.MAX_CONTENT_LENGTH < 1024 * 1024:  # Mínimo 1MB
        errors.append("MAX_CONTENT_LENGTH debe ser al menos 1MB")
    
    if errors:
        print("❌ Errores de configuración encontrados:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    print("✅ Configuración validada correctamente")
    return True

def print_config_summary():
    """Imprimir resumen de la configuración"""
    print("\n📋 Resumen de Configuración:")
    print(f"   Entorno: {Config.ENV}")
    print(f"   Debug: {Config.DEBUG}")
    print(f"   Puerto: {Config.PORT}")
    print(f"   Host: {Config.HOST}")
    print(f"   Tamaño máximo de archivo: {Config.MAX_CONTENT_LENGTH / (1024*1024):.1f} MB")
    print(f"   OpenAI configurado: {'Sí' if Config.OPENAI_API_KEY != 'your-openai-api-key-here' else 'No'}")
    print(f"   Directorio de iconos: {Config.ICONS_BASE_PATH}")
    print(f"   Directorio de uploads: {Config.UPLOAD_FOLDER}")
    print(f"   Directorio de salidas: {Config.OUTPUT_FOLDER}")
    print()

if __name__ == '__main__':
    # Ejecutar validación de configuración
    validate_config()
    print_config_summary()
