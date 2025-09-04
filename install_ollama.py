#!/usr/bin/env python3
"""
Script para instalar y configurar Ollama
"""

import os
import sys
import subprocess
import platform
import requests
import time

def detect_os():
    """Detectar sistema operativo"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    else:
        return "unknown"

def install_ollama_windows():
    """Instalar Ollama en Windows"""
    print("🪟 Instalando Ollama para Windows...")
    print("\n📝 Instrucciones para Windows:")
    print("1. Ve a: https://ollama.ai/download")
    print("2. Descarga 'Ollama for Windows'")
    print("3. Ejecuta el instalador")
    print("4. Reinicia tu terminal")
    print("5. Ejecuta: ollama pull llama3.2")
    
    input("\nPresiona Enter cuando hayas completado la instalación...")
    return test_ollama()

def install_ollama_macos():
    """Instalar Ollama en macOS"""
    print("🍎 Instalando Ollama para macOS...")
    
    # Verificar si Homebrew está instalado
    try:
        subprocess.run(["brew", "--version"], check=True, capture_output=True)
        print("✅ Homebrew detectado")
        
        # Instalar con Homebrew
        print("📦 Instalando Ollama con Homebrew...")
        subprocess.run(["brew", "install", "ollama"], check=True)
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Homebrew no encontrado. Instalación manual:")
        print("1. Ve a: https://ollama.ai/download")
        print("2. Descarga 'Ollama for macOS'")
        print("3. Arrastra Ollama a Applications")
        print("4. Abre Terminal y ejecuta: ollama pull llama3.2")
        
        input("\nPresiona Enter cuando hayas completado la instalación...")
    
    return test_ollama()

def install_ollama_linux():
    """Instalar Ollama en Linux"""
    print("🐧 Instalando Ollama para Linux...")
    
    try:
        # Descargar e instalar Ollama
        print("📥 Descargando Ollama...")
        subprocess.run([
            "curl", "-fsSL", "https://ollama.ai/install.sh"
        ], check=True, stdout=subprocess.PIPE)
        
        print("🔧 Instalando Ollama...")
        install_cmd = "curl -fsSL https://ollama.ai/install.sh | sh"
        subprocess.run(install_cmd, shell=True, check=True)
        
        print("✅ Ollama instalado")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando Ollama: {e}")
        print("\n📝 Instalación manual:")
        print("1. Ejecuta: curl -fsSL https://ollama.ai/install.sh | sh")
        print("2. O ve a: https://ollama.ai/download")
        
        input("\nPresiona Enter cuando hayas completado la instalación...")
    
    return test_ollama()

def test_ollama():
    """Probar si Ollama está funcionando"""
    print("\n🧪 Probando Ollama...")
    
    try:
        # Probar comando ollama
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Ollama instalado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama no responde correctamente")
            return False
            
    except FileNotFoundError:
        print("❌ Comando 'ollama' no encontrado")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama no responde (timeout)")
        return False

def test_ollama_api():
    """Probar API de Ollama"""
    print("🌐 Probando API de Ollama...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ API de Ollama funcionando")
            return True
        else:
            print(f"❌ API responde con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar a la API de Ollama")
        print("💡 Asegúrate de que Ollama esté ejecutándose")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout conectando a la API")
        return False

def download_model(model_name="llama3.2"):
    """Descargar modelo de IA"""
    print(f"\n📥 Descargando modelo {model_name}...")
    print("⚠️  Esto puede tomar varios minutos dependiendo de tu conexión")
    
    try:
        # Ejecutar ollama pull
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("📊 Descargando... (esto puede tomar tiempo)")
        
        # Mostrar progreso
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(f"   {output.strip()}")
        
        if process.returncode == 0:
            print(f"✅ Modelo {model_name} descargado exitosamente")
            return True
        else:
            error = process.stderr.read()
            print(f"❌ Error descargando modelo: {error}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando ollama pull: {e}")
        return False

def update_env_file():
    """Actualizar archivo .env"""
    print("\n📝 Actualizando configuración...")
    
    env_file = ".env"
    
    # Leer archivo actual
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
    else:
        # Copiar desde ejemplo
        if os.path.exists("env_example.txt"):
            with open("env_example.txt", 'r') as f:
                content = f.read()
        else:
            content = ""
    
    # Actualizar AI_PROVIDER
    if "AI_PROVIDER=" in content:
        content = content.replace("AI_PROVIDER=openai", "AI_PROVIDER=ollama")
        content = content.replace("AI_PROVIDER=groq", "AI_PROVIDER=ollama")
        content = content.replace("AI_PROVIDER=huggingface", "AI_PROVIDER=ollama")
    else:
        content = "AI_PROVIDER=ollama\n" + content
    
    # Guardar archivo
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Archivo .env actualizado para usar Ollama")

def main():
    """Función principal"""
    print("🚀 Instalador de Ollama para Diagrams Creator")
    print("=" * 60)
    
    # Detectar OS
    os_type = detect_os()
    print(f"🖥️  Sistema operativo detectado: {os_type}")
    
    if os_type == "unknown":
        print("❌ Sistema operativo no soportado")
        print("Visita https://ollama.ai/download para instalación manual")
        return
    
    # Verificar si ya está instalado
    if test_ollama():
        print("✅ Ollama ya está instalado")
        
        # Verificar API
        if test_ollama_api():
            print("✅ Todo listo para usar")
        else:
            print("⚠️  Ollama instalado pero API no responde")
            print("💡 Intenta ejecutar: ollama serve")
    else:
        # Instalar según OS
        print(f"\n📦 Instalando Ollama para {os_type}...")
        
        if os_type == "windows":
            success = install_ollama_windows()
        elif os_type == "macos":
            success = install_ollama_macos()
        elif os_type == "linux":
            success = install_ollama_linux()
        
        if not success:
            print("❌ Instalación fallida")
            return
    
    # Descargar modelo
    print("\n🤖 Configurando modelo de IA...")
    
    # Listar modelos disponibles
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, timeout=10)
        
        if "llama3.2" in result.stdout:
            print("✅ Modelo llama3.2 ya está disponible")
        else:
            if download_model("llama3.2"):
                print("✅ Modelo descargado exitosamente")
            else:
                print("⚠️  Error descargando modelo")
                print("💡 Puedes intentar manualmente: ollama pull llama3.2")
    
    except Exception as e:
        print(f"⚠️  Error verificando modelos: {e}")
    
    # Actualizar configuración
    update_env_file()
    
    # Instrucciones finales
    print("\n🎉 ¡Instalación completada!")
    print("=" * 60)
    print("📋 Siguientes pasos:")
    print("1. Reinicia tu aplicación: python start_app.py")
    print("2. La aplicación usará Ollama automáticamente")
    print("3. ¡Disfruta de IA gratuita e ilimitada!")
    
    print("\n💡 Comandos útiles:")
    print("   ollama list          - Ver modelos instalados")
    print("   ollama pull llama3.2 - Descargar modelo")
    print("   ollama serve         - Iniciar servidor")
    
    print("\n🔗 Más información:")
    print("   https://ollama.ai/library - Más modelos")
    print("   https://ollama.ai/docs   - Documentación")

if __name__ == '__main__':
    main()
