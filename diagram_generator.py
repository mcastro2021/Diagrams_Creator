import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import math # Added for network diagram

class DiagramGenerator:
    def __init__(self):
        pass
    
    def create_diagram_from_content(self, content):
        """Crea un diagrama basado en el contenido procesado del documento"""
        try:
            if content['type'] == 'network':
                return self._create_network_diagram(content)
            elif content['type'] == 'text':
                return self._create_text_diagram(content)
            elif content['type'] == 'spreadsheet':
                return self._create_spreadsheet_diagram(content)
            elif content['type'] == 'json':
                return self._create_json_diagram(content)
            else:
                return {
                    'error': f'Tipo de contenido no soportado: {content["type"]}'
                }
        except Exception as e:
            return {
                'error': f'Error generando diagrama: {str(e)}'
            }
    
    def _create_network_diagram(self, content):
        """Crea un diagrama de tabla de ruteo desde información de redes"""
        try:
            network_info = content.get('network_info', {})
            
            # Crear XML para draw.io
            mxfile = ET.Element('mxfile')
            mxfile.set('host', 'app.diagrams.net')
            mxfile.set('modified', '2024-01-01T00:00:00.000Z')
            mxfile.set('agent', '5.0')
            mxfile.set('etag', 'abc123')
            mxfile.set('version', '22.1.16')
            mxfile.set('type', 'device')
            
            diagram = ET.SubElement(mxfile, 'diagram')
            diagram.set('id', 'routing_table_diagram')
            diagram.set('name', 'Tabla de Ruteo')
            
            mxGraphModel = ET.SubElement(diagram, 'mxGraphModel')
            mxGraphModel.set('dx', '1422')
            mxGraphModel.set('dy', '794')
            mxGraphModel.set('grid', '1')
            mxGraphModel.set('gridSize', '10')
            mxGraphModel.set('guides', '1')
            mxGraphModel.set('tooltips', '1')
            mxGraphModel.set('connect', '1')
            mxGraphModel.set('arrows', '1')
            mxGraphModel.set('fold', '1')
            mxGraphModel.set('page', '1')
            mxGraphModel.set('pageScale', '1')
            mxGraphModel.set('pageWidth', '1200')
            mxGraphModel.set('pageHeight', '800')
            mxGraphModel.set('math', '0')
            mxGraphModel.set('shadow', '0')
            
            root = ET.SubElement(mxGraphModel, 'root')
            
            # Agregar celdas base (requeridas por draw.io)
            cell0 = ET.SubElement(root, 'mxCell')
            cell0.set('id', '0')
            
            cell1 = ET.SubElement(root, 'mxCell')
            cell1.set('id', '1')
            cell1.set('parent', '0')
            
            # Título del diagrama
            title_cell = ET.SubElement(root, 'mxCell')
            title_cell.set('id', 'title')
            title_cell.set('value', 'TABLA DE RUTEO - CONFIGURACIÓN DE REDES')
            title_cell.set('style', 'text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1;')
            title_cell.set('vertex', '1')
            title_cell.set('parent', '1')
            title_cell.set('geometry', '<mxGeometry x="400" y="20" width="400" height="30" as="geometry"/>')
            
            # Crear tabla de subnets
            if network_info.get('subnets') or network_info.get('ip_ranges'):
                self._add_subnet_table(root, network_info)
            else:
                # Si no hay información de red, crear una tabla de ejemplo
                self._add_example_table(root)
            
            # Crear tabla de información de ruteo
            if network_info.get('routing_info'):
                self._add_routing_table(root, network_info)
            
            # Crear diagrama de red visual
            self._add_network_visualization(root, network_info)
            
            # Convertir a string XML
            xml_str = minidom.parseString(ET.tostring(mxfile)).toprettyxml(indent="  ")
            
            return {
                'diagram_data': xml_str,
                'drawio_url': None,
                'download_url': None,
                'title': 'Tabla de Ruteo - Configuración de Redes',
                'type': 'routing_table'
            }
            
        except Exception as e:
            return {
                'error': f'Error creando diagrama de red: {str(e)}'
            }
    
    def _add_subnet_table(self, root, network_info):
        """Agrega tabla de subnets al diagrama"""
        # Encabezados de la tabla
        headers = ['Subnet/Rango IP', 'Tipo', 'Descripción']
        cell_width = 150
        cell_height = 40
        start_x = 50
        start_y = 80
        
        # Crear encabezados
        for i, header in enumerate(headers):
            cell = ET.SubElement(root, 'mxCell')
            cell.set('id', f'subnet_header_{i}')
            cell.set('value', header)
            cell.set('style', 'rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=12;')
            cell.set('vertex', '1')
            cell.set('parent', '1')
            cell.set('geometry', f'<mxGeometry x="{start_x + i * cell_width}" y="{start_y}" width="{cell_width}" height="{cell_height}" as="geometry"/>')
        
        # Agregar subnets
        y_offset = start_y + cell_height
        subnet_data = []
        
        # Agregar subnets CIDR
        for subnet in network_info.get('subnets', []):
            if '/' in subnet:
                subnet_data.append([subnet, 'CIDR', 'Subnet con máscara'])
            else:
                subnet_data.append([subnet, 'IP', 'Dirección IP individual'])
        
        # Agregar rangos de IP
        for ip_range in network_info.get('ip_ranges', []):
            subnet_data.append([ip_range, 'Rango', 'Rango de direcciones IP'])
        
        # Crear filas de datos (limitar a 15 para el diagrama)
        for row_idx, row_data in enumerate(subnet_data[:15]):
            for col_idx, value in enumerate(row_data):
                cell = ET.SubElement(root, 'mxCell')
                cell.set('id', f'subnet_cell_{row_idx}_{col_idx}')
                cell.set('value', str(value))
                cell.set('style', 'rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;')
                cell.set('vertex', '1')
                cell.set('parent', '1')
                cell.set('geometry', f'<mxGeometry x="{start_x + col_idx * cell_width}" y="{y_offset + row_idx * cell_height}" width="{cell_width}" height="{cell_height}" as="geometry"/>')
    
    def _add_example_table(self, root):
        """Agrega una tabla de ejemplo cuando no hay información de red"""
        # Encabezados de la tabla
        headers = ['Subnet/Rango IP', 'Tipo', 'Descripción']
        cell_width = 150
        cell_height = 40
        start_x = 50
        start_y = 80
        
        # Crear encabezados
        for i, header in enumerate(headers):
            cell = ET.SubElement(root, 'mxCell')
            cell.set('id', f'example_header_{i}')
            cell.set('value', header)
            cell.set('style', 'rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;fontSize=12;')
            cell.set('vertex', '1')
            cell.set('parent', '1')
            cell.set('geometry', f'<mxGeometry x="{start_x + i * cell_width}" y="{start_y}" width="{cell_width}" height="{cell_height}" as="geometry"/>')
        
        # Agregar fila de ejemplo
        example_data = ['192.168.1.0/24', 'CIDR', 'Ejemplo de subnet']
        y_offset = start_y + cell_height
        
        for col_idx, value in enumerate(example_data):
            cell = ET.SubElement(root, 'mxCell')
            cell.set('id', f'example_cell_{col_idx}')
            cell.set('value', str(value))
            cell.set('style', 'rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;')
            cell.set('vertex', '1')
            cell.set('parent', '1')
            cell.set('geometry', f'<mxGeometry x="{start_x + col_idx * cell_width}" y="{y_offset}" width="{cell_width}" height="{cell_height}" as="geometry"/>')
    
    def _add_routing_table(self, root, network_info):
        """Agrega tabla de información de ruteo al diagrama"""
        routing_info = network_info.get('routing_info', [])
        if not routing_info:
            return
        
        # Encabezados de la tabla
        headers = ['Información de Ruteo', 'Valor']
        cell_width = 200
        cell_height = 35
        start_x = 50
        start_y = 400
        
        # Crear encabezados
        for i, header in enumerate(headers):
            cell = ET.SubElement(root, 'mxCell')
            cell.set('id', f'routing_header_{i}')
            cell.set('value', header)
            cell.set('style', 'rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontStyle=1;fontSize=12;')
            cell.set('vertex', '1')
            cell.set('parent', '1')
            cell.set('geometry', f'<mxGeometry x="{start_x + i * cell_width}" y="{start_y}" width="{cell_width}" height="{cell_height}" as="geometry"/>')
        
        # Agregar información de ruteo
        y_offset = start_y + cell_height
        for row_idx, info in enumerate(routing_info[:10]):  # Limitar a 10 elementos
            # Información
            cell = ET.SubElement(root, 'mxCell')
            cell.set('id', f'routing_info_{row_idx}')
            cell.set('value', f'Ruta {row_idx + 1}')
            cell.set('style', 'rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;')
            cell.set('vertex', '1')
            cell.set('parent', '1')
            cell.set('geometry', f'<mxGeometry x="{start_x}" y="{y_offset + row_idx * cell_height}" width="{cell_width}" height="{cell_height}" as="geometry"/>')
            
            # Valor
            cell = ET.SubElement(root, 'mxCell')
            cell.set('id', f'routing_value_{row_idx}')
            cell.set('value', str(info))
            cell.set('style', 'rounded=0;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;')
            cell.set('vertex', '1')
            cell.set('parent', '1')
            cell.set('geometry', f'<mxGeometry x="{start_x + cell_width}" y="{y_offset + row_idx * cell_height}" width="{cell_width}" height="{cell_height}" as="geometry"/>')
    
    def _add_network_visualization(self, root, network_info):
        """Agrega visualización de red al diagrama"""
        # Crear nodos de red
        start_x = 600
        start_y = 100
        
        # Nodo central de red
        central_node = ET.SubElement(root, 'mxCell')
        central_node.set('id', 'central_network')
        central_node.set('value', 'RED PRINCIPAL')
        central_node.set('style', 'ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;')
        central_node.set('vertex', '1')
        central_node.set('parent', '1')
        central_node.set('geometry', f'<mxGeometry x="{start_x + 100}" y="{start_y + 100}" width="120" height="80" as="geometry"/>')
        
        # Agregar nodos de subnet
        subnet_count = len(network_info.get('subnets', [])) + len(network_info.get('ip_ranges', []))
        if subnet_count > 0:
            angle_step = 360 / min(subnet_count, 8)  # Máximo 8 nodos para evitar sobrecarga
            
            for i in range(min(subnet_count, 8)):
                angle = math.radians(i * angle_step)
                radius = 150
                x = start_x + 160 + radius * math.cos(angle)
                y = start_y + 140 + radius * math.sin(angle)
                
                # Nodo de subnet
                subnet_node = ET.SubElement(root, 'mxCell')
                subnet_node.set('id', f'subnet_node_{i}')
                subnet_node.set('value', f'Subnet {i+1}')
                subnet_node.set('style', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;')
                subnet_node.set('vertex', '1')
                subnet_node.set('parent', '1')
                subnet_node.set('geometry', f'<mxGeometry x="{x-40}" y="{y-25}" width="80" height="50" as="geometry"/>')
                
                # Conectar con nodo central
                connection = ET.SubElement(root, 'mxCell')
                connection.set('id', f'connection_{i}')
                connection.set('edge', '1')
                connection.set('parent', '1')
                connection.set('source', 'central_network')
                connection.set('target', f'subnet_node_{i}')
                connection.set('style', 'edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#666666;strokeWidth=2;')
                connection.set('geometry', '<mxGeometry relative="1" as="geometry"/>')
    
    def _create_text_diagram(self, content):
        """Crea un diagrama de flujo desde texto"""
        try:
            text = content['content']
            
            # Dividir texto en líneas
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Crear XML para draw.io
            mxfile = ET.Element('mxfile')
            mxfile.set('host', 'app.diagrams.net')
            mxfile.set('modified', '2024-01-01T00:00:00.000Z')
            mxfile.set('agent', '5.0')
            mxfile.set('etag', 'abc123')
            mxfile.set('version', '22.1.16')
            mxfile.set('type', 'device')
            
            diagram = ET.SubElement(mxfile, 'diagram')
            diagram.set('id', 'text_diagram')
            diagram.set('name', 'Diagrama de Texto')
            
            mxGraphModel = ET.SubElement(diagram, 'mxGraphModel')
            mxGraphModel.set('dx', '1422')
            mxGraphModel.set('dy', '794')
            mxGraphModel.set('grid', '1')
            mxGraphModel.set('gridSize', '10')
            mxGraphModel.set('guides', '1')
            mxGraphModel.set('tooltips', '1')
            mxGraphModel.set('connect', '1')
            mxGraphModel.set('arrows', '1')
            mxGraphModel.set('fold', '1')
            mxGraphModel.set('page', '1')
            mxGraphModel.set('pageScale', '1')
            mxGraphModel.set('pageWidth', '827')
            mxGraphModel.set('pageHeight', '1169')
            mxGraphModel.set('math', '0')
            mxGraphModel.set('shadow', '0')
            
            root = ET.SubElement(mxGraphModel, 'root')
            
            # Agregar celdas
            cell0 = ET.SubElement(root, 'mxCell')
            cell0.set('id', '0')
            
            cell1 = ET.SubElement(root, 'mxCell')
            cell1.set('id', '1')
            cell1.set('parent', '0')
            
            # Crear nodos para cada línea de texto
            y_offset = 50
            for i, line in enumerate(lines[:20]):  # Limitar a 20 líneas
                if len(line) > 50:  # Truncar líneas muy largas
                    line = line[:47] + "..."
                
                cell = ET.SubElement(root, 'mxCell')
                cell.set('id', f'text_{i}')
                cell.set('value', line)
                cell.set('style', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;')
                cell.set('vertex', '1')
                cell.set('parent', '1')
                cell.set('geometry', f'<mxGeometry x="100" y="{y_offset}" width="200" height="40" as="geometry"/>')
                
                y_offset += 60
            
            # Convertir a string XML
            xml_str = minidom.parseString(ET.tostring(mxfile)).toprettyxml(indent="  ")
            
            return {
                'diagram_data': xml_str,
                'drawio_url': None,  # No usamos URL web
                'download_url': None,
                'title': 'Diagrama de Texto',
                'type': 'text'
            }
            
        except Exception as e:
            return {
                'error': f'Error creando diagrama de texto: {str(e)}'
            }
    
    def _create_spreadsheet_diagram(self, content):
        """Crea un diagrama de tabla desde datos de hoja de cálculo"""
        try:
            headers = content.get('headers', [])
            data = content.get('data', [])
            
            # Crear XML para draw.io
            mxfile = ET.Element('mxfile')
            mxfile.set('host', 'app.diagrams.net')
            mxfile.set('modified', '2024-01-01T00:00:00.000Z')
            mxfile.set('agent', '5.0')
            mxfile.set('etag', 'abc123')
            mxfile.set('version', '22.1.16')
            mxfile.set('type', 'device')
            
            diagram = ET.SubElement(mxfile, 'diagram')
            diagram.set('id', 'spreadsheet_diagram')
            diagram.set('name', 'Diagrama de Tabla')
            
            mxGraphModel = ET.SubElement(diagram, 'mxGraphModel')
            mxGraphModel.set('dx', '1422')
            mxGraphModel.set('dy', '794')
            mxGraphModel.set('grid', '1')
            mxGraphModel.set('gridSize', '10')
            mxGraphModel.set('guides', '1')
            mxGraphModel.set('tooltips', '1')
            mxGraphModel.set('connect', '1')
            mxGraphModel.set('arrows', '1')
            mxGraphModel.set('fold', '1')
            mxGraphModel.set('page', '1')
            mxGraphModel.set('pageScale', '1')
            mxGraphModel.set('pageWidth', '827')
            mxGraphModel.set('pageHeight', '1169')
            mxGraphModel.set('math', '0')
            mxGraphModel.set('shadow', '0')
            
            root = ET.SubElement(mxGraphModel, 'root')
            
            # Agregar celdas
            cell0 = ET.SubElement(root, 'mxCell')
            cell0.set('id', '0')
            
            cell1 = ET.SubElement(root, 'mxCell')
            cell1.set('id', '1')
            cell1.set('parent', '0')
            
            # Crear tabla
            cell_width = 120
            cell_height = 40
            start_x = 50
            start_y = 50
            
            # Crear encabezados
            for i, header in enumerate(headers):
                cell = ET.SubElement(root, 'mxCell')
                cell.set('id', f'header_{i}')
                cell.set('value', str(header))
                cell.set('style', 'rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontStyle=1;')
                cell.set('vertex', '1')
                cell.set('parent', '1')
                cell.set('geometry', f'<mxGeometry x="{start_x + i * cell_width}" y="{start_y}" width="{cell_width}" height="{cell_height}" as="geometry"/>')
            
            # Crear filas de datos (limitar a 10 filas para el diagrama)
            for row_idx, row_data in enumerate(data[:10]):
                for col_idx, header in enumerate(headers):
                    value = str(row_data.get(header, ''))
                    if len(value) > 15:  # Truncar valores muy largos
                        value = value[:12] + "..."
                    
                    cell = ET.SubElement(root, 'mxCell')
                    cell.set('id', f'cell_{row_idx}_{col_idx}')
                    cell.set('value', value)
                    cell.set('style', 'rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;')
                    cell.set('vertex', '1')
                    cell.set('parent', '1')
                    cell.set('geometry', f'<mxGeometry x="{start_x + col_idx * cell_width}" y="{start_y + (row_idx + 1) * cell_height}" width="{cell_width}" height="{cell_height}" as="geometry"/>')
            
            # Convertir a string XML
            xml_str = minidom.parseString(ET.tostring(mxfile)).toprettyxml(indent="  ")
            
            return {
                'diagram_data': xml_str,
                'drawio_url': None,  # No usamos URL web
                'download_url': None,
                'title': 'Diagrama de Tabla',
                'type': 'table'
            }
            
        except Exception as e:
            return {
                'error': f'Error creando diagrama de tabla: {str(e)}'
            }
    
    def _create_json_diagram(self, content):
        """Crea un diagrama de estructura JSON"""
        try:
            json_data = content.get('content', {})
            
            # Crear XML para draw.io
            mxfile = ET.Element('mxfile')
            mxfile.set('host', 'app.diagrams.net')
            mxfile.set('modified', '2024-01-01T00:00:00.000Z')
            mxfile.set('agent', '5.0')
            mxfile.set('etag', 'abc123')
            mxfile.set('version', '22.1.16')
            mxfile.set('type', 'device')
            
            diagram = ET.SubElement(mxfile, 'diagram')
            diagram.set('id', 'json_diagram')
            diagram.set('name', 'Diagrama de Estructura JSON')
            
            mxGraphModel = ET.SubElement(diagram, 'mxGraphModel')
            mxGraphModel.set('dx', '1422')
            mxGraphModel.set('dy', '794')
            mxGraphModel.set('grid', '1')
            mxGraphModel.set('gridSize', '10')
            mxGraphModel.set('guides', '1')
            mxGraphModel.set('tooltips', '1')
            mxGraphModel.set('connect', '1')
            mxGraphModel.set('arrows', '1')
            mxGraphModel.set('fold', '1')
            mxGraphModel.set('page', '1')
            mxGraphModel.set('pageScale', '1')
            mxGraphModel.set('pageWidth', '827')
            mxGraphModel.set('pageHeight', '1169')
            mxGraphModel.set('math', '0')
            mxGraphModel.set('shadow', '0')
            
            root = ET.SubElement(mxGraphModel, 'root')
            
            # Agregar celdas
            cell0 = ET.SubElement(root, 'mxCell')
            cell0.set('id', '0')
            
            cell1 = ET.SubElement(root, 'mxCell')
            cell1.set('id', '1')
            cell1.set('parent', '0')
            
            # Crear nodo raíz
            root_cell = ET.SubElement(root, 'mxCell')
            root_cell.set('id', 'json_root')
            root_cell.set('value', 'JSON Root')
            root_cell.set('style', 'rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontStyle=1;')
            root_cell.set('vertex', '1')
            root_cell.set('parent', '1')
            root_cell.set('geometry', '<mxGeometry x="300" y="50" width="120" height="60" as="geometry"/>')
            
            # Convertir a string XML
            xml_str = minidom.parseString(ET.tostring(mxfile)).toprettyxml(indent="  ")
            
            return {
                'diagram_data': xml_str,
                'drawio_url': None,  # No usamos URL web
                'download_url': None,
                'title': 'Diagrama de Estructura JSON',
                'type': 'structure'
            }
            
        except Exception as e:
            return {
                'error': f'Error creando diagrama JSON: {str(e)}'
            }
    
    def save_diagram_to_file(self, diagram_data, filename):
        """Guarda el diagrama en un archivo"""
        try:
            if not os.path.exists('outputs'):
                os.makedirs('outputs')
            
            filepath = os.path.join('outputs', filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(diagram_data)
            
            return filepath
        except Exception as e:
            raise Exception(f"Error guardando diagrama: {str(e)}")
    
    def create_local_drawio_url(self, diagram_data):
        """Crea una URL local para abrir el diagrama en draw.io desktop"""
        try:
            # Guardar el diagrama temporalmente
            temp_file = self.save_diagram_to_file(diagram_data, 'temp_diagram.drawio')
            
            # Crear URL para abrir en draw.io desktop
            # Esto asume que draw.io desktop está instalado
            drawio_url = f"drawio://{os.path.abspath(temp_file)}"
            
            return drawio_url
        except Exception as e:
            raise Exception(f"Error generando URL local: {str(e)}")
