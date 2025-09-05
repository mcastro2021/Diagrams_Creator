#!/usr/bin/env node
/**
 * Script de prueba para verificar que los iconos de Azure se muestran correctamente
 */

const http = require('http');
const fs = require('fs');

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
                try {
                    const jsonBody = body ? JSON.parse(body) : {};
                    resolve({
                        statusCode: res.statusCode,
                        headers: res.headers,
                        body: jsonBody
                    });
                } catch (error) {
                    resolve({
                        statusCode: res.statusCode,
                        headers: res.headers,
                        body: body
                    });
                }
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

async function testIcons() {
    console.log('🎨 PRUEBAS DE ICONOS DE AZURE');
    console.log('=' .repeat(50));
    
    let testsPassed = 0;
    let totalTests = 0;
    
    // Test 1: Verificar que el archivo de iconos existe
    totalTests++;
    try {
        if (fs.existsSync('azure-icons.js')) {
            console.log('✅ Test 1: Archivo azure-icons.js existe');
            testsPassed++;
        } else {
            console.log('❌ Test 1: Archivo azure-icons.js no encontrado');
        }
    } catch (error) {
        console.log(`❌ Test 1: Error verificando archivo: ${error.message}`);
    }
    
    // Test 2: Verificar que el HTML incluye el script de iconos
    totalTests++;
    try {
        const htmlContent = fs.readFileSync('index.html', 'utf8');
        if (htmlContent.includes('azure-icons.js')) {
            console.log('✅ Test 2: HTML incluye script de iconos');
            testsPassed++;
        } else {
            console.log('❌ Test 2: HTML no incluye script de iconos');
        }
    } catch (error) {
        console.log(`❌ Test 2: Error leyendo HTML: ${error.message}`);
    }
    
    // Test 3: Probar generación con múltiples servicios para verificar iconos
    totalTests++;
    try {
        const testDescription = 'Arquitectura completa con Virtual Machine, App Service, SQL Database, Storage Account, Redis Cache, Service Bus, Azure Functions, Cosmos DB, Key Vault y Application Insights';
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log('✅ Test 3: Generación con múltiples servicios funciona');
            console.log(`   🎨 Elementos generados: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones generadas: ${data.metadata.totalConnections}`);
            console.log(`   🏷️  Servicios detectados: ${data.metadata.detectedServices.join(', ')}`);
            
            // Verificar que se detectaron múltiples servicios
            if (data.metadata.detectedServices.length >= 5) {
                console.log('   ✅ Se detectaron múltiples servicios correctamente');
                testsPassed++;
            } else {
                console.log('   ⚠️  Se detectaron pocos servicios');
            }
        } else {
            console.log(`❌ Test 3: Generación con múltiples servicios falló`);
        }
    } catch (error) {
        console.log(`❌ Test 3: Error en generación con múltiples servicios: ${error.message}`);
    }
    
    // Test 4: Probar con descripción simple
    totalTests++;
    try {
        const testDescription = 'Una aplicación web simple';
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log('✅ Test 4: Generación con descripción simple funciona');
            console.log(`   🎨 Elementos generados: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones generadas: ${data.metadata.totalConnections}`);
            testsPassed++;
        } else {
            console.log(`❌ Test 4: Generación con descripción simple falló`);
        }
    } catch (error) {
        console.log(`❌ Test 4: Error en generación simple: ${error.message}`);
    }
    
    // Test 5: Probar con descripción en español
    totalTests++;
    try {
        const testDescription = 'Necesito una máquina virtual con base de datos y almacenamiento';
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log('✅ Test 5: Generación con descripción en español funciona');
            console.log(`   🎨 Elementos generados: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones generadas: ${data.metadata.totalConnections}`);
            testsPassed++;
        } else {
            console.log(`❌ Test 5: Generación con descripción en español falló`);
        }
    } catch (error) {
        console.log(`❌ Test 5: Error en generación en español: ${error.message}`);
    }
    
    // Test 6: Probar con descripción que no menciona servicios específicos
    totalTests++;
    try {
        const testDescription = 'Sistema de gestión de usuarios';
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log('✅ Test 6: Generación con descripción genérica funciona');
            console.log(`   🎨 Elementos generados: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones generadas: ${data.metadata.totalConnections}`);
            testsPassed++;
        } else {
            console.log(`❌ Test 6: Generación con descripción genérica falló`);
        }
    } catch (error) {
        console.log(`❌ Test 6: Error en generación genérica: ${error.message}`);
    }
    
    console.log('\n' + '=' .repeat(50));
    console.log(`🎯 RESUMEN DE PRUEBAS: ${testsPassed}/${totalTests} pasaron`);
    
    if (testsPassed === totalTests) {
        console.log('🎉 ¡Todas las pruebas pasaron! Los iconos deberían mostrarse correctamente.');
        console.log('\n🌐 Para verificar los iconos:');
        console.log('   1. Abre tu navegador en http://localhost:3001');
        console.log('   2. Prueba con diferentes descripciones:');
        console.log('      • "Una aplicación web con base de datos"');
        console.log('      • "Arquitectura de microservicios con Redis y Service Bus"');
        console.log('      • "Sistema con máquinas virtuales y almacenamiento"');
        console.log('   3. Verifica que los elementos muestran iconos en lugar de solo texto');
    } else {
        console.log('⚠️  Algunas pruebas fallaron. Revisa los errores arriba.');
    }
    
    console.log('\n📝 Iconos disponibles:');
    console.log('   • Virtual Machine, App Service, SQL Database');
    console.log('   • Storage Account, Virtual Network, Load Balancer');
    console.log('   • Redis Cache, Service Bus, Azure Functions');
    console.log('   • Cosmos DB, Key Vault, Application Insights');
}

// Ejecutar las pruebas
testIcons().catch(console.error);
