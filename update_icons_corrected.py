#!/usr/bin/env python3
"""
Script para actualizar automáticamente todos los iconos en app.py para que usen las rutas correctas de Libs
"""
import re
from icon_mapping import get_icon_from_libs

def update_icons_in_file():
    """Actualiza todos los iconos en app.py para que usen las rutas correctas de Libs"""
    
    # Leer el archivo app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Buscando iconos de Azure en app.py...")
    
    # Patrón para encontrar rutas de iconos de Azure
    icon_pattern = r'/icons/Azure/[^"]+\.svg'
    
    # Encontrar todas las rutas de iconos
    icon_paths = re.findall(icon_pattern, content)
    
    if not icon_paths:
        print("✅ No se encontraron iconos de Azure para actualizar")
        return
    
    print(f"📦 Encontrados {len(icon_paths)} iconos de Azure para actualizar:")
    
    # Crear mapeo de rutas antiguas a nuevas
    path_mapping = {}
    
    for old_path in icon_paths:
        # Extraer el nombre del archivo del icono
        icon_filename = old_path.split('/')[-1]
        
        # Obtener el nuevo icono desde la carpeta Libs
        new_icon = get_icon_from_libs(icon_filename)
        
        if new_icon:
            new_path = new_icon['path']
            path_mapping[old_path] = new_path
            print(f"  🔄 {old_path} → {new_path}")
        else:
            print(f"  ⚠️ No se pudo mapear: {old_path}")
    
    # Aplicar las actualizaciones
    updated_content = content
    for old_path, new_path in path_mapping.items():
        updated_content = updated_content.replace(old_path, new_path)
    
    # Guardar el archivo actualizado
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"\n✅ Archivo app.py actualizado con {len(path_mapping)} iconos")
    print("🔄 Los iconos ahora usan las rutas correctas de la carpeta Libs")
    
    # Verificar que no queden rutas incorrectas
    remaining_incorrect = re.findall(r'/libs/azure\.xml', updated_content)
    if remaining_incorrect:
        print(f"⚠️ Aún quedan {len(remaining_incorrect)} referencias a '/libs/azure.xml' (ruta incorrecta)")
        print("🔧 Corrigiendo rutas incorrectas...")
        
        # Corregir rutas incorrectas
        updated_content = updated_content.replace('/libs/azure.xml', '/libs/integration/azure.xml')
        
        # Guardar de nuevo
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ Rutas incorrectas corregidas a '/libs/integration/azure.xml'")

if __name__ == '__main__':
    update_icons_in_file()
