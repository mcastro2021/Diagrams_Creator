# 🚀 Guía de Despliegue en Render

Esta guía te ayudará a desplegar la aplicación Azure Diagram Generator en Render paso a paso.

## 📋 Prerrequisitos

1. **Cuenta en Render**: [Regístrate aquí](https://render.com)
2. **Repositorio en GitHub**: Tu código debe estar en GitHub
3. **API Key de Groq**: [Obtén tu API key aquí](https://console.groq.com)

## 🔧 Paso 1: Preparar el Repositorio

Asegúrate de que tu repositorio tenga los siguientes archivos:

```
Diagrams_Creator/
├── server.js
├── package.json
├── index.html
├── render.yaml
├── Dockerfile
├── database/schema.sql
├── config/database.js
└── README.md
```

## 🏗️ Paso 2: Crear Servicios en Render

### 2.1 Crear Web Service

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Haz clic en "New +" → "Web Service"
3. Conecta tu repositorio de GitHub
4. Configura el servicio:

```
Name: azure-diagram-generator
Environment: Node
Region: Oregon (US West)
Branch: main
Root Directory: (dejar vacío)
Build Command: npm install
Start Command: npm start
Plan: Starter (Free)
```

### 2.2 Crear Base de Datos PostgreSQL

1. En el dashboard, haz clic en "New +" → "PostgreSQL"
2. Configura la base de datos:

```
Name: azure-diagrams-db
Database: azure_diagrams
User: azure_diagrams_user
Region: Oregon (US West)
Plan: Starter (Free)
```

### 2.3 Crear Redis (Opcional)

1. Haz clic en "New +" → "Redis"
2. Configura Redis:

```
Name: azure-diagrams-redis
Region: Oregon (US West)
Plan: Starter (Free)
```

## ⚙️ Paso 3: Configurar Variables de Entorno

En tu Web Service, ve a "Environment" y agrega:

### Variables Requeridas
```
NODE_ENV=production
GROQ_API_KEY=tu_groq_api_key_aqui
JWT_SECRET=un_jwt_secret_muy_seguro_y_largo
```

### Variables de Base de Datos
```
DATABASE_URL=postgresql://usuario:password@host:puerto/database
```
*Esta variable se genera automáticamente cuando conectas la base de datos*

### Variables de Redis (si usas Redis)
```
REDIS_URL=redis://usuario:password@host:puerto
```
*Esta variable se genera automáticamente cuando conectas Redis*

### Variables Opcionales
```
CORS_ORIGIN=https://tu-app.onrender.com
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

## 🗄️ Paso 4: Configurar Base de Datos

1. **Conectar la base de datos al Web Service**:
   - En tu Web Service, ve a "Environment"
   - Haz clic en "Link Database"
   - Selecciona tu base de datos PostgreSQL

2. **Ejecutar el schema**:
   - Ve a tu base de datos PostgreSQL
   - Haz clic en "Connect"
   - Usa el "External Connection" string
   - Ejecuta el contenido de `database/schema.sql`

## 🚀 Paso 5: Desplegar

1. **Hacer commit y push** de todos los cambios:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Render detectará automáticamente** los cambios y comenzará el despliegue

3. **Monitorear el despliegue** en el dashboard de Render

## ✅ Paso 6: Verificar el Despliegue

1. **Health Check**: Visita `https://tu-app.onrender.com/api/health`
2. **Ejemplos**: Visita `https://tu-app.onrender.com/api/examples`
3. **Aplicación**: Visita `https://tu-app.onrender.com`

## 🔧 Configuración Avanzada

### Custom Domain (Opcional)

1. En tu Web Service, ve a "Settings"
2. Haz clic en "Custom Domains"
3. Agrega tu dominio personalizado
4. Configura los DNS records según las instrucciones

### Auto-Deploy

El auto-deploy está habilitado por defecto. Cada push a la rama `main` desplegará automáticamente.

### Environment Variables Sensibles

Para variables sensibles como API keys:
1. Ve a "Environment" en tu Web Service
2. Haz clic en "Add Environment Variable"
3. Marca como "Secret" para variables sensibles

## 🐛 Troubleshooting

### Error: "Cannot connect to database"
- Verifica que `DATABASE_URL` esté configurada
- Asegúrate de que la base de datos esté "linked" al Web Service

### Error: "GROQ_API_KEY not found"
- Verifica que hayas agregado tu API key de Groq
- Asegúrate de que no tenga espacios extra

### Error: "Build failed"
- Verifica que `package.json` tenga el script `start`
- Revisa los logs de build en Render

### Error: "Application crashed"
- Revisa los logs de la aplicación
- Verifica que todas las variables de entorno estén configuradas

## 📊 Monitoreo

### Logs
- Ve a tu Web Service → "Logs" para ver logs en tiempo real
- Los logs se mantienen por 7 días en el plan gratuito

### Métricas
- Ve a "Metrics" para ver CPU, memoria y requests
- Útil para monitorear el rendimiento

## 💰 Costos

### Plan Gratuito (Starter)
- **Web Service**: 750 horas/mes gratis
- **PostgreSQL**: 1GB storage, 1 conexión
- **Redis**: 25MB storage
- **Sleep**: Los servicios se "duermen" después de 15 minutos de inactividad

### Planes Pagos
- **Starter**: $7/mes por servicio
- **Standard**: $25/mes por servicio
- **Pro**: $85/mes por servicio

## 🔄 Actualizaciones

Para actualizar la aplicación:
1. Haz cambios en tu código local
2. Commit y push a GitHub
3. Render detectará los cambios y desplegará automáticamente

## 📞 Soporte

- **Render Docs**: [docs.render.com](https://docs.render.com)
- **Render Support**: [community.render.com](https://community.render.com)
- **GitHub Issues**: Para problemas específicos de la aplicación

---

¡Tu aplicación Azure Diagram Generator debería estar funcionando en Render! 🎉
