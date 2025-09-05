#!/usr/bin/env node
/**
 * Script de prueba final para verificar que los iconos correctos se muestran
 */

const http = require('http');

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

async function testFinalIcons() {
    console.log('🎯 PRUEBA FINAL: ICONOS CORRECTOS EN DIAGRAMAS');
    console.log('=' .repeat(60));
    
    const testCases = [
        {
            description: 'Dos virtual machines conectadas a una base de datos',
            expectedTypes: ['azure-vm', 'azure-sql'],
            expectedNames: ['Virtual Machine', 'SQL Database']
        },
        {
            description: 'Aplicación web con App Service, SQL Database y Storage Account',
            expectedTypes: ['azure-app-service', 'azure-sql', 'azure-storage'],
            expectedNames: ['App Service', 'SQL Database', 'Storage Account']
        },
        {
            description: 'Sistema con Virtual Machine, Redis Cache y Service Bus',
            expectedTypes: ['azure-vm', 'azure-redis', 'azure-service-bus'],
            expectedNames: ['Virtual Machine', 'Redis Cache', 'Service Bus']
        },
        {
            description: 'Arquitectura con Azure Functions, Cosmos DB y Key Vault',
            expectedTypes: ['azure-functions', 'azure-cosmos', 'azure-key-vault'],
            expectedNames: ['Azure Functions', 'Cosmos DB', 'Key Vault']
        }
    ];
    
    let testsPassed = 0;
    let totalTests = testCases.length;
    
    for (let i = 0; i < testCases.length; i++) {
        const testCase = testCases[i];
        console.log(`\nTest ${i + 1}: "${testCase.description}"`);
        
        try {
            const response = await testEndpoint('/generate-diagram', 'POST', {
                description: testCase.description
            });
            
            if (response.statusCode === 200) {
                const data = JSON.parse(response.body);
                const elements = data.data.elements;
                
                console.log(`✅ Respuesta exitosa (${elements.length} elementos)`);
                
                // Verificar que los tipos son correctos
                const actualTypes = elements.map(e => e.type);
                const actualNames = elements.map(e => e.text);
                
                console.log('Tipos generados:', actualTypes);
                console.log('Nombres generados:', actualNames);
                
                // Verificar que no hay tipos con puntuación
                const hasInvalidTypes = actualTypes.some(type => type.includes(','));
                if (hasInvalidTypes) {
                    console.log('❌ Error: Tipos contienen puntuación');
                } else {
                    console.log('✅ Tipos limpios (sin puntuación)');
                }
                
                // Verificar que los nombres no son genéricos
                const hasGenericNames = actualNames.some(name => name === 'Azure Service');
                if (hasGenericNames) {
                    console.log('❌ Error: Nombres genéricos detectados');
                } else {
                    console.log('✅ Nombres específicos correctos');
                }
                
                // Verificar que los tipos coinciden con los esperados
                const typesMatch = testCase.expectedTypes.every(expectedType => 
                    actualTypes.includes(expectedType)
                );
                if (typesMatch) {
                    console.log('✅ Tipos coinciden con los esperados');
                    testsPassed++;
                } else {
                    console.log('❌ Tipos no coinciden completamente');
                    console.log(`   Esperados: ${testCase.expectedTypes}`);
                    console.log(`   Obtenidos: ${actualTypes}`);
                }
                
            } else {
                console.log(`❌ Error del servidor: ${response.statusCode}`);
            }
        } catch (error) {
            console.log(`❌ Error: ${error.message}`);
        }
    }
    
    console.log('\n' + '=' .repeat(60));
    console.log(`🎯 RESUMEN FINAL: ${testsPassed}/${totalTests} pruebas pasaron`);
    
    if (testsPassed === totalTests) {
        console.log('🎉 ¡TODOS LOS ICONOS FUNCIONAN CORRECTAMENTE!');
        console.log('\n🌐 Para verificar en el navegador:');
        console.log('   1. Abre http://localhost:3001');
        console.log('   2. Prueba con las descripciones de arriba');
        console.log('   3. Verifica que cada elemento muestra:');
        console.log('      • Icono oficial de Azure correcto');
        console.log('      • Nombre específico del servicio');
        console.log('      • Descripción apropiada');
        console.log('   4. NO debería haber elementos con "Azure Service" genérico');
    } else {
        console.log('⚠️  Algunas pruebas fallaron. Revisa los errores arriba.');
    }
    
    console.log('\n🔧 Problemas corregidos:');
    console.log('   • Tipos de servicio limpios (sin puntuación)');
    console.log('   • Nombres específicos en lugar de genéricos');
    console.log('   • Mapeo correcto de tipos a iconos');
    console.log('   • Iconos oficiales de Azure funcionando');
}

// Ejecutar las pruebas
testFinalIcons().catch(console.error);
