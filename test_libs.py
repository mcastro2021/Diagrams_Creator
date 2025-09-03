#!/usr/bin/env python3
"""
Prueba de las funciones de bibliotecas de iconos
"""
import os
from libs_handler import get_available_libraries, parse_library_content

def test_libraries():
    """Prueba las funciones de bibliotecas"""
    print("🧪 Probando funciones de bibliotecas...")
    
    # Probar obtener bibliotecas disponibles
    result = get_available_libraries()
    print(f"Resultado: {result}")
    
    if isinstance(result, dict) and result.get('success'):
        libraries = result.get('libraries', {})
        print(f"\n📚 Bibliotecas encontradas: {len(libraries)}")
        
        for name, info in libraries.items():
            print(f"  - {name}: {info.get('size_mb', 0)} MB")
            
            # Probar parsear una biblioteca
            if name == 'chart-icons':
                print(f"\n🔍 Parseando {name}...")
                parsed = parse_library_content(f"{name}.xml")
                if parsed:
                    print(f"  Iconos encontrados: {parsed.get('total_icons', 0)}")
                    if parsed.get('icons'):
                        print(f"  Primeros 3 iconos:")
                        for i, icon in enumerate(parsed['icons'][:3]):
                            print(f"    {i+1}. {icon.get('title', 'Sin título')} ({icon.get('width', 0)}x{icon.get('height', 0)})")
                else:
                    print(f"  Error parseando {name}")
    else:
        print(f"❌ Error: {result}")

if __name__ == '__main__':
    test_libraries()
