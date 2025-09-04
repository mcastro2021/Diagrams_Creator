#!/usr/bin/env python3
"""
Generador de diagramas XML para Draw.io
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
import logging
import base64
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class DiagramGenerator:
    """Genera diagramas en formato XML para Draw.io"""
    
    def __init__(self, libs_handler):
        self.libs_handler = libs_handler
        self.style_templates = self._load_style_templates()
    
    def _load_style_templates(self) -> Dict[str, Dict]:
        """Cargar plantillas de estilos"""
        return {
            'modern': {
                'component': {
                    'fillColor': '#E1F5FE',
                    'strokeColor': '#0277BD',
                    'strokeWidth': 2,
                    'rounded': 1,
                    'shadow': 1,
                    'fontColor': '#263238',
                    'fontSize': 12,
                    'fontStyle': 1
                },
                'database': {
                    'fillColor': '#F3E5F5',
                    'strokeColor': '#7B1FA2',
                    'strokeWidth': 2,
                    'rounded': 1,
                    'shadow': 1,
                    'fontColor': '#263238',
                    'fontSize': 12,
                    'fontStyle': 1
                },
                'api': {
                    'fillColor': '#E8F5E8',
                    'strokeColor': '#2E7D32',
                    'strokeWidth': 2,
                    'rounded': 1,
                    'shadow': 1,
                    'fontColor': '#263238',
                    'fontSize': 12,
                    'fontStyle': 1
                },
                'connection': {
                    'strokeColor': '#424242',
                    'strokeWidth': 2,
                    'endArrow': 'classic',
                    'fontColor': '#424242',
                    'fontSize': 10
                }
            },
            'minimal': {
                'component': {
                    'fillColor': '#FFFFFF',
                    'strokeColor': '#000000',
                    'strokeWidth': 1,
                    'rounded': 0,
                    'shadow': 0,
                    'fontColor': '#000000',
                    'fontSize': 11,
                    'fontStyle': 0
                },
                'database': {
                    'fillColor': '#F5F5F5',
                    'strokeColor': '#000000',
                    'strokeWidth': 1,
                    'rounded': 0,
                    'shadow': 0,
                    'fontColor': '#000000',
                    'fontSize': 11,
                    'fontStyle': 0
                },
                'api': {
                    'fillColor': '#F0F0F0',
                    'strokeColor': '#000000',
                    'strokeWidth': 1,
                    'rounded': 0,
                    'shadow': 0,
                    'fontColor': '#000000',
                    'fontSize': 11,
                    'fontStyle': 0
                },
                'connection': {
                    'strokeColor': '#000000',
                    'strokeWidth': 1,
                    'endArrow': 'classic',
                    'fontColor': '#000000',
                    'fontSize': 9
                }
            },
            'colorful': {
                'component': {
                    'fillColor': '#4CAF50',
                    'strokeColor': '#2E7D32',
                    'strokeWidth': 2,
                    'rounded': 1,
                    'shadow': 1,
                    'fontColor': '#FFFFFF',
                    'fontSize': 12,
                    'fontStyle': 1
                },
                'database': {
                    'fillColor': '#FF9800',
                    'strokeColor': '#F57C00',
                    'strokeWidth': 2,
                    'rounded': 1,
                    'shadow': 1,
                    'fontColor': '#FFFFFF',
                    'fontSize': 12,
                    'fontStyle': 1
                },
                'api': {
                    'fillColor': '#2196F3',
                    'strokeColor': '#1976D2',
                    'strokeWidth': 2,
                    'rounded': 1,
                    'shadow': 1,
                    'fontColor': '#FFFFFF',
                    'fontSize': 12,
                    'fontStyle': 1
                },
                'connection': {
                    'strokeColor': '#424242',
                    'strokeWidth': 2,
                    'endArrow': 'classic',
                    'fontColor': '#424242',
                    'fontSize': 10
                }
            }
        }
    
    def generate_diagram(self, analysis: Dict[str, Any], style: str = 'modern') -> Dict[str, Any]:
        """Generar diagrama completo desde análisis"""
        try:
            # Obtener componentes y conexiones
            components = analysis.get('components', [])
            connections = analysis.get('connections', [])
            
            # Crear XML del diagrama
            xml_content = self._create_diagram_xml(
                components, connections, analysis, style
            )
            
            # Crear respuesta
            diagram_data = {
                'xml': xml_content,
                'components': components,
                'connections': connections,
                'metadata': {
                    'title': analysis.get('title', 'Architecture Diagram'),
                    'description': analysis.get('description', ''),
                    'style': style,
                    'created_at': datetime.now().isoformat(),
                    'component_count': len(components),
                    'connection_count': len(connections)
                }
            }
            
            logger.info(f"Diagrama generado: {len(components)} componentes, {len(connections)} conexiones")
            
            return diagram_data
            
        except Exception as e:
            logger.error(f"Error generando diagrama: {str(e)}")
            raise
    
    def _create_diagram_xml(self, components: List[Dict], connections: List[Dict], 
                          analysis: Dict[str, Any], style: str) -> str:
        """Crear XML completo del diagrama"""
        
        # Crear elemento raíz
        mxfile = ET.Element('mxfile', {
            'host': 'app.diagrams.net',
            'modified': datetime.now().isoformat(),
            'agent': 'Diagrams Creator AI',
            'etag': str(uuid.uuid4()),
            'version': '24.7.17'
        })
        
        # Crear diagrama
        diagram = ET.SubElement(mxfile, 'diagram', {
            'id': str(uuid.uuid4()),
            'name': analysis.get('title', 'Architecture Diagram')
        })
        
        # Crear contenido del diagrama
        mxgraphmodel = ET.SubElement(diagram, 'mxGraphModel', {
            'dx': '1422',
            'dy': '794',
            'grid': '1',
            'gridSize': '10',
            'guides': '1',
            'tooltips': '1',
            'connect': '1',
            'arrows': '1',
            'fold': '1',
            'page': '1',
            'pageScale': '1',
            'pageWidth': '827',
            'pageHeight': '1169',
            'math': '0',
            'shadow': '0'
        })
        
        # Crear root
        root = ET.SubElement(mxgraphmodel, 'root')
        
        # Crear celdas base
        ET.SubElement(root, 'mxCell', {'id': '0'})
        ET.SubElement(root, 'mxCell', {'id': '1', 'parent': '0'})
        
        # Agregar componentes
        cell_id = 2
        component_cells = {}
        
        for component in components:
            cell_element, cell_id = self._create_component_cell(
                component, cell_id, style
            )
            root.append(cell_element)
            component_cells[component['id']] = str(cell_id - 1)
        
        # Agregar conexiones
        for connection in connections:
            if (connection['from'] in component_cells and 
                connection['to'] in component_cells):
                
                cell_element, cell_id = self._create_connection_cell(
                    connection, 
                    component_cells[connection['from']],
                    component_cells[connection['to']],
                    cell_id, 
                    style
                )
                root.append(cell_element)
        
        # Convertir a string XML
        xml_str = ET.tostring(mxfile, encoding='unicode')
        
        # Formatear XML
        return self._format_xml(xml_str)
    
    def _create_component_cell(self, component: Dict, cell_id: int, style: str) -> tuple:
        """Crear celda XML para un componente"""
        
        # Obtener estilo
        component_type = component.get('type', 'component')
        style_dict = self.style_templates[style].get(component_type, 
                                                   self.style_templates[style]['component'])
        
        # Buscar icono apropiado
        icon_data = self._find_component_icon(component)
        
        # Crear geometría con tamaños apropiados para Draw.io
        pos = component.get('position', {'x': 100, 'y': 100})
        
        # Tamaños amplios según tipo de componente
        if component.get('type') in ['subscription', 'network']:
            width = 300   # Más ancho para VNets y subscriptions
            height = 150  # Más alto para texto detallado
        elif component.get('type') in ['service', 'webapp', 'database', 'security']:
            width = 250   # Tamaño estándar para servicios
            height = 120  # Suficiente para icono y texto
        else:
            width = 200   # Tamaño por defecto
            height = 100
        
        # Crear estilo string
        style_str = self._create_style_string(style_dict, icon_data)
        
        # Crear elemento mxCell
        cell = ET.Element('mxCell', {
            'id': str(cell_id),
            'value': component.get('name', 'Component'),
            'style': style_str,
            'vertex': '1',
            'parent': '1'
        })
        
        # Crear geometría
        geometry = ET.SubElement(cell, 'mxGeometry', {
            'x': str(pos['x']),
            'y': str(pos['y']),
            'width': str(width),
            'height': str(height),
            'as': 'geometry'
        })
        
        return cell, cell_id + 1
    
    def _create_connection_cell(self, connection: Dict, source_id: str, 
                              target_id: str, cell_id: int, style: str) -> tuple:
        """Crear celda XML para una conexión"""
        
        # Obtener estilo de conexión
        style_dict = self.style_templates[style]['connection']
        
        # Crear estilo string
        style_str = ';'.join([f"{k}={v}" for k, v in style_dict.items()])
        
        # Agregar label si existe
        label = connection.get('label', '')
        if connection.get('protocol'):
            label = f"{label} ({connection['protocol']})" if label else connection['protocol']
        
        # Crear elemento mxCell
        cell = ET.Element('mxCell', {
            'id': str(cell_id),
            'value': label,
            'style': style_str,
            'edge': '1',
            'parent': '1',
            'source': source_id,
            'target': target_id
        })
        
        # Crear geometría
        geometry = ET.SubElement(cell, 'mxGeometry', {
            'relative': '1',
            'as': 'geometry'
        })
        
        return cell, cell_id + 1
    
    def _find_component_icon(self, component: Dict) -> Optional[Dict]:
        """Encontrar icono específico y apropiado para un componente"""
        try:
            component_type = component.get('type', '').lower()
            technology = component.get('technology', '').lower()
            icon_category = component.get('icon_category', '')
            component_name = component.get('name', '').lower()
            
            logger.info(f"Searching icon for: {component_name} (type: {component_type}, tech: {technology}, category: {icon_category})")
            
            # Mapeo específico para componentes Azure y tecnologías
            icon_search_strategies = [
                # 1. Categoría específica si se proporciona
                {'category': icon_category, 'terms': [component_name, technology, component_type]} if icon_category else None,
                
                # 2. Azure específicos
                {'category': 'integration_azure', 'terms': ['azure', technology.replace('azure ', ''), component_type, component_name]},
                
                # 3. Fortinet para seguridad
                {'category': 'fortinet_fortinet-products', 'terms': ['firewall', 'security', 'nsg', 'bastion']} if component_type in ['security', 'firewall'] else None,
                
                # 4. Integration para APIs y servicios
                {'category': 'integration_integration', 'terms': ['api', 'service', 'integration', 'management']} if component_type in ['api', 'service'] else None,
                
                # 5. Databases específicas
                {'category': 'integration_databases', 'terms': ['sql', 'database', 'data', 'cosmos', 'mysql']} if component_type in ['database', 'data'] else None,
                
                # 6. Infrastructure
                {'category': 'integration_infrastructure', 'terms': ['server', 'vm', 'compute', 'network', 'infrastructure']} if component_type in ['compute', 'infrastructure', 'network'] else None,
                
                # 7. Developer tools
                {'category': 'integration_developer', 'terms': ['container', 'registry', 'devops', 'build', 'pipeline']} if component_type in ['containers', 'devops'] else None,
                
                # 8. Material Design como fallback
                {'category': 'material-design-icons', 'terms': [component_type, 'server', 'service', 'application']}
            ]
            
            # Filtrar estrategias None
            icon_search_strategies = [s for s in icon_search_strategies if s is not None]
            
            # Buscar en cada estrategia
            for strategy in icon_search_strategies:
                category = strategy['category']
                search_terms = strategy['terms']
                
                # Obtener librería
                library = self.libs_handler.get_library(category)
                if not library or not library.get('icons'):
                    continue
                
                logger.info(f"Searching in library: {category} with terms: {search_terms[:3]}")
                
                # Usar función de búsqueda mejorada del libs_handler
                search_results = []
                for term in search_terms[:3]:  # Buscar con los primeros 3 términos
                    if term:
                        term_results = self.libs_handler.search_icons(term, [category])
                        search_results.extend(term_results)
                
                # Si encontramos resultados de la búsqueda, usar el mejor
                if search_results:
                    # Ordenar por score si existe
                    search_results.sort(key=lambda x: x.get('search_score', 0), reverse=True)
                    best_icon = search_results[0]
                    logger.info(f"Found icon via search: {best_icon.get('name')} (score: {best_icon.get('search_score', 0)}) in {category}")
                    return best_icon
                
                # Fallback: buscar manualmente en la librería
                best_icon = None
                best_score = 0
                
                for icon in library['icons']:
                    if not icon or not isinstance(icon, dict):
                        continue
                        
                    icon_name = str(icon.get('name', '')).lower()
                    icon_title = str(icon.get('title', '')).lower()
                    
                    score = 0
                    for term in search_terms:
                        if not term:
                            continue
                        term = str(term).lower().strip()
                        
                        # Coincidencia exacta en nombre
                        if term == icon_name or term == icon_title:
                            score += 15
                        # Coincidencia parcial en nombre
                        elif term in icon_name or term in icon_title:
                            score += 10
                        # Coincidencia con palabras clave
                        elif any(keyword in icon_name for keyword in term.split() if len(keyword) > 2):
                            score += 5
                    
                    if score > best_score:
                        best_score = score
                        best_icon = icon
                
                # Si encontramos un buen match, devolverlo
                if best_icon and best_score >= 5:
                    logger.info(f"Found good icon: {best_icon.get('name')} (score: {best_score}) in {category}")
                    return best_icon
                
                # Si no hay buen match pero la categoría es relevante, usar el primer icono
                elif category in ['integration_azure', 'integration_infrastructure'] and library['icons']:
                    logger.info(f"Using fallback icon from {category}: {library['icons'][0].get('name')}")
                    return library['icons'][0]
            
            # Último recurso: buscar cualquier icono disponible
            for category in ['integration_azure', 'material-design-icons', 'integration_infrastructure']:
                library = self.libs_handler.get_library(category)
                if library and library.get('icons') and library['icons']:
                    logger.warning(f"Using last resort icon from {category} for {component_name}")
                    return library['icons'][0]
            
            logger.warning(f"No icon found for component: {component_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error buscando icono para componente {component.get('name', 'unknown')}: {str(e)}")
            return None
    
    def _create_style_string(self, style_dict: Dict, icon_data: Optional[Dict] = None) -> str:
        """Crear string de estilo para Draw.io con iconos integrados"""
        style_parts = []
        
        # Agregar estilos básicos
        for key, value in style_dict.items():
            style_parts.append(f"{key}={value}")
        
        # INTEGRACIÓN DE ICONOS CON FORMATO HÍBRIDO
        has_icon = False
        
        if icon_data:
            logger.info(f"Integrating icon: {icon_data.get('name', 'unknown')}")
            
            # Método 1: Data URI directo
            if icon_data.get('data') and icon_data['data'].startswith('data:'):
                has_icon = True
                style_parts.append(f"image={icon_data['data']}")
                logger.info("✅ Icon integrated via data URI")
                
            # Método 2: XML/SVG embebido
            elif icon_data.get('xml'):
                try:
                    svg_content = icon_data['xml']
                    
                    # Limpiar y validar SVG
                    if not svg_content.startswith('<?xml'):
                        svg_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{svg_content}'
                    
                    # Remover caracteres problemáticos
                    svg_content = svg_content.replace('\n', '').replace('\r', '').replace('\t', ' ')
                    
                    # Codificar en base64
                    svg_b64 = base64.b64encode(svg_content.encode('utf-8')).decode()
                    data_uri = f"data:image/svg+xml;base64,{svg_b64}"
                    
                    has_icon = True
                    style_parts.append(f"image={data_uri}")
                    logger.info("✅ Icon integrated via SVG base64")
                    
                except Exception as e:
                    logger.error(f"Error encoding SVG: {e}")
                    
            # Método 3: Buscar en librería directamente
            if not has_icon and icon_data.get('library'):
                try:
                    library = self.libs_handler.get_library(icon_data['library'])
                    if library and library.get('icons'):
                        for lib_icon in library['icons']:
                            if lib_icon.get('name') == icon_data.get('name'):
                                if lib_icon.get('data') and lib_icon['data'].startswith('data:'):
                                    has_icon = True
                                    style_parts.append(f"image={lib_icon['data']}")
                                    logger.info("✅ Icon found via library search")
                                    break
                                elif lib_icon.get('xml'):
                                    try:
                                        svg_content = lib_icon['xml']
                                        if not svg_content.startswith('<?xml'):
                                            svg_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{svg_content}'
                                        svg_content = svg_content.replace('\n', '').replace('\r', '').replace('\t', ' ')
                                        svg_b64 = base64.b64encode(svg_content.encode('utf-8')).decode()
                                        has_icon = True
                                        style_parts.append(f"image=data:image/svg+xml;base64,{svg_b64}")
                                        logger.info("✅ Icon integrated via library XML")
                                        break
                                    except Exception as e:
                                        logger.warning(f"Failed to encode library icon: {e}")
                except Exception as e:
                    logger.warning(f"Error searching library: {e}")
        
        # APLICAR FORMATO SEGÚN SI HAY ICONO O NO
        if has_icon:
            # Formato específico para iconos - shape=image
            logger.info("Using image shape format")
            # Remover estilos incompatibles con shape=image
            style_parts = [part for part in style_parts if not any(incompatible in part for incompatible in 
                          ['fillColor=', 'strokeColor=', 'strokeWidth=', 'rounded=', 'shadow='])]
            
            # Añadir configuración específica para iconos
            style_parts.insert(0, "shape=image")
            style_parts.extend([
                "html=1",
                "verticalAlign=top", 
                "verticalLabelPosition=bottom",
                "labelBackgroundColor=#ffffff",
                "imageAspect=0",
                "aspect=fixed"
            ])
        else:
            # Sin icono - usar formato de rectángulo normal
            logger.info("Using rectangle shape format")
            # Mantener estilos básicos para rectángulos
            if not any('whiteSpace=' in part for part in style_parts):
                style_parts.append("whiteSpace=wrap")
            if not any('html=' in part for part in style_parts):
                style_parts.append("html=1")
        
        return ';'.join(style_parts)
    
    def _format_xml(self, xml_str: str) -> str:
        """Formatear XML para mejor legibilidad"""
        try:
            # Parsear y reformatear
            root = ET.fromstring(xml_str)
            ET.indent(root, space="  ", level=0)
            return ET.tostring(root, encoding='unicode')
        except:
            # Si falla el formateo, devolver original
            return xml_str
    
    def export_diagram(self, xml_file_path: str, export_format: str) -> str:
        """Exportar diagrama a diferentes formatos"""
        try:
            if export_format not in ['png', 'svg', 'pdf']:
                raise ValueError(f"Formato no soportado: {export_format}")
            
            # Por ahora, solo copiamos el XML
            # En una implementación completa, se usaría la API de draw.io o herramientas de conversión
            base_name = os.path.splitext(xml_file_path)[0]
            export_path = f"{base_name}.{export_format}"
            
            if export_format == 'svg':
                # Generar SVG básico
                svg_content = self._generate_basic_svg(xml_file_path)
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
            else:
                # Para PNG y PDF, por ahora copiamos el XML
                import shutil
                shutil.copy2(xml_file_path, export_path)
            
            return export_path
            
        except Exception as e:
            logger.error(f"Error exportando diagrama: {str(e)}")
            raise
    
    def _generate_basic_svg(self, xml_file_path: str) -> str:
        """Generar SVG básico desde XML de draw.io"""
        try:
            # Leer XML
            with open(xml_file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Parsear XML
            root = ET.fromstring(xml_content)
            
            # Crear SVG básico
            svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="white"/>
    <text x="400" y="300" text-anchor="middle" font-family="Arial" font-size="16">
        Diagrama generado - Use draw.io para visualización completa
    </text>
</svg>'''
            
            return svg_content
            
        except Exception as e:
            logger.error(f"Error generando SVG: {str(e)}")
            return '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="white"/>
    <text x="400" y="300" text-anchor="middle">Error generando SVG</text>
</svg>'''
    
    def create_layer_diagram(self, analysis: Dict[str, Any], style: str = 'modern') -> str:
        """Crear diagrama organizado por capas"""
        components = analysis.get('components', [])
        layers = analysis.get('layers', ['application'])
        
        # Organizar componentes por capas
        layer_components = {}
        for component in components:
            layer = component.get('layer', 'application')
            if layer not in layer_components:
                layer_components[layer] = []
            layer_components[layer].append(component)
        
        # Reorganizar posiciones por capas
        y_offset = 100
        layer_height = 200
        
        for i, layer in enumerate(layers):
            if layer in layer_components:
                x_offset = 100
                for j, component in enumerate(layer_components[layer]):
                    component['position'] = {
                        'x': x_offset + (j * 150),
                        'y': y_offset + (i * layer_height)
                    }
        
        return self._create_diagram_xml(components, analysis.get('connections', []), analysis, style)
    
    def validate_diagram(self, xml_content: str) -> Dict[str, Any]:
        """Validar contenido XML del diagrama"""
        try:
            # Intentar parsear XML
            root = ET.fromstring(xml_content)
            
            # Contar elementos
            cells = root.findall('.//mxCell')
            components = [cell for cell in cells if cell.get('vertex') == '1']
            connections = [cell for cell in cells if cell.get('edge') == '1']
            
            return {
                'valid': True,
                'component_count': len(components),
                'connection_count': len(connections),
                'total_elements': len(cells)
            }
            
        except ET.ParseError as e:
            return {
                'valid': False,
                'error': f"XML Parse Error: {str(e)}"
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f"Validation Error: {str(e)}"
            }
