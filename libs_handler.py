"""
Manejador de bibliotecas de iconos desde la carpeta Libs con estructura de subcarpetas
"""
import os
import json
import re
from flask import jsonify, send_file

def get_available_libraries():
    """Obtiene todas las bibliotecas de iconos disponibles desde la carpeta Libs y subcarpetas"""
    try:
        libraries = {}
        libs_path = 'Libs'
        
        if not os.path.exists(libs_path):
            return {'error': 'Carpeta Libs no encontrada'}, 404
        
        # Cargar bibliotecas desde archivos XML en la carpeta Libs y subcarpetas
        for root, dirs, files in os.walk(libs_path):
            for filename in files:
                if filename.endswith('.xml'):
                    # Construir ruta relativa desde Libs
                    relative_path = os.path.relpath(os.path.join(root, filename), libs_path)
                    library_name = relative_path.replace('.xml', '')
                    xml_path = os.path.join(root, filename)
                    
                    try:
                        # Obtener información del archivo
                        file_size = os.path.getsize(xml_path)
                        libraries[library_name] = {
                            'filename': filename,
                            'path': f'/libs/{relative_path}',
                            'full_path': xml_path,
                            'size': file_size,
                            'size_mb': round(file_size / (1024 * 1024), 2),
                            'type': 'drawio-library',
                            'description': f'Biblioteca de iconos {library_name}',
                            'download_url': f'/libs/{relative_path}'
                        }
                        
                    except Exception as e:
                        print(f"Error procesando {filename}: {str(e)}")
                        libraries[library_name] = {
                            'filename': filename,
                            'path': f'/libs/{relative_path}',
                            'error': str(e)
                        }
        
        # Contar total de bibliotecas
        total_libraries = len(libraries)
        
        print(f"📦 Bibliotecas de iconos cargadas: {total_libraries} desde carpeta Libs y subcarpetas")
        
        return {
            'success': True,
            'libraries': libraries,
            'total_libraries': total_libraries,
            'source': 'Libs',
            'message': f'Se encontraron {total_libraries} bibliotecas de iconos'
        }
        
    except Exception as e:
        print(f"Error cargando bibliotecas de iconos: {str(e)}")
        return {'error': f'Error cargando bibliotecas de iconos: {str(e)}'}, 500

def serve_lib_file(filename):
    """Sirve archivos de bibliotecas de iconos desde la carpeta Libs y subcarpetas"""
    try:
        # Buscar el archivo en Libs y subcarpetas
        libs_path = 'Libs'
        
        for root, dirs, files in os.walk(libs_path):
            if filename in files:
                file_path = os.path.join(root, filename)
                return send_file(file_path, mimetype='application/xml')
        
        # Si no se encuentra, intentar con la ruta directa
        libs_path = os.path.join('Libs', filename)
        if os.path.exists(libs_path):
            return send_file(libs_path, mimetype='application/xml')
        else:
            return {'error': 'Archivo de biblioteca no encontrado'}, 404
            
    except Exception as e:
        return {'error': f'Error sirviendo archivo: {str(e)}'}, 500

def parse_library_content(filename):
    """Parsea el contenido de una biblioteca de iconos para extraer información de iconos"""
    try:
        libs_path = 'Libs'
        
        # Buscar el archivo en Libs y subcarpetas
        file_found = False
        xml_path = None
        
        for root, dirs, files in os.walk(libs_path):
            if filename in files:
                xml_path = os.path.join(root, filename)
                file_found = True
                break
        
        if not file_found:
            return None
        
        with open(xml_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar entradas de iconos en el XML
        # Los archivos XML de drawio-libs tienen un formato específico
        icons = []
        
        # Buscar patrones de iconos
        icon_matches = re.findall(r'"title":\s*"([^"]+)"', content)
        width_matches = re.findall(r'"w":\s*(\d+)', content)
        height_matches = re.findall(r'"h":\s*(\d+)', content)
        data_matches = re.findall(r'"data":\s*"([^"]+)"', content)
        
        # Combinar información de iconos
        for i in range(min(len(icon_matches), len(width_matches), len(height_matches))):
            icon_info = {
                'title': icon_matches[i],
                'width': int(width_matches[i]),
                'height': int(height_matches[i])
            }
            
            if i < len(data_matches):
                icon_info['data'] = data_matches[i]
            
            icons.append(icon_info)
        
        return {
            'filename': filename,
            'total_icons': len(icons),
            'icons': icons
        }
        
    except Exception as e:
        print(f"Error parseando {filename}: {str(e)}")
        return None
