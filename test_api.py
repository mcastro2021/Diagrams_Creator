#!/usr/bin/env python3
"""
Prueba de la nueva API de iconos de la carpeta Libs
"""
import requests
import json

def test_api():
    """Prueba la nueva API de iconos"""
    base_url = "http://localhost:5000"
    
    print("🧪 Probando nueva API de iconos de la carpeta Libs...")
    
    try:
        # Probar la nueva API de iconos desde Libs
        print("\n1. Probando /api/icons/libs...")
        response = requests.get(f"{base_url}/api/icons/libs")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {data.get('total_icons', 0)} iconos desde {len(data.get('libraries', []))} bibliotecas")
            
            # Mostrar algunas bibliotecas
            libraries = data.get('libraries', [])
            for i, lib in enumerate(libraries[:5]):
                print(f"   - {lib}: {len(data['icons'].get(lib, []))} iconos")
            
            if len(libraries) > 5:
                print(f"   ... y {len(libraries) - 5} bibliotecas más")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        # Probar la API original como comparación
        print("\n2. Probando /api/icons (original)...")
        response = requests.get(f"{base_url}/api/icons")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {data.get('total_icons', 0)} iconos desde {len(data.get('providers', []))} proveedores")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
        
        # Probar la API de bibliotecas
        print("\n3. Probando /api/libs...")
        response = requests.get(f"{base_url}/api/libs")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {data.get('total_libraries', 0)} bibliotecas disponibles")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Asegúrate de que la aplicación esté ejecutándose.")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == '__main__':
    test_api()
