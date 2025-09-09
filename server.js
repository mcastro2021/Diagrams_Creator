// server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const Groq = require('groq-sdk');
const https = require('https');
const { URL } = require('url');
const axios = require('axios');
const cheerio = require('cheerio');

const app = express();
const port = process.env.PORT || 3001;

// Configurar Groq
const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
});

app.use(cors());
app.use(express.json());
app.use(express.static('.'));
app.use('/icons', express.static('icons'));

// Ruta específica para Draw.io
app.get('/drawio', (req, res) => {
  res.sendFile(__dirname + '/index-drawio.html');
});

// Servir el archivo HTML principal
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// Procesamiento inteligente de lenguaje natural para diagramas de Azure
app.post('/generate-diagram', (req, res) => {
  const { description } = req.body;
  
  if (!description || description.trim().length === 0) {
    return res.status(400).json({ 
      success: false, 
      error: 'La descripción no puede estar vacía' 
    });
  }
  
  try {
    const diagramData = processDescription(description);
    res.json({ success: true, data: diagramData });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Endpoint para obtener ejemplos de arquitecturas
app.get('/examples', (req, res) => {
  const examples = [
    {
      id: 'web-app-basic',
      name: 'Aplicación Web Básica',
      description: 'Una aplicación web con App Service, SQL Database y Storage Account',
      architecture: 'App Service conectado a SQL Database y Storage Account para archivos estáticos'
    },
    {
      id: 'microservices',
      name: 'Arquitectura de Microservicios',
      description: 'Múltiples servicios con API Gateway, Service Bus y Application Insights',
      architecture: 'API Gateway que conecta a múltiples App Services, Service Bus para comunicación asíncrona y Application Insights para monitoreo'
    },
    {
      id: 'data-pipeline',
      name: 'Pipeline de Datos',
      description: 'Procesamiento de datos con Data Factory, Data Lake y Synapse',
      architecture: 'Data Factory que extrae datos a Data Lake Storage, procesados por Synapse Analytics y almacenados en SQL Database'
    },
    {
      id: 'iot-solution',
      name: 'Solución IoT',
      description: 'Dispositivos IoT con IoT Hub, Stream Analytics y Power BI',
      architecture: 'Dispositivos IoT conectados a IoT Hub, datos procesados por Stream Analytics y visualizados en Power BI'
    }
  ];
  
  res.json({ success: true, examples });
});

function processDescription(description) {
  const elements = [];
  const connections = [];
  const text = description.toLowerCase();
  
  console.log('🔍 Procesando descripción:', description);
  console.log('📝 Texto normalizado:', text);
  
  // Función para detectar cantidades en el texto
  function detectQuantities(text) {
    const quantityMap = {
      'uno': 1, 'una': 1, 'un': 1, 'one': 1,
      'dos': 2, 'two': 2,
      'tres': 3, 'three': 3,
      'cuatro': 4, 'four': 4,
      'cinco': 5, 'five': 5,
      'seis': 6, 'six': 6,
      'siete': 7, 'seven': 7,
      'ocho': 8, 'eight': 8,
      'nueve': 9, 'nine': 9,
      'diez': 10, 'ten': 10,
      'múltiples': 3, 'multiple': 3, 'varios': 3, 'several': 3,
      'muchos': 4, 'many': 4, 'varias': 4
    };
    
    const quantities = new Map();
    
    // Patrones más específicos para detectar cantidades
    const patterns = [
      // Patrones para VMs
      { regex: /(\d+|\w+)\s+virtual\s+machines?/gi, serviceType: 'virtual machines' },
      { regex: /(\d+|\w+)\s+máquinas?\s+virtuales?/gi, serviceType: 'virtual machines' },
      { regex: /(\d+|\w+)\s+vms?/gi, serviceType: 'virtual machines' },
      
      // Patrones para bases de datos
      { regex: /(\d+|\w+)\s+bases?\s+de\s+datos?/gi, serviceType: 'bases de datos' },
      { regex: /(\d+|\w+)\s+databases?/gi, serviceType: 'bases de datos' },
      { regex: /(\d+|\w+)\s+sql\s+databases?/gi, serviceType: 'bases de datos' },
      
      // Patrones para App Services
      { regex: /(\d+|\w+)\s+app\s+services?/gi, serviceType: 'app services' },
      { regex: /(\d+|\w+)\s+aplicaciones?\s+web/gi, serviceType: 'app services' },
      
      // Patrones para Storage
      { regex: /(\d+|\w+)\s+storage\s+accounts?/gi, serviceType: 'storage accounts' },
      { regex: /(\d+|\w+)\s+cuentas?\s+de\s+almacenamiento/gi, serviceType: 'storage accounts' },
      
      // Patrones para Load Balancers
      { regex: /(\d+|\w+)\s+load\s+balancers?/gi, serviceType: 'load balancers' },
      { regex: /(\d+|\w+)\s+balanceadores?/gi, serviceType: 'load balancers' },
      
      // Patrones para Redis
      { regex: /(\d+|\w+)\s+redis\s+caches?/gi, serviceType: 'redis caches' },
      { regex: /(\d+|\w+)\s+caches?/gi, serviceType: 'redis caches' },
      
      // Patrones para Service Bus
      { regex: /(\d+|\w+)\s+service\s+buses?/gi, serviceType: 'service buses' },
      { regex: /(\d+|\w+)\s+colas?/gi, serviceType: 'service buses' },
      
      // Patrones para Kubernetes
      { regex: /(\d+|\w+)\s+kubernetes\s+services?/gi, serviceType: 'kubernetes services' },
      { regex: /(\d+|\w+)\s+aks\s+clusters?/gi, serviceType: 'kubernetes services' },
      { regex: /(\d+|\w+)\s+container\s+orchestrations?/gi, serviceType: 'kubernetes services' },
      
      // Patrones para Cognitive Services
      { regex: /(\d+|\w+)\s+cognitive\s+services?/gi, serviceType: 'cognitive services' },
      { regex: /(\d+|\w+)\s+ai\s+services?/gi, serviceType: 'cognitive services' },
      { regex: /(\d+|\w+)\s+machine\s+learning\s+services?/gi, serviceType: 'cognitive services' },
      
      // Patrones para Event Hubs
      { regex: /(\d+|\w+)\s+event\s+hubs?/gi, serviceType: 'event hubs' },
      { regex: /(\d+|\w+)\s+streaming\s+services?/gi, serviceType: 'event hubs' },
      
      // Patrones para Logic Apps
      { regex: /(\d+|\w+)\s+logic\s+apps?/gi, serviceType: 'logic apps' },
      { regex: /(\d+|\w+)\s+workflows?/gi, serviceType: 'logic apps' },
      
      // Patrones para API Management
      { regex: /(\d+|\w+)\s+api\s+gateways?/gi, serviceType: 'api gateways' },
      { regex: /(\d+|\w+)\s+api\s+managements?/gi, serviceType: 'api gateways' },
      
      // Patrones para Active Directory
      { regex: /(\d+|\w+)\s+active\s+directories?/gi, serviceType: 'active directories' },
      { regex: /(\d+|\w+)\s+identity\s+providers?/gi, serviceType: 'active directories' },
      
      // Patrones para CDN
      { regex: /(\d+|\w+)\s+cdns?/gi, serviceType: 'cdns' },
      { regex: /(\d+|\w+)\s+content\s+delivery\s+networks?/gi, serviceType: 'cdns' },
      
      // Patrones para Search
      { regex: /(\d+|\w+)\s+search\s+services?/gi, serviceType: 'search services' },
      { regex: /(\d+|\w+)\s+search\s+engines?/gi, serviceType: 'search services' },
      
      // Patrones para Notification Hubs
      { regex: /(\d+|\w+)\s+notification\s+hubs?/gi, serviceType: 'notification hubs' },
      { regex: /(\d+|\w+)\s+push\s+services?/gi, serviceType: 'notification hubs' },
      
      // Patrones para arquitecturas específicas
      { regex: /(\d+|\w+)\s+subcripciones?/gi, serviceType: 'subscriptions' },
      { regex: /(\d+|\w+)\s+subscriptions?/gi, serviceType: 'subscriptions' },
      { regex: /(\d+|\w+)\s+hub\s+and\s+spoke/gi, serviceType: 'hub and spoke' },
      { regex: /(\d+|\w+)\s+redes?\s+virtuales?/gi, serviceType: 'virtual networks' },
      { regex: /(\d+|\w+)\s+vnets?/gi, serviceType: 'virtual networks' }
    ];
    
    patterns.forEach(pattern => {
      const matches = text.match(pattern.regex);
      if (matches) {
        matches.forEach(match => {
          const parts = match.toLowerCase().trim().split(/\s+/);
          const quantityWord = parts[0];
          
          // Convertir palabra de cantidad a número
          let quantity = parseInt(quantityWord);
          if (isNaN(quantity)) {
            quantity = quantityMap[quantityWord] || 1;
          }
          
          if (quantity > 0) {
            // Sumar cantidades en lugar de sobrescribir
            const currentQuantity = quantities.get(pattern.serviceType) || 0;
            quantities.set(pattern.serviceType, currentQuantity + quantity);
            console.log(`🔢 Detectado: ${quantity} ${pattern.serviceType} (total: ${currentQuantity + quantity})`);
          }
        });
      }
    });
    
    return quantities;
  }
  
  const detectedQuantities = detectQuantities(text);
  console.log('🔢 Cantidades detectadas:', Array.from(detectedQuantities.entries()));
  
  // Patrones de reconocimiento expandidos para arquitecturas universales
  const servicePatterns = {
    'azure-vm': [
      'virtual machine', 'vm', 'máquina virtual', 'servidor', 'compute',
      'instancia', 'host', 'node', 'worker', 'servidor', 'máquina',
      'virtual machines', 'máquinas virtuales', 'servidores', 'instancias',
      'ec2', 'compute instance', 'instancia de computación', 'server',
      'compute node', 'worker node', 'master node', 'nodo', 'nodos',
      'instancia de computo', 'máquina', 'máquinas', 'servidor web',
      'web server', 'app server', 'application server', 'backend server',
      'frontend server', 'api server', 'microservice', 'microservicio'
    ],
    'azure-app-service': [
      'app service', 'web app', 'aplicación web', 'api', 'rest api',
      'web application', 'backend', 'frontend', 'servicio web', 'aplicación',
      'app', 'webapp', 'web application', 'aplicaciones web', 'apis',
      'web service', 'servicio web', 'aplicación web', 'sitio web',
      'website', 'sitio', 'portal', 'dashboard', 'admin panel',
      'user interface', 'ui', 'frontend app', 'backend app', 'api gateway',
      'gateway', 'proxy', 'load balancer', 'reverse proxy', 'cdn',
      'content delivery network', 'static website', 'spa', 'single page app'
    ],
    'azure-sql': [
      'sql database', 'sql db', 'base de datos sql', 'database', 'db',
      'sql server', 'relational database', 'tabla', 'tablas', 'sql',
      'base de datos', 'bases de datos', 'relacional', 'relacionales',
      'mysql', 'postgresql', 'postgres', 'oracle', 'sqlite',
      'data warehouse', 'data lake', 'analytics database', 'reporting db',
      'transactional database', 'oltp', 'olap', 'data mart', 'data store',
      'persistence layer', 'data layer', 'repository', 'data access layer'
    ],
    'azure-storage': [
      'storage account', 'storage', 'blob storage', 'file storage',
      'almacenamiento', 'archivos', 'blob', 'container', 'file',
      'almacenamiento', 'storage', 'archivos', 'files', 'blobs',
      's3', 'bucket', 'file system', 'sistema de archivos',
      'object storage', 'file share', 'backup storage', 'archive storage',
      'cold storage', 'hot storage', 'media storage', 'image storage',
      'document storage', 'log storage', 'temp storage', 'cache storage'
    ],
    'azure-vnet': [
      'virtual network', 'vnet', 'red virtual', 'network', 'subnet',
      'vpc', 'networking', 'conexión de red', 'red', 'networks',
      'virtual networks', 'redes virtuales', 'conexión', 'conexiones',
      'subnet', 'subred', 'vpc', 'red privada'
    ],
    'azure-load-balancer': [
      'load balancer', 'balanceador', 'load balancer', 'distribución de carga',
      'traffic manager', 'application gateway', 'balanceador de carga',
      'load balancer', 'traffic', 'gateway', 'balanceadores',
      'alb', 'nlb', 'elb', 'application load balancer'
    ],
    'azure-redis': [
      'redis cache', 'cache', 'redis', 'memoria caché', 'caching',
      'session store', 'distributed cache', 'caché', 'memoria cache',
      'redis cache', 'caches', 'cachés', 'memcache', 'memcached'
    ],
    'azure-service-bus': [
      'service bus', 'message queue', 'cola de mensajes', 'messaging',
      'event hub', 'event grid', 'pub/sub', 'cola', 'colas',
      'message queues', 'event hubs', 'service bus', 'mensajería',
      'kafka', 'rabbitmq', 'sqs', 'message broker'
    ],
    'azure-functions': [
      'azure functions', 'function app', 'serverless', 'lambda',
      'función', 'microservicio', 'event-driven', 'functions',
      'azure functions', 'function apps', 'serverless', 'funciones',
      'aws lambda', 'google cloud functions', 'serverless function'
    ],
    'azure-cosmos': [
      'cosmos db', 'cosmos database', 'nosql', 'document database',
      'base de datos no relacional', 'mongodb', 'cosmos',
      'document db', 'document database', 'nosql database',
      'dynamodb', 'cassandra', 'document store'
    ],
    'azure-key-vault': [
      'key vault', 'secrets', 'certificates', 'keys', 'contraseñas',
      'credenciales', 'authentication', 'authorization', 'vault',
      'key vaults', 'secrets', 'certificados', 'llaves',
      'secrets manager', 'hashi vault', 'secret management'
    ],
    'azure-monitor': [
      'application insights', 'monitor', 'logging', 'métricas',
      'alertas', 'dashboard', 'telemetría', 'monitoring',
      'insights', 'logs', 'métricas', 'alertas', 'dashboards',
      'cloudwatch', 'datadog', 'new relic', 'observability',
      'monitoring', 'observability', 'telemetry', 'analytics',
      'performance monitoring', 'health monitoring', 'uptime monitoring'
    ],
    
    // Servicios adicionales para arquitecturas más complejas
    'azure-kubernetes': [
      'kubernetes', 'aks', 'azure kubernetes service', 'container orchestration',
      'k8s', 'container platform', 'orchestration', 'container management',
      'pod', 'pods', 'deployment', 'service mesh', 'istio'
    ],
    'azure-container-registry': [
      'container registry', 'acr', 'azure container registry', 'docker registry',
      'image registry', 'container images', 'docker images', 'registry'
    ],
    'azure-cognitive-services': [
      'cognitive services', 'ai services', 'machine learning', 'artificial intelligence',
      'computer vision', 'speech services', 'language understanding', 'text analytics',
      'face api', 'custom vision', 'form recognizer', 'translator'
    ],
    'azure-event-hubs': [
      'event hubs', 'event streaming', 'event processing', 'stream processing',
      'real-time data', 'event sourcing', 'message streaming', 'data streaming'
    ],
    'azure-logic-apps': [
      'logic apps', 'workflow', 'automation', 'business process', 'integration',
      'workflow automation', 'process automation', 'business logic'
    ],
    'azure-api-management': [
      'api management', 'apim', 'api gateway', 'api portal', 'api documentation',
      'api versioning', 'api security', 'rate limiting', 'api analytics'
    ],
    'azure-active-directory': [
      'active directory', 'aad', 'identity', 'authentication', 'authorization',
      'single sign-on', 'sso', 'identity provider', 'user management', 'rbac'
    ],
    'azure-cdn': [
      'cdn', 'content delivery network', 'edge caching', 'global distribution',
      'static content', 'media delivery', 'web acceleration'
    ],
    'azure-search': [
      'search service', 'azure search', 'full-text search', 'search engine',
      'search index', 'search analytics', 'cognitive search'
    ],
    'azure-notification-hubs': [
      'notification hubs', 'push notifications', 'mobile notifications',
      'notification service', 'messaging service', 'alert service'
    ],
    'azure-firewall': [
      'firewall', 'azure firewall', 'network security', 'seguridad de red',
      'firewall manager', 'network security group', 'nsg', 'security rules',
      'reglas de seguridad', 'cortafuegos', 'filtrado de tráfico'
    ],
    'azure-bastion': [
      'bastion', 'azure bastion', 'remote access', 'acceso remoto',
      'rdp access', 'ssh access', 'secure access', 'acceso seguro',
      'jump host', 'bastion host', 'secure shell'
    ]
  };
  
  // Detectar patrones arquitectónicos específicos - Sistema inteligente expandido
  const architecturalPatterns = {
    'hub-and-spoke': {
      keywords: ['hub and spoke', 'hub-and-spoke', 'hub & spoke', 'centralized', 'centro y radios', 'topologia hub', 'arquitectura centralizada', 'red centralizada'],
      services: ['azure-firewall', 'azure-bastion', 'azure-vnet', 'azure-vm', 'azure-app-service', 'azure-sql', 'azure-storage'],
      description: 'Arquitectura hub and spoke con firewall central, bastion y múltiples VNets'
    },
    'multi-tier': {
      keywords: ['multi-tier', 'multi tier', '3-tier', 'three tier', 'n-tier', 'capas', 'tiers', 'tres capas', 'presentation layer', 'business layer', 'data layer', 'capa de presentación', 'capa de negocio', 'capa de datos'],
      services: ['azure-app-service', 'azure-sql', 'azure-storage', 'azure-load-balancer'],
      description: 'Arquitectura de múltiples capas'
    },
    'microservices': {
      keywords: ['microservices', 'microservicios', 'micro-service', 'distributed', 'servicios distribuidos', 'arquitectura distribuida', 'service mesh', 'malla de servicios'],
      services: ['azure-kubernetes', 'azure-app-service', 'azure-service-bus', 'azure-redis', 'azure-functions'],
      description: 'Arquitectura de microservicios'
    },
    'serverless': {
      keywords: ['serverless', 'sin servidor', 'functions as a service', 'faas', 'azure functions', 'event-driven', 'dirigido por eventos'],
      services: ['azure-functions', 'azure-logic-apps', 'azure-cosmos', 'azure-storage', 'azure-service-bus'],
      description: 'Arquitectura serverless con Azure Functions'
    },
    'big-data': {
      keywords: ['big data', 'grandes datos', 'data analytics', 'análisis de datos', 'data lake', 'lago de datos', 'data warehouse', 'almacén de datos', 'streaming', 'streaming de datos'],
      services: ['azure-data-lake', 'azure-sql', 'azure-cosmos', 'azure-storage', 'azure-functions', 'azure-event-hubs'],
      description: 'Arquitectura de big data y analytics'
    },
    'iot': {
      keywords: ['iot', 'internet of things', 'internet de las cosas', 'sensors', 'sensores', 'telemetry', 'telemetría', 'device', 'dispositivos', 'edge computing', 'computación en el borde'],
      services: ['azure-event-hubs', 'azure-iot-hub', 'azure-functions', 'azure-cosmos', 'azure-storage'],
      description: 'Arquitectura IoT con dispositivos y telemetría'
    },
    'ai-ml': {
      keywords: ['ai', 'artificial intelligence', 'inteligencia artificial', 'machine learning', 'aprendizaje automático', 'ml', 'cognitive', 'cognitivo', 'deep learning', 'aprendizaje profundo'],
      services: ['azure-cognitive', 'azure-machine-learning', 'azure-functions', 'azure-storage', 'azure-cosmos'],
      description: 'Arquitectura de inteligencia artificial y machine learning'
    },
    'high-availability': {
      keywords: ['high availability', 'alta disponibilidad', 'ha', 'disaster recovery', 'recuperación ante desastres', 'backup', 'respaldo', 'redundancy', 'redundancia', 'failover', 'conmutación por error'],
      services: ['azure-load-balancer', 'azure-app-service', 'azure-sql', 'azure-storage', 'azure-vnet', 'azure-monitor'],
      description: 'Arquitectura de alta disponibilidad'
    },
    'security-focused': {
      keywords: ['security', 'seguridad', 'secure', 'seguro', 'compliance', 'cumplimiento', 'governance', 'gobernanza', 'audit', 'auditoría', 'zero trust', 'confianza cero'],
      services: ['azure-key-vault', 'azure-security-center', 'azure-firewall', 'azure-bastion', 'azure-active-directory', 'azure-monitor'],
      description: 'Arquitectura centrada en seguridad'
    },
    'containerized': {
      keywords: ['container', 'containers', 'docker', 'kubernetes', 'aks', 'orchestration'],
      services: ['azure-kubernetes', 'azure-container-registry', 'azure-load-balancer'],
      description: 'Arquitectura basada en contenedores'
    }
  };

  // Detectar patrón arquitectónico
  let detectedPattern = null;
  for (const [patternName, pattern] of Object.entries(architecturalPatterns)) {
    for (const keyword of pattern.keywords) {
      if (text.includes(keyword.toLowerCase())) {
        detectedPattern = pattern;
        console.log(`🏗️ Patrón arquitectónico detectado: ${patternName}`);
        break;
      }
    }
    if (detectedPattern) break;
  }

  // Detectar servicios mencionados con puntuación mejorada
  const detectedServices = new Map();
  
  // Si se detectó un patrón arquitectónico, aplicar sus servicios primero
  if (detectedPattern) {
    console.log(`🏗️ Aplicando patrón arquitectónico: ${detectedPattern.description}`);
    
    // Para hub and spoke, configurar componentes específicos
    if (detectedPattern === architecturalPatterns['hub-and-spoke']) {
      console.log('🏗️ Configurando componentes específicos de Hub and Spoke');
      // Agregar componentes correctos del hub
      detectedServices.set('azure-firewall', 10); // Hub central
      detectedServices.set('azure-bastion', 10); // Hub central
      detectedServices.set('azure-vnet', 10); // Hub central
      // Agregar componentes de los spokes
      detectedServices.set('azure-vm', 8); // VMs en spokes
      detectedServices.set('azure-app-service', 8); // App Services en spokes
      detectedServices.set('azure-sql', 8); // SQL en spokes
      detectedServices.set('azure-storage', 8); // Storage en spokes
    } else {
      // Para otros patrones, usar servicios estándar
      detectedPattern.services.forEach(serviceType => {
        detectedServices.set(serviceType, 8);
      });
    }
  }
  
  Object.entries(servicePatterns).forEach(([serviceType, patterns]) => {
    let score = 0;
    patterns.forEach(pattern => {
      // Usar regex más flexible para detectar patrones
      const regex = new RegExp(`\\b${pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
      const matches = text.match(regex);
      if (matches) {
        // Puntuación basada en longitud del patrón y número de coincidencias
        score += matches.length * (pattern.length / 5);
      }
      
      // También buscar patrones parciales para casos como "web app" en "aplicación web"
      const partialRegex = new RegExp(pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
      const partialMatches = text.match(partialRegex);
      if (partialMatches) {
        score += partialMatches.length * (pattern.length / 10);
      }
    });
    
    if (score > 0) {
      detectedServices.set(serviceType, score);
    }
  });
  
  console.log('🎯 Servicios detectados con puntuación:', Array.from(detectedServices.entries()));
  
  // Si no se detectan servicios específicos, usar análisis más inteligente
  if (detectedServices.size === 0) {
    console.log('⚠️ No se detectaron servicios específicos, usando análisis inteligente');
    
    // Análisis por palabras clave y contexto
    const keywords = {
      'web': ['azure-app-service'],
      'aplicación': ['azure-app-service'],
      'app': ['azure-app-service'],
      'sitio': ['azure-app-service'],
      'sistema': ['azure-app-service'],
      'gestión': ['azure-app-service'],
      'usuarios': ['azure-app-service'],
      'database': ['azure-sql'],
      'base de datos': ['azure-sql'],
      'datos': ['azure-sql'],
      'sql': ['azure-sql'],
      'storage': ['azure-storage'],
      'almacenamiento': ['azure-storage'],
      'archivo': ['azure-storage'],
      'file': ['azure-storage'],
      'files': ['azure-storage'],
      'vm': ['azure-vm'],
      'máquina': ['azure-vm'],
      'servidor': ['azure-vm'],
      'server': ['azure-vm'],
      'cache': ['azure-redis'],
      'caché': ['azure-redis'],
      'redis': ['azure-redis'],
      'queue': ['azure-service-bus'],
      'cola': ['azure-service-bus'],
      'mensaje': ['azure-service-bus'],
      'message': ['azure-service-bus'],
      'function': ['azure-functions'],
      'función': ['azure-functions'],
      'serverless': ['azure-functions'],
      'nosql': ['azure-cosmos'],
      'document': ['azure-cosmos'],
      'cosmos': ['azure-cosmos'],
      'secret': ['azure-key-vault'],
      'key': ['azure-key-vault'],
      'vault': ['azure-key-vault'],
      'monitor': ['azure-monitor'],
      'insight': ['azure-monitor'],
      'log': ['azure-monitor'],
      'métrica': ['azure-monitor']
    };
    
    Object.entries(keywords).forEach(([keyword, services]) => {
      if (text.includes(keyword)) {
        services.forEach(service => {
          const currentScore = detectedServices.get(service) || 0;
          detectedServices.set(service, currentScore + 1);
        });
      }
    });
    
    // Si aún no hay nada, usar configuración básica basada en el contexto
    if (detectedServices.size === 0) {
      console.log('🔄 Usando configuración básica por defecto');
      
      // Si se detectó un patrón arquitectónico, usar sus servicios
      if (detectedPattern) {
        console.log(`🏗️ Aplicando patrón arquitectónico: ${detectedPattern.description}`);
        detectedPattern.services.forEach(serviceType => {
          detectedServices.set(serviceType, 8); // Alta puntuación para servicios del patrón
        });
        
        // Para hub and spoke, asegurar que se generen los componentes correctos
        if (detectedPattern === architecturalPatterns['hub-and-spoke']) {
          console.log('🏗️ Configurando componentes específicos de Hub and Spoke');
          // Limpiar servicios detectados incorrectamente
          detectedServices.clear();
          // Agregar componentes correctos del hub
          detectedServices.set('azure-firewall', 10); // Hub central
          detectedServices.set('azure-bastion', 10); // Hub central
          detectedServices.set('azure-vnet', 10); // Hub central
          // Agregar componentes de los spokes
          detectedServices.set('azure-vm', 8); // VMs en spokes
          detectedServices.set('azure-app-service', 8); // App Services en spokes
          detectedServices.set('azure-sql', 8); // SQL en spokes
          detectedServices.set('azure-storage', 8); // Storage en spokes
        }
      } else {
        // Detectar tipo de aplicación
        if (text.includes('web') || text.includes('aplicación') || text.includes('sitio')) {
          detectedServices.set('azure-app-service', 1);
          detectedServices.set('azure-sql', 1);
          detectedServices.set('azure-storage', 1);
        } else if (text.includes('microservicio') || text.includes('api') || text.includes('servicio')) {
          detectedServices.set('azure-app-service', 1);
          detectedServices.set('azure-service-bus', 1);
          detectedServices.set('azure-redis', 1);
          detectedServices.set('azure-monitor', 1);
        } else if (text.includes('datos') || text.includes('data') || text.includes('analytics')) {
          detectedServices.set('azure-sql', 1);
          detectedServices.set('azure-storage', 1);
          detectedServices.set('azure-cosmos', 1);
        } else {
          // Configuración básica por defecto
          detectedServices.set('azure-app-service', 1);
          detectedServices.set('azure-sql', 1);
          detectedServices.set('azure-storage', 1);
        }
      }
    }
  }
  
  // Crear elementos con posicionamiento inteligente y cantidades detectadas
  const serviceArray = Array.from(detectedServices);
  const elementWidth = 180;
  const elementHeight = 100;
  const spacing = 500;
  let elementIndex = 0;
  
  // Detectar si es arquitectura Hub and Spoke
  const isHubSpokeArchitecture = text.includes('hub and spoke') || text.includes('hub-and-spoke');
  
  // Función para mapear texto de servicio a tipo de Azure
  function mapServiceTextToType(serviceText) {
    const serviceTextLower = serviceText.toLowerCase();
    
    // Mapeo directo de tipos de servicio detectados
    if (serviceTextLower === 'virtual machines') {
      return 'azure-vm';
    }
    if (serviceTextLower === 'bases de datos') {
      return 'azure-sql';
    }
    if (serviceTextLower === 'app services') {
      return 'azure-app-service';
    }
    if (serviceTextLower === 'storage accounts') {
      return 'azure-storage';
    }
    if (serviceTextLower === 'load balancers') {
      return 'azure-load-balancer';
    }
    if (serviceTextLower === 'redis caches') {
      return 'azure-redis';
    }
    if (serviceTextLower === 'service buses') {
      return 'azure-service-bus';
    }
    
    // Mapeo por palabras clave (fallback)
    if (serviceTextLower.includes('virtual machine') || serviceTextLower.includes('vm') || 
        serviceTextLower.includes('máquina virtual') || serviceTextLower.includes('servidor')) {
      return 'azure-vm';
    }
    if (serviceTextLower.includes('app service') || serviceTextLower.includes('aplicación web') || 
        serviceTextLower.includes('web app') || serviceTextLower.includes('api')) {
      return 'azure-app-service';
    }
    if (serviceTextLower.includes('sql database') || serviceTextLower.includes('base de datos') || 
        serviceTextLower.includes('database') || serviceTextLower.includes('db')) {
      return 'azure-sql';
    }
    if (serviceTextLower.includes('storage account') || serviceTextLower.includes('storage') || 
        serviceTextLower.includes('almacenamiento')) {
      return 'azure-storage';
    }
    if (serviceTextLower.includes('virtual network') || serviceTextLower.includes('vnet') || 
        serviceTextLower.includes('red virtual') || serviceTextLower.includes('network')) {
      return 'azure-vnet';
    }
    if (serviceTextLower.includes('load balancer') || serviceTextLower.includes('balanceador')) {
      return 'azure-load-balancer';
    }
    if (serviceTextLower.includes('redis cache') || serviceTextLower.includes('cache') || 
        serviceTextLower.includes('redis')) {
      return 'azure-redis';
    }
    if (serviceTextLower.includes('service bus') || serviceTextLower.includes('queue') || 
        serviceTextLower.includes('cola')) {
      return 'azure-service-bus';
    }
    if (serviceTextLower.includes('azure functions') || serviceTextLower.includes('functions') || 
        serviceTextLower.includes('serverless')) {
      return 'azure-functions';
    }
    if (serviceTextLower.includes('cosmos db') || serviceTextLower.includes('cosmos') || 
        serviceTextLower.includes('nosql')) {
      return 'azure-cosmos';
    }
    if (serviceTextLower.includes('key vault') || serviceTextLower.includes('vault') || 
        serviceTextLower.includes('secrets')) {
      return 'azure-key-vault';
    }
    if (serviceTextLower.includes('application insights') || serviceTextLower.includes('monitor') || 
        serviceTextLower.includes('insights')) {
      return 'azure-monitor';
    }
    
    // Nuevos servicios para arquitecturas universales
    if (serviceTextLower.includes('kubernetes') || serviceTextLower.includes('aks') || 
        serviceTextLower.includes('container orchestration')) {
      return 'azure-kubernetes';
    }
    if (serviceTextLower.includes('cognitive services') || serviceTextLower.includes('ai services') || 
        serviceTextLower.includes('machine learning') || serviceTextLower.includes('artificial intelligence')) {
      return 'azure-cognitive-services';
    }
    if (serviceTextLower.includes('event hubs') || serviceTextLower.includes('event streaming') || 
        serviceTextLower.includes('stream processing')) {
      return 'azure-event-hubs';
    }
    if (serviceTextLower.includes('logic apps') || serviceTextLower.includes('workflow') || 
        serviceTextLower.includes('automation')) {
      return 'azure-logic-apps';
    }
    if (serviceTextLower.includes('api management') || serviceTextLower.includes('api gateway') || 
        serviceTextLower.includes('apim')) {
      return 'azure-api-management';
    }
    if (serviceTextLower.includes('active directory') || serviceTextLower.includes('aad') || 
        serviceTextLower.includes('identity') || serviceTextLower.includes('authentication')) {
      return 'azure-active-directory';
    }
    if (serviceTextLower.includes('cdn') || serviceTextLower.includes('content delivery network') || 
        serviceTextLower.includes('edge caching')) {
      return 'azure-cdn';
    }
    if (serviceTextLower.includes('search service') || serviceTextLower.includes('azure search') || 
        serviceTextLower.includes('search engine')) {
      return 'azure-search';
    }
    if (serviceTextLower.includes('notification hubs') || serviceTextLower.includes('push notifications') || 
        serviceTextLower.includes('notification service')) {
      return 'azure-notification-hubs';
    }
    
    // Mapeo para arquitecturas específicas
    if (serviceTextLower === 'subscriptions') { return 'azure-subscriptions'; } // Las subscripciones se mapean a iconos específicos
    if (serviceTextLower === 'hub and spoke') { return 'azure-vnet'; } // Hub and spoke se mapea a VNet
    if (serviceTextLower === 'virtual networks') { return 'azure-vnet'; }
    
    // Mapeo para servicios de seguridad
    if (serviceTextLower.includes('firewall') || serviceTextLower.includes('cortafuegos')) { return 'azure-firewall'; }
    if (serviceTextLower.includes('bastion') || serviceTextLower.includes('acceso remoto')) { return 'azure-bastion'; }
    
    return null;
  }
  
  // Procesar cantidades detectadas primero
  detectedQuantities.forEach((quantity, serviceText) => {
    const serviceType = mapServiceTextToType(serviceText);
    if (serviceType) {
      console.log(`📊 Generando ${quantity} elementos de tipo ${serviceType} para "${serviceText}"`);
      
      for (let i = 0; i < quantity; i++) {
        let x, y;
        
        if (isHubSpokeArchitecture) {
          // Posicionamiento especial para Hub and Spoke según documentación oficial
          if (serviceType === 'azure-subscriptions') {
            // Spokes (subscripciones) alrededor del hub
            const angle = (elementIndex * 90) * (Math.PI / 180); // 90 grados entre spokes
            const radius = 600; // Mayor distancia del hub
            x = 600 + Math.cos(angle) * radius; // Centro en 600,500
            y = 500 + Math.sin(angle) * radius;
          } else if (serviceType === 'azure-firewall') {
            // Hub central - Firewall en el centro
            x = 600;
            y = 500;
          } else if (serviceType === 'azure-bastion') {
            // Bastion cerca del firewall
            x = 700;
            y = 500;
          } else if (serviceType === 'azure-vnet') {
            // VNet del hub
            x = 500;
            y = 500;
          } else {
            // Otros servicios del hub alrededor del firewall
            const hubAngle = (elementIndex * 60) * (Math.PI / 180); // 60 grados entre servicios
            const hubRadius = 300;
            x = 600 + Math.cos(hubAngle) * hubRadius;
            y = 500 + Math.sin(hubAngle) * hubRadius;
          }
        } else {
          // Posicionamiento normal
          const row = Math.floor(elementIndex / 4);
          const col = elementIndex % 4;
          x = 100 + col * spacing;
          y = 100 + row * spacing;
        }
        
        const serviceInfo = getServiceInfo(serviceType);
        
        elements.push({
          id: `${serviceType}-${i + 1}`,
          type: serviceType,
          text: `${serviceInfo.name} ${i + 1}`,
          description: serviceInfo.description,
          x: x,
          y: y,
          width: elementWidth,
          height: elementHeight,
          color: serviceInfo.color
        });
        
        elementIndex++;
      }
      
      // NO remover servicios del patrón arquitectónico
      // Solo remover si no es un servicio del hub and spoke
      if (!isHubSpokeArchitecture || !['azure-firewall', 'azure-bastion', 'azure-vnet', 'azure-vm', 'azure-app-service', 'azure-sql', 'azure-storage'].includes(serviceType)) {
        detectedServices.delete(serviceType);
      } else {
        console.log(`🔒 Manteniendo servicio del patrón: ${serviceType}`);
      }
    }
  });
  
  // Procesar servicios restantes (sin cantidad específica)
  const remainingServices = Array.from(detectedServices);
  console.log(`🔍 Servicios restantes a procesar: ${remainingServices.map(([type, score]) => `${type}(${score})`).join(', ')}`);
  
  remainingServices.forEach(([serviceType, score]) => {
    let x, y;
    
    if (isHubSpokeArchitecture) {
      // Posicionamiento especial para Hub and Spoke según documentación oficial
      if (serviceType === 'azure-firewall') {
        // Hub central - Firewall en el centro
        x = 600;
        y = 500;
      } else if (serviceType === 'azure-bastion') {
        // Bastion cerca del firewall
        x = 700;
        y = 500;
      } else if (serviceType === 'azure-vnet') {
        // VNet del hub
        x = 500;
        y = 500;
      } else {
        // Otros servicios del hub alrededor del firewall
        const hubAngle = (elementIndex * 60) * (Math.PI / 180); // 60 grados entre servicios
        const hubRadius = 300;
        x = 600 + Math.cos(hubAngle) * hubRadius;
        y = 500 + Math.sin(hubAngle) * hubRadius;
      }
    } else {
      // Posicionamiento normal
      const row = Math.floor(elementIndex / 4);
      const col = elementIndex % 4;
      x = 100 + col * spacing;
      y = 100 + row * spacing;
    }
    
    const serviceInfo = getServiceInfo(serviceType);
    
    const element = {
      id: `${serviceType}-${elementIndex + 1}`,
      type: serviceType,
      text: serviceInfo.name,
      description: serviceInfo.description,
      x: x,
      y: y,
      width: elementWidth,
      height: elementHeight,
      color: serviceInfo.color
    };
    
    elements.push(element);
    console.log(`📦 Elemento creado: ${serviceType} - ${element.text} (x:${x}, y:${y})`);
    
    elementIndex++;
  });
  
  // Crear conexiones inteligentes basadas en patrones comunes
  createIntelligentConnections(elements, connections, text);
  
  return { 
    elements, 
    connections,
    metadata: {
      totalElements: elements.length,
      totalConnections: connections.length,
      detectedServices: Array.from(detectedServices)
    }
  };
}

function getServiceInfo(serviceType) {
  const serviceInfo = {
    'azure-vm': {
      name: 'Virtual Machine',
      description: 'Máquina virtual escalable',
      color: '#0078d4'
    },
    'azure-app-service': {
      name: 'App Service',
      description: 'Plataforma de aplicaciones web',
      color: '#0078d4'
    },
    'azure-sql': {
      name: 'SQL Database',
      description: 'Base de datos relacional',
      color: '#0078d4'
    },
    'azure-storage': {
      name: 'Storage Account',
      description: 'Almacenamiento en la nube',
      color: '#0078d4'
    },
    'azure-vnet': {
      name: 'Virtual Network',
      description: 'Red virtual privada',
      color: '#0078d4'
    },
    'azure-load-balancer': {
      name: 'Load Balancer',
      description: 'Distribución de tráfico',
      color: '#0078d4'
    },
    'azure-redis': {
      name: 'Redis Cache',
      description: 'Cache en memoria',
      color: '#0078d4'
    },
    'azure-service-bus': {
      name: 'Service Bus',
      description: 'Mensajería asíncrona',
      color: '#0078d4'
    },
    'azure-functions': {
      name: 'Azure Functions',
      description: 'Computación serverless',
      color: '#0078d4'
    },
    'azure-cosmos': {
      name: 'Cosmos DB',
      description: 'Base de datos NoSQL',
      color: '#0078d4'
    },
    'azure-key-vault': {
      name: 'Key Vault',
      description: 'Gestión de secretos',
      color: '#0078d4'
    },
    'azure-monitor': {
      name: 'Application Insights',
      description: 'Monitoreo y telemetría',
      color: '#0078d4'
    },
    'azure-kubernetes': {
      name: 'Azure Kubernetes Service',
      description: 'Orquestación de contenedores',
      color: '#0078d4'
    },
    'azure-container-registry': {
      name: 'Container Registry',
      description: 'Registro de imágenes de contenedores',
      color: '#0078d4'
    },
    'azure-cognitive-services': {
      name: 'Cognitive Services',
      description: 'Servicios de inteligencia artificial',
      color: '#0078d4'
    },
    'azure-event-hubs': {
      name: 'Event Hubs',
      description: 'Procesamiento de eventos en tiempo real',
      color: '#0078d4'
    },
    'azure-logic-apps': {
      name: 'Logic Apps',
      description: 'Automatización de procesos de negocio',
      color: '#0078d4'
    },
    'azure-api-management': {
      name: 'API Management',
      description: 'Gestión y seguridad de APIs',
      color: '#0078d4'
    },
    'azure-active-directory': {
      name: 'Active Directory',
      description: 'Gestión de identidades y acceso',
      color: '#0078d4'
    },
    'azure-cdn': {
      name: 'Content Delivery Network',
      description: 'Red de entrega de contenido',
      color: '#0078d4'
    },
    'azure-search': {
      name: 'Azure Search',
      description: 'Servicio de búsqueda en la nube',
      color: '#0078d4'
    },
    'azure-notification-hubs': {
      name: 'Notification Hubs',
      description: 'Servicio de notificaciones push',
      color: '#0078d4'
    },
    'azure-firewall': {
      name: 'Azure Firewall',
      description: 'Firewall de red administrado',
      color: '#0078d4'
    },
    'azure-bastion': {
      name: 'Azure Bastion',
      description: 'Acceso remoto seguro a VMs',
      color: '#0078d4'
    },
    'azure-subscriptions': {
      name: 'Subscriptions',
      description: 'Suscripciones de Azure',
      color: '#0078d4'
    }
  };
  
  return serviceInfo[serviceType] || {
    name: 'Azure Service',
    description: 'Servicio de Azure',
    color: '#0078d4'
  };
}

function createIntelligentConnections(elements, connections, description) {
  console.log('🔗 Creando conexiones inteligentes para', elements.length, 'elementos');
  
  // Agrupar elementos por tipo
  const elementsByType = {};
  elements.forEach(element => {
    if (!elementsByType[element.type]) {
      elementsByType[element.type] = [];
    }
    elementsByType[element.type].push(element);
  });
  
  console.log('📊 Elementos agrupados por tipo:', Object.keys(elementsByType).map(type => 
    `${type}: ${elementsByType[type].length}`
  ));
  
  // Patrones de conexión mejorados y más específicos
  const connectionPatterns = [
    // Load Balancer → VMs/App Services (distribución de carga)
    { 
      from: 'azure-load-balancer', 
      to: ['azure-vm', 'azure-app-service'], 
      pattern: 'load-balance',
      label: 'Traffic Distribution'
    },
    
    // VMs → VNet (conexión de red)
    { 
      from: 'azure-vm', 
      to: ['azure-vnet'], 
      pattern: 'network',
      label: 'Network Connection'
    },
    
    // App Services → Databases (conexiones de datos)
    { 
      from: 'azure-app-service', 
      to: ['azure-sql', 'azure-cosmos', 'azure-redis'], 
      pattern: 'data',
      label: 'Data Access'
    },
    
    // App Services → Storage (almacenamiento)
    { 
      from: 'azure-app-service', 
      to: ['azure-storage'], 
      pattern: 'storage',
      label: 'File Storage'
    },
    
    // Service Bus → Microservices (mensajería)
    { 
      from: 'azure-service-bus', 
      to: ['azure-app-service', 'azure-functions'], 
      pattern: 'messaging',
      label: 'Message Queue'
    },
    
    // Functions → Storage/Databases (serverless)
    { 
      from: 'azure-functions', 
      to: ['azure-storage', 'azure-sql', 'azure-cosmos'], 
      pattern: 'serverless',
      label: 'Serverless Access'
    },
    
    // VMs → Databases (conexión directa)
    { 
      from: 'azure-vm', 
      to: ['azure-sql', 'azure-cosmos'], 
      pattern: 'direct-db',
      label: 'Database Connection'
    },
    
    // VMs → Storage (almacenamiento directo)
    { 
      from: 'azure-vm', 
      to: ['azure-storage'], 
      pattern: 'direct-storage',
      label: 'Storage Access'
    }
  ];
  
  // Aplicar patrones de conexión
  connectionPatterns.forEach(pattern => {
    const sourceElements = elementsByType[pattern.from] || [];
    const targetTypes = pattern.to;
    
    sourceElements.forEach(source => {
      targetTypes.forEach(targetType => {
        const targetElements = elementsByType[targetType] || [];
        
        if (targetElements.length > 0) {
          // Para load balancer, conectar a TODOS los elementos de destino
          if (pattern.pattern === 'load-balance') {
            targetElements.forEach(target => {
              addConnection(connections, source, target, pattern.label);
            });
          }
          // Para conexiones de red, conectar VMs a VNet
          else if (pattern.pattern === 'network') {
            targetElements.forEach(target => {
              addConnection(connections, source, target, pattern.label);
            });
          }
          // Para conexiones de datos, conectar a TODOS los elementos de destino
          else if (pattern.pattern === 'data' || pattern.pattern === 'storage') {
            targetElements.forEach(target => {
              addConnection(connections, source, target, pattern.label);
            });
          }
          // Para otros patrones, conectar al primer elemento
          else {
            const target = targetElements[0];
            addConnection(connections, source, target, pattern.label);
          }
        }
      });
    });
  });
  
  // Conexiones específicas basadas en la descripción
  createContextualConnections(elements, connections, description, elementsByType);
  
  // Si no hay conexiones, crear conexiones básicas entre elementos relacionados
  if (connections.length === 0 && elements.length > 1) {
    createFallbackConnections(elements, connections);
  }
  
  console.log('✅ Conexiones creadas:', connections.length);
}

function addConnection(connections, source, target, label) {
  // Evitar conexiones duplicadas
  const existingConnection = connections.find(c => 
    (c.source === source.id && c.target === target.id) ||
    (c.source === target.id && c.target === source.id)
  );
  
  if (!existingConnection) {
    connections.push({
      id: `conn-${connections.length + 1}`,
      source: source.id,
      target: target.id,
      type: 'standard',
      label: label
    });
  }
}

function createContextualConnections(elements, connections, description, elementsByType) {
  const text = description.toLowerCase();
  
  // Conexiones específicas para arquitectura Hub and Spoke
  if (text.includes('hub and spoke') || text.includes('hub-and-spoke')) {
    console.log('🏗️ Creando conexiones para arquitectura Hub and Spoke');
    
    // Conectar Azure Firewall (hub) a todas las VNets (spokes)
    if (elementsByType['azure-firewall'] && elementsByType['azure-vnet']) {
      elementsByType['azure-firewall'].forEach(firewall => {
        elementsByType['azure-vnet'].forEach(vnet => {
          addConnection(connections, firewall, vnet, 'Traffic Control');
        });
      });
    }
    
    // Conectar Azure Bastion (hub) a todas las VMs (spokes)
    if (elementsByType['azure-bastion'] && elementsByType['azure-vm']) {
      elementsByType['azure-bastion'].forEach(bastion => {
        elementsByType['azure-vm'].forEach(vm => {
          addConnection(connections, bastion, vm, 'Remote Access');
        });
      });
    }
    
    // Conectar VNets (spokes) a servicios dentro de cada spoke
    if (elementsByType['azure-vnet'] && elementsByType['azure-vm']) {
      elementsByType['azure-vnet'].forEach(vnet => {
        elementsByType['azure-vm'].forEach(vm => {
          addConnection(connections, vnet, vm, 'Network');
        });
      });
    }
  }
  
  // Si hay múltiples VMs y una base de datos, conectar todas las VMs a la DB
  if (elementsByType['azure-vm'] && elementsByType['azure-vm'].length > 1 && 
      elementsByType['azure-sql'] && elementsByType['azure-sql'].length > 0) {
    console.log('🔗 Conectando múltiples VMs a base de datos');
    elementsByType['azure-vm'].forEach(vm => {
      elementsByType['azure-sql'].forEach(db => {
        addConnection(connections, vm, db, 'Database Connection');
      });
    });
  }
  
  // Si hay múltiples VMs y storage, conectar todas las VMs al storage
  if (elementsByType['azure-vm'] && elementsByType['azure-vm'].length > 1 && 
      elementsByType['azure-storage'] && elementsByType['azure-storage'].length > 0) {
    console.log('🔗 Conectando múltiples VMs a storage');
    elementsByType['azure-vm'].forEach(vm => {
      elementsByType['azure-storage'].forEach(storage => {
        addConnection(connections, vm, storage, 'Storage Access');
      });
    });
  }
  
  // Si hay load balancer y múltiples VMs, conectar load balancer a todas las VMs
  if (elementsByType['azure-load-balancer'] && elementsByType['azure-vm'] && 
      elementsByType['azure-vm'].length > 1) {
    console.log('🔗 Conectando load balancer a múltiples VMs');
    elementsByType['azure-load-balancer'].forEach(lb => {
      elementsByType['azure-vm'].forEach(vm => {
        addConnection(connections, lb, vm, 'Load Distribution');
      });
    });
  }
  
  // Si hay VNet y VMs, conectar todas las VMs a la VNet
  if (elementsByType['azure-vnet'] && elementsByType['azure-vm']) {
    console.log('🔗 Conectando VMs a Virtual Network');
    elementsByType['azure-vm'].forEach(vm => {
      elementsByType['azure-vnet'].forEach(vnet => {
        addConnection(connections, vm, vnet, 'Network Connection');
      });
    });
  }
  
  // Si hay Service Bus y VMs, conectar Service Bus a todas las VMs
  if (elementsByType['azure-service-bus'] && elementsByType['azure-vm']) {
    console.log('🔗 Conectando Service Bus a VMs');
    elementsByType['azure-service-bus'].forEach(sb => {
      elementsByType['azure-vm'].forEach(vm => {
        addConnection(connections, sb, vm, 'Message Queue');
      });
    });
  }
  
  // Si hay Redis Cache y VMs, conectar Redis a todas las VMs
  if (elementsByType['azure-redis'] && elementsByType['azure-vm']) {
    console.log('🔗 Conectando Redis Cache a VMs');
    elementsByType['azure-redis'].forEach(redis => {
      elementsByType['azure-vm'].forEach(vm => {
        addConnection(connections, vm, redis, 'Cache Access');
      });
    });
  }
}

function createFallbackConnections(elements, connections) {
  console.log('🔗 Creando conexiones de fallback');
  
  // Conectar elementos en secuencia lógica
  for (let i = 0; i < elements.length - 1; i++) {
    const source = elements[i];
    const target = elements[i + 1];
    
    addConnection(connections, source, target, 'Connection');
  }
}

function getConnectionLabel(sourceType, targetType) {
  const labels = {
    'azure-app-service-azure-sql': 'Database Connection',
    'azure-app-service-azure-storage': 'File Storage',
    'azure-app-service-azure-redis': 'Cache',
    'azure-load-balancer-azure-app-service': 'Traffic',
    'azure-vm-azure-vnet': 'Network',
    'azure-service-bus-azure-app-service': 'Messages'
  };
  
  const key = `${sourceType}-${targetType}`;
  return labels[key] || 'Connection';
}

// Función para obtener información de servicios de Azure
function getServiceInfo(serviceType) {
  const serviceInfoMap = {
    'azure-vm': {
      name: 'Virtual Machine',
      description: 'Máquina virtual escalable',
      color: '#0078d4'
    },
    'azure-sql': {
      name: 'SQL Database',
      description: 'Base de datos relacional',
      color: '#0078d4'
    },
    'azure-storage': {
      name: 'Storage Account',
      description: 'Cuenta de almacenamiento',
      color: '#0078d4'
    },
    'azure-app-service': {
      name: 'App Service',
      description: 'Servicio de aplicaciones web',
      color: '#0078d4'
    },
    'azure-load-balancer': {
      name: 'Load Balancer',
      description: 'Distribución de tráfico',
      color: '#0078d4'
    },
    'azure-vnet': {
      name: 'Virtual Network',
      description: 'Red virtual privada',
      color: '#0078d4'
    },
    'azure-firewall': {
      name: 'Azure Firewall',
      description: 'Firewall de red',
      color: '#0078d4'
    },
    'azure-bastion': {
      name: 'Azure Bastion',
      description: 'Acceso seguro a VMs',
      color: '#0078d4'
    },
    'azure-subscriptions': {
      name: 'Subscription',
      description: 'Suscripción de Azure',
      color: '#0078d4'
    },
    'azure-redis': {
      name: 'Redis Cache',
      description: 'Cache en memoria',
      color: '#0078d4'
    },
    'azure-cosmos': {
      name: 'Cosmos DB',
      description: 'Base de datos NoSQL',
      color: '#0078d4'
    },
    'azure-functions': {
      name: 'Azure Functions',
      description: 'Computación sin servidor',
      color: '#0078d4'
    },
    'azure-service-bus': {
      name: 'Service Bus',
      description: 'Mensajería en la nube',
      color: '#0078d4'
    }
  };

  return serviceInfoMap[serviceType] || {
    name: 'Azure Service',
    description: 'Servicio de Azure',
    color: '#0078d4'
  };
}

app.listen(port, () => {
  console.log(`Backend running at http://localhost:${port}`);
});