# Conversor de Documentos a Diagramas

Una aplicación web que convierte automáticamente documentos (Excel, PDF, Word, etc.) y texto libre en diagramas profesionales usando la API de draw.io.

## 🚀 Características

- **Soporte múltiple de formatos**: PDF, Excel (.xlsx), Word (.docx), CSV, TXT, JSON
- **Procesamiento inteligente**: Analiza la estructura del contenido y genera diagramas apropiados
- **Integración con draw.io**: Genera diagramas compatibles con la plataforma draw.io
- **Interfaz moderna**: Diseño responsive con drag & drop para archivos
- **Generación automática**: Crea diagramas de flujo, tablas y estructuras según el contenido
- **Edición en línea**: Abre diagramas directamente en draw.io para edición
- **Descarga de archivos**: Exporta diagramas en formato XML

## 📋 Requisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)

## 🛠️ Instalación

1. **Clona el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd Diagrams_Creator
   ```

2. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecuta la aplicación:**
   ```bash
   python app.py
   ```

4. **Abre tu navegador y ve a:**
   ```
   http://localhost:5000
   ```

## 🎯 Uso

### Subir Documentos

1. **Arrastra y suelta** un archivo en el área de subida
2. **O haz clic** para seleccionar un archivo
3. **Haz clic en "Procesar Documento"**
4. **Espera** a que se procese y se genere el diagrama
5. **Edita** el diagrama en draw.io o **descarga** el archivo XML

### Escribir Texto

1. **Escribe** tu texto en el área de texto
2. **Usa formato estructurado** para mejores resultados:
   ```
   1. INICIO
      - Punto de partida
   2. PROCESO
      - Lógica principal
   3. FINAL
      - Resultado
   ```
3. **Haz clic en "Generar Diagrama"**

## 📁 Estructura del Proyecto

```
Diagrams_Creator/
├── app.py                 # Aplicación principal Flask
├── document_processor.py  # Procesador de documentos
├── diagram_generator.py   # Generador de diagramas
├── requirements.txt       # Dependencias de Python
├── templates/
│   └── index.html        # Interfaz web
├── uploads/              # Archivos temporales (se crea automáticamente)
├── outputs/              # Diagramas generados (se crea automáticamente)
└── README.md             # Este archivo
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
FLASK_ENV=development
FLASK_DEBUG=1
MAX_FILE_SIZE=16777216  # 16MB en bytes
```

### Personalización

- **Tamaño máximo de archivo**: Modifica `MAX_CONTENT_LENGTH` en `app.py`
- **Formatos soportados**: Edita `ALLOWED_EXTENSIONS` en `app.py`
- **Estilos de diagramas**: Modifica los métodos en `diagram_generator.py`

## 📊 Tipos de Diagramas Generados

### Texto
- **Diagramas de flujo** con títulos y secciones
- **Jerarquías** basadas en estructura del texto
- **Conectores** automáticos entre elementos

### Excel/CSV
- **Tablas visuales** con encabezados y datos
- **Múltiples hojas** como diagramas separados
- **Limitación inteligente** de filas para legibilidad

### JSON
- **Estructuras de objetos** y arrays
- **Propiedades anidadas** con profundidad limitada
- **Tipos de datos** identificados automáticamente

### PDF/Word
- **Extracción de texto** estructurado
- **Análisis de párrafos** y títulos
- **Generación de flujos** basados en contenido

## 🌐 API Endpoints

### POST /upload
Sube y procesa un archivo.

**Parámetros:**
- `file`: Archivo a procesar

**Respuesta:**
```json
{
  "success": true,
  "content": {...},
  "diagram": {...}
}
```

### POST /text
Procesa texto libre.

**Parámetros:**
```json
{
  "text": "Texto a procesar"
}
```

**Respuesta:**
```json
{
  "success": true,
  "diagram": {...}
}
```

### GET /download/<filename>
Descarga un archivo generado.

## 🎨 Personalización de Diagramas

### Colores y Estilos

Los diagramas usan un esquema de colores consistente:

- **Títulos**: Azul claro (#dae8fc)
- **Contenido**: Amarillo claro (#fff2cc)
- **Arrays**: Verde claro (#d5e8d4)
- **Objetos**: Azul claro (#dae8fc)
- **Tipos básicos**: Rojo claro (#f8cecc)

### Estructura XML

Los diagramas se generan en formato XML compatible con draw.io:

```xml
<mxfile host="app.diagrams.net">
  <diagram id="diagram_id" name="Nombre del Diagrama">
    <mxGraphModel>
      <!-- Elementos del diagrama -->
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 🚨 Solución de Problemas

### Error: "Formato de archivo no soportado"
- Verifica que el archivo tenga una extensión válida
- Los formatos soportados son: .pdf, .docx, .xlsx, .csv, .txt, .json

### Error: "Error procesando documento"
- Verifica que el archivo no esté corrupto
- Asegúrate de que el archivo sea legible
- Revisa los logs del servidor para más detalles

### Error: "Error generando diagrama"
- Verifica que el contenido del documento sea válido
- Asegúrate de que haya suficiente contenido para generar un diagrama

### Problemas de rendimiento
- Los archivos grandes pueden tardar más en procesarse
- Considera dividir archivos muy grandes en partes más pequeñas

## 🔒 Seguridad

- **Validación de archivos**: Solo se aceptan formatos específicos
- **Límite de tamaño**: Archivos limitados a 16MB por defecto
- **Limpieza automática**: Los archivos temporales se eliminan después del procesamiento
- **Sanitización**: Los nombres de archivo se limpian para evitar inyecciones

## 🚀 Despliegue

### Producción

Para desplegar en producción:

1. **Configura un servidor WSGI:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Usa un proxy reverso** como Nginx

3. **Configura variables de entorno** apropiadas

4. **Habilita HTTPS** para seguridad

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **draw.io** por proporcionar la plataforma de diagramas
- **Flask** por el framework web
- **Font Awesome** por los iconos
- **Comunidad Python** por las librerías utilizadas

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de solución de problemas
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema
4. Incluye logs de error y pasos para reproducir

---

**¡Disfruta creando diagramas automáticamente! 🎉**
