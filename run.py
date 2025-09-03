#!/usr/bin/env python3
"""
Script de ejecución para la aplicación Conversor de Documentos a Diagramas
"""

import os
import sys
from app import app
from config import config

def main():
    """Función principal para ejecutar la aplicación"""
    
    # Obtener configuración del entorno
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name not in config:
        print(f"Error: Configuración '{config_name}' no válida")
        print("Configuraciones disponibles: development, production, testing")
        sys.exit(1)
    
    # Aplicar configuración
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Obtener puerto del entorno o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Iniciando Conversor de Documentos a Diagramas...")
    print(f"📁 Entorno: {config_name}")
    print(f"🌐 URL: http://{host}:{port}")
    print(f"📂 Directorio de subidas: {app.config['UPLOAD_FOLDER']}")
    print(f"📂 Directorio de salidas: {app.config['OUTPUT_FOLDER']}")
    print(f"📏 Tamaño máximo de archivo: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.1f} MB")
    print(f"🔧 Debug: {'Activado' if app.config['DEBUG'] else 'Desactivado'}")
    print("-" * 60)
    
    try:
        app.run(
            host=host,
            port=port,
            debug=app.config['DEBUG'],
            use_reloader=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando la aplicación: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
