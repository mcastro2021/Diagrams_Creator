#!/bin/bash

# Azure Diagram Generator Setup Script
# This script sets up the development environment

echo "🚀 Setting up Azure Diagram Generator..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Create uploads directory
if [ ! -d uploads ]; then
    echo "📁 Creating uploads directory..."
    mkdir -p uploads
    touch uploads/.gitkeep
fi

# Check if Docker is installed (optional)
if command -v docker &> /dev/null; then
    echo "✅ Docker is available"
    if command -v docker-compose &> /dev/null; then
        echo "✅ Docker Compose is available"
        echo "🐳 You can run 'docker-compose up' to start the development environment"
    fi
else
    echo "ℹ️  Docker is not installed (optional for development)"
fi

# Check if PostgreSQL is installed (optional for local development)
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL is available"
else
    echo "ℹ️  PostgreSQL is not installed (optional for local development)"
    echo "   You can use Docker Compose or connect to a remote database"
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Get a Groq API key from https://console.groq.com"
echo "3. Run 'npm start' to start the development server"
echo "4. Or run 'docker-compose up' to start with Docker"
echo ""
echo "For deployment to Render, see RENDER_DEPLOYMENT.md"
