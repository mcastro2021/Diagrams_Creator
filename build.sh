#!/bin/bash
# Build script for Render.com

echo "🔧 Installing dependencies..."
npm install --ignore-scripts

echo "🔍 Verifying debug module..."
if [ -f "node_modules/debug/src/debug.js" ]; then
    echo "✅ Debug module found"
else
    echo "❌ Debug module missing, reinstalling..."
    npm install debug --ignore-scripts
fi

echo "🚀 Build completed successfully"
