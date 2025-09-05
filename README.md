# Azure Diagram Generator

Una aplicación web que permite generar diagramas de arquitectura de Azure automáticamente a partir de descripciones en lenguaje natural.

## 🚀 Características

- **Generación Automática**: Crea diagramas de Azure desde descripciones en lenguaje natural
- **Reconocimiento Inteligente**: Detecta servicios de Azure en español e inglés
- **Posicionamiento Inteligente**: Organiza automáticamente los elementos del diagrama
- **Conexiones Automáticas**: Establece conexiones lógicas entre servicios
- **Interfaz Interactiva**: Elementos arrastrables y editables
- **Exportación**: Guarda y exporta diagramas en formato JSON
- **Ejemplos Predefinidos**: Plantillas de arquitecturas comunes

## 🛠️ Tecnologías

- **Backend**: Node.js + Express
- **Frontend**: HTML5 + CSS3 + JavaScript Vanilla
- **Dependencias**: Express, CORS

## 📦 Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone <repository-url>
   cd Diagrams_Creator
   ```

2. **Instalar dependencias**:
   ```bash
   npm install
   ```

3. **Ejecutar la aplicación**:
   ```bash
   npm start
   ```

4. **Abrir en el navegador**:
   ```
   http://localhost:3001
   ```

## 🎯 Uso

### Generar un Diagrama

1. Escribe una descripción de tu arquitectura Azure en el campo de texto
2. Haz clic en "Generar Diagrama" o presiona `Ctrl + Enter`
3. El diagrama se generará automáticamente con elementos y conexiones

### Ejemplos de Descripciones

```
Una aplicación web con App Service, SQL Database y Storage Account
```

```
Arquitectura de microservicios con API Gateway, Service Bus y Application Insights
```

```
Dos máquinas virtuales conectadas a una base de datos a través de una red virtual
```

### Funcionalidades Interactivas

- **Arrastrar Elementos**: Haz clic y arrastra los elementos del diagrama
- **Exportar**: Guarda el diagrama como archivo JSON
- **Limpiar**: Borra el diagrama actual
- **Guardar**: Almacena el diagrama en el navegador

## 🏗️ Servicios Azure Soportados

La aplicación reconoce automáticamente los siguientes servicios:

| Servicio | Patrones de Reconocimiento |
|----------|---------------------------|
| **Virtual Machine** | "virtual machine", "vm", "máquina virtual", "servidor" |
| **App Service** | "app service", "web app", "aplicación web", "api" |
| **SQL Database** | "sql database", "base de datos sql", "database" |
| **Storage Account** | "storage account", "storage", "blob storage" |
| **Virtual Network** | "virtual network", "vnet", "red virtual" |
| **Load Balancer** | "load balancer", "balanceador", "traffic manager" |
| **Redis Cache** | "redis cache", "cache", "memoria caché" |
| **Service Bus** | "service bus", "message queue", "cola de mensajes" |
| **Azure Functions** | "azure functions", "serverless", "función" |
| **Cosmos DB** | "cosmos db", "nosql", "document database" |
| **Key Vault** | "key vault", "secrets", "certificates" |
| **Application Insights** | "application insights", "monitor", "telemetría" |

## 🔧 API Endpoints

### POST `/generate-diagram`
Genera un diagrama a partir de una descripción.

**Request:**
```json
{
  "description": "Una aplicación web con base de datos"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "elements": [...],
    "connections": [...],
    "metadata": {
      "totalElements": 3,
      "totalConnections": 2,
      "detectedServices": ["azure-app-service", "azure-sql"]
    }
  }
}
```

### GET `/examples`
Obtiene ejemplos predefinidos de arquitecturas.

**Response:**
```json
{
  "success": true,
  "examples": [
    {
      "id": "web-app-basic",
      "name": "Aplicación Web Básica",
      "description": "Una aplicación web con App Service, SQL Database y Storage Account",
      "architecture": "App Service conectado a SQL Database y Storage Account"
    }
  ]
}
```

## 🧪 Pruebas

Ejecuta las pruebas automatizadas:

```bash
node test_app.js
```

Las pruebas verifican:
- ✅ Respuesta del servidor
- ✅ Endpoint de ejemplos
- ✅ Generación de diagramas básicos
- ✅ Generación con servicios específicos
- ✅ Validación de entrada
- ✅ Soporte para español

## 📁 Estructura del Proyecto

```
Diagrams_Creator/
├── server.js          # Servidor Express
├── index.html         # Interfaz web
├── package.json       # Configuración del proyecto
├── test_app.js        # Pruebas automatizadas
└── README.md          # Documentación
```

## 🎨 Personalización

### Agregar Nuevos Servicios

Para agregar un nuevo servicio Azure, modifica el objeto `servicePatterns` en `server.js`:

```javascript
'azure-new-service': [
  'nuevo servicio', 'new service', 'patrón de reconocimiento'
]
```

### Modificar Estilos

Los estilos CSS están definidos en `index.html`. Puedes personalizar:
- Colores de la interfaz
- Estilos de los elementos Azure
- Animaciones y transiciones

## 🚀 Despliegue

### Heroku

1. Crea un archivo `Procfile`:
   ```
   web: node server.js
   ```

2. Configura las variables de entorno:
   ```bash
   heroku config:set NODE_ENV=production
   ```

3. Despliega:
   ```bash
   git push heroku main
   ```

### Docker

1. Crea un `Dockerfile`:
   ```dockerfile
   FROM node:16-alpine
   WORKDIR /app
   COPY package*.json ./
   RUN npm install
   COPY . .
   EXPOSE 3001
   CMD ["node", "server.js"]
   ```

2. Construye y ejecuta:
   ```bash
   docker build -t azure-diagram-generator .
   docker run -p 3001:3001 azure-diagram-generator
   ```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia ISC. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación
2. Ejecuta las pruebas para verificar el funcionamiento
3. Abre un issue en GitHub
4. Contacta al equipo de desarrollo

## 🔮 Roadmap

- [ ] Integración con iconos reales de Azure
- [ ] Exportación a formatos adicionales (PNG, SVG, PDF)
- [ ] Colaboración en tiempo real
- [ ] Integración con Azure Resource Manager
- [ ] Plantillas de arquitecturas más avanzadas
- [ ] Validación de arquitecturas
- [ ] Estimación de costos

---

**¡Disfruta creando diagramas de Azure! 🎉**
