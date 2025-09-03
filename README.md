# Diagramas Creator - Editor de Diagramas con IA

Una aplicación web moderna para crear diagramas interactivos usando inteligencia artificial, con soporte para iconos de AWS y Azure, similar a draw.io pero con capacidades de generación automática.

## ✨ Características Principales

### 🤖 Generación con IA
- **Generación automática de diagramas** usando OpenAI GPT-4
- **Detección inteligente de tipos** de diagrama basada en descripción
- **Soporte especializado para Azure** con topologías Hub and Spoke
- **Diagramas de arquitectura complejos** con múltiples suscripciones

### 🎯 Tipos de Diagramas Soportados
- **Diagramas de Flujo** - Procesos y workflows
- **Diagramas de Secuencia** - Interacciones UML
- **Diagramas de Clases** - Estructuras orientadas a objetos
- **Diagramas ER** - Bases de datos y relaciones
- **Diagramas de Red** - Arquitecturas de red
- **Mapas Mentales** - Organización de ideas
- **Diagramas de Arquitectura** - Sistemas y componentes

### 📦 Sistema de Iconos Avanzado
- **Biblioteca completa de iconos AWS** organizados por categorías
- **Iconos de Azure** para arquitecturas cloud
- **Panel flotante interactivo** con búsqueda y filtros
- **Drag & drop** de iconos al canvas
- **Búsqueda inteligente** por nombre, categoría o proveedor

### 🎨 Editor Interactivo
- **Canvas estilo draw.io** con funcionalidad completa
- **Arrastrar y soltar** nodos y elementos
- **Edición de texto** con doble clic
- **Conexiones automáticas** entre elementos
- **Selección y eliminación** de elementos
- **Guardado automático** de cambios

### 📁 Procesamiento de Archivos
- **Subida de documentos** (PDF, Word, Excel, CSV, JSON)
- **Extracción de contenido** automática
- **Generación de diagramas** basada en contenido
- **Procesamiento de texto libre** para crear diagramas

### 💾 Gestión de Proyectos
- **Guardado automático** en memoria
- **Lista de diagramas** con metadatos
- **Historial de versiones** básico
- **Exportación múltiple** (SVG, PNG, JSON, Mermaid)

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8+
- pip (gestor de paquetes de Python)
- Clave API de OpenAI (opcional, para funcionalidad IA)

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/mcastro2021/Diagrams_Creator.git
cd Diagrams_Creator
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno** (opcional)
```bash
# Crear archivo .env
echo "OPENAI_API_KEY=tu-clave-openai-aqui" > .env
```

4. **Ejecutar la aplicación**
```bash
python app.py
```

5. **Abrir en navegador**
```
http://localhost:5000
```

## 📖 Guía de Uso

### 🎯 Crear Diagrama con IA

1. **Hacer clic en "Generar Diagrama IA"**
2. **Escribir descripción detallada**:
   ```
   Crear una arquitectura Azure hub and spoke con 4 suscripciones, 
   firewall centralizado, VPN gateway y conectividad entre spokes
   ```
3. **Seleccionar tipo** (o dejar en "Detectar Automáticamente")
4. **Hacer clic en "Generar con IA"**

### 📋 Usar Plantillas

1. **Seleccionar plantilla** del panel izquierdo
2. **El diagrama base se carga** automáticamente
3. **Personalizar** añadiendo/editando elementos

### 🎨 Editar Diagramas

- **Arrastrar nodos** para reposicionar
- **Doble clic** en nodo para editar texto
- **Tecla Delete** para eliminar nodo seleccionado
- **Tecla Escape** para deseleccionar

### 📦 Usar Iconos

1. **Hacer clic en botón de iconos** (lado derecho)
2. **Filtrar por proveedor** (AWS/Azure) y categoría
3. **Buscar iconos** por nombre
4. **Hacer clic en icono** para añadir al diagrama

### 📁 Procesar Archivos

1. **Seleccionar archivo** (PDF, Word, etc.)
2. **Hacer clic en "Procesar"**
3. **El diagrama se genera** automáticamente

## 🏗️ Arquitectura del Proyecto

```
Diagrams_Creator/
├── app.py                 # Servidor Flask principal
├── requirements.txt       # Dependencias Python
├── README.md             # Documentación
├── templates/
│   └── index.html        # Interfaz principal
├── static/
│   ├── css/
│   │   └── style.css     # Estilos personalizados
│   └── js/
│       ├── app.js        # Lógica principal
│       └── icons-panel.js # Panel de iconos
├── icons/
│   ├── AWS/              # Iconos AWS por categorías
│   └── Azure/            # Iconos Azure por categorías
├── uploads/              # Archivos subidos
└── outputs/              # Archivos exportados
```

## 🔧 API Endpoints

### Diagramas
- `GET /` - Interfaz principal
- `POST /create_diagram` - Crear nuevo diagrama
- `GET /diagram/<id>` - Obtener diagrama
- `PUT /diagram/<id>` - Actualizar diagrama
- `GET /diagrams` - Listar todos los diagramas
- `POST /export/<id>` - Exportar diagrama

### IA y Procesamiento
- `POST /generate_ai_diagram` - Generar con IA
- `POST /upload` - Subir archivo
- `POST /process_text` - Procesar texto libre

### Iconos
- `GET /api/icons` - Obtener todos los iconos
- `GET /api/search_icons` - Buscar iconos
- `GET /icons/<path>` - Servir archivo de icono

### Utilidades
- `GET /templates` - Obtener plantillas
- `GET /health` - Estado de la aplicación

## 🎨 Personalización

### Añadir Nuevos Iconos

1. **Crear carpeta** en `icons/PROVEEDOR/CATEGORIA/`
2. **Añadir archivos SVG** con nombres descriptivos
3. **Reiniciar aplicación** para cargar nuevos iconos

### Modificar Estilos

- **Editar** `static/css/style.css`
- **Variables CSS** disponibles en `:root`
- **Clases específicas** para cada tipo de elemento

### Extender Funcionalidad

- **Nuevos tipos de diagrama** en `get_base_diagram()`
- **Prompts de IA personalizados** en `get_system_prompt_for_type()`
- **Procesadores de archivos** adicionales

## 🔮 Ejemplos de Uso

### Arquitectura Azure Hub and Spoke
```
Descripción: "Crear una topología hub and spoke con 4 suscripciones, 
hub central con firewall y VPN gateway, spokes de producción y 
no-producción con VMs y conectividad entre ellos"
```

### Diagrama de Flujo de Proceso
```
Descripción: "Proceso de aprobación de solicitudes con validación 
inicial, revisión por supervisor, aprobación final y notificación"
```

### Arquitectura de Microservicios
```
Descripción: "Sistema de microservicios con API Gateway, 
servicios de usuario, pedidos y pagos, base de datos por servicio 
y message broker"
```

## 🤝 Contribuir

1. **Fork** el repositorio
2. **Crear rama** para nueva funcionalidad
3. **Hacer commits** con mensajes descriptivos
4. **Crear Pull Request** con descripción detallada

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 🆘 Soporte

- **Issues**: [GitHub Issues](https://github.com/mcastro2021/Diagrams_Creator/issues)
- **Documentación**: Este README.md
- **Ejemplos**: Carpeta `examples/` (próximamente)

## 🔄 Roadmap

### Próximas Funcionalidades
- [ ] **Colaboración en tiempo real** con WebSockets
- [ ] **Más proveedores de iconos** (GCP, Kubernetes, etc.)
- [ ] **Exportación a draw.io** nativa
- [ ] **Plantillas personalizadas** por usuario
- [ ] **Integración con GitHub** para diagramas como código
- [ ] **API REST completa** para integraciones
- [ ] **Modo oscuro** y temas personalizables
- [ ] **Historial de versiones** completo
- [ ] **Comentarios y anotaciones** en diagramas
- [ ] **Generación de código** desde diagramas

---

**Desarrollado con ❤️ por el equipo de Diagramas Creator**

*¿Te gusta el proyecto? ¡Dale una ⭐ en GitHub!*
