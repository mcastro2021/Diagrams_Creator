# 🚀 Diagrams Creator - Generador de Diagramas con IA

Una aplicación web avanzada que utiliza inteligencia artificial para generar diagramas de arquitectura de sistemas a partir de descripciones en texto natural o documentos.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple.svg)

## ✨ Características Principales

- 🤖 **Generación automática con IA**: Utiliza GPT para analizar descripciones y crear diagramas
- 🎨 **Librería extensa de iconos**: Soporte para AWS, Azure, GCP, Kubernetes, y más
- 📄 **Múltiples formatos de entrada**: Texto, PDF, DOCX, MD, JSON
- 🎯 **Detección automática de arquitecturas**: Identifica patrones y tecnologías
- 💾 **Exportación múltiple**: XML (Draw.io), SVG, PNG, PDF
- 🎨 **Estilos personalizables**: Moderno, minimalista, colorido
- 📱 **Interfaz responsive**: Funciona en desktop y móvil
- 🔗 **Integración con Draw.io**: Edición avanzada de diagramas

## 🏗️ Arquitecturas Soportadas

- **☁️ Cloud Providers**: AWS, Microsoft Azure, Google Cloud Platform
- **🐳 Containerización**: Kubernetes, Docker
- **🌐 Redes**: Switches, Routers, Firewalls, Load Balancers
- **🔒 Seguridad**: Fortinet, F5, componentes de seguridad
- **💾 Almacenamiento**: Commvault, soluciones de backup
- **🔧 Genérico**: Microservicios, APIs, bases de datos

## 📦 Instalación y Configuración

### Prerrequisitos

- Python 3.8 o superior
- Cuenta de OpenAI con API Key
- Git

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd Diagrams_Creator
```

### 2. Crear ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
copy env_example.txt .env

# Editar .env con tus configuraciones
# IMPORTANTE: Configurar OPENAI_API_KEY
```

### 5. Ejecutar la aplicación

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 🎯 Uso de la Aplicación

### Generación desde Texto

1. **Describe tu arquitectura**: Escribe una descripción detallada en el área de texto
2. **Selecciona el tipo**: Elige el tipo de diagrama (AWS, Azure, etc.) o usa detección automática
3. **Elige el estilo**: Moderno, minimalista o colorido
4. **Generar**: Haz clic en "Generar Diagrama"

**Ejemplo de descripción:**
```
Tengo una aplicación web con:
- Frontend en React desplegado en S3
- API REST en Node.js en EC2
- Base de datos PostgreSQL en RDS
- Cache Redis en ElastiCache
- Load Balancer ALB
- CloudFront para CDN
- Autenticación con Cognito
```

### Generación desde Documento

1. **Subir archivo**: Selecciona un documento (PDF, DOCX, etc.)
2. **Configurar opciones**: Tipo de diagrama y estilo
3. **Procesar**: La IA extraerá el texto y generará el diagrama

### Trabajar con Iconos

- **Explorar librerías**: Navega por las librerías de iconos en el panel lateral
- **Buscar iconos**: Usa la funcionalidad de búsqueda
- **Seleccionar**: Haz clic en los iconos para seleccionarlos

### Exportar Diagramas

- **Draw.io XML**: Para edición completa
- **SVG**: Gráficos vectoriales
- **PNG**: Imágenes raster
- **PDF**: Documentos imprimibles

## 🛠️ Estructura del Proyecto

```
Diagrams_Creator/
├── app.py                 # Aplicación principal Flask
├── config.py             # Configuración
├── ai_processor.py       # Procesamiento con IA
├── diagram_generator.py  # Generación de diagramas
├── libs_handler.py       # Manejo de librerías de iconos
├── requirements.txt      # Dependencias Python
├── env_example.txt       # Ejemplo de variables de entorno
├── templates/
│   └── index.html        # Interfaz web principal
├── static/
│   ├── css/
│   │   └── style.css     # Estilos personalizados
│   └── js/
│       └── app.js        # JavaScript de la aplicación
├── Libs/                 # Librerías de iconos
│   ├── arista/          # Iconos de Arista
│   ├── f5/              # Iconos de F5
│   ├── fortinet/        # Iconos de Fortinet
│   └── ...              # Otras librerías
└── outputs/             # Diagramas generados
```

## 🔧 API Endpoints

### Principales

- `GET /` - Interfaz web principal
- `POST /api/generate-diagram` - Generar diagrama desde texto
- `POST /api/upload-document` - Procesar documento
- `GET /api/libraries` - Obtener librerías disponibles
- `GET /api/icons/<library>` - Obtener iconos de librería
- `GET /api/diagram/<id>` - Descargar diagrama
- `GET /api/export-diagram/<id>/<format>` - Exportar diagrama

### Utilitarios

- `GET /api/health` - Estado de la aplicación

## 🎨 Personalización

### Estilos de Diagrama

Puedes personalizar los estilos editando `diagram_generator.py`:

```python
'modern': {
    'component': {
        'fillColor': '#E1F5FE',
        'strokeColor': '#0277BD',
        'strokeWidth': 2,
        'rounded': 1,
        'shadow': 1
    }
}
```

### Agregar Nuevas Librerías

1. Coloca los iconos en `Libs/nueva_libreria/`
2. La aplicación detectará automáticamente:
   - Archivos SVG
   - Archivos PNG
   - Archivos XML con definiciones

## 🤖 Configuración de IA

### Modelos Soportados

- `gpt-3.5-turbo` (recomendado)
- `gpt-4` (mayor precisión, más costoso)

### Parámetros Ajustables

```python
AI_TEMPERATURE=0.7    # Creatividad (0.0-1.0)
MAX_TOKENS=2000       # Longitud máxima de respuesta
```

## 📝 Ejemplos de Uso

### Arquitectura AWS

```
Descripción: "Aplicación web escalable en AWS con frontend en S3, API en Lambda, base de datos RDS MySQL, y cache ElastiCache Redis"

Resultado: Diagrama con iconos de AWS mostrando S3, Lambda, RDS, ElastiCache y sus conexiones
```

### Arquitectura Kubernetes

```
Descripción: "Cluster Kubernetes con 3 pods de aplicación, servicio LoadBalancer, ConfigMap para configuración, y PersistentVolume para datos"

Resultado: Diagrama K8s con pods, services, configmaps y volúmenes
```

## 🐛 Solución de Problemas

### Error de API Key

```
Error: OpenAI API key not configured
Solución: Configurar OPENAI_API_KEY en el archivo .env
```

### Error de Librerías

```
Error: No libraries found
Solución: Verificar que la carpeta Libs/ contenga las librerías de iconos
```

### Error de Memoria

```
Error: Request too large
Solución: Reducir el tamaño del documento o dividirlo en partes más pequeñas
```

## 🔒 Seguridad

- ✅ Validación de tipos de archivo
- ✅ Límites de tamaño de archivo (16MB)
- ✅ Sanitización de entradas
- ✅ Manejo seguro de archivos temporales
- ⚠️ **Importante**: Mantén tu API Key de OpenAI segura

## 🚀 Despliegue en Producción

### Variables de Entorno de Producción

```bash
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-segura
OPENAI_API_KEY=tu-api-key-de-openai
```

### Usando Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Opcional)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📊 Métricas y Monitoreo

La aplicación incluye:
- Health check endpoint (`/api/health`)
- Logging detallado
- Manejo de errores robusto
- Métricas de uso (componentes, conexiones)

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- **OpenAI** por la API de GPT
- **Draw.io** por la plataforma de diagramas
- **Bootstrap** por el framework CSS
- **Comunidad Open Source** por las librerías de iconos

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

**¡Feliz creación de diagramas! 🎨📊**
