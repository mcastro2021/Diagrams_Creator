# Eraser.io Clone - Editor de Diagramas con IA 🤖

Una aplicación web completa que replica la funcionalidad de [Eraser.io](https://app.eraser.io/), incluyendo la generación automática de diagramas usando Inteligencia Artificial.

## ✨ Características Principales

### 🎨 Editor de Diagramas Completo
- **Herramientas de dibujo**: Seleccionar, mover, conectar, texto, formas
- **Múltiples tipos de diagramas**: Flujo, secuencia, clases UML, ER, redes, mapas mentales, arquitectura
- **Canvas interactivo**: Arrastrar y soltar elementos, conexiones automáticas
- **Menú contextual**: Editar, duplicar, eliminar elementos

### 🤖 Generación de Diagramas con IA
- **Descripción en lenguaje natural**: Describe el diagrama que quieres crear
- **Detección automática de tipo**: La IA detecta el tipo de diagrama más apropiado
- **Generación inteligente**: Crea diagramas lógicos y bien estructurados
- **Fallback automático**: Si la IA falla, genera un diagrama básico

### 📁 Gestión de Proyectos
- **Crear diagramas**: Desde plantillas o desde cero
- **Guardar y abrir**: Sistema de archivos integrado
- **Exportar**: Múltiples formatos de salida
- **Historial**: Lista de diagramas creados

## 🚀 Instalación

### Prerrequisitos
- Python 3.8+
- API Key de OpenAI (para funcionalidad de IA)

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd Diagrams_Creator
```

2. **Crear entorno virtual**
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
cp env_example.txt .env

# Editar .env y agregar tu API key de OpenAI
OPENAI_API_KEY=tu-api-key-real-aqui
```

5. **Ejecutar la aplicación**
```bash
python app.py
```

La aplicación estará disponible en: http://localhost:5000

## 🔑 Configuración de OpenAI

Para usar la funcionalidad de generación de diagramas con IA:

1. Ve a [OpenAI Platform](https://platform.openai.com/api-keys)
2. Crea una nueva API key
3. Agrega la key a tu archivo `.env`:
```bash
OPENAI_API_KEY=sk-tu-api-key-aqui
```

## 💡 Uso de la Aplicación

### Generar Diagrama con IA

1. **Desde el sidebar**: Escribe una descripción en el campo "Generar con IA"
2. **Desde el header**: Haz clic en "Generar con IA" para abrir el modal completo
3. **Ejemplos de descripciones**:
   - "Un diagrama de flujo para el proceso de login de usuario"
   - "Diagrama de secuencia de una aplicación web con frontend, backend y base de datos"
   - "Mapa mental sobre conceptos de inteligencia artificial"

### Crear Diagrama Manualmente

1. Selecciona una plantilla del sidebar
2. Usa las herramientas del toolbar para agregar elementos
3. Arrastra y conecta elementos según necesites
4. Guarda tu trabajo

### Editar Diagramas Existentes

1. Abre un diagrama guardado
2. Usa las herramientas de edición
3. Guarda los cambios

## 🎯 Tipos de Diagramas Soportados

- **Flowchart**: Diagramas de flujo y procesos
- **Sequence**: Diagramas de secuencia UML
- **Class**: Diagramas de clases UML
- **ER**: Diagramas entidad-relación
- **Network**: Arquitectura de redes
- **Mindmap**: Mapas mentales
- **Architecture**: Arquitectura de sistemas

## 🔧 API Endpoints

### Generación de IA
- `POST /generate_ai_diagram` - Genera diagrama usando IA

### Gestión de Diagramas
- `POST /create_diagram` - Crea nuevo diagrama
- `GET /diagram/<id>` - Obtiene diagrama por ID
- `PUT /diagram/<id>` - Actualiza diagrama
- `GET /diagrams` - Lista todos los diagramas

### Plantillas
- `GET /templates` - Obtiene plantillas disponibles

### Exportación
- `POST /export/<id>` - Exporta diagrama a diferentes formatos

## 🎨 Interfaz de Usuario

### Header
- Botón principal "Generar con IA" con gradiente atractivo
- Acciones estándar: Nuevo, Abrir, Guardar, Exportar

### Sidebar
- **Sección de IA**: Generador rápido de diagramas
- **Plantillas**: Tipos de diagramas predefinidos
- **Elementos**: Herramientas de dibujo básicas

### Toolbar
- **Seleccionar**: Modo de selección y edición
- **Pan**: Navegación por el canvas
- **Conectar**: Crear conexiones entre elementos
- **Texto**: Agregar texto
- **Formas**: Insertar formas básicas

### Canvas
- Área de trabajo de 2000x2000 píxeles
- Elementos arrastrables y editables
- Conexiones automáticas entre nodos

## 🚀 Características Avanzadas

### Detección Automática de Tipo
La IA analiza tu descripción y determina automáticamente el tipo de diagrama más apropiado:
- Palabras clave como "flujo", "proceso" → Flowchart
- "Secuencia", "interacción" → Sequence
- "Clase", "UML" → Class
- "Entidad", "base de datos" → ER
- "Red", "router" → Network
- "Mapa mental", "ideas" → Mindmap
- "Arquitectura", "componentes" → Architecture

### Generación Inteligente
- Crea nodos con posiciones lógicas
- Conecta elementos de forma coherente
- Usa tipos de nodos apropiados para cada contexto
- Genera diagramas visualmente atractivos

### Sistema de Fallback
Si la IA falla por cualquier razón:
- Genera un diagrama básico basado en palabras clave
- Mantiene la funcionalidad de la aplicación
- Proporciona feedback útil al usuario

## 🎯 Casos de Uso

### Para Desarrolladores
- Documentar arquitecturas de sistemas
- Crear diagramas de flujo de aplicaciones
- Diseñar diagramas de base de datos
- Planificar flujos de usuario

### Para Analistas de Negocio
- Mapear procesos empresariales
- Crear diagramas de flujo organizacionales
- Visualizar workflows complejos
- Documentar procedimientos

### Para Educadores
- Crear diagramas explicativos
- Generar mapas mentales para conceptos
- Visualizar relaciones entre ideas
- Crear material didáctico

## 🔒 Seguridad

- Validación de entrada en todos los endpoints
- Sanitización de datos de usuario
- Manejo seguro de archivos
- Límites de tamaño de archivo

## 🚧 Limitaciones Actuales

- Los diagramas se almacenan en memoria (se pierden al reiniciar)
- Exportación limitada a formato JSON
- No hay persistencia de datos
- Sin autenticación de usuarios

## 🔮 Próximas Características

- [ ] Base de datos para persistencia
- [ ] Autenticación de usuarios
- [ ] Colaboración en tiempo real
- [ ] Más formatos de exportación
- [ ] Historial de versiones
- [ ] Plantillas personalizables

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [Eraser.io](https://app.eraser.io/) por la inspiración
- [OpenAI](https://openai.com/) por la API de IA
- [Font Awesome](https://fontawesome.com/) por los iconos
- Comunidad de desarrolladores de código abierto

## 📞 Soporte

Si tienes problemas o preguntas:
1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

**¡Disfruta creando diagramas increíbles con IA! 🎨✨**
