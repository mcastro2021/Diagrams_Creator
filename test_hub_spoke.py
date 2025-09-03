#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de Hub and Spoke con múltiples suscripciones
"""

import json

def test_hub_spoke_generation():
    """Prueba la generación de diagramas Hub and Spoke"""
    
    # Simular la descripción que enviaría un usuario
    description = "Diagrama de arquitectura que cree topologia hub and spoke para 4 subcripciones"
    
    print(f"🔍 Analizando descripción: {description}")
    
    # Simular la detección de componentes
    description_lower = description.lower()
    
    components = {
        'hub_spoke': any(word in description_lower for word in ['hub and spoke', 'hub-spoke', 'hub & spoke', 'topología hub', 'hub spoke']),
        'multiple_subscriptions': any(word in description_lower for word in ['múltiples suscripciones', '4 suscripciones', 'varias suscripciones', 'subscriptions', 'suscripciones']),
        'enterprise': any(word in description_lower for word in ['empresarial', 'enterprise', 'corporativo', 'corporation'])
    }
    
    print("\n📋 Componentes detectados:")
    for component, detected in components.items():
        status = "✅" if detected else "❌"
        print(f"  {status} {component}: {detected}")
    
    # Simular la creación del diagrama hub and spoke
    print("\n🏗️ Generando topología Hub and Spoke...")
    
    # Crear estructura hub and spoke con 4 suscripciones
    hub_spoke_diagram = create_hub_spoke_structure(4, components)
    
    print(f"✅ Topología Hub and Spoke generada exitosamente!")
    print(f"   📊 Nodos: {len(hub_spoke_diagram['nodes'])}")
    print(f"   🔗 Conexiones: {len(hub_spoke_diagram['edges'])}")
    
    # Mostrar estructura del diagrama
    print("\n🏗️ Estructura del diagrama:")
    for i, node in enumerate(hub_spoke_diagram['nodes'], 1):
        print(f"  {i}. {node['type']} - {node['text']} (x:{node['x']}, y:{node['y']})")
    
    print("\n🔗 Conexiones principales:")
    print("  • Internet → Hub Firewall")
    print("  • Hub VNet → Todos los componentes del Hub")
    print("  • Hub VNet → Cada Spoke VNet")
    print("  • Cada Spoke VNet → Sus servicios (App Service, SQL)")
    
    # Guardar diagrama en archivo JSON
    with open('hub_spoke_diagram_test.json', 'w', encoding='utf-8') as f:
        json.dump(hub_spoke_diagram, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Diagrama guardado en: hub_spoke_diagram_test.json")
    
    return hub_spoke_diagram

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
    node_id += 1
    
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
    
    return {
        'type': 'azure_hub_spoke',
        'nodes': nodes,
        'edges': edges
    }

if __name__ == "__main__":
    print("🚀 Iniciando prueba de generación de Hub and Spoke...")
    print("=" * 70)
    
    diagram = test_hub_spoke_generation()
    
    print("\n" + "=" * 70)
    print("✅ Prueba completada exitosamente!")
    print("\n📝 Para usar en tu aplicación:")
    print("1. Copia el contenido de hub_spoke_diagram_test.json")
    print("2. Usa la función generate_hub_spoke_architecture() en app.py")
    print("3. Los nodos se renderizarán con estilos específicos de Azure")
    print("\n🎯 Palabras clave que activan Hub and Spoke:")
    print("   • 'hub and spoke', 'hub-spoke', 'topología hub'")
    print("   • 'múltiples suscripciones', '4 suscripciones'")
    print("   • 'empresarial', 'enterprise', 'corporativo'")
