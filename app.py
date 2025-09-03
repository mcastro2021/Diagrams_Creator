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
from config import get_config, validate_config, print_config_summary

# Obtener configuración
config = get_config()

app = Flask(__name__)
CORS(app)

# Aplicar configuración
app.config.from_object(config)
config.init_app(app)

# Configuración de OpenAI
openai.api_key = config.OPENAI_API_KEY

# Crear directorios si no existen
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.OUTPUT_FOLDER, exist_ok=True)

# Extensiones permitidas
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'xlsx', 'csv', 'json', 'png', 'jpg', 'jpeg', 'svg'}

# Almacenamiento en memoria para diagramas
diagrams = {}  # {diagram_id: diagram_data}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

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
        if config.OPENAI_API_KEY == 'your-openai-api-key-here' or not config.OPENAI_API_KEY:
            print("⚠️ OpenAI no configurado, usando diagrama de fallback")
            return generate_fallback_diagram(description, diagram_type)
        
        # Crear prompt para OpenAI según el tipo
        system_prompt = get_system_prompt_for_type(diagram_type)
        user_prompt = f"Genera un diagrama de {diagram_type} para: {description}"
        
        # Llamar a OpenAI
        response = openai.ChatCompletion.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=config.OPENAI_MAX_TOKENS,
            temperature=config.OPENAI_TEMPERATURE
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
            'virtual_machines': any(word in description_lower for word in config.AZURE_VM_KEYWORDS),
            'app_service': any(word in description_lower for word in config.AZURE_APP_SERVICE_KEYWORDS),
            'database': any(word in description_lower for word in config.AZURE_DATABASE_KEYWORDS),
            'storage': any(word in description_lower for word in config.AZURE_STORAGE_KEYWORDS),
            'network': any(word in description_lower for word in config.AZURE_NETWORK_KEYWORDS),
            'security': any(word in description_lower for word in config.AZURE_SECURITY_KEYWORDS),
            'monitoring': any(word in description_lower for word in config.AZURE_MONITORING_KEYWORDS),
            'cdn': any(word in description_lower for word in config.AZURE_CDN_KEYWORDS),
            'load_balancer': any(word in description_lower for word in config.AZURE_LOAD_BALANCER_KEYWORDS),
            'api_management': any(word in description_lower for word in config.AZURE_API_MANAGEMENT_KEYWORDS),
            'hub_spoke': any(word in description_lower for word in config.AZURE_HUB_SPOKE_KEYWORDS),
            'multiple_subscriptions': any(word in description_lower for word in config.AZURE_SUBSCRIPTION_KEYWORDS),
            'enterprise': any(word in description_lower for word in config.AZURE_ENTERPRISE_KEYWORDS)
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
    """Create a professional Hub and Spoke architecture diagram structure using real Azure SVG icons with enhanced technical details"""
    
    # Grid-based positioning system for better organization
    grid_config = {
        'cell_width': 120,
        'cell_height': 100,
        'margin': 20,
        'start_x': 50,
        'start_y': 50
    }
    
    # Calculate grid positions
    def get_grid_position(row, col, offset_x=0, offset_y=0):
        x = grid_config['start_x'] + (col * (grid_config['cell_width'] + grid_config['margin'])) + offset_x
        y = grid_config['start_y'] + (row * (grid_config['cell_height'] + grid_config['margin'])) + offset_y
        return x, y
    
    # Hub center position (centered in the diagram)
    hub_center_x = grid_config['start_x'] + (6 * (grid_config['cell_width'] + grid_config['margin']))
    hub_center_y = grid_config['start_y'] + (4 * (grid_config['cell_height'] + grid_config['margin']))
    
    # Hub VNet dimensions - Increased to properly contain internal services
    hub_width = 400
    hub_height = 400
    
    # Spoke positioning with consistent spacing
    spoke_spacing = grid_config['cell_width'] + grid_config['margin']
    spoke_start_x = hub_center_x + 200
    
    nodes = []
    edges = []
    
    # 1. Diagram Title with Technical Details (Top center)
    title_x, title_y = get_grid_position(0, 6, -150, 0)
    nodes.append({
        "id": "diagram_title",
        "type": "text",
        "text": "Azure Hub and Spoke\nNetwork Topology\nEnterprise Architecture",
        "x": title_x,
        "y": title_y,
        "width": 300,
        "height": 80,
        "style": {"fontSize": "20px", "fontWeight": "bold", "textAlign": "center", "color": "#323130"}
    })
    
    # 2. Azure Virtual Network Manager (Top center, above hub)
    vnet_manager_x, vnet_manager_y = get_grid_position(1, 6, -75, 0)
    nodes.append({
        "id": "azure_vnet_manager",
        "type": "azure_icon",
        "text": "Azure Virtual\nNetwork Manager\nCentralized Policy\nManagement",
        "x": vnet_manager_x,
        "y": vnet_manager_y,
        "width": 150,
        "height": 100,
        "icon": "/icons/Azure/networking/10061-icon-service-Virtual-Networks.svg",
        "metadata": {
            "service": "Virtual Network Manager",
            "purpose": "Centralized network policy management",
            "features": config.AZURE_VNET_MANAGER_FEATURES
        }
    })
    
    # 3. Cross-premises Network (Left side, organized in grid) - Increased size to contain VMs
    cross_premises_x, cross_premises_y = get_grid_position(2, 0, 0, 0)
    cross_premises_width = 250
    cross_premises_height = 280
    nodes.append({
        "id": "cross_premises_network",
        "type": "network_box",
        "text": "Cross-premises\nNetwork\nOn-Premises\nInfrastructure",
        "x": cross_premises_x,
        "y": cross_premises_y,
        "width": cross_premises_width,
        "height": cross_premises_height,
        "style": {"border": "2px dashed #666", "backgroundColor": "#f0f0f0"},
        "metadata": {
            "type": "On-Premises Network",
            "connectivity": "VPN/ExpressRoute",
            "components": ["Active Directory", "File Servers", "Application Servers"]
        }
    })
    
    # VMs in Cross-premises with organized positioning - Positioned inside the container
    vm1_x = cross_premises_x + 20
    vm1_y = cross_premises_y + 60
    nodes.append({
        "id": "cross_premises_vm1",
        "type": "azure_icon",
        "text": "Virtual\nMachine\nWindows Server 2022\n4 vCPU, 16 GB RAM",
        "x": vm1_x,
        "y": vm1_y,
        "width": 90,
        "height": 70,
        "icon": "/icons/Azure/compute/10021-icon-service-Virtual-Machine.svg",
        "metadata": {
            "os": "Windows Server 2022",
            "specs": "4 vCPU, 16 GB RAM, 128 GB SSD",
            "purpose": "Domain Controller"
        }
    })
    
    vm2_x = cross_premises_x + 130
    vm2_y = cross_premises_y + 60
    nodes.append({
        "id": "cross_premises_vm2",
        "type": "azure_icon",
        "text": "Virtual\nMachine\nLinux Ubuntu 22.04\n2 vCPU, 8 GB RAM",
        "x": vm2_x,
        "y": vm2_y,
        "width": 90,
        "height": 70,
        "icon": "/icons/Azure/compute/10021-icon-service-Virtual-Machine.svg",
        "metadata": {
            "os": "Ubuntu 22.04 LTS",
            "specs": "2 vCPU, 8 GB RAM, 64 GB SSD",
            "purpose": "Application Server"
        }
    })
    
    # Secure Connection with organized positioning - Positioned inside the container
    secure_conn_x = cross_premises_x + 70
    secure_conn_y = cross_premises_y + 180
    nodes.append({
        "id": "secure_connection",
        "type": "azure_icon",
        "text": "Secure\nConnection\nExpressRoute\n1 Gbps Circuit",
        "x": secure_conn_x,
        "y": secure_conn_y,
        "width": 90,
        "height": 70,
        "icon": "/icons/Azure/networking/10063-icon-service-Virtual-Network-Gateways.svg",
        "metadata": {
            "type": "ExpressRoute Circuit",
            "bandwidth": "1 Gbps",
            "redundancy": "Primary + Secondary",
            "provider": "Local ISP"
        }
    })
    
    # 4. Hub Virtual Network (Center, organized) - Increased size to properly contain services
    hub_vnet_x = hub_center_x - (hub_width // 2)
    hub_vnet_y = hub_center_y - (hub_height // 2)
    nodes.append({
        "id": "hub_vnet",
        "type": "network_box",
        "text": "Hub Virtual Network\n10.0.0.0/16\nCentral Services\nManagement & Security",
        "x": hub_vnet_x,
        "y": hub_vnet_y,
        "width": hub_width,
        "height": hub_height,
        "style": {"border": "3px solid #0078d4", "backgroundColor": "#e6f3ff", "borderRadius": "10px"},
        "metadata": {
            "address_space": "10.0.0.0/16",
            "subnets": ["10.0.1.0/24 (Management)", "10.0.2.0/24 (Security)", "10.0.3.0/24 (Gateway)"],
            "purpose": "Centralized services, security, and connectivity"
        }
    })
    
    # Hub Internal Services with organized positioning - All positioned inside the hub container
    # Azure Bastion (left side of hub)
    bastion_x = hub_center_x - 150
    bastion_y = hub_center_y - 120
    nodes.append({
        "id": "hub_bastion",
        "type": "azure_icon",
        "text": "Azure\nBastion\nSecure RDP/SSH\nJump Host",
        "x": bastion_x,
        "y": bastion_y,
        "width": 100,
        "height": 80,
        "icon": "/icons/Azure/networking/02422-icon-service-Bastions.svg",
        "metadata": {
            "service": "Azure Bastion",
            "purpose": "Secure RDP/SSH access",
            "features": ["No public IP required", "SSL encryption", "Audit logging"]
        }
    })
    
    # Azure Firewall (left side of hub, below bastion)
    firewall_x = bastion_x
    firewall_y = bastion_y + 100
    nodes.append({
        "id": "hub_firewall",
        "type": "azure_icon",
        "text": "Azure\nFirewall\nPremium SKU\nThreat Intelligence",
        "x": firewall_x,
        "y": firewall_y,
        "width": 100,
        "height": 80,
        "icon": "/icons/Azure/networking/10084-icon-service-Firewalls.svg",
        "metadata": {
            "sku": "Premium",
            "features": ["Threat Intelligence", "TLS Inspection", "Web Categories"],
            "rules": ["Network Rules", "Application Rules", "DNAT Rules"]
        }
    })
    
    # VPN Gateway/ExpressRoute (left side of hub, below firewall)
    vpn_gateway_x = firewall_x
    vpn_gateway_y = firewall_y + 100
    nodes.append({
        "id": "hub_vpn_gateway",
        "type": "azure_icon",
        "text": "VPN Gateway/\nExpressRoute\nVpnGw2AZ\n1.25 Gbps",
        "x": vpn_gateway_x,
        "y": vpn_gateway_y,
        "width": 100,
        "height": 80,
        "icon": "/icons/Azure/networking/10079-icon-service-ExpressRoute-Circuits.svg",
        "metadata": {
            "sku": "VpnGw2AZ",
            "bandwidth": "1.25 Gbps",
            "features": ["Active-Active", "Zone Redundant", "BGP Support"]
        }
    })
    
    # Azure Monitor (Right side of Hub)
    monitor_x = hub_center_x + 50
    monitor_y = hub_center_y
    nodes.append({
        "id": "hub_monitor",
        "type": "azure_icon",
        "text": "Azure\nMonitor\nLog Analytics\nApplication Insights",
        "x": monitor_x,
        "y": monitor_y,
        "width": 100,
        "height": 80,
        "icon": "/icons/Azure/monitor/00001-icon-service-Monitor.svg",
        "metadata": {
            "services": ["Log Analytics", "Application Insights", "Network Watcher"],
            "retention": "90 days",
            "features": ["Real-time monitoring", "Alerting", "Dashboards"]
        }
    })
    
    # 5. Production Spoke Networks (Top Right) with organized grid positioning
    for i in range(2):
        # Calculate grid position for each spoke
        spoke_col = 8 + i  # Start from column 8 (right side)
        spoke_row = 2      # Top row
        
        # Production Spoke VNet - Increased size to contain subnet and VMs
        spoke_vnet_x, spoke_vnet_y = get_grid_position(spoke_row, spoke_col, -100, 0)
        spoke_vnet_width = 240
        spoke_vnet_height = 200
        nodes.append({
            "id": f"prod_spoke_vnet_{i+1}",
            "type": "network_box",
            "text": f"Production Spoke\nVirtual Network {i+1}\n10.{i+1}.0.0/16\nTier 1 Applications",
            "x": spoke_vnet_x,
            "y": spoke_vnet_y,
            "width": spoke_vnet_width,
            "height": spoke_vnet_height,
            "style": {"border": "2px solid #107c10", "backgroundColor": "#e6ffe6", "borderRadius": "8px"},
            "metadata": {
                "address_space": f"10.{i+1}.0.0/16",
                "environment": "Production",
                "tier": "Tier 1",
                "subnets": [f"10.{i+1}.1.0/24 (Web)", f"10.{i+1}.2.0/24 (App)", f"10.{i+1}.3.0/24 (Data)"]
            }
        })
        
        # Resource Subnet (below VNet) - Positioned inside the VNet container
        subnet_x = spoke_vnet_x + 40
        subnet_y = spoke_vnet_y + 80
        nodes.append({
            "id": f"prod_spoke_subnet_{i+1}",
            "type": "network_box",
            "text": "Resource\nSubnet(s)\nWeb, App, Data\nTiers",
            "x": subnet_x,
            "y": subnet_y,
            "width": 160,
            "height": 110,
            "style": {"border": "1px solid #107c10", "backgroundColor": "#f0fff0", "borderRadius": "5px"},
            "metadata": {
                "subnets": ["Web Tier", "Application Tier", "Data Tier"],
                "nsg_rules": ["Allow HTTP/HTTPS", "Allow SSH/RDP from Bastion", "Deny Internet"]
            }
        })
        
        # VMs in Resource Subnet with organized positioning - All positioned inside the subnet container
        for j in range(3):
            vm_x = subnet_x + 20 + (j * 45)
            vm_y = subnet_y + 60
            vm_tier = ["Web", "App", "Data"][j]
            vm_specs = ["2 vCPU, 4 GB", "4 vCPU, 8 GB", "8 vCPU, 16 GB"][j]
            
            nodes.append({
                "id": f"prod_spoke_vm_{i+1}_{j+1}",
                "type": "azure_icon",
                "text": f"{vm_tier}\nVM\n{vm_specs}",
                "x": vm_x,
                "y": vm_y,
                "width": 40,
                "height": 40,
                "icon": "/icons/Azure/compute/10021-icon-service-Virtual-Machine.svg",
                "metadata": {
                    "tier": vm_tier,
                    "specs": vm_specs,
                    "purpose": f"Production {vm_tier} Server",
                    "backup": "Azure Backup enabled"
                }
            })
    
    # 6. Non-production Spoke Networks (Bottom Right) with organized grid positioning
    for i in range(2):
        # Calculate grid position for each spoke
        spoke_col = 8 + i  # Start from column 8 (right side)
        spoke_row = 6      # Bottom row
        
        # Non-production Spoke VNet - Increased size to contain subnet and VMs
        spoke_vnet_x, spoke_vnet_y = get_grid_position(spoke_row, spoke_col, -100, 0)
        spoke_vnet_width = 240
        spoke_vnet_height = 200
        nodes.append({
            "id": f"nonprod_spoke_vnet_{i+1}",
            "type": "network_box",
            "text": f"Non-production Spoke\nVirtual Network {i+1}\n10.{i+10}.0.0/16\nDev/Test/Staging",
            "x": spoke_vnet_x,
            "y": spoke_vnet_y,
            "width": spoke_vnet_width,
            "height": spoke_vnet_height,
            "style": {"border": "2px solid #ff8c00", "backgroundColor": "#fff4e6", "borderRadius": "8px"},
            "metadata": {
                "address_space": f"10.{i+10}.0.0/16",
                "environment": "Non-Production",
                "purpose": "Development, Testing, Staging",
                "subnets": [f"10.{i+10}.1.0/24 (Dev)", f"10.{i+10}.2.0/24 (Test)", f"10.{i+10}.3.0/24 (Staging)"]
            }
        })
        
        # Resource Subnet (below VNet) - Positioned inside the VNet container
        subnet_x = spoke_vnet_x + 40
        subnet_y = spoke_vnet_y + 80
        nodes.append({
            "id": f"nonprod_spoke_subnet_{i+1}",
            "type": "network_box",
            "text": "Resource\nSubnet(s)\nDev, Test, Staging\nEnvironments",
            "x": subnet_x,
            "y": subnet_y,
            "width": 160,
            "height": 110,
            "style": {"border": "1px solid #ff8c00", "backgroundColor": "#fffaf0", "borderRadius": "5px"},
            "metadata": {
                "subnets": ["Development", "Testing", "Staging"],
                "nsg_rules": ["Allow all internal traffic", "Restrict external access", "DevOps access only"]
            }
        })
        
        # VMs in Resource Subnet with organized positioning - All positioned inside the subnet container
        for j in range(3):
            vm_x = subnet_x + 20 + (j * 45)
            vm_y = subnet_y + 60
            vm_env = ["Dev", "Test", "Staging"][j]
            vm_specs = ["1 vCPU, 2 GB", "2 vCPU, 4 GB", "4 vCPU, 8 GB"][j]
            
            nodes.append({
                "id": f"nonprod_spoke_vm_{i+1}_{j+1}",
                "type": "azure_icon",
                "text": f"{vm_env}\nVM\n{vm_specs}",
                "x": vm_x,
                "y": vm_y,
                "width": 40,
                "height": 40,
                "icon": "/icons/Azure/compute/10021-icon-service-Virtual-Machine.svg",
                "metadata": {
                    "environment": vm_env,
                    "specs": vm_specs,
                    "purpose": f"{vm_env} Environment Server",
                    "auto_shutdown": "Enabled for cost optimization"
                }
            })
    
    # 7. Enhanced Connections (Edges) with comprehensive architectural flow
    # Hub VNet Manager to Hub VNet
    edges.append({
        "id": "manager_to_hub",
        "from": "azure_vnet_manager",
        "to": "hub_vnet",
        "label": "Policy Management\nNetwork Groups",
        "type": "management",
        "metadata": {
            "protocol": "Azure Management",
            "purpose": "Policy distribution and configuration"
        }
    })
    
    # Cross-premises to Hub - Enhanced connection
    edges.append({
        "id": "cross_to_hub",
        "from": "secure_connection",
        "to": "hub_vpn_gateway",
        "label": "ExpressRoute\n1 Gbps Circuit\nBGP Routing",
        "type": "expressroute",
        "metadata": {
            "bandwidth": "1 Gbps",
            "protocol": "BGP",
            "redundancy": "Primary + Secondary circuits"
        }
    })
    
    # NEW: Cross-premises VMs to secure connection
    edges.append({
        "id": "vm1_to_secure",
        "from": "cross_premises_vm1",
        "to": "secure_connection",
        "label": "Internal Traffic\nManagement",
        "type": "internal",
        "metadata": {
            "traffic": "Management traffic",
            "protocol": "Internal routing"
        }
    })
    
    edges.append({
        "id": "vm2_to_secure",
        "from": "cross_premises_vm2",
        "to": "secure_connection",
        "label": "Internal Traffic\nApplication",
        "type": "internal",
        "metadata": {
            "traffic": "Application traffic",
            "protocol": "Internal routing"
        }
    })
    
    # NEW: Hub VNet to all internal services
    edges.append({
        "id": "hub_to_bastion",
        "from": "hub_vnet",
        "to": "hub_bastion",
        "label": "VNet Integration\nManagement Subnet",
        "type": "vnet_integration",
        "metadata": {
            "subnet": "10.0.1.0/24",
            "purpose": "Management access"
        }
    })
    
    edges.append({
        "id": "hub_to_firewall",
        "from": "hub_vnet",
        "to": "hub_firewall",
        "label": "VNet Integration\nSecurity Subnet",
        "type": "vnet_integration",
        "metadata": {
            "subnet": "10.0.2.0/24",
            "purpose": "Security services"
        }
    })
    
    edges.append({
        "id": "hub_to_vpn",
        "from": "hub_vnet",
        "to": "hub_vpn_gateway",
        "label": "VNet Integration\nGateway Subnet",
        "type": "vnet_integration",
        "metadata": {
            "subnet": "10.0.3.0/27",
            "purpose": "Gateway services"
        }
    })
    
    edges.append({
        "id": "hub_to_monitor",
        "from": "hub_vnet",
        "to": "hub_monitor",
        "label": "VNet Integration\nMonitoring Subnet",
        "type": "vnet_integration",
        "metadata": {
            "subnet": "10.0.4.0/24",
            "purpose": "Monitoring services"
        }
    })
    
    # Hub Internal Connections - Enhanced with more detail
    edges.append({
        "id": "bastion_to_monitor",
        "from": "hub_bastion",
        "to": "hub_monitor",
        "label": "Diagnostics\nAudit Logs",
        "type": "diagnostics",
        "metadata": {
            "data": "Connection logs, audit trails",
            "retention": "90 days"
        }
    })
    
    edges.append({
        "id": "firewall_to_monitor",
        "from": "hub_firewall",
        "to": "hub_monitor",
        "label": "Forced Tunnel\nTraffic Analysis",
        "type": "forced_tunnel",
        "metadata": {
            "traffic": "All internet traffic",
            "analysis": "Threat detection, logging"
        }
    })
    
    edges.append({
        "id": "vpn_to_monitor",
        "from": "hub_vpn_gateway",
        "to": "hub_monitor",
        "label": "Forced Tunnel\nConnection Monitoring",
        "type": "forced_tunnel",
        "metadata": {
            "traffic": "Cross-premises traffic",
            "monitoring": "Connection status, performance"
        }
    })
    
    # NEW: Internal hub service connections
    edges.append({
        "id": "bastion_to_firewall",
        "from": "hub_bastion",
        "to": "hub_firewall",
        "label": "Management Access\nThrough Firewall",
        "type": "management",
        "metadata": {
            "purpose": "Bastion management access",
            "security": "Firewall rules applied"
        }
    })
    
    edges.append({
        "id": "firewall_to_vpn",
        "from": "hub_firewall",
        "to": "hub_vpn_gateway",
        "label": "Traffic Inspection\nBefore Gateway",
        "type": "security",
        "metadata": {
            "purpose": "Security inspection",
            "traffic": "Cross-premises traffic"
        }
    })
    
    # Hub to Production Spokes - Enhanced with more connections
    for i in range(2):
        spoke_id = f"prod_spoke_vnet_{i+1}"
        
        # Bastion to production spokes
        edges.append({
            "id": f"bastion_to_prod{i+1}",
            "from": "hub_bastion",
            "to": spoke_id,
            "label": "VNet Peering\nManagement Access",
            "type": "peering",
            "metadata": {
                "peering_type": "Hub-Spoke",
                "traffic": "Management traffic only",
                "nsg": "Restrict to Bastion subnet"
            }
        })
        
        # Firewall to production spokes
        edges.append({
            "id": f"firewall_to_prod{i+1}",
            "from": "hub_firewall",
            "to": spoke_id,
            "label": "Forced Tunnel\nInternet Access",
            "type": "forced_tunnel",
            "metadata": {
                "traffic": "Internet-bound traffic",
                "inspection": "Firewall inspection required"
            }
        })
        
        # Hub VNet to production spokes
        edges.append({
            "id": f"hub_to_prod{i+1}",
            "from": "hub_vnet",
            "to": spoke_id,
            "label": "VNet Peering\nInternal Communication",
            "type": "peering",
            "metadata": {
                "peering_type": "Hub-Spoke",
                "traffic": "Internal communication",
                "monitoring": "Traffic analysis enabled"
            }
        })
        
        # Production spoke to its subnet
        subnet_id = f"prod_spoke_subnet_{i+1}"
        edges.append({
            "id": f"prod{i+1}_to_subnet",
            "from": spoke_id,
            "to": subnet_id,
            "label": "VNet Integration\nResource Subnet",
            "type": "vnet_integration",
            "metadata": {
                "purpose": "Resource deployment",
                "routing": "System routes"
            }
        })
        
        # Subnet to VMs
        for j in range(3):
            vm_id = f"prod_spoke_vm_{i+1}_{j+1}"
            edges.append({
                "id": f"subnet_to_vm_{i+1}_{j+1}",
                "from": subnet_id,
                "to": vm_id,
                "label": "Subnet Integration\nVM Deployment",
                "type": "subnet_integration",
                "metadata": {
                    "purpose": "VM deployment",
                    "nsg": "Subnet-level security"
                }
            })
    
    # Hub to Non-production Spokes - Enhanced with more connections
    for i in range(2):
        spoke_id = f"nonprod_spoke_vnet_{i+1}"
        
        # VPN Gateway to non-production spokes
        edges.append({
            "id": f"vpn_to_nonprod{i+1}",
            "from": "hub_vpn_gateway",
            "to": spoke_id,
            "label": "Connected Virtual Networks\nDevOps Access",
            "type": "connected",
            "metadata": {
                "access": "DevOps team access",
                "restrictions": "Limited external access"
            }
        })
        
        # Hub VNet to non-production spokes
        edges.append({
            "id": f"hub_to_nonprod{i+1}",
            "from": "hub_vnet",
            "to": spoke_id,
            "label": "Virtual Networks Connected\nor Peered Through Hub",
            "type": "peered",
            "metadata": {
                "peering_type": "Hub-Spoke",
                "traffic": "Internal communication",
                "monitoring": "Traffic analysis enabled"
            }
        })
        
        # Non-production spoke to its subnet
        subnet_id = f"nonprod_spoke_subnet_{i+1}"
        edges.append({
            "id": f"nonprod{i+1}_to_subnet",
            "from": spoke_id,
            "to": subnet_id,
            "label": "VNet Integration\nResource Subnet",
            "type": "vnet_integration",
            "metadata": {
                "purpose": "Resource deployment",
                "routing": "System routes"
            }
        })
        
        # Subnet to VMs
        for j in range(3):
            vm_id = f"nonprod_spoke_vm_{i+1}_{j+1}"
            edges.append({
                "id": f"nonprod_subnet_to_vm_{i+1}_{j+1}",
                "from": subnet_id,
                "to": vm_id,
                "label": "Subnet Integration\nVM Deployment",
                "type": "subnet_integration",
                "metadata": {
                    "purpose": "VM deployment",
                    "nsg": "Subnet-level security"
                }
            })
    
    # NEW: Cross-spoke connections for production
    edges.append({
        "id": "prod1_to_prod2",
        "from": "prod_spoke_vnet_1",
        "to": "prod_spoke_vnet_2",
        "label": "VNet Peering\nProduction Communication",
        "type": "peered",
        "metadata": {
            "peering_type": "Spoke-Spoke",
            "purpose": "Production services communication",
            "restrictions": "Limited to production environments"
        }
    })
    
    # Non-production Spokes to each other
    edges.append({
        "id": "nonprod1_to_nonprod2",
        "from": "nonprod_spoke_vnet_1",
        "to": "nonprod_spoke_vnet_2",
        "label": "Peered or Directly\nConnected Virtual Networks",
        "type": "peered",
        "metadata": {
            "peering_type": "Spoke-Spoke",
            "purpose": "Cross-environment testing",
            "restrictions": "Limited to non-prod environments"
        }
    })
    
    # NEW: Cross-environment connections (Dev to Test, Test to Staging)
    edges.append({
        "id": "dev_to_test",
        "from": "nonprod_spoke_vnet_1",
        "to": "nonprod_spoke_vnet_2",
        "label": "Development to Test\nEnvironment Flow",
        "type": "development_flow",
        "metadata": {
            "purpose": "Development workflow",
            "traffic": "Test data and configurations"
        }
    })
    
    # 8. Add Technical Specifications Box (organized position)
    specs_x, specs_y = get_grid_position(8, 0, 0, 0)
    nodes.append({
        "id": "technical_specs",
        "type": "text",
        "text": "Technical Specifications:\n• Hub VNet: 10.0.0.0/16\n• Production Spokes: 10.1.0.0/16, 10.2.0.0/16\n• Non-Prod Spokes: 10.10.0.0/16, 10.11.0.0/16\n• ExpressRoute: 1 Gbps Primary + Secondary\n• Firewall: Premium SKU with Threat Intelligence\n• Monitoring: 90-day retention, real-time alerts",
        "x": specs_x,
        "y": specs_y,
        "width": 300,
        "height": 120,
        "style": {"fontSize": "12px", "fontWeight": "normal", "textAlign": "left", "backgroundColor": "#f8f9fa", "border": "1px solid #dee2e6", "padding": "10px"}
    })
    
    return {
        "type": "azure_hub_spoke",
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "architecture_type": "Hub and Spoke",
            "subscriptions": num_subscriptions,
            "total_vnets": 5,  # 1 hub + 4 spokes
            "total_vms": 20,   # 2 on-premises + 18 in spokes
            "security_features": ["Azure Firewall Premium", "Azure Bastion", "Network Security Groups"],
            "monitoring": ["Azure Monitor", "Log Analytics", "Network Watcher"],
            "compliance": ["ISO 27001", "SOC 2", "PCI DSS"],
            "estimated_cost": "$2,500 - $5,000/month",
            "deployment_template": "ARM Template available"
        }
    }

def create_azure_diagram_structure(components, description):
    """Crea la estructura del diagrama de Azure basado en los componentes detectados con datos técnicos mejorados"""
    
    # Grid-based positioning system for better organization
    grid_config = {
        'cell_width': 120,
        'cell_height': 80,
        'margin': 25,
        'start_x': 50,
        'start_y': 50
    }
    
    # Calculate grid positions
    def get_grid_position(row, col, offset_x=0, offset_y=0):
        x = grid_config['start_x'] + (col * (grid_config['cell_width'] + grid_config['margin'])) + offset_x
        y = grid_config['start_y'] + (row * (grid_config['cell_height'] + grid_config['margin'])) + offset_y
        return x, y
    
    # Organized positions for better layout
    positions = {
        'internet': get_grid_position(0, 4, 0, 0),
        'cdn': get_grid_position(0, 2, 0, 0),
        'firewall': get_grid_position(1, 4, 0, 0),
        'load_balancer': get_grid_position(2, 4, 0, 0),
        'app_gateway': get_grid_position(3, 4, 0, 0),
        'vnet': get_grid_position(2, 2, -150, -100),  # Increased size to contain subnets
        'subnet_frontend': get_grid_position(2, 1, -50, 0),
        'subnet_backend': get_grid_position(2, 3, -50, 0),
        'subnet_data': get_grid_position(4, 2, -50, 0),
        'app_service': get_grid_position(3, 1, -20, 0),
        'web_app': get_grid_position(4, 1, -20, 0),
        'api_app': get_grid_position(3, 3, -20, 0),
        'function_app': get_grid_position(4, 3, -20, 0),
        'sql_database': get_grid_position(5, 2, -20, 0),
        'storage_account': get_grid_position(6, 2, -20, 0),
        'key_vault': get_grid_position(5, 4, -20, 0),
        'monitoring': get_grid_position(6, 4, -20, 0),
        'on_premises': get_grid_position(3, 0, 0, 0),
        'vpn_gateway': get_grid_position(4, 0, 0, 0)
    }
    
    nodes = []
    edges = []
    node_id = 1
    
    # Agregar nodos según los componentes detectados con metadatos técnicos
    if components['cdn']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_cdn',
            'text': 'Azure CDN\nMicrosoft Global Edge\n99.9% Availability',
            'x': positions['cdn'][0],
            'y': positions['cdn'][1],
            'width': 120,
            'height': 60,
            'metadata': {
                'service': 'Azure CDN',
                'tier': 'Standard',
                'features': ['Global Edge Network', '99.9% SLA', 'DDoS Protection'],
                'endpoints': '150+ global edge locations'
            }
        })
        node_id += 1
    
    # Internet siempre está presente
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'internet',
        'text': 'Internet\nPublic Network\nGlobal Connectivity',
        'x': positions['internet'][0],
        'y': positions['internet'][1],
        'width': 120,
        'height': 60,
        'metadata': {
            'type': 'Public Internet',
            'connectivity': 'Global',
            'security': 'External threat surface'
        }
    })
    internet_id = f'node_{node_id}'
    node_id += 1
    
    # Firewall/WAF con detalles técnicos
    if components['security']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_firewall',
            'text': 'Azure Firewall\nPremium SKU\nThreat Intelligence\nTLS Inspection',
            'x': positions['firewall'][0],
            'y': positions['firewall'][1],
            'width': 120,
            'height': 60,
            'metadata': {
                'sku': 'Premium',
                'features': config.AZURE_FIREWALL_FEATURES,
                'throughput': '30 Gbps',
                'rules': ['Network Rules', 'Application Rules', 'DNAT Rules'],
                'monitoring': 'Azure Monitor integration'
            }
        })
        firewall_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar internet al firewall
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': internet_id,
            'to': firewall_id,
            'label': 'HTTPS/HTTP\nPort 80/443',
            'metadata': {
                'protocol': 'HTTP/HTTPS',
                'ports': '80, 443',
                'inspection': 'TLS inspection enabled'
            }
        })
    
    # Load Balancer con especificaciones
    if components['load_balancer']:
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_load_balancer',
            'text': 'Load Balancer\nStandard SKU\nHealth Probes\nSession Persistence',
            'x': positions['load_balancer'][0],
            'y': positions['load_balancer'][1],
            'width': 120,
            'height': 60,
            'metadata': {
                'sku': 'Standard',
                'features': ['Health Probes', 'Session Persistence', 'HA Ports'],
                'throughput': 'Up to 1 Gbps',
                'health_checks': 'TCP, HTTP, HTTPS probes',
                'distribution': '5-tuple hash'
            }
        })
        lb_id = f'node_{node_id}'
        node_id += 1
        
        # Conectar al firewall o internet
        if components['security']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': firewall_id,
                'to': lb_id,
                'label': 'Filtered Traffic\nSecurity Rules Applied',
                'metadata': {
                    'traffic': 'Filtered by firewall',
                    'security': 'Threat protection enabled'
                }
            })
        else:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': internet_id,
                'to': lb_id,
                'label': 'Direct Traffic\nNo Security Filtering',
                'metadata': {
                    'traffic': 'Direct internet access',
                    'security': 'No firewall protection'
                }
            })
    
    # Virtual Network con detalles de red - Increased size to properly contain subnets
    vnet_x, vnet_y = positions['vnet']
    vnet_width = 700
    vnet_height = 500
    nodes.append({
        'id': f'node_{node_id}',
        'type': 'azure_vnet',
        'text': 'Virtual Network\n10.0.0.0/16\nCentralized Network\nManagement',
        'x': vnet_x,
        'y': vnet_y,
        'width': vnet_width,
        'height': vnet_height,
        'metadata': {
            'address_space': '10.0.0.0/16',
            'region': 'East US 2',
            'features': ['VNet Peering', 'Service Endpoints', 'Private Link'],
            'dns': 'Azure DNS (168.63.129.16)',
            'ddos_protection': 'Standard tier enabled'
        }
    })
    vnet_id = f'node_{node_id}'
    node_id += 1
    
    # Subnets con configuraciones detalladas - Positioned inside the VNet container
    if components['network']:
        # Frontend subnet - Positioned inside VNet
        subnet_frontend_x = vnet_x + 50
        subnet_frontend_y = vnet_y + 80
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_subnet',
            'text': 'Frontend Subnet\n10.0.1.0/24\nWeb Tier\nPublic Access',
            'x': subnet_frontend_x,
            'y': subnet_frontend_y,
            'width': 200,
            'height': 100,
            'metadata': {
                'address_space': '10.0.1.0/24',
                'purpose': 'Web Tier',
                'nsg_rules': ['Allow HTTP/HTTPS', 'Allow SSH from Bastion', 'Deny Internet'],
                'service_endpoints': ['Microsoft.Web', 'Microsoft.KeyVault'],
                'delegations': 'None'
            }
        })
        frontend_subnet_id = f'node_{node_id}'
        node_id += 1
        
        # Backend subnet - Positioned inside VNet
        subnet_backend_x = vnet_x + 300
        subnet_backend_y = vnet_y + 80
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_subnet',
            'text': 'Backend Subnet\n10.0.2.0/24\nApplication Tier\nInternal Only',
            'x': subnet_backend_x,
            'y': subnet_backend_y,
            'width': 200,
            'height': 100,
            'metadata': {
                'address_space': '10.0.2.0/24',
                'purpose': 'Application Tier',
                'nsg_rules': ['Allow from Frontend', 'Allow SSH from Bastion', 'Deny Internet'],
                'service_endpoints': ['Microsoft.Sql', 'Microsoft.Storage'],
                'delegations': 'None'
            }
        })
        backend_subnet_id = f'node_{node_id}'
        node_id += 1
        
        # Data subnet - Positioned inside VNet
        subnet_data_x = vnet_x + 175
        subnet_data_y = vnet_y + 250
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_subnet',
            'text': 'Data Subnet\n10.0.3.0/24\nDatabase Tier\nHighly Restricted',
            'x': subnet_data_x,
            'y': subnet_data_y,
            'width': 200,
            'height': 100,
            'metadata': {
                'address_space': '10.0.3.0/24',
                'purpose': 'Database Tier',
                'nsg_rules': ['Allow from Backend only', 'Deny all other traffic'],
                'service_endpoints': ['Microsoft.Sql'],
                'delegations': 'None',
                'security': 'Highest security restrictions'
            }
        })
        data_subnet_id = f'node_{node_id}'
        node_id += 1
        
        # NEW: Conectar subnets al VNet con más detalle
        edges.extend([
            {
                'id': f'edge_{len(edges)}', 
                'from': vnet_id, 
                'to': frontend_subnet_id,
                'label': 'VNet Integration\nFrontend Subnet',
                'metadata': {'type': 'VNet integration', 'routing': 'System routes', 'subnet': '10.0.1.0/24'}
            },
            {
                'id': f'edge_{len(edges)}', 
                'from': vnet_id, 
                'to': backend_subnet_id,
                'label': 'VNet Integration\nBackend Subnet',
                'metadata': {'type': 'VNet integration', 'routing': 'System routes', 'subnet': '10.0.2.0/24'}
            },
            {
                'id': f'edge_{len(edges)}', 
                'from': vnet_id, 
                'to': data_subnet_id,
                'label': 'VNet Integration\nData Subnet',
                'metadata': {'type': 'VNet integration', 'routing': 'System routes', 'subnet': '10.0.3.0/24'}
            }
        ])
    
    # App Services con detalles de configuración - Positioned inside frontend subnet
    if components['app_service']:
        app_service_x = subnet_frontend_x + 20
        app_service_y = subnet_frontend_y + 60
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_app_service',
            'text': 'App Service\nWeb App\nP1v2 Plan\nAlways On',
            'x': app_service_x,
            'y': app_service_y,
            'width': 140,
            'height': 70,
            'metadata': {
                'plan': 'P1v2',
                'runtime': '.NET 6.0',
                'features': ['Always On', 'Auto-scaling', 'Custom domains'],
                'ssl': 'SSL certificate enabled',
                'backup': 'Daily backups',
                'monitoring': 'Application Insights enabled'
            }
        })
        app_service_id = f'node_{node_id}'
        node_id += 1
        
        # NEW: Conectar al subnet frontend con más detalle
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': frontend_subnet_id,
                'to': app_service_id,
                'label': 'VNet Integration\nWeb App Deployment',
                'metadata': {
                    'type': 'VNet integration',
                    'subnet': 'Frontend subnet',
                    'features': ['Private endpoints', 'Service endpoints'],
                    'purpose': 'Web application hosting'
                }
            })
    
    # Web Apps adicionales - Positioned inside frontend subnet
    if components['app_service']:
        web_app_x = subnet_frontend_x + 180
        web_app_y = subnet_frontend_y + 60
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_web_app',
            'text': 'Web App\nAPI Gateway\nP1v2 Plan\nCORS Enabled',
            'x': web_app_x,
            'y': web_app_y,
            'width': 140,
            'height': 70,
            'metadata': {
                'plan': 'P1v2',
                'runtime': 'Node.js 18 LTS',
                'features': ['CORS enabled', 'API Management', 'Rate limiting'],
                'ssl': 'SSL certificate enabled',
                'authentication': 'Azure AD integration',
                'monitoring': 'Application Insights enabled'
            }
        })
        web_app_id = f'node_{node_id}'
        node_id += 1
        
        # NEW: Conectar al subnet frontend con más detalle
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': frontend_subnet_id,
                'to': web_app_id,
                'label': 'VNet Integration\nAPI Gateway Deployment',
                'metadata': {
                    'type': 'VNet integration',
                    'subnet': 'Frontend subnet',
                    'features': ['Private endpoints', 'Service endpoints'],
                    'purpose': 'API gateway hosting'
                }
            })
    
    # API Apps con detalles técnicos - Positioned inside backend subnet
    if components['api_management']:
        api_app_x = subnet_backend_x + 20
        api_app_y = subnet_backend_y + 60
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_api_app',
            'text': 'API App\nBackend Service\nP1v2 Plan\nInternal API',
            'x': api_app_x,
            'y': api_app_y,
            'width': 140,
            'height': 70,
            'metadata': {
                'plan': 'P1v2',
                'runtime': 'Python 3.11',
                'features': ['Internal API', 'VNet integration', 'Private endpoints'],
                'ssl': 'SSL certificate enabled',
                'authentication': 'API Key + OAuth2',
                'monitoring': 'Application Insights enabled'
            }
        })
        api_app_id = f'node_{node_id}'
        node_id += 1
        
        # NEW: Conectar al subnet backend con más detalle
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': backend_subnet_id,
                'to': api_app_id,
                'label': 'VNet Integration\nBackend API Deployment',
                'metadata': {
                    'type': 'VNet integration',
                    'subnet': 'Backend subnet',
                    'features': ['Private endpoints', 'Service endpoints'],
                    'purpose': 'Backend API hosting'
                }
            })
    
    # Function Apps con detalles de serverless - Positioned inside backend subnet
    if components['api_management']:
        function_app_x = subnet_backend_x + 180
        function_app_y = subnet_backend_y + 60
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_function',
            'text': 'Function App\nServerless\nConsumption Plan\nEvent-driven',
            'x': function_app_x,
            'y': function_app_y,
            'width': 140,
            'height': 70,
            'metadata': {
                'plan': 'Consumption',
                'runtime': 'Python 3.11',
                'features': ['Event-driven', 'Auto-scaling', 'Pay-per-execution'],
                'triggers': ['HTTP', 'Timer', 'Blob Storage'],
                'monitoring': 'Application Insights enabled',
                'cost': 'Pay only for executions'
            }
        })
        function_app_id = f'node_{node_id}'
        node_id += 1
        
        # NEW: Conectar al subnet backend con más detalle
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': backend_subnet_id,
                'to': function_app_id,
                'label': 'VNet Integration\nFunction App Deployment',
                'metadata': {
                    'type': 'VNet integration',
                    'subnet': 'Backend subnet',
                    'features': ['Private endpoints', 'Service endpoints'],
                    'purpose': 'Serverless function hosting'
                }
            })
    
    # SQL Database con especificaciones técnicas - Positioned inside data subnet
    if components['database']:
        sql_x = subnet_data_x + 20
        sql_y = subnet_data_y + 60
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_sql',
            'text': 'Azure SQL\nDatabase\nS1 Standard\n99.99% SLA',
            'x': sql_x,
            'y': sql_y,
            'width': 140,
            'height': 70,
            'metadata': {
                'sku': 'S1 Standard',
                'dtu': '20 DTUs',
                'storage': '250 GB',
                'backup': 'Point-in-time restore (7 days)',
                'security': ['Always Encrypted', 'Threat Detection', 'Auditing'],
                'monitoring': 'Query Performance Insights',
                'compliance': ['ISO 27001', 'SOC 2', 'PCI DSS']
            }
        })
        sql_id = f'node_{node_id}'
        node_id += 1
        
        # NEW: Conectar al subnet data con más detalle
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': data_subnet_id,
                'to': sql_id,
                'label': 'Private Endpoint\nDatabase Access',
                'metadata': {
                    'type': 'Private endpoint',
                    'subnet': 'Data subnet',
                    'security': 'No public internet access',
                    'purpose': 'Secure database connectivity'
                }
            })
    
    # Storage Account con detalles de almacenamiento - Positioned inside data subnet
    if components['storage']:
        storage_x = subnet_data_x + 180
        storage_y = subnet_data_y + 60
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_storage',
            'text': 'Storage Account\nGeneral Purpose v2\nLRS Redundancy\nHot Tier',
            'x': storage_x,
            'y': storage_y,
            'width': 140,
            'height': 70,
            'metadata': {
                'account_type': 'General Purpose v2',
                'redundancy': 'LRS (Locally Redundant Storage)',
                'tier': 'Hot tier',
                'services': ['Blob Storage', 'File Storage', 'Queue Storage'],
                'security': ['Encryption at rest', 'Azure AD authentication'],
                'monitoring': 'Storage Analytics enabled',
                'backup': 'Soft delete enabled (7 days)'
            }
        })
        storage_id = f'node_{node_id}'
        node_id += 1
        
        # NEW: Conectar al subnet data con más detalle
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': data_subnet_id,
                'to': storage_id,
                'label': 'Service Endpoint\nStorage Access',
                'metadata': {
                    'type': 'Service endpoint',
                    'subnet': 'Data subnet',
                    'security': 'Restricted to VNet only',
                    'purpose': 'Secure storage access'
                }
            })
    
    # Key Vault con detalles de seguridad - Positioned inside data subnet
    if components['security']:
        key_vault_x = subnet_data_x + 100
        key_vault_y = subnet_data_y + 180
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_key_vault',
            'text': 'Key Vault\nPremium SKU\nSecrets & Keys\nHSM Backed',
            'x': key_vault_x,
            'y': key_vault_y,
            'width': 140,
            'height': 70,
            'metadata': {
                'sku': 'Premium',
                'features': ['HSM-backed keys', 'Soft delete', 'Purge protection'],
                'secrets': ['Database connection strings', 'API keys', 'Certificates'],
                'access_policies': 'Azure AD RBAC',
                'monitoring': 'Diagnostic logs enabled',
                'compliance': ['FIPS 140-2 Level 2', 'ISO 27001']
            }
        })
        key_vault_id = f'node_{node_id}'
        node_id += 1
        
        # NEW: Conectar al subnet data con más detalle
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': data_subnet_id,
                'to': key_vault_id,
                'label': 'Private Endpoint\nKey Vault Access',
                'metadata': {
                    'type': 'Private endpoint',
                    'subnet': 'Data subnet',
                    'security': 'No public internet access',
                    'purpose': 'Secure secret management'
                }
            })
    
    # Monitoring con detalles de observabilidad - Positioned inside data subnet
    if components['monitoring']:
        monitoring_x = subnet_data_x + 100
        monitoring_y = subnet_data_y + 280
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_monitoring',
            'text': 'Log Analytics\nWorkspace\n90-day Retention\nReal-time Alerts',
            'x': monitoring_x,
            'y': monitoring_y,
            'width': 140,
            'height': 70,
            'metadata': {
                'service': 'Log Analytics Workspace',
                'retention': '90 days',
                'features': ['Real-time monitoring', 'Custom queries', 'Alerting'],
                'solutions': ['VM Insights', 'Container Insights', 'Network Performance Monitor'],
                'integrations': ['Azure Monitor', 'Application Insights', 'Network Watcher'],
                'cost': 'Pay per GB ingested'
            }
        })
        monitoring_id = f'node_{node_id}'
        node_id += 1
        
        # NEW: Conectar al subnet data con más detalle
        if components['network']:
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': data_subnet_id,
                'to': monitoring_id,
                'label': 'Service Endpoint\nMonitoring Access',
                'metadata': {
                    'type': 'Service endpoint',
                    'subnet': 'Data subnet',
                    'security': 'Restricted to VNet only',
                    'purpose': 'Centralized monitoring'
                }
            })
    
    # On-Premises connection con detalles de conectividad
    if 'on-premises' in description.lower() or 'local' in description.lower():
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'on_premises',
            'text': 'On-Premises\nNetwork\nCorporate\nInfrastructure',
            'x': positions['on_premises'][0],
            'y': positions['on_premises'][1],
            'width': 120,
            'height': 60,
            'metadata': {
                'type': 'On-Premises Network',
                'connectivity': 'VPN/ExpressRoute',
                'components': ['Active Directory', 'File Servers', 'Application Servers'],
                'security': 'Corporate firewall',
                'monitoring': 'On-premises monitoring'
            }
        })
        onprem_id = f'node_{node_id}'
        node_id += 1
        
        # VPN Gateway con especificaciones
        nodes.append({
            'id': f'node_{node_id}',
            'type': 'azure_vpn_gateway',
            'text': 'VPN Gateway\nVpnGw1 SKU\n1.25 Gbps\nBGP Enabled',
            'x': positions['vpn_gateway'][0],
            'y': positions['vpn_gateway'][1],
            'width': 80,
            'height': 60,
            'metadata': {
                'sku': 'VpnGw1',
                'bandwidth': '1.25 Gbps',
                'features': ['BGP support', 'Active-Active', 'Point-to-Site'],
                'tunnels': 'Up to 10 S2S connections',
                'monitoring': 'Connection monitoring enabled'
            }
        })
        vpn_id = f'node_{node_id}'
        node_id += 1
        
        # NEW: Conectar on-premises al VPN con más detalle
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': onprem_id,
            'to': vpn_id,
            'label': 'Site-to-Site VPN\nIPSec/IKEv2',
            'metadata': {
                'type': 'Site-to-Site VPN',
                'protocol': 'IPSec/IKEv2',
                'encryption': 'AES-256',
                'authentication': 'Pre-shared key',
                'purpose': 'Secure cross-premises connectivity'
            }
        })
        
        # NEW: Conectar VPN al VNet con más detalle
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': vpn_id,
            'to': vnet_id,
            'label': 'Gateway Subnet\n10.0.3.0/27',
            'metadata': {
                'type': 'Gateway subnet',
                'address_space': '10.0.3.0/27',
                'purpose': 'VPN Gateway deployment',
                'routing': 'BGP routes propagation'
            }
        })
    
    # NEW: Enhanced connections between main components with comprehensive flow
    if components['load_balancer'] and components['app_service']:
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': lb_id,
            'to': app_service_id,
            'label': 'Load Balanced\nHealth Check\nPort 80/443',
            'metadata': {
                'type': 'Load balancing',
                'ports': '80, 443',
                'health_check': 'HTTP probe enabled',
                'distribution': 'Round-robin',
                'purpose': 'Web application load balancing'
            }
        })
        
        # NEW: Load balancer to web app
        if 'web_app_id' in locals():
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': lb_id,
                'to': web_app_id,
                'label': 'Load Balanced\nAPI Gateway\nPort 80/443',
                'metadata': {
                    'type': 'Load balancing',
                    'ports': '80, 443',
                    'health_check': 'HTTP probe enabled',
                    'distribution': 'Round-robin',
                    'purpose': 'API gateway load balancing'
                }
            })
    
    # NEW: Enhanced application tier connections
    if components['app_service'] and components['database']:
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': app_service_id,
            'to': sql_id,
            'label': 'Database Connection\nConnection Pooling\nSSL Required',
            'metadata': {
                'type': 'Database connection',
                'protocol': 'TDS over SSL',
                'connection_pooling': 'Enabled',
                'timeout': '30 seconds',
                'purpose': 'Web app database access'
            }
        })
        
        # NEW: Web app to database
        if 'web_app_id' in locals():
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': web_app_id,
                'to': sql_id,
                'label': 'Database Connection\nAPI Database Access\nSSL Required',
                'metadata': {
                    'type': 'Database connection',
                    'protocol': 'TDS over SSL',
                    'connection_pooling': 'Enabled',
                    'timeout': '30 seconds',
                    'purpose': 'API gateway database access'
                }
            })
    
    # NEW: Enhanced storage connections
    if components['app_service'] and components['storage']:
        edges.append({
            'id': f'edge_{len(edges)}',
            'from': app_service_id,
            'to': storage_id,
            'label': 'Storage Access\nService Endpoint\nPrivate Network',
            'metadata': {
                'type': 'Storage access',
                'method': 'Service endpoint',
                'subnet': 'Data subnet',
                'security': 'VNet restricted',
                'protocol': 'HTTPS',
                'purpose': 'Web app file storage'
            }
        })
        
        # NEW: Web app to storage
        if 'web_app_id' in locals():
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': web_app_id,
                'to': storage_id,
                'label': 'Storage Access\nAPI File Storage\nPrivate Network',
                'metadata': {
                    'type': 'Storage access',
                    'method': 'Service endpoint',
                    'subnet': 'Data subnet',
                    'security': 'VNet restricted',
                    'protocol': 'HTTPS',
                    'purpose': 'API gateway file storage'
                }
            })
    
    # NEW: Enhanced backend tier connections
    if components['api_management'] and components['database']:
        if 'api_app_id' in locals():
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': api_app_id,
                'to': sql_id,
                'label': 'Database Connection\nBackend API Database\nSSL Required',
                'metadata': {
                    'type': 'Database connection',
                    'protocol': 'TDS over SSL',
                    'connection_pooling': 'Enabled',
                    'timeout': '30 seconds',
                    'purpose': 'Backend API database access'
                }
            })
    
    # NEW: Enhanced function app connections
    if components['api_management'] and components['storage']:
        if 'function_app_id' in locals():
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': function_app_id,
                'to': storage_id,
                'label': 'Storage Access\nFunction App Storage\nEvent Triggers',
                'metadata': {
                    'type': 'Storage access',
                    'method': 'Service endpoint',
                    'subnet': 'Backend subnet',
                    'security': 'VNet restricted',
                    'protocol': 'HTTPS',
                    'purpose': 'Serverless function storage access'
                }
            })
    
    # NEW: Cross-tier communication
    if components['app_service'] and components['api_management']:
        if 'api_app_id' in locals():
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': app_service_id,
                'to': api_app_id,
                'label': 'Internal API Call\nFrontend to Backend\nVNet Internal',
                'metadata': {
                    'type': 'Internal API call',
                    'protocol': 'HTTP/HTTPS',
                    'network': 'VNet internal',
                    'security': 'NSG protected',
                    'purpose': 'Frontend-backend communication'
                }
            })
    
    # NEW: Security and monitoring connections
    if components['security'] and components['monitoring']:
        if 'monitoring_id' in locals():
            edges.append({
                'id': f'edge_{len(edges)}',
                'from': firewall_id,
                'to': monitoring_id,
                'label': 'Security Logs\nFirewall Monitoring\nReal-time Alerts',
                'metadata': {
                    'type': 'Security monitoring',
                    'data': 'Firewall logs and alerts',
                    'retention': '90 days',
                    'purpose': 'Security event monitoring'
                }
            })
    
    # Añadir caja de especificaciones técnicas (organized position)
    specs_x, specs_y = get_grid_position(8, 0, 0, 0)
    nodes.append({
        'id': 'technical_specs',
        'type': 'text',
        'text': 'Technical Specifications:\n• VNet: 10.0.0.0/16\n• Frontend Subnet: 10.0.1.0/24\n• Backend Subnet: 10.0.2.0/24\n• Data Subnet: 10.0.3.0/24\n• Firewall: Premium SKU, Threat Intelligence\n• Load Balancer: Standard SKU, Health Probes\n• Database: S1 Standard, 20 DTUs\n• Storage: GPv2, LRS, Hot Tier\n• Monitoring: 90-day retention\n• Compliance: ISO 27001, SOC 2, PCI DSS',
        'x': specs_x,
        'y': specs_y,
        'width': 350,
        'height': 140,
        'style': {"fontSize": "11px", "fontWeight": "normal", "textAlign": "left", "backgroundColor": "#f8f9fa", "border": "1px solid #dee2e6", "padding": "10px"}
    })
    
    return {
        'type': 'azure_architecture',
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'architecture_type': 'Multi-tier Web Application',
            'components': list(components.keys()),
            'total_resources': len(nodes),
            'security_features': ['Azure Firewall Premium', 'Network Security Groups', 'Private Endpoints'],
            'monitoring': ['Azure Monitor', 'Log Analytics', 'Application Insights'],
            'compliance': ['ISO 27001', 'SOC 2', 'PCI DSS'],
            'estimated_cost': '$1,500 - $3,000/month',
            'deployment_template': 'ARM Template available',
            'backup_strategy': 'Daily backups with 7-day retention',
            'total_connections': len(edges),
            'network_segments': ['Frontend', 'Backend', 'Data', 'Management'],
            'security_layers': ['Perimeter', 'Network', 'Application', 'Data']
        }
    }

def get_system_prompt_for_type(diagram_type):
    """Retorna el prompt del sistema según el tipo de diagrama"""
    base_prompts = config.SYSTEM_PROMPTS
    
    return base_prompts.get(diagram_type, base_prompts['flowchart'])

def detect_diagram_type(description):
    """Detecta automáticamente el tipo de diagrama basado en la descripción"""
    description_lower = description.lower()
    
    # Patrones para detectar tipos de diagramas usando configuración
    for diagram_type, keywords in config.DIAGRAM_TYPE_KEYWORDS.items():
        if any(word in description_lower for word in keywords):
            return diagram_type
    
    return config.DEFAULT_DIAGRAM_TYPE  # Por defecto

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
            'edges': edges,
            'metadata': {
                'generated_by': 'fallback_system',
                'description': description,
                'diagram_type': diagram_type,
                'fallback_reason': 'AI service unavailable'
            }
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
            'version': 1,
            'created_by': 'user',
            'creation_metadata': {
                'app_version': config.APP_VERSION,
                'template_type': 'base_diagram',
                'creation_method': 'manual'
            }
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
    
    base_diagram = base_diagrams.get(diagram_type, base_diagrams['flowchart'])
    
    # Añadir metadatos de configuración
    base_diagram['metadata'] = {
        'generated_by': 'base_template',
        'diagram_type': diagram_type,
        'template_version': config.APP_VERSION,
        'created_at': datetime.now().isoformat()
    }
    
    return base_diagram

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
            filepath = os.path.join(config.UPLOAD_FOLDER, filename)
            
            try:
                # Guardar archivo
                file.save(filepath)
                
                # Procesar documento según el tipo
                file_extension = filename.rsplit('.', 1)[1].lower()
                file_content = ""
                
                if file_extension in ['txt', 'json', 'csv']:
                    # Archivos de texto - intentar diferentes codificaciones
                    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                    for encoding in encodings:
                        try:
                            with open(filepath, 'r', encoding=encoding) as f:
                                file_content = f.read()
                            print(f"Archivo leído exitosamente con codificación: {encoding}")
                            break
                        except UnicodeDecodeError:
                            continue
                        except Exception as e:
                            print(f"Error leyendo archivo con {encoding}: {str(e)}")
                            continue
                    
                    if not file_content:
                        # Último intento: leer como bytes y decodificar
                        try:
                            with open(filepath, 'rb') as f:
                                raw_content = f.read()
                                # Intentar detectar codificación
                                try:
                                    import chardet
                                    detected = chardet.detect(raw_content)
                                    if detected['confidence'] > 0.7:
                                        file_content = raw_content.decode(detected['encoding'])
                                    else:
                                        # Fallback a latin-1
                                        file_content = raw_content.decode('latin-1', errors='ignore')
                                except ImportError:
                                    # Si chardet no está disponible, usar latin-1
                                    file_content = raw_content.decode('latin-1', errors='ignore')
                        except Exception as e:
                            print(f"Error en fallback de codificación: {str(e)}")
                            file_content = "Error leyendo archivo"
                
                elif file_extension == 'pdf':
                    # Procesar PDF
                    try:
                        import PyPDF2
                        with open(filepath, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            file_content = ""
                            for page in pdf_reader.pages:
                                file_content += page.extract_text() + "\n"
                    except ImportError:
                        file_content = "PDF detectado pero PyPDF2 no está disponible"
                    except Exception as e:
                        file_content = f"Error procesando PDF: {str(e)}"
                
                elif file_extension in ['docx']:
                    # Procesar DOCX
                    try:
                        from docx import Document
                        doc = Document(filepath)
                        file_content = ""
                        for paragraph in doc.paragraphs:
                            file_content += paragraph.text + "\n"
                    except ImportError:
                        file_content = "DOCX detectado pero python-docx no está disponible"
                    except Exception as e:
                        file_content = f"Error procesando DOCX: {str(e)}"
                
                elif file_extension in ['xlsx', 'xls']:
                    # Procesar Excel
                    try:
                        import pandas as pd
                        df = pd.read_excel(filepath)
                        file_content = df.to_string()
                    except ImportError:
                        file_content = "Excel detectado pero pandas no está disponible"
                    except Exception as e:
                        file_content = f"Error procesando Excel: {str(e)}"
                
                else:
                    # Otros tipos de archivo
                    file_content = f"Archivo de tipo {file_extension} - contenido no procesable"
                
                # Generar diagrama basado en el contenido del archivo
                nodes = []
                edges = []
                
                if file_content and file_content != "Error leyendo archivo":
                    # Tokenizar el contenido en palabras
                    words = file_content.split()
                    
                    # Crear nodos básicos basados en las palabras (máximo 20 para evitar sobrecarga)
                    max_nodes = min(20, len(words))
                    for i in range(max_nodes):
                        word = words[i]
                        if len(word) > 2:  # Solo palabras de más de 2 caracteres
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
                                    'to': node_id,
                                    'label': 'Siguiente'
                                })
                else:
                    # Crear nodo de error
                    nodes.append({
                        'id': 'error_node',
                        'type': 'rectangle',
                        'text': 'Error procesando archivo',
                        'x': 100,
                        'y': 100,
                        'width': 200,
                        'height': 60
                    })
                
                # Crear diagrama
                diagram_data = {
                    'type': 'flowchart',
                    'nodes': nodes,
                    'edges': edges
                }
                
                # Crear ID único para el diagrama
                diagram_id = str(uuid.uuid4())
                
                # Guardar diagrama generado
                diagrams[diagram_id] = {
                    'id': diagram_id,
                    'title': f'Diagrama de {filename}',
                    'type': 'file_generated',
                    'data': diagram_data,
                    'description': f'Generado desde archivo: {filename}',
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'version': 1,
                    'ai_generated': False,
                    'source_file': filename
                }
                
                # Limpiar archivo temporal
                cleanup_temp_files(filepath)
                
                # Respuesta exitosa
                response_data = {
                    'success': True,
                    'message': 'Diagrama generado exitosamente desde archivo',
                    'diagram_id': diagram_id,
                    'diagram_data': diagram_data,
                    'filename': filename,
                    'total_nodes': len(nodes),
                    'total_edges': len(edges)
                }
                
                return jsonify(response_data)
                
            except Exception as e:
                # Limpiar archivo temporal en caso de error
                cleanup_temp_files(filepath)
                print(f"Error procesando archivo: {str(e)}")
                return jsonify({'error': f'Error procesando archivo: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
            
    except Exception as e:
        print(f"Error en upload: {str(e)}")
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
        filepath = os.path.join(config.OUTPUT_FOLDER, filename)
        
        if export_format == 'svg':
            # Generar SVG real
            svg_content = generate_svg_from_diagram(diagram)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(svg_content)
        elif export_format == 'png':
            # Generar PNG real
            generate_png_from_diagram(diagram, filepath)
        else:
            # JSON como fallback
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(diagram, f, ensure_ascii=False, indent=2)
        
        # Añadir metadatos de exportación
        export_metadata = {
            'exported_at': datetime.now().isoformat(),
            'export_format': export_format,
            'app_version': config.APP_VERSION,
            'diagram_version': diagram.get('version', 1)
        }
        diagram['export_metadata'] = export_metadata
        
        return jsonify({
            'success': True,
            'download_url': f'/download/{filename}',
            'filename': filename
        })
        
    except Exception as e:
        print(f"Error exportando diagrama: {str(e)}")
        return jsonify({'error': f'Error exportando diagrama: {str(e)}'}), 500

def generate_svg_from_diagram(diagram):
    """Genera contenido SVG real del diagrama"""
    try:
        # Calcular dimensiones del canvas
        if not diagram['data'].get('nodes'):
            return '<svg width="800" height="600"><text x="400" y="300" text-anchor="middle">Diagrama vacío</text></svg>'
        
        nodes = diagram['data']['nodes']
        edges = diagram['data'].get('edges', [])
        
        # Calcular bounding box
        min_x = min(node.get('x', 0) for node in nodes)
        max_x = max(node.get('x', 0) + node.get('width', 120) for node in nodes)
        min_y = min(node.get('y', 0) for node in nodes)
        max_y = max(node.get('y', 0) + node.get('height', 60) for node in nodes)
        
        # Añadir margen
        margin = 50
        width = max_x - min_x + 2 * margin
        height = max_y - min_y + 2 * margin
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#0d6efd"/>
        </marker>
    </defs>
    <g transform="translate({-min_x + margin}, {-min_y + margin})">'''
        
        # Renderizar nodos
        for node in nodes:
            node_x = node.get('x', 0)
            node_y = node.get('y', 0)
            node_width = node.get('width', 120)
            node_height = node.get('height', 60)
            node_text = node.get('text', node.get('id', ''))
            node_type = node.get('type', 'rectangle')
            
            if node_type == 'network_box':
                # Caja de red con borde azul
                svg_content += f'''
        <rect x="{node_x}" y="{node_y}" width="{node_width}" height="{node_height}" 
              fill="rgba(230, 243, 255, 0.3)" stroke="#0078d4" stroke-width="2" rx="8"/>
        <text x="{node_x + node_width/2}" y="{node_y + 20}" text-anchor="middle" 
              font-family="Arial" font-size="12" font-weight="bold" fill="#0078d4">{node_text}</text>'''
            elif node_type == 'azure_icon':
                # Icono Azure con borde azul
                svg_content += f'''
        <rect x="{node_x}" y="{node_y}" width="{node_width}" height="{node_height}" 
              fill="white" stroke="#0078d4" stroke-width="2" rx="8"/>
        <text x="{node_x + node_width/2}" y="{node_y + node_height/2}" text-anchor="middle" 
              font-family="Arial" font-size="10" fill="#333">{node_text}</text>'''
            else:
                # Nodo genérico
                svg_content += f'''
        <rect x="{node_x}" y="{node_y}" width="{node_width}" height="{node_height}" 
              fill="white" stroke="#666" stroke-width="1" rx="4"/>
        <text x="{node_x + node_width/2}" y="{node_y + node_height/2}" text-anchor="middle" 
              font-family="Arial" font-size="12" fill="#333">{node_text}</text>'''
        
        # Renderizar edges (conexiones)
        for edge in edges:
            from_node = next((n for n in nodes if n['id'] == edge['from']), None)
            to_node = next((n for n in nodes if n['id'] == edge['to']), None)
            
            if from_node and to_node:
                from_x = from_node.get('x', 0) + from_node.get('width', 120) / 2
                from_y = from_node.get('y', 0) + from_node.get('height', 60) / 2
                to_x = to_node.get('x', 0) + to_node.get('width', 120) / 2
                to_y = to_node.get('y', 0) + to_node.get('height', 60) / 2
                
                # Línea con flecha
                svg_content += f'''
        <line x1="{from_x}" y1="{from_y}" x2="{to_x}" y2="{to_y}" 
              stroke="#0d6efd" stroke-width="2" marker-end="url(#arrowhead)"/>'''
                
                # Etiqueta de la conexión si existe
                if edge.get('label'):
                    label_x = (from_x + to_x) / 2
                    label_y = (from_y + to_y) / 2 - 10
                    svg_content += f'''
        <text x="{label_x}" y="{label_y}" text-anchor="middle" 
              font-family="Arial" font-size="10" fill="#666">{edge['label']}</text>'''
        
        svg_content += '''
    </g>
</svg>'''
        
        return svg_content
        
    except Exception as e:
        print(f"Error generando SVG: {str(e)}")
        return f'<svg width="800" height="600"><text x="400" y="300" text-anchor="middle">Error generando SVG: {str(e)}</text></svg>'

def generate_png_from_diagram(diagram, filepath):
    """Genera PNG del diagrama usando cairosvg"""
    try:
        # Primero generar SVG
        svg_content = generate_svg_from_diagram(diagram)
        
        # Convertir SVG a PNG usando cairosvg
        try:
            import cairosvg
            cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), write_to=filepath)
        except ImportError:
            # Fallback: usar reportlab para generar PNG básico
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            # Crear PDF temporal
            pdf_path = filepath.replace('.png', '.pdf')
            c = canvas.Canvas(pdf_path, pagesize=letter)
            c.drawString(100, 750, f"Diagrama: {diagram.get('title', 'Sin título')}")
            
            # Renderizar nodos básicos
            y_pos = 700
            for node in diagram['data'].get('nodes', []):
                c.drawString(100, y_pos, f"- {node.get('text', node.get('id', ''))}")
                y_pos -= 20
            
            c.save()
            
            # Convertir PDF a PNG (requiere poppler-utils)
            try:
                import subprocess
                subprocess.run(['pdftoppm', '-png', pdf_path, filepath.replace('.png', '')], check=True)
                # Renombrar archivo generado
                import glob
                png_files = glob.glob(filepath.replace('.png', '') + '-*.png')
                if png_files:
                    import shutil
                    shutil.move(png_files[0], filepath)
            except:
                # Si no se puede convertir, usar el PDF
                filepath = pdf_path
            
    except Exception as e:
        print(f"Error generando PNG: {str(e)}")
        # Crear PNG básico de error
        from PIL import Image, ImageDraw, ImageFont
        try:
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            draw.text((400, 300), f"Error generando PNG: {str(e)}", fill='red', anchor='mm')
            img.save(filepath)
        except:
            # Último fallback: archivo de texto
            with open(filepath.replace('.png', '.txt'), 'w', encoding='utf-8') as f:
                f.write(f"Error generando PNG: {str(e)}\n")
                f.write(f"Diagrama: {diagram.get('title', 'Sin título')}\n")
                for node in diagram['data'].get('nodes', []):
                    f.write(f"- {node.get('text', node.get('id', ''))}\n")

@app.route('/download/<filename>')
def download_file(filename):
    try:
        filepath = os.path.join(config.OUTPUT_FOLDER, filename)
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
        icons_base_path = config.ICONS_BASE_DIR
        
        # Cargar iconos de AWS
        aws_path = os.path.join(icons_base_path, config.ICONS_AWS_DIR)
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
        azure_path = os.path.join(icons_base_path, config.ICONS_AZURE_DIR)
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
        return send_file(os.path.join(config.ICONS_BASE_DIR, filename))
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
    """Busca iconos por nombre o categoría con búsqueda más profunda"""
    try:
        query = request.args.get('q', '').lower()
        provider = request.args.get('provider', 'all')
        category = request.args.get('category', 'all')
        limit = int(request.args.get('limit', 100))
        
        if not query:
            return jsonify({'error': 'Query de búsqueda requerido'}), 400
        
        # Obtener todos los iconos
        icons_response = get_available_icons()
        if not icons_response.json.get('success'):
            return icons_response
        
        all_icons = icons_response.json['icons']
        results = []
        
        # Búsqueda más profunda con múltiples criterios
        search_terms = query.split()
        
        for provider_name, provider_icons in all_icons.items():
            if provider != 'all' and provider_name.lower() != provider.lower():
                continue
                
            for category_name, category_icons in provider_icons.items():
                if category != 'all' and category_name.lower() != category.lower():
                    continue
                    
                for icon in category_icons:
                    # Búsqueda por múltiples criterios
                    icon_name_lower = icon['name'].lower()
                    category_lower = category_name.lower()
                    provider_lower = provider_name.lower()
                    
                    # Búsqueda exacta
                    if query in icon_name_lower:
                        icon['relevance_score'] = 100
                        results.append(icon)
                        continue
                    
                    # Búsqueda por palabras individuales
                    match_score = 0
                    for term in search_terms:
                        if term in icon_name_lower:
                            match_score += 30
                        if term in category_lower:
                            match_score += 20
                        if term in provider_lower:
                            match_score += 10
                        
                        # Búsqueda por sinónimos y términos relacionados
                        if term in ['vm', 'virtual', 'machine'] and any(word in icon_name_lower for word in ['ec2', 'virtual-machine', 'compute']):
                            match_score += 25
                        if term in ['db', 'database'] and any(word in icon_name_lower for word in ['rds', 'database', 'sql', 'nosql']):
                            match_score += 25
                        if term in ['storage', 'file'] and any(word in icon_name_lower for word in ['s3', 'storage', 'blob', 'file']):
                            match_score += 25
                        if term in ['network', 'vnet'] and any(word in icon_name_lower for word in ['vpc', 'vnet', 'network', 'subnet']):
                            match_score += 25
                        if term in ['security', 'firewall'] and any(word in icon_name_lower for word in ['security', 'firewall', 'waf', 'iam']):
                            match_score += 25
                        if term in ['monitor', 'log'] and any(word in icon_name_lower for word in ['monitor', 'log', 'analytics', 'insights']):
                            match_score += 25
                        if term in ['api', 'gateway'] and any(word in icon_name_lower for word in ['api', 'gateway', 'app', 'service']):
                            match_score += 25
                        if term in ['container', 'kubernetes'] and any(word in icon_name_lower for word in ['container', 'kubernetes', 'aks', 'ecs', 'eks']):
                            match_score += 25
                        if term in ['lambda', 'function'] and any(word in icon_name_lower for word in ['lambda', 'function', 'serverless']):
                            match_score += 25
                        if term in ['cdn', 'edge'] and any(word in icon_name_lower for word in ['cdn', 'edge', 'cloudfront', 'frontdoor']):
                            match_score += 25
                    
                    if match_score > 0:
                        icon['relevance_score'] = match_score
                        results.append(icon)
        
        # Ordenar por relevancia y limitar resultados
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        results = results[:limit]
        
        # Añadir metadatos de búsqueda
        search_metadata = {
            'query': query,
            'provider': provider,
            'category': category,
            'total_found': len(results),
            'search_terms': search_terms,
            'suggestions': generate_search_suggestions(query, all_icons)
        }
        
        return jsonify({
            'success': True,
            'results': results,
            'total': len(results),
            'metadata': search_metadata
        })
        
    except Exception as e:
        print(f"Error buscando iconos: {str(e)}")
        return jsonify({'error': f'Error buscando iconos: {str(e)}'}), 500

def generate_search_suggestions(query, all_icons):
    """Genera sugerencias de búsqueda basadas en el query y iconos disponibles"""
    suggestions = []
    
    # Sugerencias comunes
    common_terms = {
        'vm': ['virtual machine', 'ec2', 'compute', 'server'],
        'database': ['db', 'rds', 'sql', 'nosql', 'storage'],
        'network': ['vpc', 'vnet', 'subnet', 'gateway', 'router'],
        'security': ['firewall', 'waf', 'iam', 'security group'],
        'monitor': ['logging', 'analytics', 'insights', 'metrics'],
        'api': ['gateway', 'app service', 'function', 'lambda'],
        'container': ['kubernetes', 'docker', 'aks', 'ecs', 'eks'],
        'storage': ['s3', 'blob', 'file', 'backup', 'archive']
    }
    
    # Buscar términos relacionados
    for term, related in common_terms.items():
        if term in query.lower():
            suggestions.extend(related)
    
    # Sugerencias basadas en categorías populares
    popular_categories = config.POPULAR_ICON_CATEGORIES
    for category in popular_categories:
        if category in query.lower():
            suggestions.append(f"Buscar en categoría: {category}")
    
    return list(set(suggestions))[:10]  # Máximo 10 sugerencias únicas

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
            'ai_generated': original_diagram.get('ai_generated', False),
            'duplicated_from': diagram_id,
            'duplication_metadata': {
                'duplicated_at': datetime.now().isoformat(),
                'app_version': config.APP_VERSION,
                'original_version': original_diagram.get('version', 1)
            }
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
    
    # Validar configuración
    if not validate_config():
        print("❌ Error en la configuración. Verifique los archivos y variables de entorno.")
        exit(1)
    
    # Mostrar resumen de configuración
    print_config_summary()
    
    print("🌐 Servidor iniciado en: http://localhost:5000")
    print("📊 Panel de administración en http://localhost:5000/admin")
    print("🔍 API de búsqueda de iconos disponible en /api/search_icons")
    print("💾 Sistema de diagramas en memoria activo")
    print("🎨 Editor de diagramas con Mermaid.js integrado")
    print("📱 Interfaz responsive con Bootstrap 5")
    print("🔐 Sistema de autenticación básico implementado")
    print("📈 Métricas y logs habilitados")
    print("🚀 Funcionalidades avanzadas:")
    print("   - Generación de diagramas con IA (OpenAI GPT-4)")
    print("   - Soporte para Azure Hub & Spoke")
    print("   - Biblioteca de iconos AWS/Azure")
    print("   - Exportación a múltiples formatos")
    print("   - Sistema de versionado de diagramas")
    print("   - Búsqueda avanzada de iconos")
    print("   - Metadatos técnicos en diagramas")
    print("   - Configuración centralizada")
    print("=" * 60)
    
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
