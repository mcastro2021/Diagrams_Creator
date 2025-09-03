import os
import PyPDF2
from docx import Document
import pandas as pd
import json
import re

class DocumentProcessor:
    def __init__(self):
        self.supported_formats = {
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            '.xlsx': self._process_excel,
            '.csv': self._process_csv,
            '.txt': self._process_text,
            '.json': self._process_json
        }
    
    def process_document(self, filepath):
        """Procesa un documento y extrae su contenido estructurado"""
        try:
            file_ext = os.path.splitext(filepath)[1].lower()
            
            if file_ext in self.supported_formats:
                return self.supported_formats[file_ext](filepath)
            else:
                raise ValueError(f"Formato de archivo no soportado: {file_ext}")
        
        except Exception as e:
            raise Exception(f"Error procesando documento: {str(e)}")
    
    def _process_pdf(self, filepath):
        """Extrae texto de archivos PDF"""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return self._structure_text_content(text)
        
        except Exception as e:
            raise Exception(f"Error procesando PDF: {str(e)}")
    
    def _process_docx(self, filepath):
        """Extrae texto de archivos Word"""
        try:
            doc = Document(filepath)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return self._structure_text_content(text)
        
        except Exception as e:
            raise Exception(f"Error procesando Word: {str(e)}")
    
    def _process_excel(self, filepath):
        """Extrae datos de archivos Excel"""
        try:
            # Leer todas las hojas
            excel_file = pd.ExcelFile(filepath)
            content = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(filepath, sheet_name=sheet_name)
                content[sheet_name] = {
                    'headers': df.columns.tolist(),
                    'data': df.values.tolist(),
                    'shape': df.shape
                }
            
            return self._structure_excel_content(content)
        
        except Exception as e:
            raise Exception(f"Error procesando Excel: {str(e)}")
    
    def _process_csv(self, filepath):
        """Extrae datos de archivos CSV"""
        try:
            df = pd.read_csv(filepath)
            content = {
                'headers': df.columns.tolist(),
                'data': df.values.tolist(),
                'shape': df.shape
            }
            
            return self._structure_excel_content(content)
        
        except Exception as e:
            raise Exception(f"Error procesando CSV: {str(e)}")
    
    def _process_text(self, filepath):
        """Procesa archivos de texto plano"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
            
            return self._structure_text_content(text)
        
        except Exception as e:
            raise Exception(f"Error procesando texto: {str(e)}")
    
    def _process_json(self, filepath):
        """Procesa archivos JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            return self._structure_json_content(data)
        
        except Exception as e:
            raise Exception(f"Error procesando JSON: {str(e)}")
    
    def _structure_text_content(self, text):
        """Estructura contenido de texto para generar diagramas"""
        # Dividir en párrafos
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Identificar títulos (líneas que empiezan con números o están en mayúsculas)
        titles = []
        content_sections = []
        
        for i, para in enumerate(paragraphs):
            if re.match(r'^\d+\.', para) or para.isupper():
                titles.append(para)
                content_sections.append([])
            elif content_sections:
                content_sections[-1].append(para)
        
        return {
            'type': 'text',
            'titles': titles,
            'sections': content_sections,
            'raw_text': text,
            'paragraphs': paragraphs
        }
    
    def _structure_excel_content(self, content):
        """Estructura contenido de Excel/CSV para generar diagramas"""
        diagrams = []
        
        for sheet_name, sheet_data in content.items():
            if sheet_data['headers'] and sheet_data['data']:
                # Crear diagrama de flujo o tabla
                diagram = {
                    'type': 'table',
                    'title': sheet_name,
                    'headers': sheet_data['headers'],
                    'data': sheet_data['data'][:10],  # Limitar a 10 filas para el diagrama
                    'total_rows': sheet_data['shape'][0]
                }
                diagrams.append(diagram)
        
        return {
            'type': 'spreadsheet',
            'diagrams': diagrams,
            'raw_content': content
        }
    
    def _structure_json_content(self, data):
        """Estructura contenido JSON para generar diagramas"""
        if isinstance(data, dict):
            return {
                'type': 'json',
                'structure': self._analyze_json_structure(data),
                'raw_data': data
            }
        elif isinstance(data, list):
            return {
                'type': 'json',
                'structure': self._analyze_list_structure(data),
                'raw_data': data
            }
        else:
            return {
                'type': 'json',
                'structure': {'type': type(data).__name__},
                'raw_data': data
            }
    
    def _analyze_json_structure(self, obj, max_depth=3, current_depth=0):
        """Analiza la estructura de un objeto JSON"""
        if current_depth >= max_depth:
            return {'type': '...'}
        
        if isinstance(obj, dict):
            structure = {'type': 'object', 'properties': {}}
            for key, value in obj.items():
                structure['properties'][key] = self._analyze_json_structure(
                    value, max_depth, current_depth + 1
                )
            return structure
        
        elif isinstance(obj, list):
            if obj:
                structure = {'type': 'array', 'items': self._analyze_json_structure(
                    obj[0], max_depth, current_depth + 1
                )}
            else:
                structure = {'type': 'array', 'items': 'empty'}
            return structure
        
        else:
            return {'type': type(obj).__name__}
    
    def _analyze_list_structure(self, lst, max_depth=3, current_depth=0):
        """Analiza la estructura de una lista JSON"""
        if current_depth >= max_depth:
            return {'type': '...'}
        
        if lst:
            return {
                'type': 'array',
                'length': len(lst),
                'sample_item': self._analyze_json_structure(lst[0], max_depth, current_depth + 1)
            }
        else:
            return {'type': 'array', 'length': 0}
