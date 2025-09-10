@echo off
REM Azure Diagram Generator Setup Script for Windows
REM This script sets up the development environment

echo 🚀 Setting up Azure Diagram Generator...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js version:
node --version

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo ✅ npm version:
npm --version

REM Install dependencies
echo 📦 Installing dependencies...
npm install

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    copy env.example .env
    echo ⚠️  Please edit .env file with your configuration
)

REM Create uploads directory
if not exist uploads (
    echo 📁 Creating uploads directory...
    mkdir uploads
    echo. > uploads\.gitkeep
)

REM Check if Docker is installed (optional)
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker is available
    docker-compose --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Docker Compose is available
        echo 🐳 You can run 'docker-compose up' to start the development environment
    )
) else (
    echo ℹ️  Docker is not installed (optional for development)
)

echo.
echo 🎉 Setup completed!
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Get a Groq API key from https://console.groq.com
echo 3. Run 'npm start' to start the development server
echo 4. Or run 'docker-compose up' to start with Docker
echo.
echo For deployment to Render, see RENDER_DEPLOYMENT.md
echo.
pause
