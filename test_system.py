#!/usr/bin/env python3
"""
Script de prueba simple para verificar el funcionamiento del sistema
"""

import requests
import json
import time

def test_basic_functionality():
    """Prueba la funcionalidad básica del sistema"""
    base_url = "http://localhost:5000"
    
    print("🧪 Iniciando pruebas del sistema...")
    
    # Prueba 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check: OK")
        else:
            print(f"❌ Health check: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Health check: Error de conexión - {e}")
        return False
    
    # Prueba 2: Cargar iconos
    try:
        response = requests.get(f"{base_url}/api/icons")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Carga de iconos: OK - {data.get('total_icons', 0)} iconos cargados")
            else:
                print(f"❌ Carga de iconos: Error - {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Carga de iconos: Error HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Carga de iconos: Error de conexión - {e}")
    
    # Prueba 3: Generar diagrama simple
    try:
        test_description = f"Diagrama de prueba generado a las {time.strftime('%H:%M:%S')}"
        response = requests.post(f"{base_url}/generate_ai_diagram", 
                               json={
                                   'description': test_description,
                                   'type': 'flowchart',
                                   'title': 'Prueba del Sistema'
                               })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Generación de diagrama: OK - ID: {data.get('diagram_id', 'N/A')}")
            else:
                print(f"❌ Generación de diagrama: Error - {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Generación de diagrama: Error HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Generación de diagrama: Error de conexión - {e}")
    
    # Prueba 4: Listar diagramas
    try:
        response = requests.get(f"{base_url}/diagrams")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                diagrams = data.get('diagrams', [])
                print(f"✅ Lista de diagramas: OK - {len(diagrams)} diagramas encontrados")
            else:
                print(f"❌ Lista de diagramas: Error - {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Lista de diagramas: Error HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Lista de diagramas: Error de conexión - {e}")
    
    print("\n🎯 Pruebas completadas!")
    return True

if __name__ == "__main__":
    test_basic_functionality()
