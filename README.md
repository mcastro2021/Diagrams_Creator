# Azure Diagram Generator

Una aplicación web avanzada que permite generar diagramas de arquitectura de Azure automáticamente a partir de descripciones en lenguaje natural, similar a Eraser.io pero especializada en Azure.

## 🚀 Características

- **🤖 IA Avanzada**: Procesamiento de lenguaje natural con Groq API
- **🎨 Generación Automática**: Crea diagramas de Azure desde descripciones en lenguaje natural
- **🔍 Reconocimiento Inteligente**: Detecta servicios de Azure en español e inglés
- **📐 Posicionamiento Inteligente**: Organiza automáticamente los elementos del diagrama
- **🔗 Conexiones Automáticas**: Establece conexiones lógicas entre servicios
- **🖱️ Interfaz Interactiva**: Elementos arrastrables y editables
- **💾 Persistencia**: Base de datos PostgreSQL para guardar diagramas
- **👥 Colaboración**: Sistema de usuarios y colaboración en tiempo real
- **📤 Exportación**: Guarda y exporta diagramas en múltiples formatos
- **📋 Ejemplos Predefinidos**: Plantillas de arquitecturas comunes
- **🔒 Seguridad**: Autenticación JWT y rate limiting
- **☁️ Despliegue**: Optimizado para Render, Heroku y Docker

## 🛠️ Tecnologías

### Backend
- **Node.js 18+** + Express.js
- **PostgreSQL** para persistencia de datos
- **Redis** para caché y sesiones
- **Groq API** para procesamiento de IA
- **JWT** para autenticación
- **Socket.io** para colaboración en tiempo real

### Frontend
- **HTML5 + CSS3 + JavaScript Vanilla**
- **React Flow** (próximamente)
- **Responsive Design**
- **PWA Ready**

### DevOps & Deployment
- **Docker** para contenedorización
- **Render** para despliegue en la nube
- **Jest** para testing
- **ESLint** para calidad de código

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

### Render (Recomendado)

1. **Conectar repositorio a Render**:
   - Ve a [Render Dashboard](https://dashboard.render.com)
   - Conecta tu repositorio de GitHub
   - Selecciona "New Web Service"

2. **Configurar el servicio**:
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Environment**: `Node`
   - **Plan**: `Starter` (gratuito)

3. **Variables de entorno**:
   ```
   NODE_ENV=production
   GROQ_API_KEY=tu_groq_api_key
   JWT_SECRET=tu_jwt_secret_seguro
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   REDIS_URL=redis://user:pass@host:port
   CORS_ORIGIN=https://tu-app.onrender.com
   ```

4. **Base de datos PostgreSQL**:
   - Crea una nueva base de datos PostgreSQL en Render
   - Ejecuta el archivo `database/schema.sql` para crear las tablas

5. **Redis (opcional)**:
   - Crea un servicio Redis en Render para caché y sesiones

### Docker

1. **Construir imagen**:
   ```bash
   docker build -t azure-diagram-generator .
   ```

2. **Ejecutar contenedor**:
   ```bash
   docker run -p 3001:3001 \
     -e GROQ_API_KEY=tu_api_key \
     -e DATABASE_URL=tu_database_url \
     azure-diagram-generator
   ```

3. **Docker Compose** (para desarrollo local):
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "3001:3001"
       environment:
         - NODE_ENV=development
         - GROQ_API_KEY=${GROQ_API_KEY}
         - DATABASE_URL=postgresql://postgres:password@db:5432/azure_diagrams
       depends_on:
         - db
         - redis
     
     db:
       image: postgres:15
       environment:
         - POSTGRES_DB=azure_diagrams
         - POSTGRES_USER=postgres
         - POSTGRES_PASSWORD=password
       volumes:
         - postgres_data:/var/lib/postgresql/data
     
     redis:
       image: redis:7-alpine
   
   volumes:
     postgres_data:
   ```

### Heroku

1. **Instalar Heroku CLI** y crear aplicación:
   ```bash
   heroku create tu-app-name
   ```

2. **Configurar variables de entorno**:
   ```bash
   heroku config:set NODE_ENV=production
   heroku config:set GROQ_API_KEY=tu_groq_api_key
   heroku config:set JWT_SECRET=tu_jwt_secret
   ```

3. **Agregar base de datos PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Desplegar**:
   ```bash
   git push heroku main
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
