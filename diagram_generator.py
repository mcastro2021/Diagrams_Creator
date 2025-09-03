import json
import requests
import base64
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re # Added missing import for re

class DiagramGenerator:
    def __init__(self):
        # URL de la API de draw.io (usando la versión web)
        self.drawio_url = "https://app.diagrams.net/"
        self.api_url = "https://app.diagrams.net/api/1/save"
    
    def create_diagram_from_content(self, content):
        """Crea un diagrama basado en el contenido procesado del documento"""
        try:
            if content['type'] == 'text':
                return self._create_text_diagram(content)
            elif content['type'] == 'spreadsheet':
                return self._create_spreadsheet_diagram(content)
            elif content['type'] == 'json':
                return self._create_json_diagram(content)
            else:
                return self._create_generic_diagram(content)
        
        except Exception as e:
            raise Exception(f"Error generando diagrama: {str(e)}")
    
    def create_diagram_from_text(self, text):
        """Crea un diagrama desde texto libre"""
        # Procesar el texto para identificar elementos
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Crear estructura básica
        content = {
            'type': 'text',
            'titles': [],
            'sections': [],
            'raw_text': text,
            'paragraphs': lines
        }
        
        # Identificar títulos y secciones
        current_section = []
        for line in lines:
            if line.isupper() or line.startswith('#') or re.match(r'^\d+\.', line):
                if current_section:
                    content['sections'].append(current_section)
                content['titles'].append(line)
                current_section = []
            else:
                current_section.append(line)
        
        if current_section:
            content['sections'].append(current_section)
        
        return self._create_text_diagram(content)
    
    def _create_text_diagram(self, content):
        """Crea un diagrama de flujo desde contenido de texto"""
        # Crear XML para draw.io
        root = ET.Element("mxfile")
        root.set("host", "app.diagrams.net")
        root.set("modified", "2024-01-01T00:00:00.000Z")
        root.set("agent", "5.0")
        root.set("etag", "abc123")
        root.set("version", "22.1.16")
        root.set("type", "device")
        
        diagram = ET.SubElement(root, "diagram")
        diagram.set("id", "text_diagram")
        diagram.set("name", "Diagrama de Texto")
        
        mxGraphModel = ET.SubElement(diagram, "mxGraphModel")
        mxGraphModel.set("dx", "1422")
        mxGraphModel.set("dy", "794")
        mxGraphModel.set("grid", "1")
        mxGraphModel.set("gridSize", "10")
        mxGraphModel.set("guides", "1")
        mxGraphModel.set("tooltips", "1")
        mxGraphModel.set("connect", "1")
        mxGraphModel.set("arrows", "1")
        mxGraphModel.set("fold", "1")
        mxGraphModel.set("page", "1")
        mxGraphModel.set("pageScale", "1")
        mxGraphModel.set("pageWidth", "827")
        mxGraphModel.set("pageHeight", "1169")
        mxGraphModel.set("math", "0")
        mxGraphModel.set("shadow", "0")
        
        root_elem = ET.SubElement(mxGraphModel, "root")
        
        # Agregar elementos del diagrama
        cell0 = ET.SubElement(root_elem, "mxCell")
        cell0.set("id", "0")
        
        cell1 = ET.SubElement(root_elem, "mxCell")
        cell1.set("id", "1")
        cell1.set("parent", "0")
        
        # Crear nodos para títulos y secciones
        y_offset = 50
        for i, title in enumerate(content.get('titles', [])):
            # Nodo del título
            title_cell = ET.SubElement(root_elem, "mxCell")
            title_cell.set("id", f"title_{i}")
            title_cell.set("value", title)
            title_cell.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=14;fontStyle=1;")
            title_cell.set("vertex", "1")
            title_cell.set("parent", "1")
            title_cell.set("geometry", f"x=100;y={y_offset};width=200;height=40;")
            
            y_offset += 80
            
            # Nodos para el contenido de la sección
            if i < len(content.get('sections', [])):
                section = content['sections'][i]
                for j, item in enumerate(section[:5]):  # Limitar a 5 elementos por sección
                    item_cell = ET.SubElement(root_elem, "mxCell")
                    item_cell.set("id", f"item_{i}_{j}")
                    item_cell.set("value", item[:50] + "..." if len(item) > 50 else item)
                    item_cell.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;")
                    item_cell.set("vertex", "1")
                    item_cell.set("parent", "1")
                    item_cell.set("geometry", f"x=150;y={y_offset};width=300;height=30;")
                    
                    # Conectar título con item
                    edge = ET.SubElement(root_elem, "mxCell")
                    edge.set("id", f"edge_{i}_{j}")
                    edge.set("style", "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;")
                    edge.set("edge", "1")
                    edge.set("parent", "1")
                    edge.set("source", f"title_{i}")
                    edge.set("target", f"item_{i}_{j}")
                    edge.set("geometry", "relative=1;")
                    
                    y_offset += 50
        
        # Convertir a string XML
        xml_str = ET.tostring(root, encoding='unicode')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        return {
            'xml': pretty_xml,
            'type': 'flowchart',
            'title': 'Diagrama de Texto',
            'description': f'Diagrama generado desde {len(content.get("titles", []))} secciones'
        }
    
    def _create_spreadsheet_diagram(self, content):
        """Crea un diagrama de tabla desde contenido de Excel/CSV"""
        root = ET.Element("mxfile")
        root.set("host", "app.diagrams.net")
        root.set("modified", "2024-01-01T00:00:00.000Z")
        root.set("agent", "5.0")
        root.set("etag", "abc123")
        root.set("version", "22.1.16")
        root.set("type", "device")
        
        diagram = ET.SubElement(root, "diagram")
        diagram.set("id", "spreadsheet_diagram")
        diagram.set("name", "Diagrama de Tabla")
        
        mxGraphModel = ET.SubElement(diagram, "mxGraphModel")
        mxGraphModel.set("dx", "1422")
        mxGraphModel.set("dy", "794")
        mxGraphModel.set("grid", "1")
        mxGraphModel.set("gridSize", "10")
        mxGraphModel.set("guides", "1")
        mxGraphModel.set("tooltips", "1")
        mxGraphModel.set("connect", "1")
        mxGraphModel.set("arrows", "1")
        mxGraphModel.set("fold", "1")
        mxGraphModel.set("page", "1")
        mxGraphModel.set("pageScale", "1")
        mxGraphModel.set("pageWidth", "1169")
        mxGraphModel.set("pageHeight", "827")
        mxGraphModel.set("math", "0")
        mxGraphModel.set("shadow", "0")
        
        root_elem = ET.SubElement(mxGraphModel, "root")
        
        cell0 = ET.SubElement(root_elem, "mxCell")
        cell0.set("id", "0")
        
        cell1 = ET.SubElement(root_elem, "mxCell")
        cell1.set("id", "1")
        cell1.set("parent", "0")
        
        y_offset = 50
        for diagram_data in content.get('diagrams', []):
            # Título de la hoja
            title_cell = ET.SubElement(root_elem, "mxCell")
            title_cell.set("id", f"title_{diagram_data['title']}")
            title_cell.set("value", diagram_data['title'])
            title_cell.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=16;fontStyle=1;")
            title_cell.set("vertex", "1")
            title_cell.set("parent", "1")
            title_cell.set("geometry", f"x=50;y={y_offset};width=300;height=40;")
            
            y_offset += 60
            
            # Crear tabla
            headers = diagram_data.get('headers', [])
            data = diagram_data.get('data', [])
            
            if headers:
                # Encabezados
                x_offset = 50
                for i, header in enumerate(headers):
                    header_cell = ET.SubElement(root_elem, "mxCell")
                    header_cell.set("id", f"header_{diagram_data['title']}_{i}")
                    header_cell.set("value", str(header))
                    header_cell.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;fontStyle=1;")
                    header_cell.set("vertex", "1")
                    header_cell.set("parent", "1")
                    header_cell.set("geometry", f"x={x_offset};y={y_offset};width=120;height=30;")
                    x_offset += 130
                
                y_offset += 40
                
                # Datos (limitado a 5 filas)
                for row_idx, row in enumerate(data[:5]):
                    x_offset = 50
                    for col_idx, cell_value in enumerate(row):
                        if col_idx < len(headers):
                            data_cell = ET.SubElement(root_elem, "mxCell")
                            data_cell.set("id", f"data_{diagram_data['title']}_{row_idx}_{col_idx}")
                            data_cell.set("value", str(cell_value)[:20] + "..." if len(str(cell_value)) > 20 else str(cell_value))
                            data_cell.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=10;")
                            data_cell.set("vertex", "1")
                            data_cell.set("parent", "1")
                            data_cell.set("geometry", f"x={x_offset};y={y_offset};width=120;height=25;")
                            x_offset += 130
                    y_offset += 35
            
            y_offset += 50
        
        xml_str = ET.tostring(root, encoding='unicode')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        return {
            'xml': pretty_xml,
            'type': 'table',
            'title': 'Diagrama de Tabla',
            'description': f'Diagrama generado desde {len(content.get("diagrams", []))} hojas de datos'
        }
    
    def _create_json_diagram(self, content):
        """Crea un diagrama de estructura desde contenido JSON"""
        root = ET.Element("mxfile")
        root.set("host", "app.diagrams.net")
        root.set("modified", "2024-01-01T00:00:00.000Z")
        root.set("agent", "5.0")
        root.set("etag", "abc123")
        root.set("version", "22.1.16")
        root.set("type", "device")
        
        diagram = ET.SubElement(root, "diagram")
        diagram.set("id", "json_diagram")
        diagram.set("name", "Diagrama de Estructura JSON")
        
        mxGraphModel = ET.SubElement(diagram, "mxGraphModel")
        mxGraphModel.set("dx", "1422")
        mxGraphModel.set("dy", "794")
        mxGraphModel.set("grid", "1")
        mxGraphModel.set("gridSize", "10")
        mxGraphModel.set("guides", "1")
        mxGraphModel.set("tooltips", "1")
        mxGraphModel.set("connect", "1")
        mxGraphModel.set("arrows", "1")
        mxGraphModel.set("fold", "1")
        mxGraphModel.set("page", "1")
        mxGraphModel.set("pageScale", "1")
        mxGraphModel.set("pageWidth", "1169")
        mxGraphModel.set("pageHeight", "827")
        mxGraphModel.set("math", "0")
        mxGraphModel.set("shadow", "0")
        
        root_elem = ET.SubElement(mxGraphModel, "root")
        
        cell0 = ET.SubElement(root_elem, "mxCell")
        cell0.set("id", "0")
        
        cell1 = ET.SubElement(root_elem, "mxCell")
        cell1.set("id", "1")
        cell1.set("parent", "0")
        
        # Crear diagrama de estructura
        structure = content.get('structure', {})
        self._add_json_structure_to_diagram(root_elem, structure, 100, 100, 0)
        
        xml_str = ET.tostring(root, encoding='unicode')
        pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")
        
        return {
            'xml': pretty_xml,
            'type': 'structure',
            'title': 'Diagrama de Estructura JSON',
            'description': 'Diagrama generado desde estructura JSON'
        }
    
    def _add_json_structure_to_diagram(self, root_elem, structure, x, y, depth):
        """Agrega elementos de estructura JSON al diagrama"""
        if depth > 3:  # Limitar profundidad
            return x, y
        
        if structure.get('type') == 'object':
            # Crear nodo de objeto
            obj_cell = ET.SubElement(root_elem, "mxCell")
            obj_cell.set("id", f"obj_{x}_{y}")
            obj_cell.set("value", "Object")
            obj_cell.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;")
            obj_cell.set("vertex", "1")
            obj_cell.set("parent", "1")
            obj_cell.set("geometry", f"x={x};y={y};width=100;height=40;")
            
            # Agregar propiedades
            properties = structure.get('properties', {})
            prop_y = y + 60
            for prop_name, prop_structure in list(properties.items())[:5]:  # Limitar a 5 propiedades
                prop_cell = ET.SubElement(root_elem, "mxCell")
                prop_cell.set("id", f"prop_{x}_{prop_y}")
                prop_cell.set("value", prop_name)
                prop_cell.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=10;")
                prop_cell.set("vertex", "1")
                prop_cell.set("parent", "1")
                prop_cell.set("geometry", f"x={x+20};y={prop_y};width=80;height=30;")
                
                # Conectar objeto con propiedad
                edge = ET.SubElement(root_elem, "mxCell")
                edge.set("id", f"edge_{x}_{prop_y}")
                edge.set("style", "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;")
                edge.set("edge", "1")
                edge.set("parent", "1")
                edge.set("source", f"obj_{x}_{y}")
                edge.set("target", f"prop_{x}_{prop_y}")
                edge.set("geometry", "relative=1;")
                
                prop_y += 40
            
            return x, prop_y
        
        elif structure.get('type') == 'array':
            # Crear nodo de array
            array_cell = ET.SubElement(root_elem, "mxCell")
            array_cell.set("id", f"array_{x}_{y}")
            array_cell.set("value", f"Array ({structure.get('length', 0)})")
            array_cell.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;")
            array_cell.set("vertex", "1")
            array_cell.set("parent", "1")
            array_cell.set("geometry", f"x={x};y={y};width=100;height=40;")
            
            return x, y + 60
        
        else:
            # Crear nodo de tipo básico
            type_cell = ET.SubElement(root_elem, "mxCell")
            type_cell.set("id", f"type_{x}_{y}")
            type_cell.set("value", structure.get('type', 'unknown'))
            type_cell.set("style", "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=10;")
            type_cell.set("vertex", "1")
            type_cell.set("parent", "1")
            type_cell.set("geometry", f"x={x};y={y};width=80;height=30;")
            
            return x, y + 40
    
    def _create_generic_diagram(self, content):
        """Crea un diagrama genérico para contenido no reconocido"""
        return {
            'xml': self._get_generic_xml(),
            'type': 'generic',
            'title': 'Diagrama Genérico',
            'description': 'Diagrama generado desde contenido no reconocido'
        }
    
    def _get_generic_xml(self):
        """Retorna XML genérico para draw.io"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2024-01-01T00:00:00.000Z" agent="5.0" etag="abc123" version="22.1.16" type="device">
  <diagram id="generic_diagram" name="Diagrama Genérico">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="2" value="Contenido Procesado" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=16;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="200" y="200" width="200" height="60" as="geometry" />
        </mxCell>
        <mxCell id="3" value="Diagrama Generado" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=14;fontStyle=1;" vertex="1" parent="1">
          <mxGeometry x="200" y="300" width="200" height="60" as="geometry" />
        </mxCell>
        <mxCell id="4" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''
    
    def save_diagram_to_file(self, diagram_data, filename):
        """Guarda el diagrama en un archivo"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(diagram_data['xml'])
            return True
        except Exception as e:
            raise Exception(f"Error guardando diagrama: {str(e)}")
    
    def get_drawio_editor_url(self, diagram_data):
        """Genera URL para editar el diagrama en draw.io"""
        try:
            # Codificar el XML en base64
            xml_bytes = diagram_data['xml'].encode('utf-8')
            xml_base64 = base64.b64encode(xml_bytes).decode('utf-8')
            
            # Crear URL para draw.io
            url = f"{self.drawio_url}?embed=1&spin=1&modified=unsavedChanges&proto=json#R{xml_base64}"
            return url
        
        except Exception as e:
            raise Exception(f"Error generando URL: {str(e)}")
