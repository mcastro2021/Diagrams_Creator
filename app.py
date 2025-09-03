from flask import Flask, request, jsonify, render_template, send_file, session
from flask_cors import CORS
import os
import json
import base64
import requests
from werkzeug.utils import secure_filename
import tempfile
import shutil
import time
import uuid
from datetime import datetime
from document_processor import DocumentProcessor
from diagram_generator import DiagramGenerator
import openai

app = Flask(__name__)
CORS(app)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['SECRET_KEY'] = 'eraser-clone-secret-key-2024'

# Configuración de OpenAI (para generación de diagramas con IA)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')
openai.api_key = OPENAI_API_KEY

# Crear directorios si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'csv', 'json', 'png', 'jpg', 'jpeg', 'svg'}

# Almacenamiento en memoria para diagramas
diagrams = {}  # {diagram_id: diagram_data}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_temp_files(filepath, max_retries=3):
    """Limpia archivos temporales con reintentos"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Archivo temporal eliminado: {filepath}")
            break
        except PermissionError:
            if attempt < max_retries - 1:
                print(f"Reintentando eliminar archivo en {attempt + 1} segundos...")
                time.sleep(attempt + 1)
            else:
                print(f"No se pudo eliminar archivo: {filepath}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_ai_diagram', methods=['POST'])
def generate_ai_diagram():
    """Genera un diagrama usando IA basado en una descripción en lenguaje natural"""
    try:
        data = request.get_json()
        if not data or 'description' not in data:
            return jsonify({'error': 'Descripción no proporcionada'}), 400
        
        description = data['description'].strip()
        if not description:
            return jsonify({'error': 'Descripción vacía'}), 400
        
        diagram_type = data.get('type', 'auto')
        title = data.get('title', 'Diagrama Generado por IA')
        
        print(f"Generando diagrama IA para: {description}")
        
        # Generar diagrama usando IA
        ai_diagram = generate_diagram_with_ai(description, diagram_type)
        
        if ai_diagram.get('error'):
            return jsonify({'error': ai_diagram['error']}), 500
        
        # Crear ID único para el diagrama
        diagram_id = str(uuid.uuid4())
        
        # Guardar diagrama generado por IA
        diagrams[diagram_id] = {
            'id': diagram_id,
            'title': title,
            'type': ai_diagram.get('type', 'ai_generated'),
            'data': ai_diagram['data'],
            'description': description,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': 1,
            'ai_generated': True
        }
        
        return jsonify({
            'success': True,
            'diagram_id': diagram_id,
            'diagram': diagrams[diagram_id],
            'message': 'Diagrama generado exitosamente con IA'
        })
        
    except Exception as e:
        print(f"Error generando diagrama IA: {str(e)}")
        return jsonify({'error': f'Error generando diagrama con IA: {str(e)}'}), 500

def generate_diagram_with_ai(description, diagram_type='auto'):
    """Genera un diagrama usando OpenAI basado en la descripción"""
    try:
        # Determinar el tipo de diagrama si es 'auto'
        if diagram_type == 'auto':
            diagram_type = detect_diagram_type(description)
        
        # Crear prompt para OpenAI
        system_prompt = f"""Eres un experto en diagramas y visualización de datos. 
        Necesito que generes un diagrama de tipo '{diagram_type}' basado en la siguiente descripción.
        
        El diagrama debe ser retornado en formato JSON con la siguiente estructura:
        {{
            "type": "{diagram_type}",
            "nodes": [
                {{
                    "id": "unique_id",
                    "type": "node_type",
                    "text": "texto del nodo",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": ancho,
                    "height": alto
                }}
            ],
            "edges": [
                {{
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "texto de la conexión (opcional)"
                }}
            ]
        }}
        
        Tipos de nodos disponibles:
        - rectangle: para procesos, pasos, entidades
        - circle: para puntos de inicio/fin, decisiones
        - diamond: para decisiones, condiciones
        - actor: para usuarios, personas
        - class: para clases UML
        - entity: para entidades de base de datos
        - router: para dispositivos de red
        - switch: para switches de red
        - pc: para computadoras, endpoints
        
        Asegúrate de que el diagrama sea lógico, bien estructurado y represente fielmente la descripción proporcionada.
        Usa posiciones x,y que permitan una visualización clara y organizada.
        """
        
        user_prompt = f"Genera un diagrama de {diagram_type} para: {description}"
        
        # Llamar a OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extraer respuesta
        ai_response = response.choices[0].message.content.strip()
        
        # Intentar parsear la respuesta JSON
        try:
            # Buscar JSON en la respuesta (a veces OpenAI incluye texto adicional)
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = ai_response[start_idx:end_idx]
                diagram_data = json.loads(json_str)
                
                # Validar estructura del diagrama
                if 'nodes' not in diagram_data or 'edges' not in diagram_data:
                    raise ValueError("Estructura de diagrama inválida")
                
                print(f"Diagrama IA generado exitosamente: {len(diagram_data['nodes'])} nodos, {len(diagram_data['edges'])} conexiones")
                
                return {
                    'success': True,
                    'type': diagram_data.get('type', diagram_type),
                    'data': diagram_data
                }
            else:
                raise ValueError("No se encontró JSON válido en la respuesta")
                
        except json.JSONDecodeError as e:
            print(f"Error parseando JSON de IA: {e}")
            print(f"Respuesta de IA: {ai_response}")
            # Fallback: generar diagrama básico
            return generate_fallback_diagram(description, diagram_type)
            
    except Exception as e:
        print(f"Error en OpenAI: {str(e)}")
        # Fallback: generar diagrama básico
        return generate_fallback_diagram(description, diagram_type)

def detect_diagram_type(description):
    """Detecta automáticamente el tipo de diagrama basado en la descripción"""
    description_lower = description.lower()
    
    # Patrones para detectar tipos de diagramas
    if any(word in description_lower for word in ['flujo', 'proceso', 'workflow', 'pasos', 'secuencia']):
        return 'flowchart'
    elif any(word in description_lower for word in ['secuencia', 'interacción', 'usuario', 'sistema']):
        return 'sequence'
    elif any(word in description_lower for word in ['clase', 'objeto', 'uml', 'herencia']):
        return 'class'
    elif any(word in description_lower for word in ['entidad', 'relación', 'base de datos', 'tabla']):
        return 'er'
    elif any(word in description_lower for word in ['red', 'redes', 'router', 'switch', 'conexión']):
        return 'network'
    elif any(word in description_lower for word in ['mapa mental', 'ideas', 'conceptos', 'organización']):
        return 'mindmap'
    elif any(word in description_lower for word in ['arquitectura', 'componentes', 'servicios']):
        return 'architecture'
    else:
        return 'flowchart'  # Por defecto

def generate_fallback_diagram(description, diagram_type):
    """Genera un diagrama de fallback cuando la IA falla"""
    try:
        # Crear un diagrama básico basado en la descripción
        words = description.split()[:5]  # Tomar las primeras 5 palabras
        
        nodes = []
        edges = []
        
        # Crear nodos básicos
        for i, word in enumerate(words):
            node_id = f"node_{i+1}"
            nodes.append({
                'id': node_id,
                'type': 'rectangle',
                'text': word.capitalize(),
                'x': 100 + (i * 150),
                'y': 100 + (i * 50),
                'width': 120,
                'height': 60
            })
            
            # Conectar nodos secuencialmente
            if i > 0:
                edges.append({
                    'id': f"edge_{i}",
                    'from': f"node_{i}",
                    'to': node_id
                })
        
        fallback_data = {
            'type': diagram_type,
            'nodes': nodes,
            'edges': edges
        }
        
        print(f"Diagrama de fallback generado: {len(nodes)} nodos, {len(edges)} conexiones")
        
        return {
            'success': True,
            'type': diagram_type,
            'data': fallback_data
        }
        
    except Exception as e:
        print(f"Error generando diagrama de fallback: {str(e)}")
        return {
            'error': f'Error generando diagrama de fallback: {str(e)}'
        }

@app.route('/create_diagram', methods=['POST'])
def create_diagram():
    """Crea un nuevo diagrama"""
    try:
        data = request.get_json()
        diagram_type = data.get('type', 'flowchart')
        title = data.get('title', 'Nuevo Diagrama')
        
        # Generar ID único para el diagrama
        diagram_id = str(uuid.uuid4())
        
        # Crear diagrama base según el tipo
        base_diagram = get_base_diagram(diagram_type)
        
        # Guardar diagrama
        diagrams[diagram_id] = {
            'id': diagram_id,
            'title': title,
            'type': diagram_type,
            'data': base_diagram,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': 1
        }
        
        return jsonify({
            'success': True,
            'diagram_id': diagram_id,
            'diagram': diagrams[diagram_id]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error creando diagrama: {str(e)}'}), 500

@app.route('/diagram/<diagram_id>', methods=['GET'])
def get_diagram(diagram_id):
    """Obtiene un diagrama por ID"""
    try:
        if diagram_id not in diagrams:
            return jsonify({'error': 'Diagrama no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'diagram': diagrams[diagram_id]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo diagrama: {str(e)}'}), 500

@app.route('/diagram/<diagram_id>', methods=['PUT'])
def update_diagram(diagram_id):
    """Actualiza un diagrama"""
    try:
        if diagram_id not in diagrams:
            return jsonify({'error': 'Diagrama no encontrado'}), 404
        
        data = request.get_json()
        
        # Actualizar diagrama
        diagrams[diagram_id]['data'] = data.get('data', diagrams[diagram_id]['data'])
        diagrams[diagram_id]['title'] = data.get('title', diagrams[diagram_id]['title'])
        diagrams[diagram_id]['updated_at'] = datetime.now().isoformat()
        diagrams[diagram_id]['version'] += 1
        
        return jsonify({
            'success': True,
            'diagram': diagrams[diagram_id]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error actualizando diagrama: {str(e)}'}), 500

@app.route('/diagrams', methods=['GET'])
def list_diagrams():
    """Lista todos los diagramas"""
    try:
        diagram_list = list(diagrams.values())
        return jsonify({
            'success': True,
            'diagrams': diagram_list
        })
        
    except Exception as e:
        return jsonify({'error': f'Error listando diagramas: {str(e)}'}), 500

@app.route('/templates', methods=['GET'])
def get_templates():
    """Obtiene plantillas disponibles"""
    try:
        templates = [
            {
                'id': 'flowchart',
                'name': 'Diagrama de Flujo',
                'description': 'Diagrama de flujo básico',
                'icon': 'fas fa-project-diagram'
            },
            {
                'id': 'sequence',
                'name': 'Diagrama de Secuencia',
                'description': 'Diagrama de secuencia UML',
                'icon': 'fas fa-clock'
            },
            {
                'id': 'class',
                'name': 'Diagrama de Clases',
                'description': 'Diagrama de clases UML',
                'icon': 'fas fa-cube'
            },
            {
                'id': 'er',
                'name': 'Diagrama ER',
                'description': 'Diagrama entidad-relación',
                'icon': 'fas fa-database'
            },
            {
                'id': 'network',
                'name': 'Diagrama de Red',
                'description': 'Arquitectura de red',
                'icon': 'fas fa-network-wired'
            },
            {
                'id': 'mindmap',
                'name': 'Mapa Mental',
                'description': 'Mapa mental organizacional',
                'icon': 'fas fa-brain'
            },
            {
                'id': 'architecture',
                'name': 'Arquitectura',
                'description': 'Diagrama de arquitectura de sistemas',
                'icon': 'fas fa-building'
            }
        ]
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        return jsonify({'error': f'Error obteniendo plantillas: {str(e)}'}), 500

def get_base_diagram(diagram_type):
    """Retorna el diagrama base según el tipo"""
    base_diagrams = {
        'flowchart': {
            'nodes': [
                {'id': 'start', 'type': 'rectangle', 'text': 'Inicio', 'x': 100, 'y': 100, 'width': 100, 'height': 50},
                {'id': 'process', 'type': 'rectangle', 'text': 'Proceso', 'x': 100, 'y': 200, 'width': 100, 'height': 50},
                {'id': 'end', 'type': 'rectangle', 'text': 'Fin', 'x': 100, 'y': 300, 'width': 100, 'height': 50}
            ],
            'edges': [
                {'id': 'e1', 'from': 'start', 'to': 'process'},
                {'id': 'e2', 'from': 'process', 'to': 'end'}
            ]
        },
        'sequence': {
            'nodes': [
                {'id': 'user', 'type': 'actor', 'text': 'Usuario', 'x': 50, 'y': 100, 'width': 80, 'height': 120},
                {'id': 'system', 'type': 'rectangle', 'text': 'Sistema', 'x': 200, 'y': 100, 'width': 100, 'height': 120}
            ],
            'edges': [
                {'id': 'e1', 'from': 'user', 'to': 'system', 'text': 'Acción'}
            ]
        },
        'class': {
            'nodes': [
                {'id': 'class1', 'type': 'class', 'text': 'Clase', 'x': 100, 'y': 100, 'width': 120, 'height': 80}
            ],
            'edges': []
        },
        'er': {
            'nodes': [
                {'id': 'entity1', 'type': 'entity', 'text': 'Entidad', 'x': 100, 'y': 100, 'width': 100, 'height': 60}
            ],
            'edges': []
        },
        'network': {
            'nodes': [
                {'id': 'router', 'type': 'router', 'text': 'Router', 'x': 200, 'y': 200, 'width': 80, 'height': 60},
                {'id': 'switch', 'type': 'switch', 'text': 'Switch', 'x': 100, 'y': 100, 'width': 80, 'height': 60},
                {'id': 'pc', 'type': 'pc', 'text': 'PC', 'x': 300, 'y': 100, 'width': 60, 'height': 40}
            ],
            'edges': [
                {'id': 'e1', 'from': 'switch', 'to': 'router'},
                {'id': 'e2', 'from': 'pc', 'to': 'switch'}
            ]
        },
        'mindmap': {
            'nodes': [
                {'id': 'central', 'type': 'circle', 'text': 'Tema Central', 'x': 200, 'y': 200, 'width': 100, 'height': 100},
                {'id': 'branch1', 'type': 'rectangle', 'text': 'Rama 1', 'x': 50, 'y': 100, 'width': 80, 'height': 40},
                {'id': 'branch2', 'type': 'rectangle', 'text': 'Rama 2', 'x': 350, 'y': 100, 'width': 80, 'height': 40}
            ],
            'edges': [
                {'id': 'e1', 'from': 'central', 'to': 'branch1'},
                {'id': 'e2', 'from': 'central', 'to': 'branch2'}
            ]
        },
        'architecture': {
            'nodes': [
                {'id': 'frontend', 'type': 'rectangle', 'text': 'Frontend', 'x': 100, 'y': 100, 'width': 120, 'height': 60},
                {'id': 'backend', 'type': 'rectangle', 'text': 'Backend', 'x': 300, 'y': 100, 'width': 120, 'height': 60},
                {'id': 'database', 'type': 'entity', 'text': 'Database', 'x': 500, 'y': 100, 'width': 120, 'height': 60}
            ],
            'edges': [
                {'id': 'e1', 'from': 'frontend', 'to': 'backend'},
                {'id': 'e2', 'from': 'backend', 'to': 'database'}
            ]
        }
    }
    
    return base_diagrams.get(diagram_type, base_diagrams['flowchart'])

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if file and allowed_file(file.filename):
            # Crear nombre de archivo seguro
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                # Guardar archivo
                file.save(filepath)
                
                # Procesar documento
                processor = DocumentProcessor()
                content = processor.process_document(filepath)
                
                if content.get('type') == 'error':
                    cleanup_temp_files(filepath)
                    return jsonify({'error': content['message']}), 400
                
                # Generar diagrama
                generator = DiagramGenerator()
                diagram_result = generator.create_diagram_from_content(content)
                
                if diagram_result.get('error'):
                    cleanup_temp_files(filepath)
                    return jsonify({'error': diagram_result['error']}), 500
                
                # Limpiar archivo temporal
                cleanup_temp_files(filepath)
                
                # Asegurar que la respuesta tenga todos los campos necesarios
                response_data = {
                    'success': True,
                    'message': 'Diagrama generado exitosamente',
                    'diagram_data': diagram_result.get('diagram_data', ''),
                    'mermaid_code': diagram_result.get('mermaid_code', ''),
                    'drawio_url': diagram_result.get('drawio_url', ''),
                    'download_url': diagram_result.get('download_url', ''),
                    'title': diagram_result.get('title', 'Diagrama Generado'),
                    'type': diagram_result.get('type', 'generic')
                }
                
                return jsonify(response_data)
                
            except Exception as e:
                cleanup_temp_files(filepath)
                return jsonify({'error': f'Error procesando archivo: {str(e)}'}), 500
        
        return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/process_text', methods=['POST'])
def process_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Texto no proporcionado'}), 400
        
        text_content = data['text'].strip()
        if not text_content:
            return jsonify({'error': 'Texto vacío'}), 400
        
        # Crear contenido estructurado
        content = {
            'type': 'text',
            'content': text_content,
            'characters': len(text_content),
            'format': 'text_input'
        }
        
        # Generar diagrama
        generator = DiagramGenerator()
        diagram_result = generator.create_diagram_from_content(content)
        
        if diagram_result.get('error'):
            return jsonify({'error': diagram_result['error']}), 500
        
        # Asegurar que la respuesta tenga todos los campos necesarios
        response_data = {
            'success': True,
            'message': 'Diagrama generado exitosamente',
            'diagram_data': diagram_result.get('diagram_data', ''),
            'mermaid_code': diagram_result.get('mermaid_code', ''),
            'drawio_url': diagram_result.get('drawio_url', ''),
            'download_url': diagram_result.get('download_url', ''),
            'title': diagram_result.get('title', 'Diagrama de Texto'),
            'type': diagram_result.get('type', 'text')
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/export/<diagram_id>', methods=['POST'])
def export_diagram(diagram_id):
    """Exporta un diagrama a diferentes formatos"""
    try:
        if diagram_id not in diagrams:
            return jsonify({'error': 'Diagrama no encontrado'}), 404
        
        data = request.get_json()
        export_format = data.get('format', 'svg')
        
        diagram = diagrams[diagram_id]
        
        # Generar archivo de exportación
        filename = f"{diagram['title']}_{diagram_id}.{export_format}"
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Aquí implementarías la lógica de exportación según el formato
        # Por ahora, solo guardamos el diagrama como JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(diagram, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{filename}',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({'error': f'Error exportando diagrama: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Error descargando archivo: {str(e)}'}), 500

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Aplicación funcionando correctamente'})

if __name__ == '__main__':
    print("🚀 Iniciando Eraser.io Clone - Editor de Diagramas con IA...")
    print("📁 Directorio de uploads:", app.config['UPLOAD_FOLDER'])
    print("📁 Directorio de salidas:", app.config['OUTPUT_FOLDER'])
    print("🤖 Funcionalidad de IA habilitada")
    print("🌐 Servidor iniciado en: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
