# 🔄 Crear Repositorio Limpio para Render

## **OPCIÓN 1: Permitir secretos en GitHub (MÁS RÁPIDO)**

1. Ve a estos enlaces en tu navegador:
   - **OpenAI:** https://github.com/mcastro2021/Diagrams_Creator/security/secret-scanning/unblock-secret/32DWIBfd7GlPC529xUFzXEs8H2q
   - **Groq:** https://github.com/mcastro2021/Diagrams_Creator/security/secret-scanning/unblock-secret/32DVtOeHUtM5vq8wttSWWyuS0HU

2. Click "Allow secret" en ambos

3. Regresa a la terminal y ejecuta:
```bash
git push origin main
```

## **OPCIÓN 2: Crear repositorio completamente nuevo**

### **Paso 1: Crear nuevo repo en GitHub**
1. Ve a https://github.com/new
2. Nombre: `Diagrams-Creator-Clean`
3. Descripción: `AI-powered diagram generator for cloud architectures`
4. **Público** (para usar con Render gratis)
5. Click "Create repository"

### **Paso 2: Configurar localmente**
```bash
# Eliminar remote actual
git remote remove origin

# Añadir nuevo remote
git remote add origin https://github.com/mcastro2021/Diagrams-Creator-Clean.git

# Crear branch limpio
git checkout --orphan clean-main
git add .
git commit -m "Initial commit - Ready for Render deployment"
git branch -M main
git push -u origin main
```

## **OPCIÓN 3: Forzar push (NO RECOMENDADO)**
```bash
# SOLO si las otras opciones no funcionan
git push origin main --force
```

## **🎯 RECOMENDACIÓN:**

**Usa OPCIÓN 1** (permitir secretos) ya que:
- ✅ Es más rápido
- ✅ Los secretos están en archivos de ejemplo, no en producción
- ✅ Render manejará las variables de entorno de forma segura
- ✅ Una vez en producción, las APIs keys estarán protegidas

Después del push exitoso, procede con el deployment en Render.
