#!/usr/bin/env python3
"""
Diagrams Creator - Aplicación para generar diagramas de arquitectura con IA
Autor: Manuel
Fecha: 2025
"""

import os
import json
import uuid
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import openai
from dotenv import load_dotenv

# Importar módulos personalizados
from libs_handler import LibsHandler
from diagram_generator import DiagramGenerator
from ai_processor import AIProcessor
from config import Config

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
app.config.from_object(Config)

# Configurar para producción
if os.environ.get('RENDER'):
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'render-production-key-2025')
    app.config['DEBUG'] = False
    # Configurar para servir archivos estáticos en producción
    from whitenoise import WhiteNoise
    app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/')

CORS(app)

# Inicializar componentes
libs_handler = LibsHandler()
diagram_generator = DiagramGenerator(libs_handler)
ai_processor = AIProcessor()

@app.route('/')
def index():
    """Página principal de la aplicación"""
    return render_template('index.html')


@app.route('/api/library-icons/<library_name>')
def get_library_icons(library_name):
    """Endpoint para obtener la lista de nombres de iconos en una librería"""
    try:
        from urllib.parse import unquote
        decoded_library_name = unquote(library_name)
        
        library = libs_handler.get_library(decoded_library_name)
        if not library or not library.get('icons'):
            return jsonify({'error': 'Library not found'}), 404
        
        # Extraer solo los nombres de los iconos
        icon_names = [icon.get('name', 'Unknown') for icon in library['icons'] if icon.get('name')]
        
        return jsonify({
            'library': decoded_library_name,
            'count': len(icon_names),
            'icons': sorted(icon_names)  # Ordenar alfabéticamente
        })
        
    except Exception as e:
        logger.error(f"Error getting icons for library {library_name}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health')
def health_check():
    """Endpoint para verificar la salud de la aplicación"""
    # Verificar directorios
    upload_folder_exists = os.path.exists(app.config['UPLOAD_FOLDER'])
    libs_folder_exists = os.path.exists(app.config['LIBS_FOLDER'])
    
    # Contar archivos
    diagram_count = 0
    if upload_folder_exists:
        diagram_count = len([f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.xml')])
    
    library_count = len(libs_handler.libraries_cache)
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'ai_provider': ai_processor.active_provider,
        'directories': {
            'upload_folder': upload_folder_exists,
            'libs_folder': libs_folder_exists
        },
        'counts': {
            'diagrams': diagram_count,
            'libraries': library_count
        }
    })

@app.route('/api/icon/<library_name>/<icon_name>')
def get_icon(library_name, icon_name):
    """Endpoint para servir iconos específicos"""
    try:
        # Decodificar URL encoding
        from urllib.parse import unquote
        decoded_library_name = unquote(library_name)
        decoded_icon_name = unquote(icon_name)
        
        logger.info(f"Buscando icono: {decoded_icon_name} en librería: {decoded_library_name}")
        
        # Buscar el icono en las librerías
        library = libs_handler.get_library(decoded_library_name)
        if not library or not library.get('icons'):
            logger.error(f"Librería no encontrada: {decoded_library_name}")
            return jsonify({'error': 'Library not found'}), 404
        
        # Buscar el icono específico
        for icon in library['icons']:
            if icon.get('name') == decoded_icon_name:
                # Si tiene data URI, devolverlo directamente
                if icon.get('data') and icon.get('data').startswith('data:'):
                    # Extraer el tipo de contenido y los datos
                    header, data = icon['data'].split(',', 1)
                    content_type = header.split(';')[0].split(':')[1]
                    
                    # Decodificar base64
                    import base64
                    icon_data = base64.b64decode(data)
                    
                    from flask import Response
                    return Response(
                        icon_data,
                        mimetype=content_type,
                        headers={
                            'Cache-Control': 'public, max-age=3600',
                            'Content-Disposition': f'inline; filename="{icon_name}"'
                        }
                    )
                
                # Si tiene XML, convertirlo a SVG
                elif icon.get('xml'):
                    svg_content = icon['xml']
                    if not svg_content.startswith('<?xml'):
                        svg_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{svg_content}'
                    
                    from flask import Response
                    return Response(
                        svg_content,
                        mimetype='image/svg+xml',
                        headers={
                            'Cache-Control': 'public, max-age=3600',
                            'Content-Disposition': f'inline; filename="{icon_name}.svg"'
                        }
                    )
        
        return jsonify({'error': 'Icon not found'}), 404
        
    except Exception as e:
        logger.error(f"Error serving icon {decoded_library_name}/{decoded_icon_name}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/icon-preview/<library_name>/<icon_name>')
def get_icon_preview(library_name, icon_name):
    """Endpoint para obtener preview de iconos en formato JSON"""
    try:
        # Decodificar URL encoding
        from urllib.parse import unquote
        decoded_library_name = unquote(library_name)
        decoded_icon_name = unquote(icon_name)
        
        library = libs_handler.get_library(decoded_library_name)
        if not library or not library.get('icons'):
            return jsonify({'error': 'Library not found'}), 404
        
        for icon in library['icons']:
            if icon.get('name') == decoded_icon_name:
                return jsonify({
                    'name': icon.get('name'),
                    'library': library_name,
                    'data': icon.get('data'),
                    'xml': icon.get('xml'),
                    'preview_url': f'/api/icon/{library_name}/{icon_name}'
                })
        
        return jsonify({'error': 'Icon not found'}), 404
        
    except Exception as e:
        logger.error(f"Error getting icon preview {decoded_library_name}/{decoded_icon_name}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/export/<diagram_id>/<format>')
def export_diagram(diagram_id, format):
    """Exportar diagrama en diferentes formatos"""
    try:
        # Validar formato
        valid_formats = ['xml', 'svg', 'png', 'pdf']
        if format not in valid_formats:
            return jsonify({'error': f'Formato no válido. Formatos disponibles: {", ".join(valid_formats)}'}), 400
        
        # Buscar el diagrama
        diagram_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{diagram_id}.xml')
        if not os.path.exists(diagram_path):
            return jsonify({'error': 'Diagrama no encontrado'}), 404
        
        # Leer el XML del diagrama
        with open(diagram_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        if format == 'xml':
            # Devolver XML directamente
            return Response(
                xml_content,
                mimetype='application/xml',
                headers={
                    'Content-Disposition': f'attachment; filename="diagram_{diagram_id}.xml"'
                }
            )
        
        elif format == 'svg':
            # Convertir a SVG (implementación básica)
            # En una implementación real, usarías una librería como drawio-tools
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" viewBox="0 0 800 600">
    <rect width="800" height="600" fill="white"/>
    <text x="400" y="300" text-anchor="middle" font-family="Arial" font-size="16" fill="black">
        Diagrama exportado como SVG
    </text>
    <text x="400" y="330" text-anchor="middle" font-family="Arial" font-size="12" fill="gray">
        ID: {diagram_id}
    </text>
</svg>'''
            
            return Response(
                svg_content,
                mimetype='image/svg+xml',
                headers={
                    'Content-Disposition': f'attachment; filename="diagram_{diagram_id}.svg"'
                }
            )
        
        elif format == 'png':
            # Para PNG, necesitarías una librería como Pillow o cairosvg
            # Por ahora, devolvemos un mensaje
            return jsonify({
                'message': 'Exportación PNG no implementada aún',
                'suggestion': 'Usa el formato XML y ábrelo en Draw.io para exportar a PNG'
            }), 501
        
        elif format == 'pdf':
            # Para PDF, necesitarías una librería como reportlab
            # Por ahora, devolvemos un mensaje
            return jsonify({
                'message': 'Exportación PDF no implementada aún',
                'suggestion': 'Usa el formato XML y ábrelo en Draw.io para exportar a PDF'
            }), 501
        
    except Exception as e:
        logger.error(f"Error exporting diagram {diagram_id} as {format}: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/diagrams')
def list_diagrams():
    """Listar diagramas disponibles"""
    try:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            return jsonify({
                'success': True,
                'diagrams': []
            })
        
        diagrams = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith('diagram_') and filename.endswith('.xml'):
                diagram_id = filename.replace('diagram_', '').replace('.xml', '')
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_stats = os.stat(file_path)
                
                diagrams.append({
                    'id': diagram_id,
                    'filename': filename,
                    'created': datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                    'size': file_stats.st_size
                })
        
        # Ordenar por fecha de creación (más recientes primero)
        diagrams.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'success': True,
            'diagrams': diagrams
        })
        
    except Exception as e:
        logger.error(f"Error listing diagrams: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/diagrams-debug')
def diagrams_debug():
    """Debug: listar todos los diagramas disponibles con detalles"""
    try:
        diagrams = []
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                if filename.endswith('.xml') and filename.startswith('diagram_'):
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    stat = os.stat(file_path)
                    
                    # Extraer ID del nombre del archivo
                    diagram_id = filename.replace('diagram_', '').replace('.xml', '')
                    
                    # Leer primer línea del archivo para verificar contenido
                    content_preview = "Error reading file"
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content_preview = f.read(100) + "..." if len(f.read()) > 100 else f.read()
                    except:
                        pass
                    
                    diagrams.append({
                        'id': diagram_id,
                        'filename': filename,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'url': f'/api/diagram/{diagram_id}',
                        'direct_url': f'{request.url_root}api/diagram/{diagram_id}',
                        'content_preview': content_preview[:100]
                    })
        
        diagrams.sort(key=lambda x: x['modified'], reverse=True)  # Más recientes primero
        
        return jsonify({
            'success': True,
            'count': len(diagrams),
            'diagrams': diagrams,
            'folder_path': app.config['UPLOAD_FOLDER']
        })
        
    except Exception as e:
        logger.error(f"Error in diagrams debug: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/libraries')
def get_libraries():
    """Obtener todas las librerías de iconos disponibles"""
    try:
        libraries = libs_handler.get_available_libraries()
        return jsonify({
            'success': True,
            'libraries': libraries
        })
    except Exception as e:
        logger.error(f"Error getting libraries: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/icons/<library>')
def get_icons(library):
    """Obtener iconos de una librería específica"""
    try:
        icons = libs_handler.get_library_icons(library)
        return jsonify({
            'success': True,
            'library': library,
            'icons': icons
        })
    except Exception as e:
        logger.error(f"Error getting icons for library {library}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-diagram', methods=['POST'])
def generate_diagram():
    """Generar diagrama basado en texto de entrada"""
    try:
        data = request.get_json()
        
        if not data or 'input_text' not in data:
            return jsonify({
                'success': False,
                'error': 'Se requiere input_text'
            }), 400
        
        input_text = data['input_text']
        diagram_type = data.get('diagram_type', 'auto')
        style = data.get('style', 'modern')
        
        logger.info(f"Generating diagram for input: {input_text[:100]}...")
        
        # Procesar texto con IA
        analysis = ai_processor.analyze_architecture(input_text, diagram_type)
        
        # Generar diagrama
        diagram_data = diagram_generator.generate_diagram(analysis, style)
        
        # Guardar diagrama
        diagram_id = str(uuid.uuid4())
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], f'diagram_{diagram_id}.xml')
        
        # Crear directorio si no existe
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        logger.info(f"💾 Saving diagram to: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(diagram_data['xml'])
        
        # Verificar que el archivo se guardó correctamente
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            logger.info(f"✅ Diagrama guardado exitosamente: {output_file} ({file_size} bytes)")
        else:
            logger.error(f"❌ ERROR: Archivo no se guardó: {output_file}")
        
        # Listar archivos en el directorio para debug
        try:
            files_in_dir = os.listdir(app.config['UPLOAD_FOLDER'])
            xml_files = [f for f in files_in_dir if f.endswith('.xml')]
            logger.info(f"📁 Total archivos XML en directorio: {len(xml_files)}")
            logger.info(f"📋 Archivos XML: {xml_files}")
        except Exception as list_error:
            logger.error(f"❌ Error listando directorio: {list_error}")
        
        return jsonify({
            'success': True,
            'diagram_id': diagram_id,
            'analysis': analysis,
            'diagram_url': f'/api/diagram/{diagram_id}',
            'components': diagram_data.get('components', []),
            'connections': diagram_data.get('connections', [])
        })
        
    except Exception as e:
        logger.error(f"Error generating diagram: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload-document', methods=['POST'])
def upload_document():
    """Subir y procesar documento para generar diagrama"""
    try:
        logger.info("Upload document endpoint called")
        
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({
                'success': False,
                'error': 'No se encontró archivo en la petición'
            }), 400
        
        file = request.files['file']
        logger.info(f"File received: {file.filename}")
        
        if file.filename == '' or file.filename is None:
            logger.error("Empty filename")
            return jsonify({
                'success': False,
                'error': 'No se seleccionó archivo válido'
            }), 400
        
        if not allowed_file(file.filename):
            logger.error(f"File type not allowed: {file.filename}")
            return jsonify({
                'success': False,
                'error': f'Tipo de archivo no permitido. Formatos soportados: {", ".join(app.config["ALLOWED_EXTENSIONS"])}'
            }), 400
        
        # Verificar tamaño del archivo
        file.seek(0, 2)  # Ir al final del archivo
        file_size = file.tell()
        file.seek(0)  # Volver al inicio
        
        if file_size > app.config['MAX_CONTENT_LENGTH']:
            logger.error(f"File too large: {file_size} bytes")
            return jsonify({
                'success': False,
                'error': f'Archivo demasiado grande. Máximo: {app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB'
            }), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        logger.info(f"Saving file to: {filepath}")
        file.save(filepath)
        
        if not os.path.exists(filepath):
            logger.error(f"Failed to save file: {filepath}")
            return jsonify({
                'success': False,
                'error': 'Error guardando archivo'
            }), 500
        
        # Procesar documento
        logger.info(f"Extracting text from: {filepath}")
        extracted_text = ai_processor.extract_text_from_document(filepath)
        
        if not extracted_text.strip():
            logger.warning("No text extracted from document")
            extracted_text = "No se pudo extraer texto del documento"
        
        # Analizar con IA
        diagram_type = request.form.get('diagram_type', 'auto')
        analysis = ai_processor.analyze_architecture(extracted_text, diagram_type)
        
        # Generar diagrama
        style = request.form.get('style', 'modern')
        diagram_data = diagram_generator.generate_diagram(analysis, style)
        
        # Guardar diagrama
        diagram_id = str(uuid.uuid4())
        output_file = os.path.join(app.config['UPLOAD_FOLDER'], f'diagram_{diagram_id}.xml')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(diagram_data['xml'])
        
        # Limpiar archivo temporal
        try:
            os.remove(filepath)
        except:
            pass
        
        logger.info(f"Document processed successfully. Diagram ID: {diagram_id}")
        
        return jsonify({
            'success': True,
            'diagram_id': diagram_id,
            'analysis': analysis,
            'diagram_url': f'/api/diagram/{diagram_id}',
            'extracted_text': extracted_text[:500] + '...' if len(extracted_text) > 500 else extracted_text,
            'file_info': {
                'filename': filename,
                'size': file_size
            }
        })
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/diagram/<diagram_id>')
def get_diagram(diagram_id):
    """Obtener diagrama generado"""
    try:
        logger.info(f"Requested diagram: {diagram_id}")
        
        # Validar diagram_id para evitar ataques de path traversal
        if not diagram_id.replace('-', '').replace('_', '').isalnum():
            logger.error(f"Invalid diagram ID: {diagram_id}")
            return jsonify({
                'success': False,
                'error': 'ID de diagrama inválido'
            }), 400
        
        diagram_file = os.path.join(app.config['UPLOAD_FOLDER'], f'diagram_{diagram_id}.xml')
        logger.info(f"Looking for file: {diagram_file}")
        
        if not os.path.exists(diagram_file):
            logger.error(f"Diagram file not found: {diagram_file}")
            
            # Listar archivos disponibles para debug
            available_files = []
            if os.path.exists(app.config['UPLOAD_FOLDER']):
                available_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.xml')]
            
            logger.info(f"Available diagrams: {available_files}")
            
            return jsonify({
                'success': False,
                'error': f'Diagrama no encontrado: {diagram_id}',
                'available_diagrams': available_files
            }), 404
        
        logger.info(f"Serving diagram file: {diagram_file}")
        
        # Crear respuesta con headers CORS apropiados
        from flask import Response
        
        with open(diagram_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        response = Response(
            xml_content,
            mimetype='application/xml',
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Cache-Control': 'no-cache'
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting diagram {diagram_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def allowed_file(filename):
    """Verificar si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500

if __name__ == '__main__':
    # Crear directorios necesarios
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
