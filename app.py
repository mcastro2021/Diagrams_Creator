from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import json
import base64
import requests
from werkzeug.utils import secure_filename
import tempfile
import shutil
import time
from document_processor import DocumentProcessor
from diagram_generator import DiagramGenerator

app = Flask(__name__)
CORS(app)

# Configuración
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Crear directorios si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'csv', 'json'}

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
            'drawio_url': diagram_result.get('drawio_url', ''),
            'download_url': diagram_result.get('download_url', ''),
            'title': diagram_result.get('title', 'Diagrama de Texto'),
            'type': diagram_result.get('type', 'text')
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

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
    print("🚀 Iniciando Conversor de Documentos a Diagramas...")
    print("📁 Directorio de uploads:", app.config['UPLOAD_FOLDER'])
    print("📁 Directorio de salidas:", app.config['OUTPUT_FOLDER'])
    print("🌐 Servidor iniciado en: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
