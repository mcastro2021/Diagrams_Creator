# 🚀 Deployment en Render

## Instrucciones para desplegar Diagrams Creator en Render

### 1. **Preparación**
- Tu aplicación ya está configurada para Render
- Archivos incluidos: `Procfile`, `render.yaml`, `runtime.txt`
- Dependencies actualizadas en `requirements.txt`

### 2. **Variables de Entorno Necesarias**
Configura estas variables en Render:

**Obligatorias:**
- `GROQ_API_KEY` - Tu clave API de Groq
- `SECRET_KEY` - Se genera automáticamente

**Opcionales:**
- `OPENAI_API_KEY` - Si quieres usar OpenAI
- `AI_PROVIDER` - Por defecto "groq"

### 3. **Deployment Steps**

#### Opción A: Usando Render Dashboard
1. Ve a [render.com](https://render.com)
2. Conecta tu repositorio de GitHub
3. Crea un nuevo "Web Service"
4. Selecciona tu repositorio
5. Render detectará automáticamente el `render.yaml`
6. Configura las variables de entorno
7. Deploy!

#### Opción B: Usando Render CLI (si tienes acceso)
```bash
# Instalar Render CLI
npm install -g @render/cli

# Login
render login

# Deploy
render deploy
```

### 4. **Configuración Automática**
- **Runtime:** Python 3.11.0
- **Build:** `pip install -r requirements.txt`  
- **Start:** `gunicorn app:app`
- **Plan:** Starter (gratis)
- **Static Files:** Configurado con WhiteNoise

### 5. **Verificación Post-Deploy**
Una vez desplegado, verifica:
- ✅ Aplicación carga en la URL de Render
- ✅ API health endpoint: `/api/health`
- ✅ Librerías de iconos: `/api/libraries`
- ✅ Generación de diagramas funciona

### 6. **URLs Importantes**
- **App:** `https://your-app-name.onrender.com`
- **Health:** `https://your-app-name.onrender.com/api/health`
- **Libraries:** `https://your-app-name.onrender.com/api/libraries`

### 7. **Troubleshooting**
- **Logs:** Ver en Render Dashboard > Service > Logs
- **Environment:** Verificar variables están configuradas
- **Build:** Si falla, revisar `requirements.txt`

## 🎯 Ventajas de Render
- ✅ HTTPS automático
- ✅ Dominio personalizable  
- ✅ Auto-deploy desde Git
- ✅ Escalado automático
- ✅ Logs centralizados
- ✅ Variables de entorno seguras
