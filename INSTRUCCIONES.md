# 📋 **Instrucciones de Uso - Diagrams Creator**

## 🎯 **Cómo Usar Tu Aplicación**

### **1. 🌐 Acceder a la Aplicación**
```
URL: http://localhost:5000
```

### **2. 📝 Generar Diagramas desde Texto**

#### **Paso a Paso:**
1. **Describe tu arquitectura** en el área de texto
2. **Selecciona el tipo** de diagrama (Azure, AWS, etc.)
3. **Elige el estilo** visual (Moderno, Minimalista, Colorido)
4. **Haz clic en "Generar Diagrama"**

#### **Ejemplos de Descripciones:**

```bash
# Azure Hub and Spoke
"Crear diagrama Azure Hub and Spoke con 5 suscripciones"

# Seguridad Fortinet
"Red segura con FortiGate firewall, FortiAnalyzer y switches Arista"

# Microservicios
"Aplicación con API Gateway, 3 microservicios, Redis cache y PostgreSQL"

# AWS
"Aplicación web AWS con EC2, RDS, S3, Lambda y CloudFront"
```

### **3. 🔍 Buscar Iconos**

#### **Campo de Búsqueda:**
```
🔍 "fortinet" → 1,203 iconos de seguridad
🔍 "azure" → 253 iconos de Azure
🔍 "integration" → 2,131 iconos de conectores
🔍 "database" → Iconos de bases de datos
🔍 "network" → Equipos de red
```

#### **Filtros Rápidos:**
- 🛡️ **Fortinet Security** - Firewalls, amenazas
- ☁️ **Azure** - Servicios Microsoft
- 🔗 **Integration** - APIs, microservicios
- 🟧 **AWS** - Servicios Amazon
- 🐳 **Kubernetes** - Contenedores

#### **Lista Desplegable:**
- Selecciona una librería específica
- Ve todos los iconos de esa categoría
- Organizado por tipos (Fortinet, Integration, etc.)

### **4. 💾 Trabajar con Diagramas**

#### **Opciones Disponibles:**

1. **📱 Descargar XML:**
   - Haz clic en "Descargar XML"
   - Guarda el archivo .xml
   - Importa en Draw.io manualmente

2. **🌐 Abrir en Draw.io:**
   - Haz clic en "Abrir en Draw.io"
   - Se abre automáticamente en nueva pestaña
   - Edita el diagrama online

3. **🔗 Copiar URL:**
   - Haz clic en "Copiar URL"
   - Comparte el enlace directo
   - Otros pueden ver el diagrama

4. **📤 Exportar:**
   - XML (Draw.io)
   - SVG (vectorial)
   - PNG (imagen)
   - PDF (documento)

### **5. 📄 Subir Documentos**

#### **Formatos Soportados:**
- **TXT** - Archivos de texto
- **PDF** - Documentos PDF
- **DOCX** - Microsoft Word
- **MD** - Markdown
- **JSON** - Archivos JSON

#### **Proceso:**
1. **Cambia a la pestaña "Documento"**
2. **Selecciona archivo** (máximo 16MB)
3. **Configura opciones** de diagrama
4. **Haz clic en "Procesar Documento"**

### **6. 🛠️ Solución de Problemas**

#### **Error "Archivo no encontrado":**
```
✅ Solución:
1. Usa "Descargar XML" en lugar de "Abrir en Draw.io"
2. Ve a https://app.diagrams.net
3. Arrastra el archivo XML descargado
```

#### **Error de codificación:**
```
✅ Solución:
1. Haz clic en "Copiar URL"
2. Ve a https://app.diagrams.net
3. File → Import from → URL
4. Pega la URL copiada
```

#### **Diagrama vacío o simple:**
```
✅ Causa: Cuota de OpenAI agotada (normal)
✅ Solución: El modo fallback está funcionando
✅ Resultado: Diagramas generados usando patrones inteligentes
```

### **7. 🎨 Personalización**

#### **Estilos Disponibles:**
- **Moderno**: Colores suaves, sombras, redondeado
- **Minimalista**: Líneas simples, sin efectos
- **Colorido**: Colores vibrantes, alto contraste

#### **Tipos de Diagrama:**
- **Auto**: Detección automática
- **AWS**: Amazon Web Services
- **Azure**: Microsoft Azure
- **GCP**: Google Cloud Platform
- **Kubernetes**: Contenedores
- **Network**: Redes y conectividad
- **Genérico**: Uso general

### **8. 🔧 Estado de la Aplicación**

#### **Verificar Estado:**
```
URL: http://localhost:5000/api/health
```

#### **Estado Actual:**
```
✅ Proveedor IA: Groq
✅ Librerías: 61 cargadas
✅ Iconos: 5,000+ disponibles
✅ Diagramas: Se generan automáticamente
```

### **9. 💡 Tips Productivos**

#### **Para Mejores Resultados:**
1. **Sé específico** en las descripciones
2. **Menciona tecnologías** por nombre (FortiGate, Azure, etc.)
3. **Describe conexiones** entre componentes
4. **Usa palabras clave** conocidas

#### **Ejemplos Efectivos:**
```
❌ "sistema web"
✅ "aplicación React con API Node.js y PostgreSQL"

❌ "red segura"  
✅ "FortiGate firewall conectado a switch Arista DCS-7050"

❌ "cloud"
✅ "Azure Hub VNet con 3 spoke VNets y VPN Gateway"
```

### **10. 🚀 Casos de Uso Avanzados**

#### **Arquitecturas Complejas:**
```
"Centro de datos con:
- FortiGate 3000D como firewall perimetral
- Switches Arista 7050 para core
- Servidores Dell en DMZ
- Conexión Azure ExpressRoute
- Backup Commvault a cloud"
```

#### **Microservicios:**
```
"Plataforma microservicios con:
- API Gateway Kong
- 5 servicios Node.js en Kubernetes
- PostgreSQL cluster
- Redis cache
- Kafka para mensajería
- Prometheus monitoring"
```

## 🎉 **¡Disfruta tu Herramienta Profesional!**

Tu **Diagrams Creator** está completamente optimizado para generar diagramas de arquitectura de nivel profesional con IA y una colección masiva de iconos técnicos.

**¡Ve a http://localhost:5000 y comienza a crear!** 🚀📊🎨
