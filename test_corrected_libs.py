#!/usr/bin/env python3
"""
Prueba de las correcciones de las rutas de Libs
"""
from icon_mapping import map_azure_icon_to_libs, get_icon_from_libs, get_all_available_libraries

def test_corrected_libs():
    """Prueba las correcciones de las rutas de Libs"""
    print("🧪 Probando correcciones de rutas de Libs...")
    
    # 1. Probar mapeo de iconos de Azure
    print("\n1. 🔍 Probando mapeo de iconos de Azure:")
    test_azure_icons = [
        "10063-icon-service-Virtual-Network-Gateways.svg",
        "10061-icon-service-Virtual-Networks.svg",
        "02422-icon-service-Bastions.svg",
        "10084-icon-service-Firewalls.svg",
        "10079-icon-service-ExpressRoute-Circuits.svg",
        "10021-icon-service-Virtual-Machine.svg",
        "00001-icon-service-Monitor.svg"
    ]
    
    for icon_name in test_azure_icons:
        mapped = map_azure_icon_to_libs(icon_name)
        if mapped:
            print(f"  ✅ {icon_name} → {mapped['path']}")
        else:
            print(f"  ❌ {icon_name} → No mapeado")
    
    # 2. Probar búsqueda de iconos en bibliotecas
    print("\n2. 🔍 Probando búsqueda de iconos en bibliotecas:")
    for icon_name in test_azure_icons[:3]:  # Solo probar 3 para no saturar
        found = get_icon_from_libs(icon_name)
        if found:
            print(f"  ✅ {icon_name} encontrado en: {found['path']}")
        else:
            print(f"  ❌ {icon_name} no encontrado")
    
    # 3. Probar obtención de todas las bibliotecas disponibles
    print("\n3. 📚 Probando obtención de todas las bibliotecas:")
    libraries = get_all_available_libraries()
    print(f"  📦 Total de bibliotecas encontradas: {len(libraries)}")
    
    # Mostrar algunas bibliotecas importantes
    important_libs = ['integration/azure', 'integration/aws', 'kubernetes', 'material-design-icons']
    for lib_name in important_libs:
        for lib in libraries:
            if lib['name'] == lib_name:
                print(f"  ✅ {lib['name']}: {lib['size_mb']} MB - {lib['path']}")
                break
        else:
            print(f"  ❌ {lib_name}: No encontrado")

if __name__ == '__main__':
    test_corrected_libs()
