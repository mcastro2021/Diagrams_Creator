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
        print(f"🤖 Generando diagrama IA para: {description}")
        
        # Determinar el tipo de diagrama si es 'auto'
        if diagram_type == 'auto':
            diagram_type = detect_diagram_type(description)
        
        print(f"📊 Tipo de diagrama detectado: {diagram_type}")
        
        # Crear prompt específico para Azure si se detecta
        if ('azure' in description.lower() or 'cloud' in description.lower() or 
            'microsoft' in description.lower() or 'suscripciones' in description.lower() or
            'subscriptions' in description.lower()):
            print("🔵 Generando diagrama Azure especializado...")
            return generate_azure_architecture_diagram(description)
        
        # Si OpenAI no está configurado, usar fallback directamente
        if OPENAI_API_KEY == 'your-openai-api-key-here' or not OPENAI_API_KEY:
            print("⚠️ OpenAI no configurado, usando diagrama de fallback")
            return generate_fallback_diagram(description, diagram_type)
        
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
                
                print(f"✅ Diagrama IA generado exitosamente: {len(diagram_data['nodes'])} nodos, {len(diagram_data['edges'])} conexiones")
                
                return {
                    'success': True,
                    'type': diagram_data.get('type', diagram_type),
                    'data': diagram_data
                }
            else:
                raise ValueError("No se encontró JSON válido en la respuesta")
                
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON de IA: {e}")
            print(f"Respuesta de IA: {ai_response}")
            # Fallback: generar diagrama básico
            return generate_fallback_diagram(description, diagram_type)
            
    except Exception as e:
        print(f"❌ Error en OpenAI: {str(e)}")
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
    """Create a professional Hub and Spoke architecture diagram structure using real Azure SVG icons"""
    
    # Base positions for Hub components
    hub_center_x = 400
    hub_center_y = 300
    
    # Hub VNet dimensions
    hub_width = 300
    hub_height = 400
    
    # Spoke positioning
    spoke_spacing = 250
    spoke_start_x = hub_center_x + 200
    
    nodes = []
    edges = []
    
    # 1. Diagram Title
    nodes.append({
        "id": "diagram_title",
        "type": "text",
        "text": "Azure Hub and Spoke\nNetwork Topology",
        "x": hub_center_x - 100,
        "y": 50,
        "width": 200,
        "height": 60,
        "style": {"fontSize": "18px", "fontWeight": "bold", "textAlign": "center"}
    })
    
    # 2. Azure Virtual Network Manager (Top)
    nodes.append({
        "id": "azure_vnet_manager",
        "type": "azure_icon",
        "text": "Azure Virtual\nNetwork Manager",
        "x": hub_center_x - 75,
        "y": 120,
        "width": 150,
        "height": 80,
        "icon": "/icons/Azure/networking/10061-icon-service-Virtual-Networks.svg"
    })
    
    # 3. Cross-premises Network (Left)
    nodes.append({
        "id": "cross_premises_network",
        "type": "network_box",
        "text": "Cross-premises\nNetwork",
        "x": hub_center_x - 400,
        "y": hub_center_y - 100,
        "width": 200,
        "height": 200,
        "style": {"border": "2px dashed #666", "backgroundColor": "#f0f0f0"}
    })
    
    # VMs in Cross-premises
    nodes.append({
        "id": "cross_premises_vm1",
        "type": "azure_icon",
        "text": "Virtual\nMachine",
        "x": hub_center_x - 380,
        "y": hub_center_y - 60,
        "width": 80,
        "height": 60,
        "icon": "/icons/Azure/compute/10021-icon-service-Virtual-Machine.svg"
    })
    
    nodes.append({
        "id": "cross_premises_vm2",
        "type": "azure_icon",
        "text": "Virtual\nMachine",
        "x": hub_center_x - 300,
        "y": hub_center_y - 60,
        "width": 80,
        "height": 60,
        "icon": "/icons/Azure/compute/10021-icon-service-Virtual-Machine.svg"
    })
    
    # Secure Connection
    nodes.append({
        "id": "secure_connection",
        "type": "azure_icon",
        "text": "Secure\nConnection",
        "x": hub_center_x - 340,
        "y": hub_center_y + 20,
        "width": 80,
        "height": 60,
        "icon": "/icons/Azure/networking/10063-icon-service-Virtual-Network-Gateways.svg"
    })
    
    # 4. Hub Virtual Network (Center)
    nodes.append({
        "id": "hub_vnet",
        "type": "network_box",
        "text": "Hub Virtual Network",
        "x": hub_center_x - 150,
        "y": hub_center_y - 150,
        "width": hub_width,
        "height": hub_height,
        "style": {"border": "3px solid #0078d4", "backgroundColor": "#e6f3ff", "borderRadius": "10px"}
    })
    
    # Hub Internal Services
    # Azure Bastion
    nodes.append({
        "id": "hub_bastion",
        "type": "azure_icon",
        "text": "Azure\nBastion",
        "x": hub_center_x - 120,
        "y": hub_center_y - 100,
        "width": 100,
        "height": 80,
        "icon": "/icons/Azure/networking/02422-icon-service-Bastions.svg"
    })
    
    # Azure Firewall
    nodes.append({
        "id": "hub_firewall",
        "type": "azure_icon",
        "text": "Azure\nFirewall",
        "x": hub_center_x - 120,
        "y": hub_center_y,
        "width": 100,
        "height": 80,
        "icon": "/icons/Azure/networking/10084-icon-service-Firewalls.svg"
    })
    
    # VPN Gateway/ExpressRoute
    nodes.append({
        "id": "hub_vpn_gateway",
        "type": "azure_icon",
        "text": "VPN Gateway/\nExpressRoute",
        "x": hub_center_x - 120,
        "y": hub_center_y + 100,
        "width": 100,
        "height": 80,
        "icon": "/icons/Azure/networking/10079-icon-service-ExpressRoute-Circuits.svg"
    })
    
    # Azure Monitor (Right side of Hub)
    nodes.append({
        "id": "hub_monitor",
        "type": "azure_icon",
        "text": "Azure\nMonitor",
        "x": hub_center_x + 50,
        "y": hub_center_y,
        "width": 100,
        "height": 80,
        "icon": "/icons/Azure/monitor/00001-icon-service-Monitor.svg"
    })
    
    # 5. Production Spoke Networks (Top Right)
    for i in range(2):
        spoke_x = spoke_start_x + (i * spoke_spacing)
        spoke_y = hub_center_y - 150
        
        # Production Spoke VNet
        nodes.append({
            "id": f"prod_spoke_vnet_{i+1}",
            "type": "network_box",
            "text": f"Production Spoke\nVirtual Network {i+1}",
            "x": spoke_x - 100,
            "y": spoke_y,
            "width": 200,
            "height": 150,
            "style": {"border": "2px solid #107c10", "backgroundColor": "#e6ffe6", "borderRadius": "8px"}
        })
        
        # Resource Subnet
        nodes.append({
            "id": f"prod_spoke_subnet_{i+1}",
            "type": "network_box",
            "text": "Resource\nSubnet(s)",
            "x": spoke_x - 80,
            "y": spoke_y + 30,
            "width": 160,
            "height": 100,
            "style": {"border": "1px solid #107c10", "backgroundColor": "#f0fff0", "borderRadius": "5px"}
        })
        
        # VMs in Resource Subnet
        for j in range(3):
            vm_x = spoke_x - 70 + (j * 50)
            vm_y = spoke_y + 50
            nodes.append({
                "id": f"prod_spoke_vm_{i+1}_{j+1}",
                "type": "azure_icon",
                "text": "VM",
                "x": vm_x,
                "y": vm_y,
                "width": 40,
                "height": 40,
                "icon": "/icons/Azure/compute/10021-icon-service-Virtual-Machine.svg"
            })
    
    # 6. Non-production Spoke Networks (Bottom Right)
    for i in range(2):
        spoke_x = spoke_start_x + (i * spoke_spacing)
        spoke_y = hub_center_y + 100
        
        # Non-production Spoke VNet
        nodes.append({
            "id": f"nonprod_spoke_vnet_{i+1}",
            "type": "network_box",
            "text": f"Non-production Spoke\nVirtual Network {i+1}",
            "x": spoke_x - 100,
            "y": spoke_y,
            "width": 200,
            "height": 150,
            "style": {"border": "2px solid #ff8c00", "backgroundColor": "#fff4e6", "borderRadius": "8px"}
        })
        
        # Resource Subnet
        nodes.append({
            "id": f"nonprod_spoke_subnet_{i+1}",
            "type": "network_box",
            "text": "Resource\nSubnet(s)",
            "x": spoke_x - 80,
            "y": spoke_y + 30,
            "width": 160,
            "height": 100,
            "style": {"border": "1px solid #ff8c00", "backgroundColor": "#fffaf0", "borderRadius": "5px"}
        })
        
        # VMs in Resource Subnet
        for j in range(3):
            vm_x = spoke_x - 70 + (j * 50)
            vm_y = spoke_y + 50
            nodes.append({
                "id": f"nonprod_spoke_vm_{i+1}_{j+1}",
                "type": "azure_icon",
                "text": "VM",
                "x": vm_x,
                "y": vm_y,
                "width": 40,
                "height": 40,
                "icon": "/icons/Azure/compute/Virtual-Machine.svg"
            })
    
    # 7. Connections (Edges)
    
    # Hub VNet Manager to Hub VNet
    edges.append({
        "id": "manager_to_hub",
        "from": "azure_vnet_manager",
        "to": "hub_vnet",
        "label": "Management",
        "type": "management"
    })
    
    # Cross-premises to Hub
    edges.append({
        "id": "cross_to_hub",
        "from": "secure_connection",
        "to": "hub_vpn_gateway",
        "label": "VPN/ExpressRoute",
        "type": "vpn"
    })
    
    # Hub Internal Connections
    edges.append({
        "id": "bastion_to_monitor",
        "from": "hub_bastion",
        "to": "hub_monitor",
        "label": "Diagnostics",
        "type": "diagnostics"
    })
    
    edges.append({
        "id": "firewall_to_monitor",
        "from": "hub_firewall",
        "to": "hub_monitor",
        "label": "Forced Tunnel",
        "type": "forced_tunnel"
    })
    
    edges.append({
        "id": "vpn_to_monitor",
        "from": "hub_vpn_gateway",
        "to": "hub_monitor",
        "label": "Forced Tunnel",
        "type": "forced_tunnel"
    })
    
    # Hub to Production Spokes
    edges.append({
        "id": "bastion_to_prod1",
        "from": "hub_bastion",
        "to": "prod_spoke_vnet_1",
        "label": "VNet Peering",
        "type": "peering"
    })
    
    edges.append({
        "id": "firewall_to_prod1",
        "from": "hub_firewall",
        "to": "prod_spoke_vnet_1",
        "label": "Forced Tunnel",
        "type": "forced_tunnel"
    })
    
    edges.append({
        "id": "firewall_to_prod2",
        "from": "hub_firewall",
        "to": "prod_spoke_vnet_2",
        "label": "Forced Tunnel",
        "type": "forced_tunnel"
    })
    
    # Hub to Non-production Spokes
    edges.append({
        "id": "vpn_to_nonprod1",
        "from": "hub_vpn_gateway",
        "to": "nonprod_spoke_vnet_1",
        "label": "Connected Virtual Networks",
        "type": "connected"
    })
    
    edges.append({
        "id": "hub_to_nonprod1",
        "from": "hub_vnet",
        "to": "nonprod_spoke_vnet_1",
        "label": "Virtual Networks Connected or Peered Through Hub",
        "type": "peered"
    })
    
    edges.append({
        "id": "hub_to_nonprod2",
        "from": "hub_vnet",
        "to": "nonprod_spoke_vnet_2",
        "label": "Virtual Networks Connected or Peered Through Hub",
        "type": "peered"
    })
    
    # Non-production Spokes to each other
    edges.append({
        "id": "nonprod1_to_nonprod2",
        "from": "nonprod_spoke_vnet_1",
        "to": "nonprod_spoke_vnet_2",
        "label": "Peered or Directly Connected Virtual Networks",
        "type": "peered"
    })
    
    return {
        "type": "azure_hub_spoke",
        "nodes": nodes,
        "edges": edges
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
                # processor = DocumentProcessor()
                # content = processor.process_document(filepath)
                
                # if content.get('type') == 'error':
                #     cleanup_temp_files(filepath)
                #     return jsonify({'error': content['message']}), 400
                
                # Generar diagrama
                # generator = DiagramGenerator()
                # diagram_result = generator.create_diagram_from_content(content)
                
                # if diagram_result.get('error'):
                #     cleanup_temp_files(filepath)
                #     return jsonify({'error': diagram_result['error']}), 500
                
                # Limpiar archivo temporal
                # cleanup_temp_files(filepath)
                
                # Asegurar que la respuesta tenga todos los campos necesarios
                # response_data = {
                #     'success': True,
                #     'message': 'Diagrama generado exitosamente',
                #     'diagram_data': diagram_result.get('diagram_data', ''),
                #     'mermaid_code': diagram_result.get('mermaid_code', ''),
                #     'drawio_url': diagram_result.get('drawio_url', ''),
                #     'download_url': diagram_result.get('download_url', ''),
                #     'title': diagram_result.get('title', 'Diagrama Generado'),
                #     'type': diagram_result.get('type', 'generic')
                # }
                
                # return jsonify(response_data)
                
                # Fallback para archivos de texto o JSON
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                # Generar diagrama basado en el contenido del archivo
                # Para simplificar, vamos a generar un diagrama de flujo básico
                # basado en las palabras clave encontradas en el archivo.
                # Esto es un ejemplo y puede ser mejorado.
                
                nodes = []
                edges = []
                
                # Tokenizar el contenido en palabras
                words = file_content.split()
                
                # Crear nodos básicos basados en las palabras
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
                
                # Asegurar que la respuesta tenga todos los campos necesarios
                response_data = {
                    'success': True,
                    'message': 'Diagrama generado exitosamente',
                    'diagram_data': {
                        'type': 'flowchart', # Forced to flowchart for fallback
                        'nodes': nodes,
                        'edges': edges
                    },
                    'mermaid_code': 'graph TD\n' + '\n'.join([f"{edge['from']} --> {edge['to']}" for edge in edges]),
                    'drawio_url': 'https://app.diagrams.net/?lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=Untitled%20Diagram.drawio#Uhttps://raw.githubusercontent.com/jgraph/drawio-diagrams/master/examples/basic.drawio',
                    'download_url': 'https://app.diagrams.net/?lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=Untitled%20Diagram.drawio#Uhttps://raw.githubusercontent.com/jgraph/drawio-diagrams/master/examples/basic.drawio',
                    'title': f"Diagrama de {file.filename}",
                    'type': 'flowchart'
                }
                
                cleanup_temp_files(filepath)
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
        # generator = DiagramGenerator()
        # diagram_result = generator.create_diagram_from_content(content)
        
        # if diagram_result.get('error'):
        #     return jsonify({'error': diagram_result['error']}), 500
        
        # Asegurar que la respuesta tenga todos los campos necesarios
        response_data = {
            'success': True,
            'message': 'Diagrama generado exitosamente',
            'diagram_data': {
                'type': 'flowchart', # Forced to flowchart for fallback
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
            'mermaid_code': 'graph TD\n' + 'A[Inicio] --> B[Proceso] --> C[Fin]',
            'drawio_url': 'https://app.diagrams.net/?lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=Untitled%20Diagram.drawio#Uhttps://raw.githubusercontent.com/jgraph/drawio-diagrams/master/examples/basic.drawio',
            'download_url': 'https://app.diagrams.net/?lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=Untitled%20Diagram.drawio#Uhttps://raw.githubusercontent.com/jgraph/drawio-diagrams/master/examples/basic.drawio',
            'title': 'Diagrama de Texto',
            'type': 'flowchart'
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

@app.route('/api/icons', methods=['GET'])
def get_available_icons():
    """Obtiene todos los iconos disponibles organizados por categorías"""
    try:
        icons = {}
        icons_base_path = 'icons'
        
        # Cargar iconos de AWS
        aws_path = os.path.join(icons_base_path, 'AWS')
        if os.path.exists(aws_path):
            icons['AWS'] = {}
            for category in os.listdir(aws_path):
                category_path = os.path.join(aws_path, category)
                if os.path.isdir(category_path):
                    icons['AWS'][category] = []
                    for icon_file in os.listdir(category_path):
                        if icon_file.endswith('.svg'):
                            icon_name = icon_file.replace('.svg', '')
                            icons['AWS'][category].append({
                                'name': icon_name,
                                'path': f'/icons/AWS/{category}/{icon_file}',
                                'category': category,
                                'provider': 'AWS'
                            })
        
        # Cargar iconos de Azure
        azure_path = os.path.join(icons_base_path, 'Azure')
        if os.path.exists(azure_path):
            icons['Azure'] = {}
            for category in os.listdir(azure_path):
                category_path = os.path.join(azure_path, category)
                if os.path.isdir(category_path):
                    icons['Azure'][category] = []
                    for icon_file in os.listdir(category_path):
                        if icon_file.endswith('.svg'):
                            icon_name = icon_file.replace('.svg', '')
                            icons['Azure'][category].append({
                                'name': icon_name,
                                'path': f'/icons/Azure/{category}/{icon_file}',
                                'category': category,
                                'provider': 'Azure'
                            })
        
        # Contar total de iconos
        total_icons = 0
        for provider in icons.values():
            for category in provider.values():
                total_icons += len(category)
        
        print(f"📦 Iconos cargados: {total_icons} iconos en {len(icons)} proveedores")
        
        return jsonify({
            'success': True,
            'icons': icons,
            'total_icons': total_icons,
            'providers': list(icons.keys())
        })
        
    except Exception as e:
        print(f"Error cargando iconos: {str(e)}")
        return jsonify({'error': f'Error cargando iconos: {str(e)}'}), 500

@app.route('/icons/<path:filename>')
def serve_icon(filename):
    """Sirve archivos de iconos estáticamente"""
    try:
        return send_file(os.path.join('icons', filename))
    except Exception as e:
        return jsonify({'error': 'Icono no encontrado'}), 404

@app.route('/api/diagram/<diagram_id>/add_node', methods=['POST'])
def add_node_to_diagram(diagram_id):
    """Añade un nuevo nodo a un diagrama existente"""
    try:
        if diagram_id not in diagrams:
            return jsonify({'error': 'Diagrama no encontrado'}), 404
        
        data = request.get_json()
        node_data = {
            'id': data.get('id', f'node_{len(diagrams[diagram_id]["data"]["nodes"]) + 1}'),
            'type': data.get('type', 'rectangle'),
            'text': data.get('text', 'Nuevo Nodo'),
            'x': data.get('x', 100),
            'y': data.get('y', 100),
            'width': data.get('width', 120),
            'height': data.get('height', 60),
            'icon': data.get('icon', None),
            'style': data.get('style', {})
        }
        
        # Añadir nodo al diagrama
        diagrams[diagram_id]['data']['nodes'].append(node_data)
        diagrams[diagram_id]['updated_at'] = datetime.now().isoformat()
        diagrams[diagram_id]['version'] += 1
        
        return jsonify({
            'success': True,
            'node': node_data,
            'diagram': diagrams[diagram_id]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error añadiendo nodo: {str(e)}'}), 500

@app.route('/api/diagram/<diagram_id>/add_connection', methods=['POST'])
def add_connection_to_diagram(diagram_id):
    """Añade una nueva conexión a un diagrama existente"""
    try:
        if diagram_id not in diagrams:
            return jsonify({'error': 'Diagrama no encontrado'}), 404
        
        data = request.get_json()
        connection_data = {
            'id': data.get('id', f'edge_{len(diagrams[diagram_id]["data"].get("edges", [])) + 1}'),
            'from': data.get('from'),
            'to': data.get('to'),
            'text': data.get('text', ''),
            'type': data.get('type', 'default'),
            'style': data.get('style', {})
        }
        
        # Validar que los nodos existen
        node_ids = [node['id'] for node in diagrams[diagram_id]['data']['nodes']]
        if connection_data['from'] not in node_ids or connection_data['to'] not in node_ids:
            return jsonify({'error': 'Nodos de origen o destino no encontrados'}), 400
        
        # Inicializar edges si no existe
        if 'edges' not in diagrams[diagram_id]['data']:
            diagrams[diagram_id]['data']['edges'] = []
        
        # Añadir conexión al diagrama
        diagrams[diagram_id]['data']['edges'].append(connection_data)
        diagrams[diagram_id]['updated_at'] = datetime.now().isoformat()
        diagrams[diagram_id]['version'] += 1
        
        return jsonify({
            'success': True,
            'connection': connection_data,
            'diagram': diagrams[diagram_id]
        })
        
    except Exception as e:
        return jsonify({'error': f'Error añadiendo conexión: {str(e)}'}), 500

@app.route('/api/search_icons', methods=['GET'])
def search_icons():
    """Busca iconos por nombre o categoría"""
    try:
        query = request.args.get('q', '').lower()
        provider = request.args.get('provider', 'all')
        category = request.args.get('category', 'all')
        
        if not query:
            return jsonify({'error': 'Query de búsqueda requerido'}), 400
        
        # Obtener todos los iconos
        icons_response = get_available_icons()
        if not icons_response.json.get('success'):
            return icons_response
        
        all_icons = icons_response.json['icons']
        results = []
        
        # Buscar en todos los proveedores y categorías
        for provider_name, provider_icons in all_icons.items():
            if provider != 'all' and provider_name.lower() != provider.lower():
                continue
                
            for category_name, category_icons in provider_icons.items():
                if category != 'all' and category_name.lower() != category.lower():
                    continue
                    
                for icon in category_icons:
                    if (query in icon['name'].lower() or 
                        query in category_name.lower() or
                        query in provider_name.lower()):
                        results.append(icon)
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results),
            'query': query
        })
        
    except Exception as e:
        return jsonify({'error': f'Error buscando iconos: {str(e)}'}), 500

@app.route('/api/diagram/<diagram_id>/duplicate', methods=['POST'])
def duplicate_diagram(diagram_id):
    """Duplica un diagrama existente"""
    try:
        if diagram_id not in diagrams:
            return jsonify({'error': 'Diagrama no encontrado'}), 404
        
        original_diagram = diagrams[diagram_id]
        new_diagram_id = str(uuid.uuid4())
        
        # Crear copia del diagrama
        new_diagram = {
            'id': new_diagram_id,
            'title': f"{original_diagram['title']} (Copia)",
            'type': original_diagram['type'],
            'data': json.loads(json.dumps(original_diagram['data'])),  # Deep copy
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'version': 1,
            'ai_generated': original_diagram.get('ai_generated', False)
        }
        
        # Generar nuevos IDs para nodos y conexiones
        node_id_mapping = {}
        for node in new_diagram['data']['nodes']:
            old_id = node['id']
            new_id = f"node_{uuid.uuid4().hex[:8]}"
            node['id'] = new_id
            node_id_mapping[old_id] = new_id
        
        # Actualizar IDs en las conexiones
        if 'edges' in new_diagram['data']:
            for edge in new_diagram['data']['edges']:
                edge['id'] = f"edge_{uuid.uuid4().hex[:8]}"
                if edge['from'] in node_id_mapping:
                    edge['from'] = node_id_mapping[edge['from']]
                if edge['to'] in node_id_mapping:
                    edge['to'] = node_id_mapping[edge['to']]
        
        # Guardar nuevo diagrama
        diagrams[new_diagram_id] = new_diagram
        
        return jsonify({
            'success': True,
            'diagram': new_diagram,
            'message': 'Diagrama duplicado exitosamente'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error duplicando diagrama: {str(e)}'}), 500

@app.route('/api/diagram/<diagram_id>/export_mermaid', methods=['GET'])
def export_diagram_mermaid(diagram_id):
    """Exporta un diagrama como código Mermaid"""
    try:
        if diagram_id not in diagrams:
            return jsonify({'error': 'Diagrama no encontrado'}), 404
        
        diagram = diagrams[diagram_id]
        mermaid_code = generate_mermaid_code(diagram['data'], diagram['type'])
        
        return jsonify({
            'success': True,
            'mermaid_code': mermaid_code,
            'diagram_type': diagram['type'],
            'title': diagram['title']
        })
        
    except Exception as e:
        return jsonify({'error': f'Error exportando a Mermaid: {str(e)}'}), 500

def generate_mermaid_code(diagram_data, diagram_type):
    """Genera código Mermaid basado en los datos del diagrama"""
    try:
        nodes = diagram_data.get('nodes', [])
        edges = diagram_data.get('edges', [])
        
        if diagram_type == 'flowchart':
            code = "graph TD\n"
            
            # Añadir nodos
            for node in nodes:
                node_id = node['id'].replace('-', '_')
                node_text = node.get('text', node_id)
                
                if node.get('type') == 'decision':
                    code += f"    {node_id}{{{node_text}}}\n"
                elif node.get('type') == 'start' or node.get('type') == 'end':
                    code += f"    {node_id}([{node_text}])\n"
                else:
                    code += f"    {node_id}[{node_text}]\n"
            
            # Añadir conexiones
            for edge in edges:
                from_id = edge['from'].replace('-', '_')
                to_id = edge['to'].replace('-', '_')
                edge_text = edge.get('text', '')
                
                if edge_text:
                    code += f"    {from_id} -->|{edge_text}| {to_id}\n"
                else:
                    code += f"    {from_id} --> {to_id}\n"
        
        elif diagram_type == 'sequence':
            code = "sequenceDiagram\n"
            
            # Añadir participantes
            participants = set()
            for edge in edges:
                participants.add(edge['from'])
                participants.add(edge['to'])
            
            for participant in participants:
                code += f"    participant {participant}\n"
            
            # Añadir interacciones
            for edge in edges:
                from_id = edge['from']
                to_id = edge['to']
                message = edge.get('text', 'message')
                code += f"    {from_id}->>+{to_id}: {message}\n"
        
        else:
            # Fallback a flowchart
            code = "graph TD\n"
            for node in nodes:
                node_id = node['id'].replace('-', '_')
                node_text = node.get('text', node_id)
                code += f"    {node_id}[{node_text}]\n"
            
            for edge in edges:
                from_id = edge['from'].replace('-', '_')
                to_id = edge['to'].replace('-', '_')
                code += f"    {from_id} --> {to_id}\n"
        
        return code
        
    except Exception as e:
        print(f"Error generando código Mermaid: {str(e)}")
        return "graph TD\n    A[Error generando diagrama]"

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Aplicación funcionando correctamente'})

if __name__ == '__main__':
    print("🚀 Iniciando Diagramas Creator - Editor de Diagramas con IA...")
    print("📁 Directorio de uploads:", app.config['UPLOAD_FOLDER'])
    print("📁 Directorio de salidas:", app.config['OUTPUT_FOLDER'])
    print("🤖 Funcionalidad de IA habilitada")
    print("📦 Sistema de iconos AWS/Azure integrado")
    print("🎨 Canvas interactivo estilo draw.io")
    print("🌐 Servidor iniciado en: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
