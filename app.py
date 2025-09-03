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
        
        # Crear prompt específico para Azure si se detecta
        if 'azure' in description.lower() or 'cloud' in description.lower() or 'microsoft' in description.lower():
            return generate_azure_architecture_diagram(description)
        
        # Crear prompt para OpenAI según el tipo
        system_prompt = get_system_prompt_for_type(diagram_type)
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

def generate_azure_architecture_diagram(description):
    """Genera un diagrama de arquitectura Azure específico y detallado"""
    try:
        # Analizar la descripción para extraer componentes específicos
        description_lower = description.lower()
        
        # Detectar componentes de Azure mencionados
        components = {
            'virtual_machines': any(word in description_lower for word in ['vm', 'virtual machine', 'máquina virtual', 'servidor']),
            'app_service': any(word in description_lower for word in ['app service', 'web app', 'aplicación web', 'web service']),
            'database': any(word in description_lower for word in ['database', 'sql', 'cosmos', 'base de datos', 'db']),
            'storage': any(word in description_lower for word in ['storage', 'blob', 'file', 'almacenamiento']),
            'network': any(word in description_lower for word in ['network', 'vnet', 'red', 'subnet']),
            'security': any(word in description_lower for word in ['security', 'firewall', 'seguridad', 'waf']),
            'monitoring': any(word in description_lower for word in ['monitoring', 'log analytics', 'monitoreo', 'logs']),
            'cdn': any(word in description_lower for word in ['cdn', 'content delivery', 'distribución de contenido']),
            'load_balancer': any(word in description_lower for word in ['load balancer', 'balanceador', 'carga']),
            'api_management': any(word in description_lower for word in ['api', 'api management', 'gateway', 'puerta de enlace']),
            'hub_spoke': any(word in description_lower for word in ['hub and spoke', 'hub-spoke', 'hub & spoke', 'topología hub', 'hub spoke']),
            'multiple_subscriptions': any(word in description_lower for word in ['múltiples suscripciones', '4 suscripciones', 'varias suscripciones', 'subscriptions', 'suscripciones']),
            'enterprise': any(word in description_lower for word in ['empresarial', 'enterprise', 'corporativo', 'corporation'])
        }
        
        # Si se detecta hub and spoke o múltiples suscripciones, generar topología compleja
        if components['hub_spoke'] or components['multiple_subscriptions'] or components['enterprise']:
            return generate_hub_spoke_architecture(description, components)
        
        # Crear diagrama de Azure con componentes detectados
        azure_diagram = create_azure_diagram_structure(components, description)
        
        return {
            'success': True,
            'type': 'azure_architecture',
            'data': azure_diagram
        }
        
    except Exception as e:
        print(f"Error generando diagrama Azure: {str(e)}")
        return generate_fallback_diagram(description, 'azure_architecture')

def generate_hub_spoke_architecture(description, components):
    """Genera una topología hub and spoke con múltiples suscripciones"""
    try:
        # Determinar número de suscripciones
        num_subscriptions = 4  # Por defecto
        if '4' in description:
            num_subscriptions = 4
        elif '3' in description:
            num_subscriptions = 3
        elif '5' in description:
            num_subscriptions = 5
        
        print(f"🏗️ Generando topología Hub and Spoke con {num_subscriptions} suscripciones...")
        
        # Crear diagrama hub and spoke
        hub_spoke_diagram = create_hub_spoke_structure(num_subscriptions, components)
        
        return {
            'success': True,
            'type': 'azure_hub_spoke',
            'data': hub_spoke_diagram
        }
        
    except Exception as e:
        print(f"Error generando hub and spoke: {str(e)}")
        return generate_fallback_diagram(description, 'azure_architecture')

def create_hub_spoke_structure(num_subscriptions, components):
    """Crea la estructura hub and spoke con múltiples suscripciones"""
    
    # Posiciones base para organizar el diagrama
    positions = {
        'internet': {'x': 500, 'y': 50, 'width': 120, 'height': 60},
        'hub_vnet': {'x': 400, 'y': 150, 'width': 300, 'height': 200},
        'hub_firewall': {'x': 500, 'y': 200, 'width': 120, 'height': 60},
        'hub_bastion': {'x': 400, 'y': 250, 'width': 120, 'height': 60},
        'hub_vpn': {'x': 600, 'y': 250, 'width': 120, 'height': 60},
        'hub_express_route': {'x': 500, 'y': 320, 'width': 120, 'height': 60},
        'hub_monitoring': {'x': 400, 'y': 400, 'width': 120, 'height': 60},
        'hub_key_vault': {'x': 600, 'y': 400, 'width': 120, 'height': 60},
        'hub_shared_services': {'x': 500, 'y': 480, 'width': 120, 'height': 60}
    }
    
    nodes = []
    edges = []
    node_id = 1
    
    # Agregar nodos del hub
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'internet',
        'text': 'Internet',
        'x': positions['internet']['x'],
        'y': positions['internet']['y'],
        'width': positions['internet']['width'],
        'height': positions['internet']['height']
    })
    internet_id = f'node_{node_id}'
    node_id += 1
    
    # Hub VNet
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'azure_vnet',
        'text': 'Hub VNet\n10.0.0.0/16\nSuscripción Hub',
        'x': positions['hub_vnet']['x'],
        'y': positions['hub_vnet']['y'],
        'width': positions['hub_vnet']['width'],
        'height': positions['hub_vnet']['height']
    })
    hub_vnet_id = f'node_{node_id}'
    node_id += 1
    
    # Hub Firewall
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'azure_firewall',
        'text': 'Azure Firewall\nHub',
        'x': positions['hub_firewall']['x'],
        'y': positions['hub_firewall']['y'],
        'width': positions['hub_firewall']['width'],
        'height': positions['hub_firewall']['height']
    })
    hub_firewall_id = f'node_{node_id}'
    node_id += 1
    
    # Hub Bastion
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'azure_bastion',
        'text': 'Bastion Host\nHub',
        'x': positions['hub_bastion']['x'],
        'y': positions['hub_bastion']['y'],
        'width': positions['hub_bastion']['width'],
        'height': positions['hub_bastion']['height']
    })
    hub_bastion_id = f'node_{node_id}'
    node_id += 1
    
    # Hub VPN Gateway
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'azure_vpn_gateway',
        'text': 'VPN Gateway\nHub',
        'x': positions['hub_vpn']['x'],
        'y': positions['hub_vpn']['y'],
        'width': positions['hub_vpn']['width'],
        'height': positions['hub_vpn']['height']
    })
    hub_vpn_id = f'node_{node_id}'
    node_id += 1
    
    # Hub Express Route
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'azure_express_route',
        'text': 'Express Route\nHub',
        'x': positions['hub_express_route']['x'],
        'y': positions['hub_express_route']['y'],
        'width': positions['hub_express_route']['width'],
        'height': positions['hub_express_route']['height']
    })
    hub_express_id = f'node_{node_id}'
    node_id += 1
    
    # Hub Monitoring
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'azure_monitoring',
        'text': 'Log Analytics\nHub',
        'x': positions['hub_monitoring']['x'],
        'y': positions['hub_monitoring']['y'],
        'width': positions['hub_monitoring']['width'],
        'height': positions['hub_monitoring']['height']
    })
    hub_monitoring_id = f'node_{node_id}'
    node_id += 1
    
    # Hub Key Vault
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'azure_key_vault',
        'text': 'Key Vault\nHub',
        'x': positions['hub_key_vault']['x'],
        'y': positions['hub_key_vault']['y'],
        'width': positions['hub_key_vault']['width'],
        'height': positions['hub_key_vault']['height']
    })
    hub_key_vault_id = f'node_{node_id}'
    node_id += 1
    
    # Hub Shared Services
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'azure_shared_services',
        'text': 'Shared Services\nHub',
        'x': positions['hub_shared_services']['x'],
        'y': positions['hub_shared_services']['y'],
        'width': positions['hub_shared_services']['width'],
        'height': positions['hub_shared_services']['height']
    })
    hub_shared_id = f'node_{node_id}'
    node_id += 1
    
    # Conectar Internet al Hub
    edges.append({
        'id': f'edge_{len(edges)}',
        'from': internet_id,
        'to': hub_firewall_id
    })
    
    # Conectar componentes del Hub
    edges.extend([
        {'id': f'edge_{len(edges)}', 'from': hub_vnet_id, 'to': hub_firewall_id},
        {'id': f'edge_{len(edges)}', 'from': hub_vnet_id, 'to': hub_bastion_id},
        {'id': f'edge_{len(edges)}', 'from': hub_vnet_id, 'to': hub_vpn_id},
        {'id': f'edge_{len(edges)}', 'from': hub_vnet_id, 'to': hub_express_id},
        {'id': f'edge_{len(edges)}', 'from': hub_vnet_id, 'to': hub_monitoring_id},
        {'id': f'edge_{len(edges)}', 'from': hub_vnet_id, 'to': hub_key_vault_id},
        {'id': f'edge_{len(edges)}', 'from': hub_vnet_id, 'to': hub_shared_id}
    ])
    
    # Generar nodos de spoke para cada suscripción
    spoke_spacing = 800 // (num_subscriptions + 1)
    for i in range(num_subscriptions):
        spoke_x = 100 + (i + 1) * spoke_spacing
        spoke_y = 600
        
        # Spoke VNet
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_vnet',
            'text': f'Spoke VNet {i+1}\n10.{i+1}.0.0/16\nSuscripción {i+1}',
            'x': spoke_x - 100,
            'y': spoke_y,
            'width': 200,
            'height': 150
        })
        spoke_vnet_id = f'node_{node_id}'
        node_id += 1
        
        # Spoke App Service
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_app_service',
            'text': f'App Service\nSpoke {i+1}',
            'x': spoke_x - 70,
            'y': spoke_y + 170,
            'width': 140,
            'height': 70
        })
        spoke_app_id = f'node_{node_id}'
        node_id += 1
        
        # Spoke SQL Database
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_sql',
            'text': f'SQL Database\nSpoke {i+1}',
            'x': spoke_x + 30,
            'y': spoke_y + 170,
            'width': 140,
            'height': 70
        })
        spoke_sql_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar Spoke al Hub
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': hub_vnet_id,
            'to': spoke_vnet_id
        })
        
        # Conectar componentes del Spoke
        edges.extend([
            {'id': f'edge_{len(edges)}', 'from': spoke_vnet_id, 'to': spoke_app_id},
            {'id': f'edge_{len(edges)}', 'from': spoke_vnet_id, 'to': spoke_sql_id},
            {'id': f'edge_{len(edges)}', 'from': spoke_app_id, 'to': spoke_sql_id}
        ])
    
    # Agregar título del diagrama
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'diagram_title',
        'text': f'Topología Hub and Spoke\n{num_subscriptions} Suscripciones Azure',
        'x': 400,
        'y': 20,
        'width': 400,
        'height': 40
    })
    
    return {
        'type': 'azure_hub_spoke',
        'nodes': nodes,
        'edges': edges
    }

def create_azure_diagram_structure(components, description):
    """Crea la estructura del diagrama de Azure basado en los componentes detectados"""
    
    # Posiciones base para organizar el diagrama
    positions = {
        'internet': {'x': 400, 'y': 50, 'width': 120, 'height': 60},
        'cdn': {'x': 200, 'y': 50, 'width': 120, 'height': 60},
        'firewall': {'x': 400, 'y': 150, 'width': 120, 'height': 60},
        'load_balancer': {'x': 400, 'y': 250, 'width': 120, 'height': 60},
        'app_gateway': {'x': 400, 'y': 350, 'width': 120, 'height': 60},
        'vnet': {'x': 200, 'y': 200, 'width': 600, 'height': 400},
        'subnet_frontend': {'x': 250, 'y': 250, 'width': 200, 'height': 100},
        'subnet_backend': {'x': 500, 'y': 250, 'width': 200, 'height': 100},
        'subnet_data': {'x': 350, 'y': 400, 'width': 200, 'height': 100},
        'app_service': {'x': 280, 'y': 280, 'width': 140, 'height': 70},
        'web_app': {'x': 280, 'y': 360, 'width': 140, 'height': 70},
        'api_app': {'x': 530, 'y': 280, 'width': 140, 'height': 70},
        'function_app': {'x': 530, 'y': 360, 'width': 140, 'height': 70},
        'sql_database': {'x': 380, 'y': 420, 'width': 140, 'height': 70},
        'storage_account': {'x': 380, 'y': 500, 'width': 140, 'height': 70},
        'key_vault': {'x': 600, 'y': 420, 'width': 140, 'height': 70},
        'monitoring': {'x': 600, 'y': 500, 'width': 140, 'height': 70},
        'on_premises': {'x': 50, 'y': 300, 'width': 120, 'height': 60},
        'vpn_gateway': {'x': 150, 'y': 300, 'width': 80, 'height': 60}
    }
    
    nodes = []
    edges = []
    node_id = 1
    
    # Agregar nodos según los componentes detectados
    if components['cdn']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_cdn',
            'text': 'Azure CDN',
            'x': positions['cdn']['x'],
            'y': positions['cdn']['y'],
            'width': positions['cdn']['width'],
            'height': positions['cdn']['height']
        })
        node_id += 1
    
    # Internet siempre está presente
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'internet',
        'text': 'Internet',
        'x': positions['internet']['x'],
        'y': positions['internet']['y'],
        'width': positions['internet']['width'],
        'height': positions['internet']['height']
    })
    internet_id = f'node_{node_id}'
    node_id += 1
    
    # Firewall/WAF
    if components['security']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_firewall',
            'text': 'Azure Firewall\nWAF',
            'x': positions['firewall']['x'],
            'y': positions['firewall']['y'],
            'width': positions['firewall']['width'],
            'height': positions['firewall']['height']
        })
        firewall_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar internet al firewall
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': internet_id,
            'to': firewall_id
        })
    
    # Load Balancer
    if components['load_balancer']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_load_balancer',
            'text': 'Load Balancer',
            'x': positions['load_balancer']['x'],
            'y': positions['load_balancer']['y'],
            'width': positions['load_balancer']['width'],
            'height': positions['load_balancer']['height']
        })
        lb_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar al firewall o internet
        if components['security']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': firewall_id,
                'to': lb_id
            })
        else:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': internet_id,
                'to': lb_id
            })
    
    # Virtual Network
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'azure_vnet',
        'text': 'Virtual Network\n10.0.0.0/16',
        'x': positions['vnet']['x'],
        'y': positions['vnet']['y'],
        'width': positions['vnet']['width'],
        'height': positions['vnet']['height']
    })
    vnet_id = f'node_{node_id}'
    node_id += 1
    
    # Subnets
    if components['network']:
        # Frontend subnet
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_subnet',
            'text': 'Frontend Subnet\n10.0.1.0/24',
            'x': positions['subnet_frontend']['x'],
            'y': positions['subnet_frontend']['y'],
            'width': positions['subnet_frontend']['width'],
            'height': positions['subnet_frontend']['height']
        })
        frontend_subnet_id = f'node_{node_id}'
        node_id += 1
        
        # Backend subnet
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_subnet',
            'text': 'Backend Subnet\n10.0.2.0/24',
            'x': positions['subnet_backend']['x'],
            'y': positions['subnet_backend']['y'],
            'width': positions['subnet_backend']['width'],
            'height': positions['subnet_backend']['height']
        })
        backend_subnet_id = f'node_{node_id}'
        node_id += 1
        
        # Data subnet
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_subnet',
            'text': 'Data Subnet\n10.0.3.0/24',
            'x': positions['subnet_data']['x'],
            'y': positions['subnet_data']['y'],
            'width': positions['subnet_data']['width'],
            'height': positions['subnet_data']['height']
        })
        data_subnet_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar subnets al VNet
        edges.extend([
            {'id': f'edge_{len(edges)}', 'from': vnet_id, 'to': frontend_subnet_id},
            {'id': f'edge_{len(edges)}', 'from': vnet_id, 'to': backend_subnet_id},
            {'id': f'edge_{len(edges)}', 'from': vnet_id, 'to': data_subnet_id}
        ])
    
    # App Services
    if components['app_service']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_app_service',
            'text': 'App Service\nWeb App',
            'x': positions['app_service']['x'],
            'y': positions['app_service']['y'],
            'width': positions['app_service']['width'],
            'height': positions['app_service']['height']
        })
        app_service_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar al subnet frontend
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': frontend_subnet_id,
                'to': app_service_id
            })
    
    # Web Apps adicionales
    if components['app_service']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_web_app',
            'text': 'Web App\nAPI',
            'x': positions['web_app']['x'],
            'y': positions['web_app']['y'],
            'width': positions['web_app']['width'],
            'height': positions['web_app']['height']
        })
        web_app_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar al subnet frontend
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': frontend_subnet_id,
                'to': web_app_id
            })
    
    # API Apps
    if components['api_management']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_api_app',
            'text': 'API App\nBackend',
            'x': positions['api_app']['x'],
            'y': positions['api_app']['y'],
            'width': positions['api_app']['width'],
            'height': positions['api_app']['height']
        })
        api_app_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar al subnet backend
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': backend_subnet_id,
                'to': api_app_id
            })
    
    # Function Apps
    if components['api_management']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_function',
            'text': 'Function App\nServerless',
            'x': positions['function_app']['x'],
            'y': positions['function_app']['y'],
            'width': positions['function_app']['width'],
            'height': positions['function_app']['height']
        })
        function_app_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar al subnet backend
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': backend_subnet_id,
                'to': function_app_id
            })
    
    # SQL Database
    if components['database']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_sql',
            'text': 'Azure SQL\nDatabase',
            'x': positions['sql_database']['x'],
            'y': positions['sql_database']['y'],
            'width': positions['sql_database']['width'],
            'height': positions['sql_database']['height']
        })
        sql_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar al subnet data
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': data_subnet_id,
                'to': sql_id
            })
    
    # Storage Account
    if components['storage']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_storage',
            'text': 'Storage Account\nBlob & File',
            'x': positions['storage_account']['x'],
            'y': positions['storage_account']['y'],
            'width': positions['storage_account']['width'],
            'height': positions['storage_account']['height']
        })
        storage_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar al subnet data
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': data_subnet_id,
                'to': storage_id
            })
    
    # Key Vault
    if components['security']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_key_vault',
            'text': 'Key Vault\nSecrets',
            'x': positions['key_vault']['x'],
            'y': positions['key_vault']['y'],
            'width': positions['key_vault']['width'],
            'height': positions['key_vault']['height']
        })
        key_vault_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar al subnet data
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': data_subnet_id,
                'to': key_vault_id
            })
    
    # Monitoring
    if components['monitoring']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_monitoring',
            'text': 'Log Analytics\nMonitoring',
            'x': positions['monitoring']['x'],
            'y': positions['monitoring']['y'],
            'width': positions['monitoring']['width'],
            'height': positions['monitoring']['height']
        })
        monitoring_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar al subnet data
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': data_subnet_id,
                'to': monitoring_id
            })
    
    # On-Premises connection
    if 'on-premises' in description.lower() or 'local' in description.lower():
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'on_premises',
            'text': 'On-Premises\nNetwork',
            'x': positions['on_premises']['x'],
            'y': positions['on_premises']['y'],
            'width': positions['on_premises']['width'],
            'height': positions['on_premises']['height']
        })
        onprem_id = f'node_{node_id}'
        node_id += 1
        
        # VPN Gateway
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_vpn_gateway',
            'text': 'VPN Gateway',
            'x': positions['vpn_gateway']['x'],
            'y': positions['vpn_gateway']['y'],
            'width': positions['vpn_gateway']['width'],
            'height': positions['vpn_gateway']['height']
        })
        vpn_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar on-premises al VPN
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': onprem_id,
            'to': vpn_id
        })
        
        # Conectar VPN al VNet
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': vpn_id,
            'to': vnet_id
        })
    
    # Conectar componentes principales
    if components['load_balancer'] and components['app_service']:
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': lb_id,
            'to': app_service_id
        })
    
    if components['app_service'] and components['database']:
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': app_service_id,
            'to': sql_id
        })
    
    if components['app_service'] and components['storage']:
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': app_service_id,
            'to': storage_id
        })
    
    return {
        'type': 'azure_architecture',
        'nodes': nodes,
        'edges': edges
    }

def get_system_prompt_for_type(diagram_type):
    """Retorna el prompt del sistema según el tipo de diagrama"""
    base_prompts = {
        'flowchart': """Eres un experto en diagramas de flujo. 
        Genera un diagrama de flujo lógico y bien estructurado con la siguiente estructura JSON:
        {
            "type": "flowchart",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "start|process|decision|end",
                    "text": "texto descriptivo",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 120,
                    "height": 60
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "texto de la conexión (opcional)"
                }
            ]
        }
        
        Usa tipos de nodos apropiados:
        - start: para el inicio del proceso
        - process: para pasos o acciones
        - decision: para decisiones o condiciones
        - end: para el final del proceso
        
        Organiza los nodos en un flujo lógico de arriba hacia abajo o de izquierda a derecha.""",
        
        'sequence': """Eres un experto en diagramas de secuencia UML.
        Genera un diagrama de secuencia con la siguiente estructura JSON:
        {
            "type": "sequence",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "actor|system|database|external",
                    "text": "nombre del componente",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 100,
                    "height": 120
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "acción o mensaje"
                }
            ]
        }
        
        Usa tipos de nodos apropiados:
        - actor: para usuarios o sistemas externos
        - system: para componentes del sistema
        - database: para bases de datos
        - external: para servicios externos""",
        
        'class': """Eres un experto en diagramas de clases UML.
        Genera un diagrama de clases con la siguiente estructura JSON:
        {
            "type": "class",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "class|interface|abstract",
                    "text": "NombreClase\\n+atributo1: tipo\\n+atributo2: tipo\\n\\n+metodo1()\\n+metodo2()",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 150,
                    "height": 100
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "herencia|implementa|asociación"
                }
            ]
        }
        
        Usa tipos de nodos apropiados:
        - class: para clases regulares
        - interface: para interfaces
        - abstract: para clases abstractas""",
        
        'er': """Eres un experto en diagramas entidad-relación.
        Genera un diagrama ER con la siguiente estructura JSON:
        {
            "type": "er",
            "nodes": [
                {
                    "id": "unique_id",
                    "type": "entity|relationship|attribute",
                    "text": "NombreEntidad\\n+atributo1\\n+atributo2\\n+atributo3",
                    "x": posicion_x,
                    "y": posicion_y,
                    "width": 140,
                    "height": 80
                }
            ],
            "edges": [
                {
                    "id": "edge_id",
                    "from": "id_nodo_origen",
                    "to": "id_nodo_destino",
                    "text": "1:N|N:M|1:1"
                }
            ]
        }
        
        Usa tipos de nodos apropiados:
        - entity: para entidades principales
        - relationship: para relaciones
        - attribute: para atributos clave"""
    }
    
    return base_prompts.get(diagram_type, base_prompts['flowchart'])

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
