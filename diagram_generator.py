import json
import os
import subprocess
import tempfile
from pathlib import Path

class DiagramGenerator:
    def __init__(self):
        self.mermaid_path = self._find_mermaid()
    
    def _find_mermaid(self):
        """Busca la instalación de Mermaid CLI"""
        try:
            # Intentar usar npx si está disponible
            result = subprocess.run(['npx', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return 'npx'
        except:
            pass
        
        try:
            # Intentar usar mmdc directamente
            result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                return 'mmdc'
        except:
            pass
        
        return None
    
    def create_diagram_from_content(self, content):
        """Crea un diagrama basado en el contenido procesado del documento"""
        try:
            print(f"DEBUG: Procesando contenido de tipo: {content.get('type')}")
            
            if content['type'] == 'network':
                return self._create_azure_network_diagram(content)
            elif content['type'] == 'text':
                return self._create_azure_text_diagram(content)
            elif content['type'] == 'spreadsheet':
                return self._create_azure_spreadsheet_diagram(content)
            elif content['type'] == 'json':
                return self._create_azure_json_diagram(content)
            else:
                return self._create_azure_basic_diagram(content)
        except Exception as e:
            print(f"DEBUG: Error en create_diagram_from_content: {str(e)}")
            return {
                'error': f'Error generando diagrama: {str(e)}'
            }
    
    def _create_azure_network_diagram(self, content):
        """Crea un diagrama de arquitectura Azure desde información de redes"""
        try:
            network_info = content.get('network_info', {})
            print(f"DEBUG: Creando diagrama Azure de red")
            
            # Generar código Mermaid para diagrama de arquitectura Azure
            mermaid_code = self._generate_azure_architecture_mermaid(network_info)
            
            # Convertir Mermaid a SVG usando Mermaid CLI
            svg_content = self._convert_mermaid_to_svg(mermaid_code)
            
            if svg_content:
                return {
                    'diagram_data': svg_content,
                    'mermaid_code': mermaid_code,
                    'drawio_url': None,
                    'download_url': None,
                    'title': 'Arquitectura Azure - Configuración de Redes',
                    'type': 'azure_architecture'
                }
            else:
                # Fallback: retornar código Mermaid para que el usuario lo use
                return {
                    'diagram_data': mermaid_code,
                    'mermaid_code': mermaid_code,
                    'drawio_url': None,
                    'download_url': None,
                    'title': 'Código Mermaid - Arquitectura Azure',
                    'type': 'mermaid_code'
                }
            
        except Exception as e:
            print(f"DEBUG: Error creando diagrama Azure: {str(e)}")
            return {
                'error': f'Error creando diagrama Azure: {str(e)}'
            }
    
    def _generate_azure_architecture_mermaid(self, network_info):
        """Genera código Mermaid para diagrama de arquitectura Azure"""
        try:
            mermaid_code = """graph TB
    subgraph "Azure Cloud"
        subgraph "Virtual Network"
            vnet["Virtual Network<br/>10.0.0.0/16"]
            
            subgraph "Subnets"
"""
            
            # Agregar subnets basadas en los datos
            if network_info.get('data'):
                for i, row in enumerate(network_info['data'][:8]):  # Máximo 8 subnets
                    subnet_name = row.get('Subnet', f'Subnet_{i+1}')
                    ip_range = row.get('IP_Range', '10.0.0.0/24')
                    gateway = row.get('Gateway', '10.0.0.1')
                    description = row.get('Description', 'Red de datos')
                    
                    # Crear nodo de subnet
                    mermaid_code += f"""                subnet{i}["{subnet_name}<br/>{ip_range}<br/>Gateway: {gateway}<br/>{description}"]
"""
            else:
                # Subnets de ejemplo si no hay datos
                mermaid_code += """                subnet1["LAN Principal<br/>192.168.1.0/24<br/>Gateway: 192.168.1.1<br/>Red principal de la oficina"]
                subnet2["DMZ<br/>10.0.1.0/24<br/>Gateway: 10.0.1.1<br/>Red desmilitarizada"]
                subnet3["VPN<br/>172.16.1.0/24<br/>Gateway: 172.16.1.1<br/>Red VPN"]
"""
            
            mermaid_code += """            end
        end
        
        subgraph "Azure Services"
            appgw["Application Gateway<br/>Load Balancer"]
            vmss["VM Scale Set<br/>Web Servers"]
            storage["Storage Account<br/>Blob Storage"]
            sql["Azure SQL<br/>Database"]
            keyvault["Key Vault<br/>Secrets Management"]
        end
        
        subgraph "Security"
            nsg["Network Security Group<br/>Firewall Rules"]
            waf["Web Application Firewall<br/>DDoS Protection"]
        end
    end
    
    subgraph "On-Premises"
        onprem["On-Premises Network<br/>192.168.0.0/16"]
        vpngw["VPN Gateway<br/>Site-to-Site"]
    end
    
    subgraph "Internet"
        users["Internet Users<br/>Public Access"]
    end
    
    %% Conexiones
    vnet --> subnet1
    vnet --> subnet2
    vnet --> subnet3
    
    subnet1 --> vmss
    subnet2 --> appgw
    subnet3 --> storage
    
    appgw --> waf
    waf --> nsg
    
    vmss --> sql
    vmss --> keyvault
    
    onprem <--> vpngw
    vpngw <--> vnet
    
    users --> appgw
    
    %% Estilos
    classDef azure fill:#0078d4,stroke:#fff,stroke-width:2px,color:#fff
    classDef subnet fill:#00a1f1,stroke:#fff,stroke-width:2px,color:#fff
    classDef security fill:#d13438,stroke:#fff,stroke-width:2px,color:#fff
    classDef onprem fill:#ff8c00,stroke:#fff,stroke-width:2px,color:#fff
    classDef internet fill:#107c10,stroke:#fff,stroke-width:2px,color:#fff
    
    class vnet,appgw,vmss,storage,sql,keyvault azure
    class subnet1,subnet2,subnet3 subnet
    class nsg,waf security
    class onprem,vpngw onprem
    class users internet"""
            
            print(f"DEBUG: Código Mermaid generado: {len(mermaid_code)} caracteres")
            return mermaid_code
            
        except Exception as e:
            print(f"DEBUG: Error generando Mermaid: {str(e)}")
            return self._get_fallback_mermaid()
    
    def _get_fallback_mermaid(self):
        """Retorna código Mermaid de fallback"""
        return """graph TB
    subgraph "Azure Architecture"
        vnet["Virtual Network"]
        subnet1["Subnet 1<br/>192.168.1.0/24"]
        subnet2["Subnet 2<br/>10.0.1.0/24"]
        vm["Virtual Machine"]
        storage["Storage Account"]
    end
    
    vnet --> subnet1
    vnet --> subnet2
    subnet1 --> vm
    vm --> storage
    
    classDef azure fill:#0078d4,stroke:#fff,stroke-width:2px,color:#fff
    class vnet,subnet1,subnet2,vm,storage azure"""
    
    def _convert_mermaid_to_svg(self, mermaid_code):
        """Convierte código Mermaid a SVG usando Mermaid CLI"""
        try:
            if not self.mermaid_path:
                print("DEBUG: Mermaid CLI no encontrado, retornando código Mermaid")
                return None
            
            # Crear archivo temporal con código Mermaid
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as temp_file:
                temp_file.write(mermaid_code)
                temp_mmd_path = temp_file.name
            
            # Crear archivo de salida SVG
            svg_path = temp_mmd_path.replace('.mmd', '.svg')
            
            try:
                if self.mermaid_path == 'npx':
                    # Usar npx para ejecutar mermaid-cli
                    cmd = ['npx', '@mermaid-js/mermaid-cli', '-i', temp_mmd_path, '-o', svg_path]
                else:
                    # Usar mmdc directamente
                    cmd = ['mmdc', '-i', temp_mmd_path, '-o', svg_path]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(svg_path):
                    # Leer el SVG generado
                    with open(svg_path, 'r', encoding='utf-8') as f:
                        svg_content = f.read()
                    
                    # Limpiar archivos temporales
                    os.unlink(temp_mmd_path)
                    os.unlink(svg_path)
                    
                    print(f"DEBUG: SVG generado exitosamente: {len(svg_content)} caracteres")
                    return svg_content
                else:
                    print(f"DEBUG: Error ejecutando Mermaid CLI: {result.stderr}")
                    return None
                    
            except subprocess.TimeoutExpired:
                print("DEBUG: Timeout ejecutando Mermaid CLI")
                return None
            except Exception as e:
                print(f"DEBUG: Error ejecutando Mermaid CLI: {str(e)}")
                return None
                
        except Exception as e:
            print(f"DEBUG: Error convirtiendo Mermaid a SVG: {str(e)}")
            return None
    
    def _create_azure_text_diagram(self, content):
        """Crea un diagrama Azure desde texto"""
        return self._create_azure_basic_diagram(content)
    
    def _create_azure_spreadsheet_diagram(self, content):
        """Crea un diagrama Azure desde hoja de cálculo"""
        return self._create_azure_basic_diagram(content)
    
    def _create_azure_json_diagram(self, content):
        """Crea un diagrama Azure desde JSON"""
        return self._create_azure_basic_diagram(content)
    
    def _create_azure_basic_diagram(self, content):
        """Crea un diagrama Azure básico"""
        try:
            mermaid_code = """graph TB
    subgraph "Azure Cloud"
        vnet["Virtual Network<br/>10.0.0.0/16"]
        subnet1["Subnet 1<br/>10.0.1.0/24"]
        subnet2["Subnet 2<br/>10.0.2.0/24"]
        vm["Virtual Machine<br/>Compute Resource"]
        storage["Storage Account<br/>Data Storage"]
    end
    
    vnet --> subnet1
    vnet --> subnet2
    subnet1 --> vm
    vm --> storage
    
    classDef azure fill:#0078d4,stroke:#fff,stroke-width:2px,color:#fff
    class vnet,subnet1,subnet2,vm,storage azure"""
            
            return {
                'diagram_data': mermaid_code,
                'mermaid_code': mermaid_code,
                'drawio_url': None,
                'download_url': None,
                'title': 'Diagrama Azure Básico',
                'type': 'azure_basic'
            }
            
        except Exception as e:
            return {
                'error': f'Error creando diagrama Azure básico: {str(e)}'
            }
    
    def save_diagram_to_file(self, diagram_data, filename):
        """Guarda el diagrama en un archivo"""
        try:
            if not os.path.exists('outputs'):
                os.makedirs('outputs')
            
            filepath = os.path.join('outputs', filename)
            
            # Determinar extensión basada en el contenido
            if diagram_data.startswith('<svg'):
                ext = '.svg'
            elif diagram_data.startswith('graph'):
                ext = '.mmd'
            else:
                ext = '.txt'
            
            filepath = filepath.replace('.drawio', ext)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(diagram_data)
            
            return filepath
        except Exception as e:
            raise Exception(f"Error guardando diagrama: {str(e)}")
    
    def create_local_drawio_url(self, diagram_data):
        """Crea una URL local para abrir el diagrama en draw.io desktop"""
        try:
            # Guardar el diagrama temporalmente
            temp_file = self.save_diagram_to_file(diagram_data, 'temp_diagram')
            
            # Crear URL para abrir en draw.io desktop
            drawio_url = f"drawio://{os.path.abspath(temp_file)}"
            
            return drawio_url
        except Exception as e:
            raise Exception(f"Error generando URL local: {str(e)}")
