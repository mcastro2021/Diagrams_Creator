#!/usr/bin/env python3
"""
Generador mejorado para arquitecturas Azure Hub and Spoke - VERSIÓN CORREGIDA
"""

import re
from typing import Dict, List, Any

def create_enhanced_azure_hub_spoke(text: str) -> Dict[str, Any]:
    """Crear arquitectura Azure Hub and Spoke con detalles empresariales completos"""
    
    # Detectar número de spokes/subscripciones
    spoke_numbers = re.findall(r'(\d+)\s*(?:spoke|subscription|suscripcion)', text.lower())
    num_spokes = int(spoke_numbers[0]) if spoke_numbers else 4
    
    components = []
    connections = []
    
    # Hub VNet con detalles completos - COORDENADAS AMPLIAS PARA DRAW.IO
    components.append({
        'id': 'hub_vnet',
        'name': 'Hub VNet\n10.0.0.0/16',
        'type': 'network',
        'technology': 'Azure Virtual Network',
        'description': 'Red virtual central con servicios compartidos\nSubnets: Gateway(10.0.0.0/24), Firewall(10.0.1.0/24), Shared(10.0.2.0/24)',
        'layer': 'network',
        'icon_category': 'integration_azure',
        'position': {'x': 1200, 'y': 600}  # Centro amplio
    })
    
    # VPN Gateway detallado
    components.append({
        'id': 'vpn_gateway',
        'name': 'VPN Gateway\n(VpnGw2)',
        'type': 'gateway',
        'technology': 'Azure VPN Gateway',
        'description': 'Gateway VPN para conectividad híbrida\nSKU: VpnGw2, Throughput: 1.25 Gbps\nGatewaySubnet: 10.0.0.0/24',
        'layer': 'network',
        'icon_category': 'integration_azure',
        'position': {'x': 1200, 'y': 200}  # Arriba del hub
    })
    
    # Azure Firewall
    components.append({
        'id': 'azure_firewall',
        'name': 'Azure Firewall\n(Premium)',
        'type': 'security',
        'technology': 'Azure Firewall Premium',
        'description': 'Firewall centralizado con IDPS avanzado\nFeatures: URL Filtering, TLS Inspection, Threat Intelligence\nSubnet: AzureFirewallSubnet (10.0.1.0/24)',
        'layer': 'security',
        'icon_category': 'fortinet_fortinet-products',
        'position': {'x': 1600, 'y': 400}  # Derecha del hub
    })
    
    # Log Analytics Workspace
    components.append({
        'id': 'log_analytics',
        'name': 'Log Analytics\nWorkspace',
        'type': 'monitoring',
        'technology': 'Azure Monitor',
        'description': 'Centralización de logs y métricas\nRetention: 30 days\nSources: NSG Flow Logs, Firewall Logs, Activity Logs',
        'layer': 'management',
        'icon_category': 'integration_azure',
        'position': {'x': 800, 'y': 400}  # Izquierda del hub
    })
    
    # Key Vault central
    components.append({
        'id': 'key_vault_hub',
        'name': 'Key Vault\n(Hub)',
        'type': 'security',
        'technology': 'Azure Key Vault',
        'description': 'Gestión centralizada de secretos\nCertificates, Keys, Secrets\nPremium tier with HSM',
        'layer': 'security',
        'icon_category': 'integration_azure',
        'position': {'x': 1400, 'y': 200}  # Arriba derecha
    })
    
    # Configuraciones detalladas para cada spoke
    spoke_configs = [
        {
            'name': 'Production', 
            'cidr': '10.1.0.0/16', 
            'environment': 'prod',
            'cost_center': 'CC-1001',
            'services': [
                {'name': 'App Service Plan\n(Premium P2v3)', 'type': 'webapp', 'icon': 'integration_azure'},
                {'name': 'SQL Database\n(Gen5 8vCore)', 'type': 'database', 'icon': 'integration_databases'},
                {'name': 'Key Vault\n(Premium)', 'type': 'security', 'icon': 'integration_azure'},
                {'name': 'Application Gateway\n(WAF v2)', 'type': 'loadbalancer', 'icon': 'integration_azure'}
            ]
        },
        {
            'name': 'Development', 
            'cidr': '10.2.0.0/16', 
            'environment': 'dev',
            'cost_center': 'CC-1002',
            'services': [
                {'name': 'App Service\n(Standard S2)', 'type': 'webapp', 'icon': 'integration_azure'},
                {'name': 'Storage Account\n(Standard LRS)', 'type': 'storage', 'icon': 'integration_azure'},
                {'name': 'Container Registry\n(Basic)', 'type': 'containers', 'icon': 'integration_developer'},
                {'name': 'Azure DevOps\nAgents', 'type': 'devops', 'icon': 'integration_developer'}
            ]
        },
        {
            'name': 'Testing', 
            'cidr': '10.3.0.0/16', 
            'environment': 'test',
            'cost_center': 'CC-1003',
            'services': [
                {'name': 'Virtual Machines\n(Standard_B4ms)', 'type': 'compute', 'icon': 'integration_infrastructure'},
                {'name': 'Load Balancer\n(Standard)', 'type': 'loadbalancer', 'icon': 'integration_azure'},
                {'name': 'Backup Vault\n(GRS)', 'type': 'backup', 'icon': 'integration_azure'},
                {'name': 'Test Automation\nFramework', 'type': 'testing', 'icon': 'integration_developer'}
            ]
        },
        {
            'name': 'DMZ', 
            'cidr': '10.4.0.0/16', 
            'environment': 'dmz',
            'cost_center': 'CC-1004',
            'services': [
                {'name': 'Application Gateway\n(WAF v2)', 'type': 'gateway', 'icon': 'integration_azure'},
                {'name': 'Web Apps\n(Isolated v2)', 'type': 'webapp', 'icon': 'integration_azure'},
                {'name': 'API Management\n(Premium)', 'type': 'api', 'icon': 'integration_integration'},
                {'name': 'CDN Profile\n(Premium Verizon)', 'type': 'cdn', 'icon': 'integration_azure'}
            ]
        }
    ]
    
    # COORDENADAS AMPLIAS PARA DRAW.IO - Sin superposición
    component_width = 300   # Ancho real de componentes en Draw.io
    component_height = 200  # Alto real de componentes en Draw.io
    margin_x = 500         # Margen horizontal AMPLIO
    margin_y = 400         # Margen vertical AMPLIO
    
    total_width_needed = component_width + margin_x
    total_height_needed = component_height + margin_y
    
    if num_spokes <= 3:
        # Disposición horizontal con espacio muy amplio
        spoke_positions = []
        start_x = 400  # Comenzar más a la derecha
        for i in range(num_spokes):
            spoke_positions.append({
                'x': start_x + (i * total_width_needed),
                'y': 1200  # Muy abajo del hub
            })
    elif num_spokes <= 6:
        # Disposición en 2 filas con espaciado muy amplio
        spoke_positions = []
        start_x = 200  # Comenzar más a la izquierda para 3 columnas
        for i in range(num_spokes):
            row = i // 3
            col = i % 3
            spoke_positions.append({
                'x': start_x + (col * total_width_needed),
                'y': 1200 + (row * total_height_needed)  # Primera fila abajo del hub
            })
    else:
        # Disposición en múltiples filas con espaciado máximo
        spoke_positions = []
        cols_per_row = min(4, num_spokes)  # Máximo 4 columnas
        start_x = 100
        for i in range(num_spokes):
            row = i // cols_per_row
            col = i % cols_per_row
            spoke_positions.append({
                'x': start_x + (col * total_width_needed),
                'y': 1200 + (row * total_height_needed)
            })
    
    # Crear spokes con servicios detallados
    for i in range(min(num_spokes, len(spoke_configs))):
        config = spoke_configs[i]
        spoke_id = f'spoke_vnet_{i+1}'
        
        # Spoke VNet con información completa
        components.append({
            'id': spoke_id,
            'name': f'{config["name"]} VNet\n{config["cidr"]}',
            'type': 'network',
            'technology': 'Azure Virtual Network',
            'description': f'Spoke VNet para entorno {config["name"]}\nAddress Space: {config["cidr"]}\nEnvironment: {config["environment"]}\nSubnets: Web, App, Data, Management',
            'layer': 'network',
            'icon_category': 'integration_azure',
            'position': spoke_positions[i]
        })
        
        # Subscription con detalles financieros
        sub_id = f'subscription_{i+1}'
        components.append({
            'id': sub_id,
            'name': f'{config["name"]}\nSubscription\n({config["cost_center"]})',
            'type': 'subscription',
            'technology': 'Azure Subscription',
            'description': f'Azure Subscription - {config["name"]}\nCost Center: {config["cost_center"]}\nEnvironment: {config["environment"]}\nResource Groups: rg-{config["environment"]}-001, rg-{config["environment"]}-network-001',
            'layer': 'management',
            'icon_category': 'integration_azure',
            'position': {'x': spoke_positions[i]['x'], 'y': spoke_positions[i]['y'] + 300}
        })
        
        # Servicios específicos del spoke con posicionamiento muy amplio
        service_positions = [
            {'x': -300, 'y': -200},   # Arriba izquierda - MUY separado
            {'x': 300, 'y': -200},    # Arriba derecha - MUY separado
            {'x': -300, 'y': 500},    # Abajo izquierda - MUY separado  
            {'x': 300, 'y': 500}      # Abajo derecha - MUY separado
        ]
        
        for j, service in enumerate(config['services'][:4]):  # Máximo 4 servicios por spoke
            service_id = f'service_{i+1}_{j+1}'
            service_pos = service_positions[j] if j < len(service_positions) else {'x': 0, 'y': 40}
            
            components.append({
                'id': service_id,
                'name': service['name'],
                'type': service['type'],
                'technology': f'Azure {service["name"].split()[0]}',
                'description': f'{service["name"]} en {config["name"]}\nEnvironment: {config["environment"]}',
                'layer': 'application',
                'icon_category': service['icon'],
                'position': {
                    'x': spoke_positions[i]['x'] + service_pos['x'],
                    'y': spoke_positions[i]['y'] + service_pos['y']
                }
            })
            
            # Conexiones de servicios
            connections.extend([
                {
                    'from': service_id,
                    'to': spoke_id,
                    'type': 'hosted_in',
                    'label': f'Hosted in VNet',
                    'protocol': 'VNET Integration'
                }
            ])
        
        # Conexiones principales del spoke
        connections.extend([
            {
                'from': 'hub_vnet',
                'to': spoke_id,
                'type': 'peering',
                'label': f'VNet Peering\n{config["cidr"]} ↔ 10.0.0.0/16\nBidirectional, Gateway Transit',
                'protocol': 'Azure VNet Peering'
            },
            {
                'from': spoke_id,
                'to': sub_id,
                'type': 'contains',
                'label': 'Resource Container\nGovernance & Billing',
                'protocol': 'Azure ARM'
            }
        ])
    
    # Conexiones centrales del hub
    connections.extend([
        {
            'from': 'vpn_gateway',
            'to': 'hub_vnet',
            'type': 'gateway_connection',
            'label': 'Site-to-Site VPN\nBGP: AS65515 ↔ AS65001\nThroughput: 1.25 Gbps',
            'protocol': 'IPSec/BGP'
        },
        {
            'from': 'hub_vnet',
            'to': 'azure_firewall',
            'type': 'security_flow',
            'label': 'Centralized Security\nAll North-South Traffic\nIDPS + TLS Inspection',
            'protocol': 'HTTPS/443'
        },
        {
            'from': 'hub_vnet',
            'to': 'log_analytics',
            'type': 'monitoring',
            'label': 'Centralized Logging\nNSG Flow Logs\nActivity Logs\nDiagnostic Settings',
            'protocol': 'HTTPS/REST API'
        },
        {
            'from': 'key_vault_hub',
            'to': 'hub_vnet',
            'type': 'security',
            'label': 'Central Secrets Management\nCertificates & Keys\nPrivate Endpoint',
            'protocol': 'HTTPS/443'
        }
    ])
    
    return {
        'diagram_type': 'azure_hub_spoke_enterprise',
        'title': f'Azure Enterprise Hub & Spoke Architecture - {num_spokes} Specialized Environments',
        'description': f'Arquitectura empresarial Azure Hub and Spoke con {num_spokes} entornos especializados, seguridad multicapa, monitoreo centralizado, gestión de identidades y cumplimiento normativo',
        'components': components,
        'connections': connections,
        'layers': ['network', 'security', 'application', 'management', 'governance'],
        'technologies': [
            'Azure Virtual Network', 'Azure VPN Gateway (VpnGw2)', 'Azure Firewall Premium', 
            'Azure Monitor & Log Analytics', 'Azure Key Vault Premium',
            'Azure App Service', 'Azure SQL Database',
            'Azure Storage', 'Azure Container Registry'
        ],
        'patterns': [
            'Hub and Spoke Architecture', 'Azure Landing Zone', 'Network Micro-segmentation', 
            'Centralized Security', 'Environment Separation', 'Zero Trust Network',
            'Centralized Logging', 'Hybrid Connectivity', 'Cost Management'
        ]
    }
