#!/usr/bin/env node
/**
 * Script para descargar iconos oficiales de Azure
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Crear directorio para iconos
const iconsDir = path.join(__dirname, 'public', 'icons', 'azure');
if (!fs.existsSync(iconsDir)) {
    fs.mkdirSync(iconsDir, { recursive: true });
}

// Iconos oficiales de Azure con URLs directas
const azureIcons = {
    'virtual-machines': {
        name: 'Virtual Machines',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Compute%20Services/Virtual%20Machines.svg',
        filename: 'virtual-machines.svg'
    },
    'app-service': {
        name: 'App Service',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Compute%20Services/App%20Service.svg',
        filename: 'app-service.svg'
    },
    'sql-database': {
        name: 'SQL Database',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Databases/SQL%20Database.svg',
        filename: 'sql-database.svg'
    },
    'storage-account': {
        name: 'Storage Account',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Storage/Storage%20Account.svg',
        filename: 'storage-account.svg'
    },
    'virtual-network': {
        name: 'Virtual Network',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Networking/Virtual%20Network.svg',
        filename: 'virtual-network.svg'
    },
    'load-balancer': {
        name: 'Load Balancer',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Networking/Load%20Balancer.svg',
        filename: 'load-balancer.svg'
    },
    'redis-cache': {
        name: 'Redis Cache',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Databases/Redis%20Cache.svg',
        filename: 'redis-cache.svg'
    },
    'service-bus': {
        name: 'Service Bus',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Integration/Service%20Bus.svg',
        filename: 'service-bus.svg'
    },
    'azure-functions': {
        name: 'Azure Functions',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Compute%20Services/Azure%20Functions.svg',
        filename: 'azure-functions.svg'
    },
    'cosmos-db': {
        name: 'Cosmos DB',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Databases/Cosmos%20DB.svg',
        filename: 'cosmos-db.svg'
    },
    'key-vault': {
        name: 'Key Vault',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Security/Key%20Vault.svg',
        filename: 'key-vault.svg'
    },
    'application-insights': {
        name: 'Application Insights',
        url: 'https://raw.githubusercontent.com/microsoft/CloudAdoptionFramework/master/ready/Azure%20icons/Management%20and%20Governance/Application%20Insights.svg',
        filename: 'application-insights.svg'
    }
};

function downloadIcon(iconName, iconData) {
    return new Promise((resolve, reject) => {
        const filePath = path.join(iconsDir, iconData.filename);
        
        // Si el archivo ya existe, no descargarlo
        if (fs.existsSync(filePath)) {
            console.log(`✅ ${iconName} ya existe`);
            resolve();
            return;
        }
        
        const file = fs.createWriteStream(filePath);
        
        https.get(iconData.url, (response) => {
            if (response.statusCode === 200) {
                response.pipe(file);
                file.on('finish', () => {
                    file.close();
                    console.log(`✅ ${iconName} descargado`);
                    resolve();
                });
            } else {
                console.log(`❌ Error descargando ${iconName}: ${response.statusCode}`);
                reject(new Error(`HTTP ${response.statusCode}`));
            }
        }).on('error', (error) => {
            console.log(`❌ Error descargando ${iconName}: ${error.message}`);
            // Crear un icono SVG básico como fallback
            createFallbackIcon(iconName, iconData, filePath);
            resolve();
        });
    });
}

function createFallbackIcon(iconName, iconData, filePath) {
    const fallbackSvg = `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="3" width="20" height="18" rx="2" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
        <rect x="4" y="5" width="16" height="14" fill="white"/>
        <text x="12" y="14" text-anchor="middle" font-family="Arial" font-size="8" fill="#0078D4">${iconData.name}</text>
    </svg>`;
    
    fs.writeFileSync(filePath, fallbackSvg);
    console.log(`⚠️  ${iconName} - usando icono fallback`);
}

async function downloadAllIcons() {
    console.log('📥 Descargando iconos oficiales de Azure...');
    console.log('=' .repeat(50));
    
    const downloadPromises = Object.entries(azureIcons).map(([key, iconData]) => 
        downloadIcon(key, iconData)
    );
    
    try {
        await Promise.all(downloadPromises);
        console.log('\n' + '=' .repeat(50));
        console.log('🎉 ¡Todos los iconos descargados exitosamente!');
        
        // Crear archivo de mapeo
        createIconMapping();
        
    } catch (error) {
        console.error('❌ Error descargando iconos:', error.message);
    }
}

function createIconMapping() {
    const mapping = {};
    Object.entries(azureIcons).forEach(([key, iconData]) => {
        mapping[key] = {
            name: iconData.name,
            path: `/icons/azure/${iconData.filename}`,
            filename: iconData.filename
        };
    });
    
    const mappingPath = path.join(__dirname, 'azure-icon-mapping.json');
    fs.writeFileSync(mappingPath, JSON.stringify(mapping, null, 2));
    console.log('📋 Mapeo de iconos creado: azure-icon-mapping.json');
}

// Ejecutar descarga
downloadAllIcons().catch(console.error);
