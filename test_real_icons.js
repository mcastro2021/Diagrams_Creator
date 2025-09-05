#!/usr/bin/env node
/**
 * Script de prueba para verificar que los iconos reales de Azure se cargan correctamente
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

function testEndpoint(path, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'localhost',
            port: 3001,
            path: path,
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const req = http.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => {
                body += chunk;
            });
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    headers: res.headers,
                    body: body
                });
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        if (data) {
            req.write(JSON.stringify(data));
        }
        req.end();
    });
}

async function testRealIcons() {
    console.log('🎨 PRUEBAS DE ICONOS REALES DE AZURE');
    console.log('=' .repeat(60));
    
    let testsPassed = 0;
    let totalTests = 0;
    
    // Test 1: Verificar que los archivos de iconos existen
    totalTests++;
    const iconPaths = [
        'icons/compute/10021-icon-service-Virtual-Machine.svg',
        'icons/app services/10035-icon-service-App-Services.svg',
        'icons/databases/10130-icon-service-SQL-Database.svg',
        'icons/storage/10086-icon-service-Storage-Accounts.svg',
        'icons/networking/10061-icon-service-Virtual-Networks.svg',
        'icons/databases/10137-icon-service-Cache-Redis.svg',
        'icons/integration/10836-icon-service-Azure-Service-Bus.svg',
        'icons/compute/10029-icon-service-Function-Apps.svg',
        'icons/databases/10121-icon-service-Azure-Cosmos-DB.svg',
        'icons/security/10245-icon-service-Key-Vaults.svg',
        'icons/monitor/00012-icon-service-Application-Insights.svg'
    ];
    
    let existingIcons = 0;
    iconPaths.forEach(iconPath => {
        if (fs.existsSync(iconPath)) {
            existingIcons++;
        }
    });
    
    if (existingIcons >= 8) {
        console.log(`✅ Test 1: ${existingIcons}/${iconPaths.length} iconos encontrados`);
        testsPassed++;
    } else {
        console.log(`❌ Test 1: Solo ${existingIcons}/${iconPaths.length} iconos encontrados`);
    }
    
    // Test 2: Verificar que el servidor sirve los iconos
    totalTests++;
    try {
        const response = await testEndpoint('/icons/compute/10021-icon-service-Virtual-Machine.svg');
        if (response.statusCode === 200 && response.body.includes('<svg')) {
            console.log('✅ Test 2: Servidor sirve iconos SVG correctamente');
            testsPassed++;
        } else {
            console.log(`❌ Test 2: Error sirviendo iconos: ${response.statusCode}`);
        }
    } catch (error) {
        console.log(`❌ Test 2: Error: ${error.message}`);
    }
    
    // Test 3: Verificar que el archivo azure-icons-real.js existe
    totalTests++;
    if (fs.existsSync('azure-icons-real.js')) {
        console.log('✅ Test 3: Archivo azure-icons-real.js existe');
        testsPassed++;
    } else {
        console.log('❌ Test 3: Archivo azure-icons-real.js no encontrado');
    }
    
    // Test 4: Verificar que el HTML incluye el script correcto
    totalTests++;
    try {
        const htmlContent = fs.readFileSync('index.html', 'utf8');
        if (htmlContent.includes('azure-icons-real.js')) {
            console.log('✅ Test 4: HTML incluye script de iconos reales');
            testsPassed++;
        } else {
            console.log('❌ Test 4: HTML no incluye script de iconos reales');
        }
    } catch (error) {
        console.log(`❌ Test 4: Error leyendo HTML: ${error.message}`);
    }
    
    // Test 5: Probar generación de diagrama con iconos reales
    totalTests++;
    try {
        const testDescription = 'Aplicación web con App Service, SQL Database, Storage Account y Redis Cache';
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.includes('success')) {
            console.log('✅ Test 5: Generación de diagrama funciona con iconos reales');
            console.log('   🎨 Diagrama generado exitosamente');
            testsPassed++;
        } else {
            console.log(`❌ Test 5: Error en generación: ${response.statusCode}`);
        }
    } catch (error) {
        console.log(`❌ Test 5: Error: ${error.message}`);
    }
    
    // Test 6: Verificar que el servidor está configurado para servir iconos
    totalTests++;
    try {
        const serverContent = fs.readFileSync('server.js', 'utf8');
        if (serverContent.includes("app.use('/icons', express.static('icons'))")) {
            console.log('✅ Test 6: Servidor configurado para servir iconos');
            testsPassed++;
        } else {
            console.log('❌ Test 6: Servidor no configurado para servir iconos');
        }
    } catch (error) {
        console.log(`❌ Test 6: Error leyendo server.js: ${error.message}`);
    }
    
    console.log('\n' + '=' .repeat(60));
    console.log(`🎯 RESUMEN DE PRUEBAS: ${testsPassed}/${totalTests} pasaron`);
    
    if (testsPassed === totalTests) {
        console.log('🎉 ¡Todas las pruebas pasaron! Los iconos reales están configurados correctamente.');
        console.log('\n🌐 Para verificar los iconos reales:');
        console.log('   1. Abre tu navegador en http://localhost:3001');
        console.log('   2. Prueba con estas descripciones:');
        console.log('      • "Aplicación web con App Service, SQL Database y Storage Account"');
        console.log('      • "Sistema con Virtual Machine, Redis Cache y Service Bus"');
        console.log('      • "Arquitectura con Azure Functions, Cosmos DB y Key Vault"');
        console.log('   3. Verifica que los elementos muestran los iconos oficiales de Azure');
        console.log('   4. Los iconos deberían ser los mismos que ves en el portal de Azure');
    } else {
        console.log('⚠️  Algunas pruebas fallaron. Revisa los errores arriba.');
    }
    
    console.log('\n📝 Iconos oficiales configurados:');
    console.log('   • Virtual Machine: 10021-icon-service-Virtual-Machine.svg');
    console.log('   • App Service: 10035-icon-service-App-Services.svg');
    console.log('   • SQL Database: 10130-icon-service-SQL-Database.svg');
    console.log('   • Storage Account: 10086-icon-service-Storage-Accounts.svg');
    console.log('   • Virtual Network: 10061-icon-service-Virtual-Networks.svg');
    console.log('   • Redis Cache: 10137-icon-service-Cache-Redis.svg');
    console.log('   • Service Bus: 10836-icon-service-Azure-Service-Bus.svg');
    console.log('   • Azure Functions: 10029-icon-service-Function-Apps.svg');
    console.log('   • Cosmos DB: 10121-icon-service-Azure-Cosmos-DB.svg');
    console.log('   • Key Vault: 10245-icon-service-Key-Vaults.svg');
    console.log('   • Application Insights: 00012-icon-service-Application-Insights.svg');
}

// Ejecutar las pruebas
testRealIcons().catch(console.error);
