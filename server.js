// server.js
const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());
app.use(express.static('.'));
app.use('/icons', express.static('icons'));

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
      { regex: /(\d+|\w+)\s+colas?/gi, serviceType: 'service buses' }
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
  
  // Patrones de reconocimiento mejorados y más específicos
  const servicePatterns = {
    'azure-vm': [
      'virtual machine', 'vm', 'máquina virtual', 'servidor', 'compute',
      'instancia', 'host', 'node', 'worker', 'servidor', 'máquina',
      'virtual machines', 'máquinas virtuales', 'servidores', 'instancias',
      'ec2', 'compute instance', 'instancia de computación'
    ],
    'azure-app-service': [
      'app service', 'web app', 'aplicación web', 'api', 'rest api',
      'web application', 'backend', 'frontend', 'servicio web', 'aplicación',
      'app', 'webapp', 'web application', 'aplicaciones web', 'apis',
      'web service', 'servicio web', 'aplicación web', 'sitio web'
    ],
    'azure-sql': [
      'sql database', 'sql db', 'base de datos sql', 'database', 'db',
      'sql server', 'relational database', 'tabla', 'tablas', 'sql',
      'base de datos', 'bases de datos', 'relacional', 'relacionales',
      'mysql', 'postgresql', 'postgres', 'oracle', 'sqlite'
    ],
    'azure-storage': [
      'storage account', 'storage', 'blob storage', 'file storage',
      'almacenamiento', 'archivos', 'blob', 'container', 'file',
      'almacenamiento', 'storage', 'archivos', 'files', 'blobs',
      's3', 'bucket', 'file system', 'sistema de archivos'
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
      'cloudwatch', 'datadog', 'new relic', 'observability'
    ]
  };
  
  // Detectar servicios mencionados con puntuación mejorada
  const detectedServices = new Map();
  
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
  
  // Crear elementos con posicionamiento inteligente y cantidades detectadas
  const serviceArray = Array.from(detectedServices);
  const elementWidth = 150;
  const elementHeight = 80;
  const spacing = 200;
  let elementIndex = 0;
  
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
    
    return null;
  }
  
  // Procesar cantidades detectadas primero
  detectedQuantities.forEach((quantity, serviceText) => {
    const serviceType = mapServiceTextToType(serviceText);
    if (serviceType) {
      console.log(`📊 Generando ${quantity} elementos de tipo ${serviceType} para "${serviceText}"`);
      
      for (let i = 0; i < quantity; i++) {
        const row = Math.floor(elementIndex / 4); // Máximo 4 columnas
        const col = elementIndex % 4;
        
        const x = 100 + col * spacing;
        const y = 100 + row * spacing;
        
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
      
      // Remover el servicio de la lista de servicios detectados para evitar duplicados
      detectedServices.delete(serviceType);
    }
  });
  
  // Procesar servicios restantes (sin cantidad específica)
  const remainingServices = Array.from(detectedServices);
  remainingServices.forEach(([serviceType, score]) => {
    const row = Math.floor(elementIndex / 4);
    const col = elementIndex % 4;
    
    const x = 100 + col * spacing;
    const y = 100 + row * spacing;
    
    const serviceInfo = getServiceInfo(serviceType);
    
    elements.push({
      id: `${serviceType}-${elementIndex + 1}`,
      type: serviceType,
      text: serviceInfo.name,
      description: serviceInfo.description,
      x: x,
      y: y,
      width: elementWidth,
      height: elementHeight,
      color: serviceInfo.color
    });
    
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

app.listen(port, () => {
  console.log(`Backend running at http://localhost:${port}`);
});