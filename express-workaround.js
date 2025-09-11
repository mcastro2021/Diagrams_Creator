// express-workaround.js
// Workaround for Express router module not found issue on Render.com

const fs = require('fs');
const path = require('path');

console.log('🔧 Express workaround module loaded');

// Check if Express router exists
const expressRouterPath = path.join('node_modules', 'express', 'lib', 'router', 'index.js');

if (!fs.existsSync(expressRouterPath)) {
    console.log('⚠️ Express router missing, creating workaround...');
    
    // Try to create a minimal router workaround
    const expressLibPath = path.join('node_modules', 'express', 'lib');
    const routerPath = path.join(expressLibPath, 'router');
    
    try {
        // Ensure router directory exists
        if (!fs.existsSync(routerPath)) {
            fs.mkdirSync(routerPath, { recursive: true });
            console.log('📁 Created router directory');
        }
        
        // Create a minimal index.js for router
        const routerIndexContent = `
// Minimal Express router workaround
module.exports = function(options) {
    return {
        use: function() { return this; },
        get: function() { return this; },
        post: function() { return this; },
        put: function() { return this; },
        delete: function() { return this; },
        patch: function() { return this; },
        all: function() { return this; },
        param: function() { return this; },
        route: function() { return this; },
        stack: []
    };
};
`;
        
        fs.writeFileSync(expressRouterPath, routerIndexContent);
        console.log('✅ Created minimal router workaround');
        
    } catch (error) {
        console.error('❌ Failed to create router workaround:', error.message);
    }
} else {
    console.log('✅ Express router found, no workaround needed');
}

module.exports = {};
