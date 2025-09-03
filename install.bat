@echo off
echo ========================================
echo Conversor de Documentos a Diagramas
echo ========================================
echo.

echo Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo Por favor, instala Python 3.7 o superior desde https://python.org
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Error instalando dependencias
    pause
    exit /b 1
)

echo.
echo Dependencias instaladas exitosamente!
echo.

echo Creando archivo de configuracion...
if not exist .env (
    copy env_example.txt .env
    echo Archivo .env creado. Editalo si es necesario.
) else (
    echo Archivo .env ya existe.
)

echo.
echo ========================================
echo Instalacion completada!
echo ========================================
echo.
echo Para ejecutar la aplicacion:
echo 1. python run.py
echo 2. O python app.py
echo.
echo La aplicacion estara disponible en:
echo http://localhost:5000
echo.
pause
