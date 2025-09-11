#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🚀 Starting application with verification...');

// Check critical modules before starting
const expressRouterPath = path.join('node_modules', 'express', 'lib', 'router', 'index.js');
const debugPath = path.join('node_modules', 'debug', 'src', 'node.js');

console.log('🔍 Final verification before start...');

if (!fs.existsSync(expressRouterPath)) {
    console.error('❌ CRITICAL: Express router missing at startup:', expressRouterPath);
    console.error('This should not happen if postinstall script worked correctly');
    process.exit(1);
}

if (!fs.existsSync(debugPath)) {
    console.error('❌ CRITICAL: Debug module missing at startup:', debugPath);
    console.error('This should not happen if postinstall script worked correctly');
    process.exit(1);
}

console.log('✅ All critical modules verified');
console.log('🎯 Starting server...');

// Start the actual server
require('./server.js');
