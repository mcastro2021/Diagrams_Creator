# 🔑 Configurar Git para Push sin Secrets

## **OPCIÓN 1: Personal Access Token (Recomendado)**

### **Paso 1: Crear Personal Access Token en GitHub**
1. Ve a GitHub.com e inicia sesión
2. Click en tu avatar (esquina superior derecha) → **Settings**
3. En el menú izquierdo: **Developer settings** 
4. Click **Personal access tokens** → **Tokens (classic)**
5. Click **Generate new token** → **Generate new token (classic)**
6. Configuración del token:
   - **Note:** `Diagrams Creator Deploy`
   - **Expiration:** `90 days` (o lo que prefieras)
   - **Scopes:** Marcar ✅ **repo** (acceso completo a repositorios)
7. Click **Generate token**
8. **¡IMPORTANTE!** Copia el token inmediatamente (solo se muestra una vez)

### **Paso 2: Configurar Git con el Token**
```bash
# Configurar credenciales (usar tu email de GitHub)
git config --global user.name "Manuel Castro"
git config --global user.email "mcastrotorres2008@gmail.com"

# Cuando hagas push, usa:
# Usuario: tu-usuario-github
# Password: el-token-que-copiaste
git push origin main
```

## **OPCIÓN 2: GitHub CLI (Alternativa)**

### **Instalar GitHub CLI**
```bash
# Descargar desde: https://cli.github.com/
# O con winget:
winget install GitHub.cli
```

### **Autenticar**
```bash
gh auth login
# Seguir las instrucciones en pantalla
```

### **Push**
```bash
git push origin main
```

## **OPCIÓN 3: SSH (Más Seguro)**

### **Generar clave SSH**
```bash
ssh-keygen -t ed25519 -C "mcastrotorres2008@gmail.com"
# Presionar Enter para ubicación por defecto
# Enter para passphrase vacía (o crear una)
```

### **Agregar clave a GitHub**
1. Copiar clave pública:
```bash
cat ~/.ssh/id_ed25519.pub
```
2. GitHub → Settings → SSH and GPG keys → New SSH key
3. Pegar la clave pública

### **Cambiar remote a SSH**
```bash
git remote set-url origin git@github.com:mcastro2021/Diagrams_Creator.git
git push origin main
```

## **🚀 DESPUÉS DEL PUSH EXITOSO:**

1. Ve a tu repositorio en GitHub
2. Verifica que todos los archivos estén subidos
3. Procede con el deployment en Render usando la URL del repo
