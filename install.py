#!/usr/bin/env python3
"""
Script de instalación para Diagrams Creator
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 o superior es requerido")
        print(f"   Versión actual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def check_git():
    """Verificar si git está disponible"""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        print("✅ Git disponible")
        return True
    except:
        print("⚠️  Git no encontrado (opcional)")
        return False

def create_venv():
    """Crear ambiente virtual"""
    print("📦 Creando ambiente virtual...")
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Ambiente virtual creado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando ambiente virtual: {e}")
        return False

def get_pip_path():
    """Obtener ruta del pip del ambiente virtual"""
    if os.name == 'nt':  # Windows
        return os.path.join('venv', 'Scripts', 'pip.exe')
    else:  # Linux/Mac
        return os.path.join('venv', 'bin', 'pip')

def install_dependencies():
    """Instalar dependencias"""
    print("📚 Instalando dependencias...")
    pip_path = get_pip_path()
    
    if not os.path.exists(pip_path):
        print("❌ No se encontró pip en el ambiente virtual")
        return False
    
    try:
        # Actualizar pip
        subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
        
        # Instalar dependencias
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        
        print("✅ Dependencias instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def create_env_file():
    """Crear archivo .env desde el ejemplo"""
    if os.path.exists('.env'):
        print("✅ Archivo .env ya existe")
        return True
    
    if os.path.exists('env_example.txt'):
        try:
            shutil.copy('env_example.txt', '.env')
            print("✅ Archivo .env creado desde env_example.txt")
            print("   ⚠️  Recuerda configurar OPENAI_API_KEY en el archivo .env")
            return True
        except Exception as e:
            print(f"❌ Error creando .env: {e}")
            return False
    else:
        # Crear .env básico
        env_content = """# Configuración de Diagrams Creator
FLASK_ENV=development
SECRET_KEY=change-this-secret-key-in-production

# OpenAI Configuration (requerido para IA completa)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Application Configuration
PORT=5000
LOG_LEVEL=INFO
AI_TEMPERATURE=0.7
MAX_TOKENS=2000
"""
        try:
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ Archivo .env creado")
            print("   ⚠️  Recuerda configurar OPENAI_API_KEY en el archivo .env")
            return True
        except Exception as e:
            print(f"❌ Error creando .env: {e}")
            return False

def create_directories():
    """Crear directorios necesarios"""
    directories = ['outputs', 'templates', 'static/css', 'static/js']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directorios creados")
    return True

def check_libs_folder():
    """Verificar carpeta Libs"""
    if os.path.exists('Libs') and os.path.isdir('Libs'):
        lib_count = len([f for f in os.listdir('Libs') 
                        if os.path.isfile(os.path.join('Libs', f)) or 
                           os.path.isdir(os.path.join('Libs', f))])
        print(f"✅ Carpeta Libs encontrada con {lib_count} elementos")
        return True
    else:
        print("⚠️  Carpeta Libs no encontrada")
        print("   Las librerías de iconos no estarán disponibles")
        return False

def run_tests():
    """Ejecutar pruebas básicas"""
    print("🧪 Ejecutando pruebas básicas...")
    
    try:
        # Test de importación
        result = subprocess.run([
            get_python_path(), '-c', 
            'from app import app; print("Import test passed")'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Test de importación: OK")
        else:
            print(f"❌ Test de importación falló: {result.stderr}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        return False

def get_python_path():
    """Obtener ruta del python del ambiente virtual"""
    if os.name == 'nt':  # Windows
        return os.path.join('venv', 'Scripts', 'python.exe')
    else:  # Linux/Mac
        return os.path.join('venv', 'bin', 'python')

def main():
    """Función principal de instalación"""
    print("🚀 Diagrams Creator - Instalación Automática")
    print("=" * 60)
    
    # Verificaciones previas
    if not check_python_version():
        sys.exit(1)
    
    check_git()
    
    # Proceso de instalación
    steps = [
        ("Crear ambiente virtual", create_venv),
        ("Instalar dependencias", install_dependencies),
        ("Crear archivo de configuración", create_env_file),
        ("Crear directorios", create_directories),
        ("Verificar librerías de iconos", check_libs_folder),
        ("Ejecutar pruebas", run_tests)
    ]
    
    print("\n📋 Iniciando proceso de instalación...")
    print("-" * 40)
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            failed_steps.append(step_name)
    
    # Resumen
    print("\n📊 Resumen de Instalación")
    print("=" * 60)
    
    if not failed_steps:
        print("🎉 ¡Instalación completada exitosamente!")
        print("\n🚀 Siguientes pasos:")
        print("   1. Configura tu OPENAI_API_KEY en el archivo .env")
        print("   2. Ejecuta: python start_app.py")
        print("   3. Abre http://localhost:5000 en tu navegador")
        print("\n💡 Comandos útiles:")
        print("   - python test_app.py    (ejecutar pruebas)")
        print("   - python start_app.py   (iniciar aplicación)")
        
    else:
        print(f"⚠️  Instalación completada con {len(failed_steps)} advertencias:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\n📖 Consulta el README.md para solución de problemas")
    
    print("\n📚 Documentación:")
    print("   - README.md: Guía completa de uso")
    print("   - env_example.txt: Ejemplo de configuración")
    
    print("\n🙏 ¡Gracias por usar Diagrams Creator!")

if __name__ == '__main__':
    main()
