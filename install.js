#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🔧 Custom install script for Render.com');

// Check if Express router exists
const expressRouterPath = path.join('node_modules', 'express', 'lib', 'router', 'index.js');
const debugPath = path.join('node_modules', 'debug', 'src', 'node.js');

console.log('🔍 Verifying critical modules...');

let needsReinstall = false;

// Check Express router
if (!fs.existsSync(expressRouterPath)) {
    console.error('❌ Express router missing:', expressRouterPath);
    needsReinstall = true;
} else {
    console.log('✅ Express router found');
}

// Check debug module
if (!fs.existsSync(debugPath)) {
    console.error('❌ Debug module missing:', debugPath);
    needsReinstall = true;
} else {
    console.log('✅ Debug module found');
}

if (needsReinstall) {
    console.log('🔄 Reinstalling missing modules...');
    try {
        execSync('npm install express debug --ignore-scripts', { stdio: 'inherit' });
        console.log('✅ Modules reinstalled successfully');
    } catch (error) {
        console.error('❌ Failed to reinstall modules:', error.message);
        process.exit(1);
    }
} else {
    console.log('✅ All critical modules found');
}

console.log('🚀 Install verification completed');
