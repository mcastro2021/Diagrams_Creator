// server.js
const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());
app.use(express.static('.'));

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
  
  // Patrones de reconocimiento para servicios de Azure
  const servicePatterns = {
    'azure-vm': [
      'virtual machine', 'vm', 'máquina virtual', 'servidor', 'compute',
      'instancia', 'host', 'node', 'worker'
    ],
    'azure-app-service': [
      'app service', 'web app', 'aplicación web', 'api', 'rest api',
      'web application', 'backend', 'frontend', 'servicio web'
    ],
    'azure-sql': [
      'sql database', 'sql db', 'base de datos sql', 'database', 'db',
      'sql server', 'relational database', 'tabla', 'tablas'
    ],
    'azure-storage': [
      'storage account', 'storage', 'blob storage', 'file storage',
      'almacenamiento', 'archivos', 'blob', 'container'
    ],
    'azure-vnet': [
      'virtual network', 'vnet', 'red virtual', 'network', 'subnet',
      'vpc', 'networking', 'conexión de red'
    ],
    'azure-load-balancer': [
      'load balancer', 'balanceador', 'load balancer', 'distribución de carga',
      'traffic manager', 'application gateway'
    ],
    'azure-redis': [
      'redis cache', 'cache', 'redis', 'memoria caché', 'caching',
      'session store', 'distributed cache'
    ],
    'azure-service-bus': [
      'service bus', 'message queue', 'cola de mensajes', 'messaging',
      'event hub', 'event grid', 'pub/sub'
    ],
    'azure-functions': [
      'azure functions', 'function app', 'serverless', 'lambda',
      'función', 'microservicio', 'event-driven'
    ],
    'azure-cosmos': [
      'cosmos db', 'cosmos database', 'nosql', 'document database',
      'base de datos no relacional', 'mongodb'
    ],
    'azure-key-vault': [
      'key vault', 'secrets', 'certificates', 'keys', 'contraseñas',
      'credenciales', 'authentication', 'authorization'
    ],
    'azure-monitor': [
      'application insights', 'monitor', 'logging', 'métricas',
      'alertas', 'dashboard', 'telemetría'
    ]
  };
  
  // Detectar servicios mencionados
  const detectedServices = new Set();
  
  Object.entries(servicePatterns).forEach(([serviceType, patterns]) => {
    patterns.forEach(pattern => {
      if (text.includes(pattern)) {
        detectedServices.add(serviceType);
      }
    });
  });
  
  // Si no se detectan servicios específicos, usar servicios básicos
  if (detectedServices.size === 0) {
    detectedServices.add('azure-app-service');
    detectedServices.add('azure-sql');
    detectedServices.add('azure-storage');
  }
  
  // Crear elementos con posicionamiento inteligente
  const serviceArray = Array.from(detectedServices);
  const gridCols = Math.ceil(Math.sqrt(serviceArray.length));
  const elementWidth = 150;
  const elementHeight = 80;
  const spacing = 200;
  
  serviceArray.forEach((serviceType, index) => {
    const row = Math.floor(index / gridCols);
    const col = index % gridCols;
    
    const x = 100 + col * spacing;
    const y = 100 + row * spacing;
    
    const serviceInfo = getServiceInfo(serviceType);
    
    elements.push({
      id: `${serviceType}-${index + 1}`,
      type: serviceType,
      text: serviceInfo.name,
      description: serviceInfo.description,
      x: x,
      y: y,
      width: elementWidth,
      height: elementHeight,
      color: serviceInfo.color
    });
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
  // Patrones de conexión comunes
  const connectionPatterns = [
    // App Service típicamente se conecta a bases de datos
    { from: 'azure-app-service', to: ['azure-sql', 'azure-cosmos', 'azure-redis'] },
    // App Service también se conecta a storage
    { from: 'azure-app-service', to: ['azure-storage'] },
    // VMs se conectan a través de VNet
    { from: 'azure-vm', to: ['azure-vnet'] },
    // Load balancer distribuye tráfico a App Services o VMs
    { from: 'azure-load-balancer', to: ['azure-app-service', 'azure-vm'] },
    // Service Bus conecta microservicios
    { from: 'azure-service-bus', to: ['azure-app-service', 'azure-functions'] },
    // Functions pueden conectarse a storage y databases
    { from: 'azure-functions', to: ['azure-storage', 'azure-sql', 'azure-cosmos'] }
  ];
  
  connectionPatterns.forEach(pattern => {
    const sourceElements = elements.filter(e => e.type === pattern.from);
    const targetTypes = pattern.to;
    
    sourceElements.forEach(source => {
      targetTypes.forEach(targetType => {
        const targetElements = elements.filter(e => e.type === targetType);
        
        // Conectar con el primer elemento de cada tipo
        if (targetElements.length > 0) {
          const target = targetElements[0];
          
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
              label: getConnectionLabel(source.type, target.type)
            });
          }
        }
      });
    });
  });
  
  // Si no hay conexiones, crear una conexión básica entre los primeros elementos
  if (connections.length === 0 && elements.length > 1) {
    connections.push({
      id: 'conn-1',
      source: elements[0].id,
      target: elements[1].id,
      type: 'standard',
      label: 'Connection'
    });
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