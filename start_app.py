#!/usr/bin/env python3
"""
Script para iniciar la aplicación Diagrams Creator
"""

import os
import sys
from app import app

def main():
    """Iniciar la aplicación"""
    print("🚀 Starting Diagrams Creator")
    print("=" * 50)
    
    # Verificar configuración
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OpenAI API Key not configured")
        print("   AI features will use fallback mode")
        print("   To enable full AI features, set OPENAI_API_KEY in .env file")
        print()
    else:
        print("✅ OpenAI API Key configured")
        print()
    
    # Mostrar información de la aplicación
    print("📋 Application Information:")
    print(f"   Name: {app.config.get('APP_NAME', 'Diagrams Creator')}")
    print(f"   Version: {app.config.get('APP_VERSION', '1.0.0')}")
    print(f"   Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"   Port: {os.getenv('PORT', '5000')}")
    print()
    
    print("🌐 Server will be available at:")
    print("   http://localhost:5000")
    print("   http://127.0.0.1:5000")
    print()
    
    print("💡 Tips:")
    print("   - Use Ctrl+C to stop the server")
    print("   - Check the README.md for usage instructions")
    print("   - Visit /api/health to check server status")
    print()
    
    try:
        # Iniciar la aplicación
        app.run(
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)),
            debug=os.environ.get('FLASK_ENV') == 'development'
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down Diagrams Creator...")
        print("Thanks for using the application!")
    except Exception as e:
        print(f"\n❌ Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
