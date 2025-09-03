#!/usr/bin/env python3
"""
Prueba del mapeo de iconos de Azure a la carpeta Libs
"""
from icon_mapping import map_azure_icon_to_libs, get_icon_from_libs

def test_icon_mapping():
    """Prueba el mapeo de iconos"""
    print("🧪 Probando mapeo de iconos de Azure a Libs...")
    
    # Lista de iconos que necesitan ser mapeados
    test_icons = [
        "10063-icon-service-Virtual-Network-Gateways.svg",
        "10061-icon-service-Virtual-Networks.svg",
        "02422-icon-service-Bastions.svg",
        "10084-icon-service-Firewalls.svg",
        "10079-icon-service-ExpressRoute-Circuits.svg",
        "10021-icon-service-Virtual-Machine.svg",
        "00001-icon-service-Monitor.svg"
    ]
    
    for icon_name in test_icons:
        print(f"\n🔍 Probando icono: {icon_name}")
        
        # Probar mapeo directo
        mapped = map_azure_icon_to_libs(icon_name)
        if mapped:
            print(f"  ✅ Mapeado a: {mapped['library']} - {mapped['path']}")
        else:
            print(f"  ❌ No se pudo mapear")
        
        # Probar búsqueda en bibliotecas
        found = get_icon_from_libs(icon_name)
        if found:
            print(f"  ✅ Encontrado en: {found['library']} - {found['path']}")
        else:
            print(f"  ❌ No encontrado en bibliotecas")

if __name__ == '__main__':
    test_icon_mapping()
