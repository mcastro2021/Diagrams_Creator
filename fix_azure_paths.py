#!/usr/bin/env python3
"""
Script para corregir las rutas incorrectas de azure.xml en app.py
"""
import re

def fix_azure_paths():
    """Corrige las rutas incorrectas de azure.xml en app.py"""
    
    # Leer el archivo app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Buscando rutas incorrectas de azure.xml en app.py...")
    
    # Patrón para encontrar rutas incorrectas
    incorrect_pattern = r'/libs/azure\.xml'
    
    # Encontrar todas las rutas incorrectas
    incorrect_paths = re.findall(incorrect_pattern, content)
    
    if not incorrect_paths:
        print("✅ No se encontraron rutas incorrectas de azure.xml")
        return
    
    print(f"📦 Encontradas {len(incorrect_paths)} rutas incorrectas de azure.xml:")
    
    # Corregir las rutas
    corrected_content = content.replace('/libs/azure.xml', '/libs/integration/azure.xml')
    
    # Guardar el archivo corregido
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(corrected_content)
    
    print(f"✅ Archivo app.py corregido: {len(incorrect_paths)} rutas cambiadas")
    print("🔄 Las rutas ahora apuntan a '/libs/integration/azure.xml'")
    
    # Verificar que no queden rutas incorrectas
    remaining_incorrect = re.findall(r'/libs/azure\.xml', corrected_content)
    if remaining_incorrect:
        print(f"⚠️ Aún quedan {len(remaining_incorrect)} rutas incorrectas")
    else:
        print("✅ Todas las rutas incorrectas han sido corregidas")

if __name__ == '__main__':
    fix_azure_paths()
