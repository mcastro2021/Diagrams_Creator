#!/usr/bin/env python3
"""
Manejador de librerías de iconos para Diagrams Creator
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class LibsHandler:
    """Maneja las librerías de iconos disponibles"""
    
    def __init__(self, libs_folder: str = 'Libs'):
        self.libs_folder = libs_folder
        self.libraries_cache = {}
        self._load_libraries()
    
    def _load_libraries(self):
        """Cargar todas las librerías disponibles"""
        try:
            if not os.path.exists(self.libs_folder):
                logger.error(f"Carpeta de librerías no encontrada: {self.libs_folder}")
                return
            
            for item in os.listdir(self.libs_folder):
                item_path = os.path.join(self.libs_folder, item)
                
                if os.path.isfile(item_path) and item.endswith('.xml'):
                    # Librería en archivo XML
                    library_name = item.replace('.xml', '')
                    self._load_xml_library(library_name, item_path)
                    
                elif os.path.isdir(item_path):
                    # Librería en carpeta - puede contener múltiples XML
                    self._load_folder_library(item, item_path)
            
            logger.info(f"Cargadas {len(self.libraries_cache)} librerías")
            
        except Exception as e:
            logger.error(f"Error cargando librerías: {str(e)}")
    
    def _load_xml_library(self, library_name: str, file_path: str):
        """Cargar librería desde archivo XML"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Intentar parsear como mxlibrary
            if '<mxlibrary>' in content:
                self._parse_mxlibrary(library_name, content)
            else:
                # Intentar parsear como XML estándar
                self._parse_standard_xml(library_name, content)
                
        except Exception as e:
            logger.error(f"Error cargando librería XML {library_name}: {str(e)}")
    
    def _parse_mxlibrary(self, library_name: str, content: str):
        """Parsear librería en formato mxlibrary"""
        try:
            # Extraer JSON de la librería
            start = content.find('[')
            end = content.rfind(']') + 1
            
            if start != -1 and end != -1:
                json_content = content[start:end]
                icons_data = json.loads(json_content)
                
                icons = []
                for i, icon_data in enumerate(icons_data):
                    # Obtener nombre del icono
                    name = icon_data.get('title', icon_data.get('name', f'Icon_{i+1}'))
                    
                    icon = {
                        'name': name,
                        'xml': icon_data.get('xml', ''),
                        'width': int(icon_data.get('w', 48)),
                        'height': int(icon_data.get('h', 48)),
                        'aspect': icon_data.get('aspect', 'fixed'),
                        'data': icon_data.get('data', ''),
                        'library': library_name,
                        'desc': icon_data.get('desc', '')
                    }
                    
                    # Si hay data URL, usarla como preview
                    if not icon['data'] and icon['xml']:
                        # Generar data URL desde XML si es SVG
                        if '<svg' in icon['xml']:
                            icon['data'] = f"data:image/svg+xml;base64,{self._encode_base64(icon['xml'])}"
                    
                    icons.append(icon)
                
                if icons:
                    self.libraries_cache[library_name] = {
                        'name': library_name,
                        'type': 'mxlibrary',
                        'icons': icons,
                        'count': len(icons)
                    }
                    logger.info(f"Cargada librería {library_name}: {len(icons)} iconos")
                
        except Exception as e:
            logger.error(f"Error parseando mxlibrary {library_name}: {str(e)}")
    
    def _parse_standard_xml(self, library_name: str, content: str):
        """Parsear librería en formato XML estándar"""
        try:
            root = ET.fromstring(content)
            icons = []
            
            # Buscar elementos que puedan ser iconos
            for element in root.iter():
                if element.tag in ['shape', 'icon', 'symbol', 'g', 'path']:
                    name = element.get('name') or element.get('id') or element.get('title') or f"icon_{len(icons)}"
                    
                    icon = {
                        'name': name,
                        'xml': ET.tostring(element, encoding='unicode'),
                        'width': int(element.get('width', 100)),
                        'height': int(element.get('height', 100)),
                        'aspect': 'fixed',
                        'data': ''
                    }
                    icons.append(icon)
            
            if icons:
                self.libraries_cache[library_name] = {
                    'name': library_name,
                    'type': 'xml',
                    'icons': icons,
                    'count': len(icons)
                }
                
        except Exception as e:
            logger.error(f"Error parseando XML estándar {library_name}: {str(e)}")
    
    def _load_folder_library(self, library_name: str, folder_path: str):
        """Cargar librería desde carpeta"""
        try:
            all_icons = []
            xml_files_found = 0
            
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                
                if os.path.isfile(file_path):
                    if file_name.endswith('.svg'):
                        # Cargar archivo SVG
                        icon = self._load_svg_icon(file_name, file_path)
                        if icon:
                            all_icons.append(icon)
                    
                    elif file_name.endswith('.png'):
                        # Cargar archivo PNG
                        icon = self._load_png_icon(file_name, file_path)
                        if icon:
                            all_icons.append(icon)
                    
                    elif file_name.endswith('.xml'):
                        # Cargar archivo XML individual como sub-librería
                        xml_files_found += 1
                        sub_library_name = f"{library_name}_{file_name.replace('.xml', '')}"
                        self._load_xml_library(sub_library_name, file_path)
            
            # Si encontramos archivos SVG/PNG, crear una librería para la carpeta
            if all_icons:
                self.libraries_cache[library_name] = {
                    'name': library_name,
                    'type': 'folder',
                    'icons': all_icons,
                    'count': len(all_icons)
                }
            
            # Si solo hay XMLs, no crear librería de carpeta (ya se crearon sub-librerías)
            if xml_files_found > 0 and not all_icons:
                logger.info(f"Cargados {xml_files_found} archivos XML de {library_name}")
                
        except Exception as e:
            logger.error(f"Error cargando librería de carpeta {library_name}: {str(e)}")
    
    def _load_svg_icon(self, file_name: str, file_path: str) -> Optional[Dict]:
        """Cargar icono SVG"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
            
            # Extraer dimensiones del SVG
            width = 100
            height = 100
            
            try:
                root = ET.fromstring(svg_content)
                width = int(float(root.get('width', 100)))
                height = int(float(root.get('height', 100)))
            except:
                pass
            
            return {
                'name': file_name.replace('.svg', ''),
                'xml': svg_content,
                'width': width,
                'height': height,
                'aspect': 'fixed',
                'data': f'data:image/svg+xml;base64,{self._encode_base64(svg_content)}',
                'file_path': file_path
            }
            
        except Exception as e:
            logger.error(f"Error cargando SVG {file_name}: {str(e)}")
            return None
    
    def _load_png_icon(self, file_name: str, file_path: str) -> Optional[Dict]:
        """Cargar icono PNG"""
        try:
            import base64
            
            with open(file_path, 'rb') as f:
                png_data = f.read()
            
            # Obtener dimensiones usando PIL si está disponible
            width = 100
            height = 100
            
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    width, height = img.size
            except ImportError:
                pass
            except Exception:
                pass
            
            return {
                'name': file_name.replace('.png', ''),
                'xml': '',
                'width': width,
                'height': height,
                'aspect': 'fixed',
                'data': f'data:image/png;base64,{base64.b64encode(png_data).decode()}',
                'file_path': file_path
            }
            
        except Exception as e:
            logger.error(f"Error cargando PNG {file_name}: {str(e)}")
            return None
    
    def _encode_base64(self, content: str) -> str:
        """Codificar contenido en base64"""
        import base64
        return base64.b64encode(content.encode('utf-8')).decode()
    
    def get_available_libraries(self) -> List[Dict]:
        """Obtener lista de librerías disponibles"""
        return [
            {
                'name': lib_data['name'],
                'type': lib_data['type'],
                'count': lib_data['count']
            }
            for lib_data in self.libraries_cache.values()
        ]
    
    def get_library(self, library_name: str) -> Optional[Dict]:
        """Obtener librería completa por nombre"""
        return self.libraries_cache.get(library_name)
    
    def get_library_icons(self, library_name: str) -> List[Dict]:
        """Obtener iconos de una librería específica"""
        if library_name in self.libraries_cache:
            return self.libraries_cache[library_name]['icons']
        return []
    
    def search_icons(self, query: str, libraries: Optional[List[str]] = None) -> List[Dict]:
        """Buscar iconos por nombre o descripción con scoring mejorado"""
        results = []
        query_lower = query.lower().strip()
        
        if not query_lower:
            return []
        
        libraries_to_search = libraries or list(self.libraries_cache.keys())
        
        logger.info(f"Searching for '{query}' in {len(libraries_to_search)} libraries")
        
        # Buscar en las librerías con scoring
        scored_results = []
        
        for lib_name in libraries_to_search:
            if lib_name not in self.libraries_cache:
                continue
                
            lib_data = self.libraries_cache[lib_name]
            if not lib_data.get('icons'):
                continue
                
            for icon in lib_data.get('icons', []):
                if not isinstance(icon, dict):
                    continue
                    
                icon_name = str(icon.get('name', '')).lower()
                icon_title = str(icon.get('title', '')).lower()
                
                score = 0
                
                # Coincidencia exacta en nombre (máxima prioridad)
                if query_lower == icon_name or query_lower == icon_title:
                    score += 100
                # Coincidencia al inicio del nombre
                elif icon_name.startswith(query_lower) or icon_title.startswith(query_lower):
                    score += 80
                # Coincidencia en cualquier parte del nombre
                elif query_lower in icon_name or query_lower in icon_title:
                    score += 60
                # Coincidencia con palabras clave
                elif any(word in icon_name for word in query_lower.split() if len(word) > 2):
                    score += 40
                
                # Bonificación por librería específica
                if 'azure' in lib_name.lower() and 'azure' in query_lower:
                    score += 20
                elif 'fortinet' in lib_name.lower() and any(x in query_lower for x in ['security', 'firewall', 'fortinet']):
                    score += 20
                elif 'integration' in lib_name.lower():
                    score += 10
                
                if score > 0:
                    result_icon = icon.copy()
                    result_icon['library'] = lib_name
                    result_icon['search_score'] = score
                    scored_results.append(result_icon)
        
        # Ordenar por score y limitar resultados
        scored_results.sort(key=lambda x: x.get('search_score', 0), reverse=True)
        results = scored_results[:50]  # Aumentar límite
        
        logger.info(f"Found {len(results)} icons for query '{query}'")
        if results:
            logger.info(f"Top result: {results[0].get('name')} (score: {results[0].get('search_score')}) from {results[0].get('library')}")
        
        return results
    
    def get_icon_by_name(self, library_name: str, icon_name: str) -> Optional[Dict]:
        """Obtener un icono específico por nombre"""
        if library_name in self.libraries_cache:
            for icon in self.libraries_cache[library_name]['icons']:
                if icon['name'] == icon_name:
                    return icon
        return None
    
    def get_cloud_icons(self) -> Dict[str, List[Dict]]:
        """Obtener iconos específicos para proveedores cloud"""
        cloud_providers = {
            'aws': ['aws', 'amazon'],
            'azure': ['azure', 'microsoft'],
            'gcp': ['gcp', 'google', 'cloud'],
            'digitalocean': ['digitalocean', 'do'],
            'kubernetes': ['kubernetes', 'k8s'],
            'docker': ['docker', 'container']
        }
        
        results = {}
        
        for provider, keywords in cloud_providers.items():
            provider_icons = []
            
            for keyword in keywords:
                icons = self.search_icons(keyword)
                provider_icons.extend(icons)
            
            # Eliminar duplicados
            unique_icons = {}
            for icon in provider_icons:
                key = f"{icon['library']}_{icon['name']}"
                if key not in unique_icons:
                    unique_icons[key] = icon
            
            results[provider] = list(unique_icons.values())
        
        return results
    
    def get_network_icons(self) -> List[Dict]:
        """Obtener iconos de red y networking"""
        network_keywords = [
            'switch', 'router', 'firewall', 'load', 'balancer',
            'network', 'ethernet', 'wifi', 'vpn', 'gateway'
        ]
        
        results = []
        for keyword in network_keywords:
            results.extend(self.search_icons(keyword))
        
        return results
    
    def get_security_icons(self) -> List[Dict]:
        """Obtener iconos de seguridad"""
        security_keywords = [
            'security', 'firewall', 'shield', 'lock', 'key',
            'cert', 'ssl', 'auth', 'identity', 'access'
        ]
        
        results = []
        for keyword in security_keywords:
            results.extend(self.search_icons(keyword))
        
        return results
