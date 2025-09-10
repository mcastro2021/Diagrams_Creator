#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 Setting up Azure Diagram Generator...');

// Check if Node.js version is 18+
function checkNodeVersion() {
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.slice(1).split('.')[0]);
  
  if (majorVersion < 18) {
    console.error('❌ Node.js version 18+ is required. Current version:', nodeVersion);
    process.exit(1);
  }
  
  console.log('✅ Node.js version:', nodeVersion);
}

// Check if npm is available
function checkNpm() {
  try {
    const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
    console.log('✅ npm version:', npmVersion);
  } catch (error) {
    console.error('❌ npm is not available');
    process.exit(1);
  }
}

// Install dependencies
function installDependencies() {
  console.log('📦 Installing dependencies...');
  try {
    execSync('npm install', { stdio: 'inherit' });
    console.log('✅ Dependencies installed successfully');
  } catch (error) {
    console.error('❌ Failed to install dependencies');
    process.exit(1);
  }
}

// Create .env file if it doesn't exist
function createEnvFile() {
  const envPath = '.env';
  const envExamplePath = 'env.example';
  
  if (!fs.existsSync(envPath)) {
    if (fs.existsSync(envExamplePath)) {
      fs.copyFileSync(envExamplePath, envPath);
      console.log('📝 Created .env file from env.example');
      console.log('⚠️  Please edit .env file with your configuration');
    } else {
      console.log('⚠️  env.example not found, creating basic .env file');
      const basicEnv = `# Server Configuration
PORT=3001
NODE_ENV=development

# AI/ML Configuration
GROQ_API_KEY=your_groq_api_key_here

# Database Configuration (optional for development)
DATABASE_URL=

# JWT Configuration
JWT_SECRET=development_jwt_secret_key

# Security
CORS_ORIGIN=http://localhost:3001
`;
      fs.writeFileSync(envPath, basicEnv);
    }
  } else {
    console.log('✅ .env file already exists');
  }
}

// Create uploads directory
function createUploadsDir() {
  const uploadsDir = 'uploads';
  const gitkeepPath = path.join(uploadsDir, '.gitkeep');
  
  if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
    fs.writeFileSync(gitkeepPath, '');
    console.log('📁 Created uploads directory');
  } else {
    console.log('✅ uploads directory already exists');
  }
}

// Check if Docker is available
function checkDocker() {
  try {
    execSync('docker --version', { encoding: 'utf8' });
    console.log('✅ Docker is available');
    
    try {
      execSync('docker-compose --version', { encoding: 'utf8' });
      console.log('✅ Docker Compose is available');
      console.log('🐳 You can run "npm run docker:dev" to start the development environment');
    } catch (error) {
      console.log('ℹ️  Docker Compose is not available');
    }
  } catch (error) {
    console.log('ℹ️  Docker is not installed (optional for development)');
  }
}

// Check if PostgreSQL is available
function checkPostgreSQL() {
  try {
    execSync('psql --version', { encoding: 'utf8' });
    console.log('✅ PostgreSQL is available');
  } catch (error) {
    console.log('ℹ️  PostgreSQL is not installed (optional for local development)');
    console.log('   You can use Docker Compose or connect to a remote database');
  }
}

// Main setup function
function main() {
  try {
    checkNodeVersion();
    checkNpm();
    installDependencies();
    createEnvFile();
    createUploadsDir();
    checkDocker();
    checkPostgreSQL();
    
    console.log('');
    console.log('🎉 Setup completed!');
    console.log('');
    console.log('Next steps:');
    console.log('1. Edit .env file with your configuration');
    console.log('2. Get a Groq API key from https://console.groq.com');
    console.log('3. Run "npm start" to start the development server');
    console.log('4. Or run "npm run docker:dev" to start with Docker');
    console.log('');
    console.log('For deployment to Render, see RENDER_DEPLOYMENT.md');
    
  } catch (error) {
    console.error('❌ Setup failed:', error.message);
    process.exit(1);
  }
}

// Run setup
main();
