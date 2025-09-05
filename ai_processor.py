#!/usr/bin/env python3
"""
Procesador de IA para análisis de arquitecturas y generación de diagramas
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
import openai
import requests
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import markdown
import re

load_dotenv()
logger = logging.getLogger(__name__)

class AIProcessor:
    """Procesa texto y documentos usando IA para generar análisis de arquitectura"""
    
    def __init__(self):
        # Configurar proveedores de IA
        self.ai_provider = os.getenv('AI_PROVIDER', 'openai').lower()
        self.temperature = float(os.getenv('AI_TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2000'))
        
        # OpenAI
        self.openai_client = None
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.openai_client = openai.OpenAI(api_key=openai_key)
        
        # Ollama (local or hosted)
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.ollama_api_key = os.getenv('OLLAMA_API_KEY')  # Para servicios hospedados
        
        # Groq
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.groq_model = os.getenv('GROQ_MODEL', 'llama-3.1-70b-versatile')
        
        # Hugging Face
        self.hf_api_key = os.getenv('HUGGINGFACE_API_KEY')
        self.hf_model = os.getenv('HUGGINGFACE_MODEL', 'microsoft/DialoGPT-large')
        
        # Determinar proveedor disponible
        self._setup_ai_provider()
    
    def _setup_ai_provider(self):
        """Configurar el proveedor de IA disponible"""
        if self.ai_provider == 'openai' and self.openai_client:
            logger.info("Using OpenAI as AI provider")
            self.active_provider = 'openai'
            self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        elif self.ai_provider == 'ollama' and self._test_ollama():
            logger.info(f"Using Ollama as AI provider with model {self.ollama_model}")
            self.active_provider = 'ollama'
            self.model = self.ollama_model
        elif self.ai_provider == 'groq' and self.groq_api_key:
            logger.info("Using Groq as AI provider")
            self.active_provider = 'groq'
            self.model = self.groq_model
        elif self.ai_provider == 'huggingface' and self.hf_api_key:
            logger.info("Using Hugging Face as AI provider")
            self.active_provider = 'huggingface'
            self.model = self.hf_model
        else:
            # Auto-detect available provider
            if self._test_ollama():
                logger.info("Auto-detected Ollama as AI provider")
                self.active_provider = 'ollama'
                self.model = self.ollama_model
            elif self.groq_api_key:
                logger.info("Auto-detected Groq as AI provider")
                self.active_provider = 'groq'
                self.model = self.groq_model
            elif self.openai_client:
                logger.info("Auto-detected OpenAI as AI provider")
                self.active_provider = 'openai'
                self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
            else:
                logger.warning("No AI provider available. Using fallback mode.")
                self.active_provider = 'fallback'
    
    def _test_ollama(self) -> bool:
        """Probar si Ollama está disponible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def analyze_architecture(self, text: str, diagram_type: str = 'auto') -> Dict[str, Any]:
        """Analizar texto para extraer componentes de arquitectura"""
        try:
            if self.active_provider == 'fallback':
                logger.info("Using fallback analysis (no AI provider available)")
                return self._get_fallback_analysis(text)
            
            system_prompt = self._get_system_prompt(diagram_type)
            user_prompt = self._get_user_prompt(text, diagram_type)
            
            # Usar el proveedor activo
            if self.active_provider == 'openai':
                analysis_text = self._call_openai(system_prompt, user_prompt)
            elif self.active_provider == 'ollama':
                analysis_text = self._call_ollama(system_prompt, user_prompt)
            elif self.active_provider == 'groq':
                analysis_text = self._call_groq(system_prompt, user_prompt)
            elif self.active_provider == 'huggingface':
                analysis_text = self._call_huggingface(system_prompt, user_prompt)
            else:
                raise Exception(f"Unknown AI provider: {self.active_provider}")
            
            analysis = self._parse_analysis(analysis_text)
            
            logger.info(f"Análisis completado con {self.active_provider}: {len(analysis.get('components', []))} componentes encontrados")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de IA ({self.active_provider}): {str(e)}")
            return self._get_fallback_analysis(text)
    
    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Llamar a OpenAI API"""
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        return response.choices[0].message.content
    
    def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """Llamar a Ollama API (local o hospedado)"""
        headers = {"Content-Type": "application/json"}
        
        # Agregar API key si está configurada (para servicios hospedados)
        if self.ollama_api_key:
            headers["Authorization"] = f"Bearer {self.ollama_api_key}"
        
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens
            }
        }
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['response']
        else:
            raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    def _call_groq(self, system_prompt: str, user_prompt: str) -> str:
        """Llamar a Groq API"""
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Groq API error: {response.status_code}")
    
    def _call_huggingface(self, system_prompt: str, user_prompt: str) -> str:
        """Llamar a Hugging Face API"""
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": f"{system_prompt}\n\n{user_prompt}",
            "parameters": {
                "temperature": self.temperature,
                "max_new_tokens": self.max_tokens
            }
        }
        
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{self.hf_model}",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            return str(result)
        else:
            raise Exception(f"Hugging Face API error: {response.status_code}")
    
    def _get_system_prompt(self, diagram_type: str) -> str:
        """Obtener prompt del sistema según el tipo de diagrama"""
        base_prompt = """🚀 ARQUITECTO SIN LÍMITES - Genera EXACTAMENTE lo que se solicita.

🎯 REGLAS ABSOLUTAS:
1. ✅ NÚMEROS EXACTOS: Si dice "20 suscripciones", genera EXACTAMENTE 20 componentes
2. ✅ NO IMPONER LÍMITES: Genera cualquier cantidad solicitada
3. ✅ AMBIENTES ESPECÍFICOS: "bajo/medio/alto" = clasificar componentes
4. ✅ ICONOS OBLIGATORIOS: Cada componente DEBE tener icon_category válida

📋 CATEGORÍAS DE ICONOS:
- integration_azure (servicios Azure)
- fortinet_fortinet-products (firewalls, seguridad)
- material-design-icons (iconos generales)
- kubernetes (contenedores)
- arista (networking)

🎨 POSICIONAMIENTO INTELIGENTE:
- Hub: x:1200, y:600
- Spokes: Grid con separación 800x600
- Distribución automática según cantidad

Responde ÚNICAMENTE en formato JSON válido:
{
    "diagram_type": "tipo_identificado",
    "title": "Título del diagrama",
    "description": "Breve descripción",
    "components": [
        {
            "id": "id_unico",
            "name": "Nombre del componente",
            "type": "tipo (service, database, api, frontend, etc.)",
            "technology": "tecnología específica",
            "description": "descripción breve",
            "layer": "capa arquitectónica",
            "icon_category": "categoría de icono sugerida",
            "position": {"x": posicion_x, "y": posicion_y}
        }
    ],
    "connections": [
        {
            "from": "id_origen",
            "to": "id_destino",
            "type": "tipo_conexion",
            "label": "etiqueta opcional",
            "protocol": "protocolo si aplica"
        }
    ],
    "layers": ["lista de capas identificadas"],
    "technologies": ["lista de tecnologías"],
    "patterns": ["patrones arquitectónicos identificados"]
}"""
        
        if diagram_type == 'aws':
            return base_prompt + "\n\nEnfócate en servicios AWS como EC2, RDS, S3, Lambda, etc."
        elif diagram_type == 'azure':
            return base_prompt + "\n\nEnfócate en servicios Azure como VMs, SQL Database, Blob Storage, Functions, etc."
        elif diagram_type == 'gcp':
            return base_prompt + "\n\nEnfócate en servicios GCP como Compute Engine, Cloud SQL, Cloud Storage, Cloud Functions, etc."
        elif diagram_type == 'kubernetes':
            return base_prompt + "\n\nEnfócate en componentes Kubernetes como Pods, Services, Deployments, ConfigMaps, etc."
        elif diagram_type == 'network':
            return base_prompt + "\n\nEnfócate en componentes de red como routers, switches, firewalls, load balancers, etc."
        else:
            return base_prompt + "\n\nIdentifica automáticamente el tipo de arquitectura más apropiado."
    
    def _get_user_prompt(self, text: str, diagram_type: str) -> str:
        """Obtener prompt del usuario"""
        return f"""Analiza la siguiente descripción de arquitectura y extrae los componentes y conexiones:

Tipo de diagrama solicitado: {diagram_type}

Texto a analizar:
{text}

Recuerda responder ÚNICAMENTE con JSON válido."""
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parsear respuesta de IA a formato estructurado"""
        try:
            # Limpiar texto y extraer JSON
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                analysis = json.loads(json_text)
                
                # Validar estructura
                if not isinstance(analysis.get('components'), list):
                    analysis['components'] = []
                if not isinstance(analysis.get('connections'), list):
                    analysis['connections'] = []
                
                # Asignar posiciones si no existen
                self._assign_positions(analysis['components'])
                
                return analysis
            else:
                return self._extract_components_fallback(analysis_text)
                
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de IA: {str(e)}")
            return self._extract_components_fallback(analysis_text)
    
    def _assign_positions(self, components: List[Dict]):
        """Asignar posiciones automáticas a componentes"""
        cols = 3
        spacing_x = 200
        spacing_y = 150
        start_x = 100
        start_y = 100
        
        for i, component in enumerate(components):
            if 'position' not in component:
                row = i // cols
                col = i % cols
                component['position'] = {
                    'x': start_x + col * spacing_x,
                    'y': start_y + row * spacing_y
                }
    
    def _extract_components_fallback(self, text: str) -> Dict[str, Any]:
        """Extracción de componentes usando reglas básicas como fallback"""
        components = []
        connections = []
        
        # Buscar patrones comunes con más detalle
        patterns = {
            'database': {
                'pattern': r'\b(database|db|mysql|postgresql|postgres|mongodb|redis|sqlite|oracle|sql server|mariadb|cassandra|dynamodb|rds)\b',
                'icon_category': 'database'
            },
            'api': {
                'pattern': r'\b(api|rest|graphql|endpoint|microservice|service)\b',
                'icon_category': 'api'
            },
            'frontend': {
                'pattern': r'\b(frontend|ui|web|app|client|react|angular|vue|html|css|javascript)\b',
                'icon_category': 'frontend'
            },
            'cache': {
                'pattern': r'\b(cache|redis|memcached|elasticache)\b',
                'icon_category': 'cache'
            },
            'queue': {
                'pattern': r'\b(queue|kafka|rabbitmq|sqs|message|broker)\b',
                'icon_category': 'queue'
            },
            'storage': {
                'pattern': r'\b(storage|s3|blob|file|bucket|disk|volume)\b',
                'icon_category': 'storage'
            },
            'loadbalancer': {
                'pattern': r'\b(load.?balancer|lb|nginx|apache|haproxy|alb|elb)\b',
                'icon_category': 'loadbalancer'
            },
            'container': {
                'pattern': r'\b(docker|container|kubernetes|k8s|pod|deployment)\b',
                'icon_category': 'container'
            },
            'cloud': {
                'pattern': r'\b(aws|azure|gcp|google.?cloud|amazon|microsoft|ec2|lambda|s3|rds)\b',
                'icon_category': 'cloud'
            },
            'network': {
                'pattern': r'\b(hub|spoke|vnet|subnet|gateway|vpn|expressroute|peering|network|routing)\b',
                'icon_category': 'network'
            },
            'subscription': {
                'pattern': r'\b(subscription|suscripcion|tenant|resource.?group)\b',
                'icon_category': 'subscription'
            }
        }
        
        component_id = 1
        found_components = set()  # Para evitar duplicados
        
        for component_type, config in patterns.items():
            matches = re.finditer(config['pattern'], text, re.IGNORECASE)
            for match in matches:
                component_name = match.group(0).title()
                
                # Evitar duplicados
                if component_name.lower() not in found_components:
                    found_components.add(component_name.lower())
                    
                    # Determinar tecnología más específica
                    technology = self._determine_technology(component_name, component_type)
                    
                    components.append({
                        'id': f'comp_{component_id}',
                        'name': component_name,
                        'type': component_type,
                        'technology': technology,
                        'description': f'Auto-detected {component_type}',
                        'layer': self._determine_layer(component_type),
                        'icon_category': config['icon_category'],
                        'position': self._calculate_position(component_id, component_type)
                    })
                    component_id += 1
        
        # Generar conexiones básicas
        connections = self._generate_basic_connections(components)
        
        return {
            'diagram_type': 'auto',
            'title': 'Auto-generated Architecture',
            'description': 'Automatically extracted from text using pattern matching',
            'components': components,
            'connections': connections,
            'layers': list(set([comp['layer'] for comp in components])),
            'technologies': list(set([comp['technology'] for comp in components])),
            'patterns': ['layered', 'service-oriented']
        }
    
    def _determine_technology(self, component_name: str, component_type: str) -> str:
        """Determinar tecnología específica basada en el nombre"""
        name_lower = component_name.lower()
        
        tech_mapping = {
            'mysql': 'MySQL',
            'postgresql': 'PostgreSQL', 'postgres': 'PostgreSQL',
            'mongodb': 'MongoDB',
            'redis': 'Redis',
            'nginx': 'Nginx',
            'apache': 'Apache',
            'docker': 'Docker',
            'kubernetes': 'Kubernetes', 'k8s': 'Kubernetes',
            'aws': 'AWS', 'ec2': 'AWS EC2', 'rds': 'AWS RDS', 's3': 'AWS S3',
            'azure': 'Microsoft Azure',
            'gcp': 'Google Cloud Platform',
            'react': 'React',
            'angular': 'Angular',
            'vue': 'Vue.js'
        }
        
        return tech_mapping.get(name_lower, component_name)
    
    def _determine_layer(self, component_type: str) -> str:
        """Determinar capa arquitectónica"""
        layer_mapping = {
            'frontend': 'presentation',
            'api': 'application',
            'service': 'application',
            'database': 'data',
            'cache': 'data',
            'storage': 'data',
            'loadbalancer': 'infrastructure',
            'queue': 'infrastructure',
            'container': 'infrastructure',
            'cloud': 'infrastructure'
        }
        
        return layer_mapping.get(component_type, 'application')
    
    def _calculate_position(self, component_id: int, component_type: str) -> Dict[str, int]:
        """Calcular posición basada en tipo y orden"""
        # Posiciones base por capa
        layer_y = {
            'presentation': 50,
            'application': 200,
            'data': 350,
            'infrastructure': 500
        }
        
        layer = self._determine_layer(component_type)
        base_y = layer_y.get(layer, 200)
        
        # Distribuir horizontalmente
        x = 100 + ((component_id - 1) % 4) * 200
        y = base_y + ((component_id - 1) // 4) * 100
        
        return {'x': x, 'y': y}
    
    def _generate_basic_connections(self, components: List[Dict]) -> List[Dict]:
        """Generar conexiones básicas entre componentes"""
        connections = []
        
        # Buscar patrones de conexión comunes
        frontend_components = [c for c in components if c['type'] == 'frontend']
        api_components = [c for c in components if c['type'] in ['api', 'service']]
        db_components = [c for c in components if c['type'] == 'database']
        cache_components = [c for c in components if c['type'] == 'cache']
        
        # Frontend -> API
        for frontend in frontend_components:
            for api in api_components:
                connections.append({
                    'from': frontend['id'],
                    'to': api['id'],
                    'type': 'http',
                    'label': 'HTTP/HTTPS',
                    'protocol': 'HTTP'
                })
        
        # API -> Database
        for api in api_components:
            for db in db_components:
                connections.append({
                    'from': api['id'],
                    'to': db['id'],
                    'type': 'data',
                    'label': 'Database Query',
                    'protocol': 'SQL/NoSQL'
                })
        
        # API -> Cache
        for api in api_components:
            for cache in cache_components:
                connections.append({
                    'from': api['id'],
                    'to': cache['id'],
                    'type': 'cache',
                    'label': 'Cache Access',
                    'protocol': 'Redis/Memcached'
                })
        
        return connections
    
    def _create_azure_hub_spoke_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura específica Azure Hub and Spoke"""
        components = []
        connections = []
        
        # Detectar número de spokes mencionados
        spoke_numbers = re.findall(r'(\d+)\s*(?:spoke|subscription|suscripcion)', text.lower())
        num_spokes = int(spoke_numbers[0]) if spoke_numbers else 3
        
        # Crear Hub VNet
        components.append({
            'id': 'hub_vnet',
            'name': 'Hub VNet',
            'type': 'network',
            'technology': 'Azure Virtual Network',
            'description': 'Central hub for connectivity',
            'layer': 'infrastructure',
            'icon_category': 'network',
            'position': {'x': 400, 'y': 200}
        })
        
        # Crear Gateway
        components.append({
            'id': 'vpn_gateway',
            'name': 'VPN Gateway',
            'type': 'network',
            'technology': 'Azure VPN Gateway',
            'description': 'Connectivity gateway',
            'layer': 'infrastructure',
            'icon_category': 'network',
            'position': {'x': 400, 'y': 100}
        })
        
        # Crear Spokes
        for i in range(num_spokes):
            spoke_id = f'spoke_vnet_{i+1}'
            components.append({
                'id': spoke_id,
                'name': f'Spoke VNet {i+1}',
                'type': 'network',
                'technology': 'Azure Virtual Network',
                'description': f'Spoke network {i+1}',
                'layer': 'infrastructure',
                'icon_category': 'network',
                'position': {
                    'x': 200 + (i * 150),
                    'y': 350
                }
            })
            
            # Crear suscripción para cada spoke
            sub_id = f'subscription_{i+1}'
            components.append({
                'id': sub_id,
                'name': f'Subscription {i+1}',
                'type': 'subscription',
                'technology': 'Azure Subscription',
                'description': f'Azure subscription {i+1}',
                'layer': 'infrastructure',
                'icon_category': 'subscription',
                'position': {
                    'x': 200 + (i * 150),
                    'y': 450
                }
            })
            
            # Conexiones Hub-Spoke
            connections.append({
                'from': 'hub_vnet',
                'to': spoke_id,
                'type': 'network',
                'label': 'VNet Peering',
                'protocol': 'Azure Peering'
            })
            
            # Conexiones Spoke-Subscription
            connections.append({
                'from': spoke_id,
                'to': sub_id,
                'type': 'contains',
                'label': 'Contains',
                'protocol': 'Azure Resource'
            })
        
        # Conexión Gateway-Hub
        connections.append({
            'from': 'vpn_gateway',
            'to': 'hub_vnet',
            'type': 'network',
            'label': 'Gateway Connection',
            'protocol': 'VPN/ExpressRoute'
        })
        
        return {
            'diagram_type': 'azure',
            'title': f'Azure Hub and Spoke - {num_spokes} Subscriptions',
            'description': f'Azure Hub and Spoke architecture with {num_spokes} spoke networks and subscriptions',
            'components': components,
            'connections': connections,
            'layers': ['infrastructure'],
            'technologies': ['Azure Virtual Network', 'Azure VPN Gateway', 'Azure Subscription'],
            'patterns': ['hub-and-spoke', 'network-segmentation']
        }
    
    def _get_fallback_analysis(self, text: str) -> Dict[str, Any]:
        """Análisis de fallback inteligente - detecta múltiples patrones de arquitectura"""
        logger.info("Using enhanced fallback analysis with comprehensive pattern matching")
        
        text_lower = text.lower()
        
        # ========================
        # 1. AZURE ARCHITECTURES
        # ========================
        
        # Azure Hub and Spoke
        if 'azure' in text_lower and ('hub' in text_lower or 'spoke' in text_lower):
            logger.info("Detected Azure Hub and Spoke architecture pattern")
            return self._create_azure_hub_spoke_architecture(text)
        
        # Azure Security Architecture
        if any(sec_word in text_lower for sec_word in ['firewall', 'waf', 'application gateway', 'security', 'nsg']):
            logger.info("Detected Security Architecture pattern")
            return self._create_security_architecture(text)
        
        # Azure Network Architecture 
        if any(net_word in text_lower for net_word in ['vnet', 'subnet', 'gateway', 'load balancer', 'traffic manager']):
            logger.info("Detected Network Architecture pattern")
            return self._create_network_architecture(text)
        
        # Azure Application Architecture
        if any(app_word in text_lower for app_word in ['app service', 'function', 'logic app', 'api management']):
            logger.info("Detected Application Architecture pattern")
            return self._create_application_architecture(text)
        
        # Azure Data Architecture
        if any(data_word in text_lower for data_word in ['sql', 'cosmos', 'synapse', 'data factory', 'storage']):
            logger.info("Detected Data Architecture pattern")  
            return self._create_data_architecture(text)
        
        # ========================
        # 2. AWS ARCHITECTURES
        # ========================
        
        if 'aws' in text_lower:
            logger.info("Detected AWS Architecture pattern")
            return self._create_aws_architecture(text)
        
        # ========================
        # 3. GCP ARCHITECTURES
        # ========================
        
        if any(gcp_word in text_lower for gcp_word in ['gcp', 'google cloud', 'compute engine', 'cloud sql']):
            logger.info("Detected GCP Architecture pattern")
            return self._create_gcp_architecture(text)
        
        # ========================
        # 4. MULTI-CLOUD / HYBRID
        # ========================
        
        if any(multi_word in text_lower for multi_word in ['multi-cloud', 'hybrid', 'on-premise', 'cross-cloud']):
            logger.info("Detected Multi-Cloud/Hybrid Architecture pattern")
            return self._create_hybrid_architecture(text)
        
        # ========================
        # 5. KUBERNETES / CONTAINER
        # ========================
        
        if any(k8s_word in text_lower for k8s_word in ['kubernetes', 'k8s', 'docker', 'container', 'pod', 'helm']):
            logger.info("Detected Kubernetes/Container Architecture pattern")
            return self._create_kubernetes_architecture(text)
        
        # ========================
        # 6. ANÁLISIS GENERAL INTELIGENTE
        # ========================
        
        logger.info("Using general intelligent component analysis")
        return self._extract_components_intelligent(text)
    
    def _create_security_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura de seguridad específica"""
        logger.info("Creating Security Architecture")
        
        components = []
        connections = []
        
        # Extraer componentes mencionados en el texto
        text_lower = text.lower()
        
        # Posiciones iniciales
        positions = {
            'firewall': {'x': 800, 'y': 400},
            'waf': {'x': 1200, 'y': 300},
            'app_gateway': {'x': 1400, 'y': 400},
            'load_balancer': {'x': 1600, 'y': 500},
            'backend': {'x': 2000, 'y': 400},
            'internet': {'x': 400, 'y': 400},
            'nsg': {'x': 1000, 'y': 600}
        }
        
        # Internet/External
        components.append({
            'id': 'internet',
            'name': 'Internet\nTraffic',
            'type': 'external',
            'technology': 'External Network',
            'description': 'Incoming traffic from internet',
            'layer': 'network',
            'icon_category': 'integration_infrastructure',
            'position': positions['internet']
        })
        
        # Azure Firewall si se menciona
        if any(fw_word in text_lower for fw_word in ['firewall', 'azure firewall']):
            components.append({
                'id': 'azure_firewall',
                'name': 'Azure Firewall\n(Premium)',
                'type': 'security',
                'technology': 'Azure Firewall Premium',
                'description': 'Network security with IDPS, URL filtering, and threat intelligence',
                'layer': 'security',
                'icon_category': 'fortinet_fortinet-products',
                'position': positions['firewall']
            })
            
            connections.append({
                'from': 'internet',
                'to': 'azure_firewall',
                'type': 'security_flow',
                'label': 'Traffic Inspection\nIDPS + Threat Intel',
                'protocol': 'Multiple'
            })
        
        # Application Gateway con WAF si se menciona
        if any(waf_word in text_lower for waf_word in ['waf', 'application gateway', 'app gateway']):
            components.append({
                'id': 'app_gateway',
                'name': 'Application Gateway\n(WAF v2)',
                'type': 'security',
                'technology': 'Azure Application Gateway',
                'description': 'Layer 7 load balancer with Web Application Firewall',
                'layer': 'application',
                'icon_category': 'integration_azure',
                'position': positions['app_gateway']
            })
            
            # Conectar desde firewall o internet
            source = 'azure_firewall' if 'azure_firewall' in [c['id'] for c in components] else 'internet'
            connections.append({
                'from': source,
                'to': 'app_gateway',
                'type': 'application_flow',
                'label': 'HTTP/HTTPS Traffic\nWAF Protection',
                'protocol': 'HTTPS/443'
            })
        
        # Load Balancer si se menciona
        if any(lb_word in text_lower for lb_word in ['load balancer', 'balancer']):
            components.append({
                'id': 'load_balancer',
                'name': 'Load Balancer\n(Standard)',
                'type': 'loadbalancer',
                'technology': 'Azure Load Balancer',
                'description': 'Layer 4 traffic distribution across backend pool',
                'layer': 'network',
                'icon_category': 'integration_azure',
                'position': positions['load_balancer']
            })
            
            # Conectar desde app gateway si existe
            if 'app_gateway' in [c['id'] for c in components]:
                connections.append({
                    'from': 'app_gateway',
                    'to': 'load_balancer',
                    'type': 'traffic_flow',
                    'label': 'Backend Traffic\nHealth Probes',
                    'protocol': 'HTTP/HTTPS'
                })
        
        # Backend Services
        backend_services = []
        if any(web_word in text_lower for web_word in ['web', 'app service', 'website']):
            backend_services.append({'name': 'Web App\nService', 'type': 'webapp', 'icon': 'integration_azure'})
        if any(api_word in text_lower for api_word in ['api', 'api management']):
            backend_services.append({'name': 'API\nManagement', 'type': 'api', 'icon': 'integration_integration'})
        if any(db_word in text_lower for db_word in ['database', 'sql']):
            backend_services.append({'name': 'SQL Database\n(Premium)', 'type': 'database', 'icon': 'integration_databases'})
        
        # Si no hay servicios específicos, crear genérico
        if not backend_services:
            backend_services.append({'name': 'Backend\nServices', 'type': 'service', 'icon': 'integration_azure'})
        
        # Agregar servicios backend
        for i, service in enumerate(backend_services):
            service_id = f'backend_service_{i+1}'
            components.append({
                'id': service_id,
                'name': service['name'],
                'type': service['type'],
                'technology': f'Azure {service["name"].split()[0]}',
                'description': f'{service["name"]} with enterprise security',
                'layer': 'application',
                'icon_category': service['icon'],
                'position': {'x': positions['backend']['x'] + (i * 300), 'y': positions['backend']['y']}
            })
            
            # Conectar desde load balancer o app gateway
            source = 'load_balancer' if 'load_balancer' in [c['id'] for c in components] else 'app_gateway'
            if source in [c['id'] for c in components]:
                connections.append({
                    'from': source,
                    'to': service_id,
                    'type': 'service_flow',
                    'label': 'Protected Traffic\nSSL Termination',
                    'protocol': 'HTTPS'
                })
        
        # Network Security Group si se menciona
        if any(nsg_word in text_lower for nsg_word in ['nsg', 'network security', 'security group']):
            components.append({
                'id': 'nsg',
                'name': 'Network Security\nGroup (NSG)',
                'type': 'security',
                'technology': 'Azure NSG',
                'description': 'Subnet-level security rules and micro-segmentation',
                'layer': 'network',
                'icon_category': 'fortinet_fortinet-products',
                'position': positions['nsg']
            })
        
        return {
            'diagram_type': 'security_architecture',
            'title': 'Security Architecture with Multi-Layer Protection',
            'description': 'Comprehensive security architecture with firewall, WAF, and application protection',
            'components': components,
            'connections': connections,
            'layers': ['network', 'security', 'application'],
            'technologies': [
                'Azure Firewall Premium', 'Azure Application Gateway', 'Azure Load Balancer',
                'Web Application Firewall', 'Network Security Groups'
            ],
            'patterns': [
                'Defense in Depth', 'Zero Trust Network', 'Layer 7 Protection',
                'Traffic Inspection', 'SSL Termination'
            ]
        }
    
    def _create_network_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura de red específica"""
        logger.info("Creating Network Architecture")
        
        components = []
        connections = []
        text_lower = text.lower()
        
        # VNet principal
        components.append({
            'id': 'main_vnet',
            'name': 'Virtual Network\n10.0.0.0/16',
            'type': 'network',
            'technology': 'Azure Virtual Network',
            'description': 'Main virtual network with multiple subnets',
            'layer': 'network',
            'icon_category': 'integration_azure',
            'position': {'x': 1200, 'y': 600}
        })
        
        # Subnets comunes
        subnets = [
            {'name': 'Web Subnet\n10.0.1.0/24', 'type': 'subnet', 'pos': {'x': 800, 'y': 400}},
            {'name': 'App Subnet\n10.0.2.0/24', 'type': 'subnet', 'pos': {'x': 1200, 'y': 400}},
            {'name': 'Data Subnet\n10.0.3.0/24', 'type': 'subnet', 'pos': {'x': 1600, 'y': 400}}
        ]
        
        for subnet in subnets:
            subnet_id = subnet['name'].split()[0].lower() + '_subnet'
            components.append({
                'id': subnet_id,
                'name': subnet['name'],
                'type': 'subnet',
                'technology': 'Azure Subnet',
                'description': f'Isolated subnet for {subnet["name"].split()[0].lower()} tier',
                'layer': 'network',
                'icon_category': 'integration_infrastructure',
                'position': subnet['pos']
            })
            
            connections.append({
                'from': 'main_vnet',
                'to': subnet_id,
                'type': 'contains',
                'label': 'Subnet Segmentation',
                'protocol': 'Internal'
            })
        
        # Gateway si se menciona
        if any(gw_word in text_lower for gw_word in ['gateway', 'vpn', 'expressroute']):
            components.append({
                'id': 'vnet_gateway',
                'name': 'VNet Gateway\n(VpnGw2)',
                'type': 'gateway',
                'technology': 'Azure VPN Gateway',
                'description': 'Hybrid connectivity gateway',
                'layer': 'network',
                'icon_category': 'integration_azure',
                'position': {'x': 1200, 'y': 200}
            })
            
            connections.append({
                'from': 'vnet_gateway',
                'to': 'main_vnet',
                'type': 'gateway_connection',
                'label': 'Hybrid Connectivity\nSite-to-Site VPN',
                'protocol': 'IPSec'
            })
        
        return {
            'diagram_type': 'network_architecture',
            'title': 'Network Architecture with Subnet Segmentation',
            'description': 'Virtual network architecture with proper segmentation and connectivity',
            'components': components,
            'connections': connections,
            'layers': ['network'],
            'technologies': ['Azure Virtual Network', 'Azure Subnets', 'Azure VPN Gateway'],
            'patterns': ['Network Segmentation', 'Hybrid Connectivity', 'Micro-segmentation']
        }
    
    def _extract_components_intelligent(self, text: str) -> Dict[str, Any]:
        """Análisis inteligente general para cualquier arquitectura"""
        logger.info("Performing intelligent component analysis")
        
        components = []
        connections = []
        text_lower = text.lower()
        
        # DICCIONARIO MASIVO DE COMPONENTES - SOPORTE ILIMITADO
        known_components = {
            # ==================== AZURE SERVICES ====================
            'app service': {'type': 'webapp', 'icon': 'integration_azure', 'tech': 'Azure App Service'},
            'function app': {'type': 'function', 'icon': 'integration_azure', 'tech': 'Azure Functions'},
            'logic app': {'type': 'workflow', 'icon': 'integration_azure', 'tech': 'Azure Logic Apps'},
            'sql database': {'type': 'database', 'icon': 'integration_databases', 'tech': 'Azure SQL Database'},
            'cosmos db': {'type': 'database', 'icon': 'integration_databases', 'tech': 'Azure Cosmos DB'},
            'storage account': {'type': 'storage', 'icon': 'integration_azure', 'tech': 'Azure Storage'},
            'key vault': {'type': 'security', 'icon': 'integration_azure', 'tech': 'Azure Key Vault'},
            'application gateway': {'type': 'gateway', 'icon': 'integration_azure', 'tech': 'Azure Application Gateway'},
            'load balancer': {'type': 'loadbalancer', 'icon': 'integration_azure', 'tech': 'Azure Load Balancer'},
            'firewall': {'type': 'security', 'icon': 'fortinet_fortinet-products', 'tech': 'Azure Firewall'},
            'virtual machine': {'type': 'compute', 'icon': 'integration_infrastructure', 'tech': 'Azure Virtual Machine'},
            'api management': {'type': 'api', 'icon': 'integration_integration', 'tech': 'Azure API Management'},
            'service bus': {'type': 'messaging', 'icon': 'integration_integration', 'tech': 'Azure Service Bus'},
            'event hub': {'type': 'streaming', 'icon': 'integration_azure', 'tech': 'Azure Event Hub'},
            'redis cache': {'type': 'cache', 'icon': 'integration_databases', 'tech': 'Azure Redis Cache'},
            'virtual network': {'type': 'network', 'icon': 'integration_azure', 'tech': 'Azure Virtual Network'},
            'vpn gateway': {'type': 'gateway', 'icon': 'integration_azure', 'tech': 'Azure VPN Gateway'},
            'express route': {'type': 'connectivity', 'icon': 'integration_azure', 'tech': 'Azure ExpressRoute'},
            'traffic manager': {'type': 'dns', 'icon': 'integration_azure', 'tech': 'Azure Traffic Manager'},
            'azure ad': {'type': 'identity', 'icon': 'integration_azure', 'tech': 'Azure Active Directory'},
            'container registry': {'type': 'containers', 'icon': 'integration_developer', 'tech': 'Azure Container Registry'},
            'kubernetes service': {'type': 'containers', 'icon': 'integration_developer', 'tech': 'Azure Kubernetes Service'},
            'data factory': {'type': 'etl', 'icon': 'integration_azure', 'tech': 'Azure Data Factory'},
            'synapse': {'type': 'analytics', 'icon': 'integration_azure', 'tech': 'Azure Synapse Analytics'},
            'power bi': {'type': 'bi', 'icon': 'integration_power-bi', 'tech': 'Power BI'},
            'monitor': {'type': 'monitoring', 'icon': 'integration_azure', 'tech': 'Azure Monitor'},
            'security center': {'type': 'security', 'icon': 'integration_azure', 'tech': 'Azure Security Center'},
            'sentinel': {'type': 'siem', 'icon': 'integration_azure', 'tech': 'Microsoft Sentinel'},
            'backup': {'type': 'backup', 'icon': 'integration_azure', 'tech': 'Azure Backup'},
            'site recovery': {'type': 'dr', 'icon': 'integration_azure', 'tech': 'Azure Site Recovery'},
            
            # ==================== AWS SERVICES ====================
            'ec2': {'type': 'compute', 'icon': 'integration_infrastructure', 'tech': 'Amazon EC2'},
            'rds': {'type': 'database', 'icon': 'integration_databases', 'tech': 'Amazon RDS'},
            's3': {'type': 'storage', 'icon': 'integration_infrastructure', 'tech': 'Amazon S3'},
            'lambda': {'type': 'function', 'icon': 'integration_developer', 'tech': 'AWS Lambda'},
            'elb': {'type': 'loadbalancer', 'icon': 'integration_infrastructure', 'tech': 'AWS ELB'},
            'cloudfront': {'type': 'cdn', 'icon': 'integration_infrastructure', 'tech': 'AWS CloudFront'},
            'route 53': {'type': 'dns', 'icon': 'integration_infrastructure', 'tech': 'AWS Route 53'},
            'cloudformation': {'type': 'iac', 'icon': 'integration_developer', 'tech': 'AWS CloudFormation'},
            'iam': {'type': 'identity', 'icon': 'integration_infrastructure', 'tech': 'AWS IAM'},
            'vpc': {'type': 'network', 'icon': 'integration_infrastructure', 'tech': 'AWS VPC'},
            'eks': {'type': 'containers', 'icon': 'integration_developer', 'tech': 'Amazon EKS'},
            'ecs': {'type': 'containers', 'icon': 'integration_developer', 'tech': 'Amazon ECS'},
            'fargate': {'type': 'containers', 'icon': 'integration_developer', 'tech': 'AWS Fargate'},
            'api gateway': {'type': 'api', 'icon': 'integration_integration', 'tech': 'AWS API Gateway'},
            'sqs': {'type': 'messaging', 'icon': 'integration_integration', 'tech': 'Amazon SQS'},
            'sns': {'type': 'messaging', 'icon': 'integration_integration', 'tech': 'Amazon SNS'},
            'dynamodb': {'type': 'database', 'icon': 'integration_databases', 'tech': 'Amazon DynamoDB'},
            'redshift': {'type': 'datawarehouse', 'icon': 'integration_databases', 'tech': 'Amazon Redshift'},
            'kinesis': {'type': 'streaming', 'icon': 'integration_azure', 'tech': 'Amazon Kinesis'},
            'cloudwatch': {'type': 'monitoring', 'icon': 'integration_infrastructure', 'tech': 'AWS CloudWatch'},
            'waf': {'type': 'security', 'icon': 'fortinet_fortinet-products', 'tech': 'AWS WAF'},
            'cognito': {'type': 'identity', 'icon': 'integration_infrastructure', 'tech': 'AWS Cognito'},
            
            # ==================== GCP SERVICES ====================
            'compute engine': {'type': 'compute', 'icon': 'integration_infrastructure', 'tech': 'Google Compute Engine'},
            'cloud sql': {'type': 'database', 'icon': 'integration_databases', 'tech': 'Google Cloud SQL'},
            'cloud storage': {'type': 'storage', 'icon': 'integration_infrastructure', 'tech': 'Google Cloud Storage'},
            'cloud functions': {'type': 'function', 'icon': 'integration_developer', 'tech': 'Google Cloud Functions'},
            'cloud run': {'type': 'containers', 'icon': 'integration_developer', 'tech': 'Google Cloud Run'},
            'gke': {'type': 'containers', 'icon': 'integration_developer', 'tech': 'Google Kubernetes Engine'},
            'cloud load balancing': {'type': 'loadbalancer', 'icon': 'integration_infrastructure', 'tech': 'Google Cloud Load Balancing'},
            'cloud cdn': {'type': 'cdn', 'icon': 'integration_infrastructure', 'tech': 'Google Cloud CDN'},
            'cloud dns': {'type': 'dns', 'icon': 'integration_infrastructure', 'tech': 'Google Cloud DNS'},
            'firebase': {'type': 'platform', 'icon': 'integration_developer', 'tech': 'Google Firebase'},
            'pub/sub': {'type': 'messaging', 'icon': 'integration_integration', 'tech': 'Google Pub/Sub'},
            'bigquery': {'type': 'analytics', 'icon': 'integration_databases', 'tech': 'Google BigQuery'},
            'dataflow': {'type': 'etl', 'icon': 'integration_developer', 'tech': 'Google Dataflow'},
            'cloud armor': {'type': 'security', 'icon': 'fortinet_fortinet-products', 'tech': 'Google Cloud Armor'},
            
            # ==================== VMWARE COMPONENTS ====================
            'vcenter': {'type': 'management', 'icon': 'integration_infrastructure', 'tech': 'VMware vCenter'},
            'esxi': {'type': 'hypervisor', 'icon': 'integration_infrastructure', 'tech': 'VMware ESXi'},
            'vsan': {'type': 'storage', 'icon': 'integration_infrastructure', 'tech': 'VMware vSAN'},
            'nsx': {'type': 'networking', 'icon': 'integration_infrastructure', 'tech': 'VMware NSX'},
            'vrops': {'type': 'monitoring', 'icon': 'integration_infrastructure', 'tech': 'VMware vRealize Operations'},
            'vra': {'type': 'automation', 'icon': 'integration_infrastructure', 'tech': 'VMware vRealize Automation'},
            'horizon': {'type': 'vdi', 'icon': 'integration_infrastructure', 'tech': 'VMware Horizon'},
            'tanzu': {'type': 'containers', 'icon': 'integration_developer', 'tech': 'VMware Tanzu'},
            
            # ==================== KUBERNETES COMPONENTS ====================
            'pod': {'type': 'containers', 'icon': 'integration_developer', 'tech': 'Kubernetes Pod'},
            'service': {'type': 'networking', 'icon': 'integration_integration', 'tech': 'Kubernetes Service'},
            'deployment': {'type': 'workload', 'icon': 'integration_developer', 'tech': 'Kubernetes Deployment'},
            'ingress': {'type': 'networking', 'icon': 'integration_integration', 'tech': 'Kubernetes Ingress'},
            'configmap': {'type': 'config', 'icon': 'integration_developer', 'tech': 'Kubernetes ConfigMap'},
            'secret': {'type': 'security', 'icon': 'integration_developer', 'tech': 'Kubernetes Secret'},
            'namespace': {'type': 'isolation', 'icon': 'integration_developer', 'tech': 'Kubernetes Namespace'},
            'persistent volume': {'type': 'storage', 'icon': 'integration_infrastructure', 'tech': 'Kubernetes PV'},
            'helm': {'type': 'packagemanager', 'icon': 'integration_developer', 'tech': 'Helm'},
            'istio': {'type': 'servicemesh', 'icon': 'integration_integration', 'tech': 'Istio Service Mesh'},
            'prometheus': {'type': 'monitoring', 'icon': 'integration_infrastructure', 'tech': 'Prometheus'},
            'grafana': {'type': 'visualization', 'icon': 'integration_infrastructure', 'tech': 'Grafana'},
            
            # ==================== NETWORK COMPONENTS ====================
            'router': {'type': 'networking', 'icon': 'integration_infrastructure', 'tech': 'Network Router'},
            'switch': {'type': 'networking', 'icon': 'integration_infrastructure', 'tech': 'Network Switch'},
            'firewall': {'type': 'security', 'icon': 'fortinet_fortinet-products', 'tech': 'Network Firewall'},
            'proxy': {'type': 'security', 'icon': 'integration_infrastructure', 'tech': 'Proxy Server'},
            'dns server': {'type': 'dns', 'icon': 'integration_infrastructure', 'tech': 'DNS Server'},
            'dhcp server': {'type': 'networking', 'icon': 'integration_infrastructure', 'tech': 'DHCP Server'},
            'ntp server': {'type': 'infrastructure', 'icon': 'integration_infrastructure', 'tech': 'NTP Server'},
            
            # ==================== GENERIC COMPONENTS ====================
            'database': {'type': 'database', 'icon': 'integration_databases', 'tech': 'Database'},
            'web server': {'type': 'webapp', 'icon': 'integration_infrastructure', 'tech': 'Web Server'},
            'api': {'type': 'api', 'icon': 'integration_integration', 'tech': 'API Service'},
            'cache': {'type': 'cache', 'icon': 'integration_databases', 'tech': 'Cache'},
            'queue': {'type': 'messaging', 'icon': 'integration_integration', 'tech': 'Message Queue'},
            'server': {'type': 'compute', 'icon': 'integration_infrastructure', 'tech': 'Server'},
            'application': {'type': 'webapp', 'icon': 'integration_azure', 'tech': 'Application'},
            'service': {'type': 'service', 'icon': 'integration_integration', 'tech': 'Service'},
            'component': {'type': 'component', 'icon': 'integration_azure', 'tech': 'Component'},
            'system': {'type': 'system', 'icon': 'integration_infrastructure', 'tech': 'System'},
            'platform': {'type': 'platform', 'icon': 'integration_azure', 'tech': 'Platform'},
            'microservice': {'type': 'microservice', 'icon': 'integration_integration', 'tech': 'Microservice'},
            'container': {'type': 'containers', 'icon': 'integration_developer', 'tech': 'Container'},
            'endpoint': {'type': 'api', 'icon': 'integration_integration', 'tech': 'Endpoint'},
            'interface': {'type': 'interface', 'icon': 'integration_integration', 'tech': 'Interface'}
        }
        
        # ALGORITMO INTELIGENTE DE BÚSQUEDA Y EXTRACCIÓN
        found_components = []
        words = text_lower.split()
        
        # 1. Búsqueda por coincidencias exactas y parciales
        for component_name, component_info in known_components.items():
            if component_name in text_lower:
                found_components.append((component_name, component_info))
        
        # 2. Búsqueda por palabras clave específicas
        component_keywords = {
            'web': ['web', 'website', 'frontend', 'ui', 'portal'],
            'database': ['db', 'database', 'data', 'storage', 'sql', 'nosql'],
            'api': ['api', 'rest', 'endpoint', 'service', 'microservice'],
            'cache': ['cache', 'redis', 'memcached', 'session'],
            'queue': ['queue', 'messaging', 'broker', 'kafka', 'rabbit'],
            'monitoring': ['monitor', 'metrics', 'logging', 'observability'],
            'security': ['security', 'auth', 'authentication', 'authorization'],
            'network': ['network', 'networking', 'vpc', 'vnet', 'subnet'],
            'compute': ['compute', 'vm', 'server', 'instance', 'node'],
            'container': ['container', 'docker', 'k8s', 'kubernetes', 'pod'],
            'storage': ['storage', 'disk', 'volume', 'blob', 'file'],
            'function': ['function', 'lambda', 'serverless', 'faas'],
            'gateway': ['gateway', 'proxy', 'reverse proxy', 'ingress'],
            'identity': ['identity', 'iam', 'rbac', 'sso', 'oauth'],
            'backup': ['backup', 'recovery', 'snapshot', 'archive'],
            'analytics': ['analytics', 'reporting', 'bi', 'warehouse']
        }
        
        for category, keywords in component_keywords.items():
            for keyword in keywords:
                if keyword in text_lower and not any(category in fc[0] for fc in found_components):
                    # Buscar componente apropiado en known_components
                    best_match = None
                    for comp_name, comp_info in known_components.items():
                        if comp_info['type'] == category or category in comp_name:
                            best_match = (comp_name, comp_info)
                            break
                    
                    if best_match:
                        found_components.append(best_match)
                    else:
                        # Crear componente genérico
                        found_components.append((f'{category}', {
                            'type': category,
                            'icon': 'integration_azure',
                            'tech': f'{category.title()} Component'
                        }))
                    break
        
        # 3. Extracción inteligente de nombres específicos
        # Buscar patrones como "crear X con Y" o "diagrama de X"
        import re
        patterns = [
            r'crear\s+(?:un\s+)?(.+?)\s+con',
            r'diagrama\s+(?:de\s+)?(.+?)(?:\s+con|\s*$)',
            r'arquitectura\s+(?:de\s+)?(.+?)(?:\s+con|\s*$)',
            r'sistema\s+(?:de\s+)?(.+?)(?:\s+con|\s*$)',
            r'infraestructura\s+(?:de\s+)?(.+?)(?:\s+con|\s*$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                match = match.strip()
                # Buscar si coincide con algún componente conocido
                for comp_name, comp_info in known_components.items():
                    if comp_name in match or match in comp_name:
                        if not any(comp_name in fc[0] for fc in found_components):
                            found_components.append((comp_name, comp_info))
        
        # 4. Si aún no hay componentes, análisis más profundo
        if not found_components:
            # Buscar cualquier cosa que parezca un servicio tecnológico
            tech_indicators = [
                'service', 'server', 'app', 'application', 'system', 'platform',
                'solution', 'infrastructure', 'architecture', 'component',
                'tool', 'framework', 'engine', 'manager', 'controller'
            ]
            
            for word in words:
                for indicator in tech_indicators:
                    if indicator in word and len(word) > 3:
                        found_components.append((f'{word}', {
                            'type': 'service',
                            'icon': 'integration_azure',
                            'tech': f'{word.title()} Service'
                        }))
                        break
                if found_components:
                    break
        
        # 5. Último recurso: crear componentes genéricos
        if not found_components:
            generic_components = [
                ('frontend', {'type': 'webapp', 'icon': 'integration_azure', 'tech': 'Frontend Application'}),
                ('backend', {'type': 'api', 'icon': 'integration_integration', 'tech': 'Backend Service'}),
                ('database', {'type': 'database', 'icon': 'integration_databases', 'tech': 'Database'})
            ]
            found_components.extend(generic_components)
        
        # Crear componentes con posicionamiento
        start_x = 800
        start_y = 400
        spacing = 400
        
        for i, (comp_name, comp_info) in enumerate(found_components[:6]):  # Max 6 componentes
            comp_id = f'component_{i+1}'
            col = i % 3
            row = i // 3
            
            components.append({
                'id': comp_id,
                'name': comp_name.title().replace('_', ' '),
                'type': comp_info['type'],
                'technology': comp_info['tech'],
                'description': f'{comp_info["tech"]} component extracted from requirements',
                'layer': 'application',
                'icon_category': comp_info['icon'],
                'position': {
                    'x': start_x + (col * spacing),
                    'y': start_y + (row * spacing)
                }
            })
        
        # Crear conexiones básicas entre componentes
        for i in range(len(components) - 1):
            connections.append({
                'from': components[i]['id'],
                'to': components[i + 1]['id'],
                'type': 'data_flow',
                'label': 'Data Flow',
                'protocol': 'HTTPS'
            })
        
        return {
            'diagram_type': 'intelligent_analysis',
            'title': f'Intelligent Architecture Analysis - {len(components)} Components',
            'description': 'Architecture derived from intelligent text analysis',
            'components': components,
            'connections': connections,
            'layers': ['application', 'data', 'network'],
            'technologies': [comp['technology'] for comp in components],
            'patterns': ['Service-Oriented Architecture', 'Microservices', 'Cloud-Native']
        }
    
    def _create_application_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura de aplicación con análisis más específico"""
        logger.info("Creating Application Architecture")
        
        text_lower = text.lower()
        
        # Detectar tipo específico de arquitectura
        if 'microservices' in text_lower:
            return self._create_microservices_architecture(text)
        elif 'serverless' in text_lower:
            return self._create_serverless_architecture(text)
        elif 'kubernetes' in text_lower or 'k8s' in text_lower:
            return self._create_kubernetes_architecture(text)
        elif 'hub' in text_lower and 'spoke' in text_lower:
            return self._create_hub_spoke_architecture(text)
        
        components = []
        connections = []
        
        # Frontend
        if any(fe_word in text_lower for fe_word in ['frontend', 'ui', 'web', 'portal', 'client']):
            components.append({
                'id': 'frontend',
                'name': 'Frontend\nApplication',
                'type': 'webapp',
                'technology': 'Web Application',
                'description': 'User interface and client-side logic',
                'layer': 'presentation',
                'icon_category': 'integration_azure',
                'position': {'x': 400, 'y': 300}
            })
        
        # API Gateway si se menciona
        if any(gw_word in text_lower for gw_word in ['api gateway', 'gateway', 'proxy']):
            components.append({
                'id': 'api_gateway',
                'name': 'API Gateway',
                'type': 'api',
                'technology': 'API Management',
                'description': 'API routing, authentication, and rate limiting',
                'layer': 'integration',
                'icon_category': 'integration_integration',
                'position': {'x': 800, 'y': 300}
            })
        
        # Backend Services
        backend_services = []
        if any(be_word in text_lower for be_word in ['backend', 'api', 'service', 'microservice']):
            backend_services.append({'name': 'Backend\nService', 'type': 'api', 'icon': 'integration_integration'})
        if any(func_word in text_lower for func_word in ['function', 'lambda', 'serverless']):
            backend_services.append({'name': 'Functions', 'type': 'function', 'icon': 'integration_azure'})
        if any(logic_word in text_lower for logic_word in ['logic app', 'workflow', 'orchestration']):
            backend_services.append({'name': 'Logic Apps', 'type': 'workflow', 'icon': 'integration_azure'})
            
        if not backend_services:
            backend_services.append({'name': 'App Service', 'type': 'webapp', 'icon': 'integration_azure'})
        
        for i, service in enumerate(backend_services):
            components.append({
                'id': f'service_{i+1}',
                'name': service['name'],
                'type': service['type'],
                'technology': f'Application {service["type"].title()}',
                'description': f'{service["name"]} for business logic processing',
                'layer': 'application',
                'icon_category': service['icon'],
                'position': {'x': 1200 + (i * 300), 'y': 300}
            })
        
        # Database
        if any(db_word in text_lower for db_word in ['database', 'sql', 'cosmos', 'storage']):
            components.append({
                'id': 'database',
                'name': 'Database',
                'type': 'database',
                'technology': 'Database Server',
                'description': 'Data persistence and storage',
                'layer': 'data',
                'icon_category': 'integration_databases',
                'position': {'x': 1200, 'y': 600}
            })
        
        # Crear conexiones
        if len(components) >= 2:
            for i in range(len(components) - 1):
                connections.append({
                    'from': components[i]['id'],
                    'to': components[i + 1]['id'],
                    'type': 'api_call',
                    'label': 'API Call',
                    'protocol': 'HTTPS'
                })
        
        return {
            'diagram_type': 'application_architecture',
            'title': 'Application Architecture',
            'description': 'Modern application architecture with frontend, backend, and data layers',
            'components': components,
            'connections': connections,
            'layers': ['presentation', 'integration', 'application', 'data'],
            'technologies': [comp['technology'] for comp in components],
            'patterns': ['Layered Architecture', 'API-First', 'Microservices']
        }
    
    def _create_microservices_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura de microservicios"""
        logger.info("Creating Microservices Architecture")
        
        components = []
        connections = []
        
        # API Gateway
        components.append({
            'id': 'api_gateway',
            'name': 'API Gateway',
            'type': 'api',
            'technology': 'API Management',
            'description': 'API routing and management',
            'layer': 'integration',
            'icon_category': 'integration_integration',
            'position': {'x': 400, 'y': 200}
        })
        
        # Microservicios
        services = ['User Service', 'Order Service', 'Payment Service', 'Notification Service']
        for i, service in enumerate(services):
            components.append({
                'id': f'service_{i+1}',
                'name': service,
                'type': 'api',
                'technology': 'Microservice',
                'description': f'{service} business logic',
                'layer': 'application',
                'icon_category': 'integration_integration',
                'position': {'x': 100 + i * 200, 'y': 400}
            })
            
            # Conectar con API Gateway
            connections.append({
                'from': 'api_gateway',
                'to': f'service_{i+1}',
                'type': 'api_call',
                'label': 'API Call',
                'protocol': 'HTTP'
            })
        
        return {
            'title': 'Microservices Architecture',
            'description': 'Distributed microservices architecture with API gateway',
            'diagram_type': 'microservices',
            'components': components,
            'connections': connections,
            'layers': ['integration', 'application'],
            'technologies': ['API Gateway', 'Microservices'],
            'patterns': ['Microservices', 'API Gateway']
        }
    
    def _create_serverless_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura serverless"""
        logger.info("Creating Serverless Architecture")
        
        components = []
        connections = []
        
        # Function Apps
        functions = ['HTTP Trigger', 'Timer Trigger', 'Queue Trigger']
        for i, func in enumerate(functions):
            components.append({
                'id': f'function_{i+1}',
                'name': func,
                'type': 'function',
                'technology': 'Azure Functions',
                'description': f'{func} function',
                'layer': 'compute',
                'icon_category': 'integration_azure',
                'position': {'x': 100 + i * 250, 'y': 300}
            })
        
        return {
            'title': 'Serverless Architecture',
            'description': 'Event-driven serverless architecture',
            'diagram_type': 'serverless',
            'components': components,
            'connections': connections,
            'layers': ['compute'],
            'technologies': ['Azure Functions'],
            'patterns': ['Serverless', 'Event-Driven']
        }
    
    def _create_data_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura de datos"""
        logger.info("Creating Data Architecture")
        
        components = []
        connections = []
        text_lower = text.lower()
        
        # Data Sources
        sources = []
        if any(app_word in text_lower for app_word in ['application', 'app', 'system']):
            sources.append({'name': 'Application\nSystems', 'type': 'application', 'icon': 'integration_azure'})
        if any(api_word in text_lower for api_word in ['api', 'rest', 'service']):
            sources.append({'name': 'API\nSources', 'type': 'api', 'icon': 'integration_integration'})
        if any(file_word in text_lower for file_word in ['file', 'csv', 'json', 'xml']):
            sources.append({'name': 'File\nSources', 'type': 'files', 'icon': 'integration_files'})
            
        if not sources:
            sources.append({'name': 'Data\nSources', 'type': 'data', 'icon': 'integration_azure'})
        
        for i, source in enumerate(sources):
            components.append({
                'id': f'source_{i+1}',
                'name': source['name'],
                'type': source['type'],
                'technology': f'Data {source["type"].title()}',
                'description': f'{source["name"]} providing raw data',
                'layer': 'source',
                'icon_category': source['icon'],
                'position': {'x': 400 + (i * 300), 'y': 200}
            })
        
        # ETL/Processing
        if any(etl_word in text_lower for etl_word in ['etl', 'data factory', 'pipeline', 'processing']):
            components.append({
                'id': 'etl_pipeline',
                'name': 'ETL Pipeline',
                'type': 'etl',
                'technology': 'Data Processing',
                'description': 'Extract, Transform, Load data processing',
                'layer': 'processing',
                'icon_category': 'integration_azure',
                'position': {'x': 800, 'y': 400}
            })
        
        # Storage/Database
        storage_types = []
        if any(sql_word in text_lower for sql_word in ['sql', 'database', 'relational']):
            storage_types.append({'name': 'SQL Database', 'type': 'database', 'icon': 'integration_databases'})
        if any(nosql_word in text_lower for nosql_word in ['nosql', 'cosmos', 'mongodb', 'document']):
            storage_types.append({'name': 'NoSQL Store', 'type': 'nosql', 'icon': 'integration_databases'})
        if any(dw_word in text_lower for dw_word in ['warehouse', 'synapse', 'redshift', 'bigquery']):
            storage_types.append({'name': 'Data Warehouse', 'type': 'datawarehouse', 'icon': 'integration_databases'})
            
        if not storage_types:
            storage_types.append({'name': 'Data Store', 'type': 'storage', 'icon': 'integration_databases'})
        
        for i, storage in enumerate(storage_types):
            components.append({
                'id': f'storage_{i+1}',
                'name': storage['name'],
                'type': storage['type'],
                'technology': f'Data {storage["type"].title()}',
                'description': f'{storage["name"]} for structured data',
                'layer': 'storage',
                'icon_category': storage['icon'],
                'position': {'x': 600 + (i * 300), 'y': 600}
            })
        
        # Analytics/BI
        if any(bi_word in text_lower for bi_word in ['analytics', 'bi', 'reporting', 'visualization']):
            components.append({
                'id': 'analytics',
                'name': 'Analytics\n& BI',
                'type': 'analytics',
                'technology': 'Business Intelligence',
                'description': 'Data analysis and visualization',
                'layer': 'analytics',
                'icon_category': 'integration_power-bi',
                'position': {'x': 1200, 'y': 400}
            })
        
        # Crear conexiones de flujo de datos
        for i in range(len(components) - 1):
            connections.append({
                'from': components[i]['id'],
                'to': components[i + 1]['id'],
                'type': 'data_flow',
                'label': 'Data Flow',
                'protocol': 'ETL'
            })
        
        return {
            'diagram_type': 'data_architecture',
            'title': 'Data Architecture',
            'description': 'End-to-end data architecture with ingestion, processing, and analytics',
            'components': components,
            'connections': connections,
            'layers': ['source', 'processing', 'storage', 'analytics'],
            'technologies': [comp['technology'] for comp in components],
            'patterns': ['ETL Pipeline', 'Data Lake', 'Data Warehouse', 'Real-time Analytics']
        }
    
    def _create_aws_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura AWS"""
        logger.info("Creating AWS Architecture")
        
        components = []
        connections = []
        text_lower = text.lower()
        
        # VPC
        components.append({
            'id': 'vpc',
            'name': 'VPC\n10.0.0.0/16',
            'type': 'network',
            'technology': 'AWS VPC',
            'description': 'Virtual Private Cloud for network isolation',
            'layer': 'network',
            'icon_category': 'integration_infrastructure',
            'position': {'x': 800, 'y': 400}
        })
        
        # EC2 si se menciona
        if any(ec2_word in text_lower for ec2_word in ['ec2', 'instance', 'compute', 'server']):
            components.append({
                'id': 'ec2',
                'name': 'EC2 Instances',
                'type': 'compute',
                'technology': 'Amazon EC2',
                'description': 'Elastic Compute Cloud instances',
                'layer': 'compute',
                'icon_category': 'integration_infrastructure',
                'position': {'x': 600, 'y': 600}
            })
        
        # RDS si se menciona
        if any(db_word in text_lower for db_word in ['rds', 'database', 'sql', 'mysql', 'postgres']):
            components.append({
                'id': 'rds',
                'name': 'RDS Database',
                'type': 'database',
                'technology': 'Amazon RDS',
                'description': 'Relational Database Service',
                'layer': 'data',
                'icon_category': 'integration_databases',
                'position': {'x': 1000, 'y': 600}
            })
        
        # S3 si se menciona
        if any(s3_word in text_lower for s3_word in ['s3', 'storage', 'bucket', 'object']):
            components.append({
                'id': 's3',
                'name': 'S3 Bucket',
                'type': 'storage',
                'technology': 'Amazon S3',
                'description': 'Simple Storage Service',
                'layer': 'storage',
                'icon_category': 'integration_infrastructure',
                'position': {'x': 1200, 'y': 400}
            })
        
        # Lambda si se menciona
        if any(lambda_word in text_lower for lambda_word in ['lambda', 'function', 'serverless']):
            components.append({
                'id': 'lambda',
                'name': 'Lambda Functions',
                'type': 'function',
                'technology': 'AWS Lambda',
                'description': 'Serverless compute functions',
                'layer': 'compute',
                'icon_category': 'integration_developer',
                'position': {'x': 400, 'y': 500}
            })
        
        # ELB si se menciona
        if any(lb_word in text_lower for lb_word in ['elb', 'load balancer', 'alb']):
            components.append({
                'id': 'elb',
                'name': 'Load Balancer',
                'type': 'loadbalancer',
                'technology': 'AWS ELB',
                'description': 'Elastic Load Balancer',
                'layer': 'network',
                'icon_category': 'integration_infrastructure',
                'position': {'x': 600, 'y': 200}
            })
        
        # Crear conexiones
        vpc_component = next((c for c in components if c['id'] == 'vpc'), None)
        if vpc_component:
            for comp in components:
                if comp['id'] != 'vpc':
                    connections.append({
                        'from': 'vpc',
                        'to': comp['id'],
                        'type': 'contains',
                        'label': 'VPC Network',
                        'protocol': 'TCP/IP'
                    })
        
        return {
            'diagram_type': 'aws_architecture',
            'title': 'AWS Cloud Architecture',
            'description': 'AWS-based cloud architecture with compute, storage, and networking',
            'components': components,
            'connections': connections,
            'layers': ['network', 'compute', 'storage', 'data'],
            'technologies': [comp['technology'] for comp in components],
            'patterns': ['Cloud-Native', 'Serverless', 'Microservices', 'Auto-Scaling']
        }
    
    def _create_gcp_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura GCP"""
        logger.info("Creating GCP Architecture")
        
        components = []
        connections = []
        text_lower = text.lower()
        
        # Project
        components.append({
            'id': 'gcp_project',
            'name': 'GCP Project',
            'type': 'project',
            'technology': 'Google Cloud Project',
            'description': 'Google Cloud project container',
            'layer': 'management',
            'icon_category': 'integration_infrastructure',
            'position': {'x': 800, 'y': 200}
        })
        
        # Compute Engine
        if any(compute_word in text_lower for compute_word in ['compute engine', 'vm', 'instance']):
            components.append({
                'id': 'compute_engine',
                'name': 'Compute Engine',
                'type': 'compute',
                'technology': 'Google Compute Engine',
                'description': 'Virtual machine instances',
                'layer': 'compute',
                'icon_category': 'integration_infrastructure',
                'position': {'x': 600, 'y': 400}
            })
        
        # Cloud SQL
        if any(sql_word in text_lower for sql_word in ['cloud sql', 'database', 'sql']):
            components.append({
                'id': 'cloud_sql',
                'name': 'Cloud SQL',
                'type': 'database',
                'technology': 'Google Cloud SQL',
                'description': 'Managed relational database',
                'layer': 'data',
                'icon_category': 'integration_databases',
                'position': {'x': 1000, 'y': 400}
            })
        
        # Cloud Storage
        if any(storage_word in text_lower for storage_word in ['cloud storage', 'storage', 'bucket']):
            components.append({
                'id': 'cloud_storage',
                'name': 'Cloud Storage',
                'type': 'storage',
                'technology': 'Google Cloud Storage',
                'description': 'Object storage service',
                'layer': 'storage',
                'icon_category': 'integration_infrastructure',
                'position': {'x': 1200, 'y': 400}
            })
        
        # Cloud Functions
        if any(func_word in text_lower for func_word in ['cloud functions', 'function', 'serverless']):
            components.append({
                'id': 'cloud_functions',
                'name': 'Cloud Functions',
                'type': 'function',
                'technology': 'Google Cloud Functions',
                'description': 'Serverless compute platform',
                'layer': 'compute',
                'icon_category': 'integration_developer',
                'position': {'x': 400, 'y': 400}
            })
        
        # GKE
        if any(k8s_word in text_lower for k8s_word in ['gke', 'kubernetes', 'container']):
            components.append({
                'id': 'gke',
                'name': 'GKE Cluster',
                'type': 'containers',
                'technology': 'Google Kubernetes Engine',
                'description': 'Managed Kubernetes service',
                'layer': 'containers',
                'icon_category': 'integration_developer',
                'position': {'x': 600, 'y': 600}
            })
        
        # Crear conexiones al proyecto
        for comp in components:
            if comp['id'] != 'gcp_project':
                connections.append({
                    'from': 'gcp_project',
                    'to': comp['id'],
                    'type': 'contains',
                    'label': 'Project Resource',
                    'protocol': 'GCP API'
                })
        
        return {
            'diagram_type': 'gcp_architecture',
            'title': 'Google Cloud Architecture',
            'description': 'GCP-based cloud architecture with managed services',
            'components': components,
            'connections': connections,
            'layers': ['management', 'compute', 'containers', 'storage', 'data'],
            'technologies': [comp['technology'] for comp in components],
            'patterns': ['Cloud-Native', 'Managed Services', 'Serverless', 'Container Orchestration']
        }
    
    def _create_kubernetes_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura Kubernetes"""
        logger.info("Creating Kubernetes Architecture")
        
        components = []
        connections = []
        text_lower = text.lower()
        
        # Cluster
        components.append({
            'id': 'k8s_cluster',
            'name': 'Kubernetes\nCluster',
            'type': 'cluster',
            'technology': 'Kubernetes Cluster',
            'description': 'Kubernetes cluster with master and worker nodes',
            'layer': 'infrastructure',
            'icon_category': 'integration_developer',
            'position': {'x': 800, 'y': 200}
        })
        
        # Namespaces
        if any(ns_word in text_lower for ns_word in ['namespace', 'environment']):
            components.append({
                'id': 'namespace',
                'name': 'Namespaces',
                'type': 'isolation',
                'technology': 'Kubernetes Namespace',
                'description': 'Resource isolation and organization',
                'layer': 'organization',
                'icon_category': 'integration_developer',
                'position': {'x': 600, 'y': 400}
            })
        
        # Pods
        if any(pod_word in text_lower for pod_word in ['pod', 'container', 'app']):
            components.append({
                'id': 'pods',
                'name': 'Pods',
                'type': 'containers',
                'technology': 'Kubernetes Pod',
                'description': 'Application containers running in pods',
                'layer': 'application',
                'icon_category': 'integration_developer',
                'position': {'x': 600, 'y': 600}
            })
        
        # Services
        if any(svc_word in text_lower for svc_word in ['service', 'networking', 'exposure']):
            components.append({
                'id': 'services',
                'name': 'Services',
                'type': 'networking',
                'technology': 'Kubernetes Service',
                'description': 'Service discovery and load balancing',
                'layer': 'networking',
                'icon_category': 'integration_integration',
                'position': {'x': 1000, 'y': 600}
            })
        
        # Ingress
        if any(ingress_word in text_lower for ingress_word in ['ingress', 'gateway', 'routing']):
            components.append({
                'id': 'ingress',
                'name': 'Ingress\nController',
                'type': 'networking',
                'technology': 'Kubernetes Ingress',
                'description': 'HTTP/HTTPS routing and SSL termination',
                'layer': 'networking',
                'icon_category': 'integration_integration',
                'position': {'x': 1000, 'y': 400}
            })
        
        # ConfigMaps/Secrets
        if any(config_word in text_lower for config_word in ['config', 'secret', 'configuration']):
            components.append({
                'id': 'config',
                'name': 'ConfigMaps\n& Secrets',
                'type': 'config',
                'technology': 'Kubernetes Configuration',
                'description': 'Configuration and secret management',
                'layer': 'configuration',
                'icon_category': 'integration_developer',
                'position': {'x': 400, 'y': 500}
            })
        
        # Storage
        if any(storage_word in text_lower for storage_word in ['volume', 'storage', 'persistent']):
            components.append({
                'id': 'storage',
                'name': 'Persistent\nVolumes',
                'type': 'storage',
                'technology': 'Kubernetes PV',
                'description': 'Persistent storage for applications',
                'layer': 'storage',
                'icon_category': 'integration_infrastructure',
                'position': {'x': 800, 'y': 700}
            })
        
        # Crear conexiones
        for comp in components:
            if comp['id'] != 'k8s_cluster':
                connections.append({
                    'from': 'k8s_cluster',
                    'to': comp['id'],
                    'type': 'orchestrates',
                    'label': 'K8s Management',
                    'protocol': 'Kubernetes API'
                })
        
        return {
            'diagram_type': 'kubernetes_architecture',
            'title': 'Kubernetes Architecture',
            'description': 'Container orchestration with Kubernetes components',
            'components': components,
            'connections': connections,
            'layers': ['infrastructure', 'organization', 'networking', 'application', 'configuration', 'storage'],
            'technologies': [comp['technology'] for comp in components],
            'patterns': ['Container Orchestration', 'Microservices', 'Service Mesh', 'GitOps']
        }
    
    def _create_hybrid_architecture(self, text: str) -> Dict[str, Any]:
        """Crear arquitectura híbrida/multi-cloud"""
        logger.info("Creating Hybrid/Multi-Cloud Architecture")
        
        components = []
        connections = []
        text_lower = text.lower()
        
        # On-Premises
        components.append({
            'id': 'on_premises',
            'name': 'On-Premises\nDatacenter',
            'type': 'datacenter',
            'technology': 'Physical Infrastructure',
            'description': 'On-premises servers and infrastructure',
            'layer': 'physical',
            'icon_category': 'integration_infrastructure',
            'position': {'x': 200, 'y': 400}
        })
        
        # Azure si se menciona
        if any(azure_word in text_lower for azure_word in ['azure', 'microsoft']):
            components.append({
                'id': 'azure_cloud',
                'name': 'Microsoft Azure',
                'type': 'cloud',
                'technology': 'Azure Cloud',
                'description': 'Microsoft Azure cloud services',
                'layer': 'cloud',
                'icon_category': 'integration_azure',
                'position': {'x': 600, 'y': 300}
            })
        
        # AWS si se menciona
        if any(aws_word in text_lower for aws_word in ['aws', 'amazon']):
            components.append({
                'id': 'aws_cloud',
                'name': 'Amazon AWS',
                'type': 'cloud',
                'technology': 'AWS Cloud',
                'description': 'Amazon Web Services cloud',
                'layer': 'cloud',
                'icon_category': 'integration_infrastructure',
                'position': {'x': 600, 'y': 500}
            })
        
        # GCP si se menciona
        if any(gcp_word in text_lower for gcp_word in ['gcp', 'google']):
            components.append({
                'id': 'gcp_cloud',
                'name': 'Google Cloud',
                'type': 'cloud',
                'technology': 'GCP Cloud',
                'description': 'Google Cloud Platform services',
                'layer': 'cloud',
                'icon_category': 'integration_infrastructure',
                'position': {'x': 600, 'y': 700}
            })
        
        # Connectivity
        components.append({
            'id': 'connectivity',
            'name': 'Hybrid\nConnectivity',
            'type': 'connectivity',
            'technology': 'VPN/ExpressRoute',
            'description': 'Secure connections between environments',
            'layer': 'connectivity',
            'icon_category': 'integration_infrastructure',
            'position': {'x': 1000, 'y': 400}
        })
        
        # Management
        if any(mgmt_word in text_lower for mgmt_word in ['management', 'monitor', 'governance']):
            components.append({
                'id': 'management',
                'name': 'Unified\nManagement',
                'type': 'management',
                'technology': 'Multi-Cloud Management',
                'description': 'Centralized management and monitoring',
                'layer': 'management',
                'icon_category': 'integration_infrastructure',
                'position': {'x': 1200, 'y': 400}
            })
        
        # Crear conexiones híbridas
        on_prem = next((c for c in components if c['id'] == 'on_premises'), None)
        if on_prem:
            for comp in components:
                if comp['layer'] == 'cloud':
                    connections.append({
                        'from': 'on_premises',
                        'to': comp['id'],
                        'type': 'hybrid_connection',
                        'label': 'Secure Connection',
                        'protocol': 'VPN/Dedicated Line'
                    })
        
        return {
            'diagram_type': 'hybrid_architecture',
            'title': 'Hybrid/Multi-Cloud Architecture',
            'description': 'Hybrid architecture spanning on-premises and multiple cloud providers',
            'components': components,
            'connections': connections,
            'layers': ['physical', 'cloud', 'connectivity', 'management'],
            'technologies': [comp['technology'] for comp in components],
            'patterns': ['Hybrid Cloud', 'Multi-Cloud', 'Cloud Bursting', 'Unified Management']
        }
    
    def extract_text_from_document(self, file_path: str) -> str:
        """Extraer texto de diferentes tipos de documentos"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_ext in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            elif file_ext == '.md':
                return self._extract_from_markdown(file_path)
            elif file_ext == '.txt':
                return self._extract_from_txt(file_path)
            elif file_ext == '.json':
                return self._extract_from_json(file_path)
            else:
                raise ValueError(f"Tipo de archivo no soportado: {file_ext}")
                
        except Exception as e:
            logger.error(f"Error extrayendo texto de {file_path}: {str(e)}")
            raise
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extraer texto de PDF"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extraer texto de DOCX"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _extract_from_markdown(self, file_path: str) -> str:
        """Extraer texto de Markdown"""
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
            # Convertir markdown a texto plano
            html = markdown.markdown(md_content)
            # Remover tags HTML básicos
            text = re.sub(r'<[^>]+>', '', html)
            return text
    
    def _extract_from_txt(self, file_path: str) -> str:
        """Extraer texto de TXT"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _extract_from_json(self, file_path: str) -> str:
        """Extraer texto de JSON"""
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            return json.dumps(json_data, indent=2)
    
    def enhance_analysis_with_context(self, analysis: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """Mejorar análisis con contexto adicional"""
        if not context:
            return analysis
        
        try:
            enhanced_prompt = f"""
            Mejora el siguiente análisis de arquitectura con el contexto adicional proporcionado:
            
            Análisis actual: {json.dumps(analysis, indent=2)}
            
            Contexto adicional: {context}
            
            Responde con el análisis mejorado en formato JSON.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            enhanced_text = response.choices[0].message.content
            enhanced_analysis = self._parse_analysis(enhanced_text)
            
            return enhanced_analysis if enhanced_analysis else analysis
            
        except Exception as e:
            logger.error(f"Error mejorando análisis: {str(e)}")
            return analysis
    
    def suggest_improvements(self, analysis: Dict[str, Any]) -> List[str]:
        """Sugerir mejoras para la arquitectura"""
        suggestions = []
        
        components = analysis.get('components', [])
        connections = analysis.get('connections', [])
        
        # Verificar patrones comunes
        if len(components) > 10:
            suggestions.append("Considere agrupar componentes relacionados en módulos")
        
        # Verificar bases de datos
        db_components = [c for c in components if c.get('type') == 'database']
        if len(db_components) > 3:
            suggestions.append("Evalúe la consolidación de bases de datos para reducir complejidad")
        
        # Verificar conexiones
        if len(connections) < len(components) - 1:
            suggestions.append("Verifique que todos los componentes estén correctamente conectados")
        
        # Verificar seguridad
        security_components = [c for c in components if 'security' in c.get('type', '').lower()]
        if not security_components:
            suggestions.append("Considere añadir componentes de seguridad como firewalls o gateways")
        
        return suggestions
