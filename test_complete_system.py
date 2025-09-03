#!/usr/bin/env python3
"""
Prueba completa del sistema de iconos y generación de diagramas
"""
import requests
import json

def test_complete_system():
    """Prueba completa del sistema"""
    base_url = "http://localhost:5000"
    
    print("🧪 PRUEBA COMPLETA DEL SISTEMA")
    print("=" * 50)
    
    try:
        # 1. Probar API de iconos desde Libs
        print("\n1. 🔍 Probando API de iconos desde Libs...")
        response = requests.get(f"{base_url}/api/icons/libs")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {data.get('total_icons', 0)} iconos desde {len(data.get('libraries', []))} bibliotecas")
            
            # Mostrar algunas bibliotecas importantes
            libraries = data.get('libraries', [])
            important_libs = ['integration/azure', 'integration/aws', 'kubernetes', 'material-design-icons']
            for lib_name in important_libs:
                if lib_name in libraries:
                    icon_count = len(data['icons'].get(lib_name, []))
                    print(f"   📦 {lib_name}: {icon_count} iconos")
                else:
                    print(f"   ❌ {lib_name}: No encontrado")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        # 2. Probar API de bibliotecas
        print("\n2. 📚 Probando API de bibliotecas...")
        response = requests.get(f"{base_url}/api/libs")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {data.get('total_libraries', 0)} bibliotecas disponibles")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        # 3. Probar generación de diagrama NO-Azure
        print("\n3. 🏗️ Probando generación de diagrama NO-Azure...")
        test_description = "Crear diagrama de flujo de proceso de ventas con 3 departamentos"
        response = requests.post(f"{base_url}/generate_ai_diagram", 
                               json={'description': test_description, 'type': 'flowchart'})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: Diagrama generado con ID {data.get('diagram_id')}")
            print(f"   📊 Tipo: {data.get('diagram', {}).get('type')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        # 4. Probar generación de diagrama Azure específico
        print("\n4. 🔵 Probando generación de diagrama Azure específico...")
        test_description = "Crear diagrama de arquitectura de azure hub and spoke para 4 subcripciones"
        response = requests.post(f"{base_url}/generate_ai_diagram", 
                               json={'description': test_description, 'type': 'architecture'})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: Diagrama Azure generado con ID {data.get('diagram_id')}")
            print(f"   📊 Tipo: {data.get('diagram', {}).get('type')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        # 5. Probar acceso a archivos de bibliotecas
        print("\n5. 📁 Probando acceso a archivos de bibliotecas...")
        test_files = ['integration/azure.xml', 'kubernetes.xml', 'material-design-icons.xml']
        for test_file in test_files:
            response = requests.get(f"{base_url}/libs/{test_file}")
            if response.status_code == 200:
                print(f"   ✅ {test_file}: Accesible")
            else:
                print(f"   ❌ {test_file}: Error {response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎯 PRUEBA COMPLETA FINALIZADA")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Asegúrate de que la aplicación esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == '__main__':
    test_complete_system()
