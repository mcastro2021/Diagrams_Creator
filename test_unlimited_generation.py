#!/usr/bin/env python3
"""
Prueba de generación sin límites - 20 suscripciones
"""

import sys
sys.path.append('.')
from azure_enhanced_generator import create_enhanced_azure_hub_spoke

def test_unlimited_generation():
    """Probar generación con 20 suscripciones"""
    print("🚀 PROBANDO GENERACIÓN SIN LÍMITES")
    print("=" * 50)
    
    # Texto de prueba con 20 suscripciones
    test_text = 'Crear diagrama de arquitectura de azure hub and spoke para 20 suscripciones de ambientes bajos, medios y altos'
    
    print(f"📝 Texto de entrada: {test_text}")
    print("\n🔄 Generando arquitectura...")
    
    try:
        result = create_enhanced_azure_hub_spoke(test_text)
        
        print(f"\n✅ RESULTADOS:")
        print(f"📊 Componentes generados: {len(result['components'])}")
        print(f"🔗 Conexiones generadas: {len(result['connections'])}")
        
        # Contar tipos específicos
        subs = [c for c in result['components'] if 'subscription' in c['id'].lower()]
        vnets = [c for c in result['components'] if 'spoke_vnet' in c['id'].lower()]
        
        print(f"🏢 Suscripciones: {len(subs)}")
        print(f"🌐 Spoke VNets: {len(vnets)}")
        
        print(f"\n📋 PRIMEROS 10 COMPONENTES:")
        for i, component in enumerate(result['components'][:10]):
            icon_info = f" (🎨 {component.get('icon_category', 'NO ICON')})" if component.get('icon_category') else " (❌ SIN ICONO)"
            print(f"  {i+1:2d}. {component['id']:20s}: {component['name'].replace(chr(10), ' | ')}{icon_info}")
        
        # Verificar ambientes
        environments = set()
        for comp in result['components']:
            if 'environment' in comp.get('description', '').lower():
                env_desc = comp['description'].lower()
                if 'bajo' in env_desc or 'development' in env_desc:
                    environments.add('bajo')
                elif 'medio' in env_desc or 'staging' in env_desc:
                    environments.add('medio')
                elif 'alto' in env_desc or 'production' in env_desc:
                    environments.add('alto')
        
        print(f"\n🏷️  AMBIENTES DETECTADOS: {list(environments)}")
        
        # Verificar iconos
        with_icons = len([c for c in result['components'] if c.get('icon_category')])
        without_icons = len(result['components']) - with_icons
        
        print(f"\n🎨 ICONOS:")
        print(f"  ✅ Con iconos: {with_icons}")
        print(f"  ❌ Sin iconos: {without_icons}")
        
        if len(subs) == 20:
            print(f"\n🎉 ¡ÉXITO! Se generaron exactamente 20 suscripciones como se pidió")
        else:
            print(f"\n⚠️  Se esperaban 20 suscripciones, se generaron {len(subs)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_unlimited_generation()
