#!/usr/bin/env python3
"""
Mapeo de iconos de Azure a la carpeta Libs con estructura correcta
"""

def map_azure_icon_to_libs(icon_name):
    """Mapea nombres de iconos de Azure a iconos disponibles en la carpeta Libs"""
    try:
        # Mapeo de iconos de Azure a iconos disponibles en Libs
        icon_mapping = {
            # Networking
            "10063-icon-service-Virtual-Network-Gateways.svg": "integration/azure",
            "10061-icon-service-Virtual-Networks.svg": "integration/azure", 
            "02422-icon-service-Bastions.svg": "integration/azure",
            "10084-icon-service-Firewalls.svg": "integration/azure",
            "10079-icon-service-ExpressRoute-Circuits.svg": "integration/azure",
            
            # Compute
            "10021-icon-service-Virtual-Machine.svg": "integration/azure",
            
            # Monitor
            "00001-icon-service-Monitor.svg": "integration/azure",
            
            # Default fallback
            "default": "integration/azure"
        }
        
        # Obtener el tipo de biblioteca para el icono
        library_type = icon_mapping.get(icon_name, icon_mapping.get("default", "integration/azure"))
        
        # Construir la ruta al archivo de biblioteca
        lib_path = f"/libs/{library_type}.xml"
        
        print(f"🔍 Mapeando icono {icon_name} a biblioteca {library_type}")
        
        return {
            'library': library_type,
            'path': lib_path,
            'original_name': icon_name,
            'type': 'drawio-icon'
        }
        
    except Exception as e:
        print(f"Error mapeando icono {icon_name}: {str(e)}")
        return None

def get_icon_from_libs(icon_name):
    """Obtiene un icono específico desde la carpeta Libs"""
    try:
        # Primero intentar mapear el icono
        mapped_icon = map_azure_icon_to_libs(icon_name)
        if mapped_icon:
            return mapped_icon
        
        # Si no se puede mapear, buscar en todas las bibliotecas
        import os
        libs_path = 'Libs'
        
        if not os.path.exists(libs_path):
            return None
        
        # Buscar en todas las bibliotecas y subcarpetas
        for root, dirs, files in os.walk(libs_path):
            for filename in files:
                if filename.endswith('.xml'):
                    # Construir ruta relativa desde Libs
                    relative_path = os.path.relpath(os.path.join(root, filename), libs_path)
                    xml_path = os.path.join(root, filename)
                    
                    try:
                        with open(xml_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Buscar si el icono está en esta biblioteca
                        if icon_name.replace('.svg', '') in content:
                            return {
                                'library': relative_path.replace('.xml', ''),
                                'path': f'/libs/{relative_path}',
                                'original_name': icon_name,
                                'type': 'drawio-icon'
                            }
                            
                    except Exception as e:
                        print(f"Error buscando en {filename}: {str(e)}")
                        continue
        
        return None
        
    except Exception as e:
        print(f"Error obteniendo icono {icon_name}: {str(e)}")
        return None

def get_all_available_libraries():
    """Obtiene todas las bibliotecas XML disponibles en Libs y subcarpetas"""
    try:
        import os
        libs_path = 'Libs'
        
        if not os.path.exists(libs_path):
            return []
        
        libraries = []
        
        # Recorrer todas las carpetas y subcarpetas
        for root, dirs, files in os.walk(libs_path):
            for filename in files:
                if filename.endswith('.xml'):
                    # Construir ruta relativa desde Libs
                    relative_path = os.path.relpath(os.path.join(root, filename), libs_path)
                    full_path = os.path.join(root, filename)
                    
                    try:
                        file_size = os.path.getsize(full_path)
                        libraries.append({
                            'name': relative_path.replace('.xml', ''),
                            'path': f'/libs/{relative_path}',
                            'full_path': full_path,
                            'size': file_size,
                            'size_mb': round(file_size / (1024 * 1024), 2)
                        })
                    except Exception as e:
                        print(f"Error procesando {filename}: {str(e)}")
                        continue
        
        return libraries
        
    except Exception as e:
        print(f"Error obteniendo bibliotecas: {str(e)}")
        return []
