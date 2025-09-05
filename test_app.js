#!/usr/bin/env node
/**
 * Script de prueba para la aplicación Azure Diagram Generator
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

async function runTests() {
    console.log('🧪 PRUEBAS DE LA APLICACIÓN AZURE DIAGRAM GENERATOR');
    console.log('=' .repeat(60));
    
    let testsPassed = 0;
    let totalTests = 0;
    
    // Test 1: Servidor responde
    totalTests++;
    try {
        const response = await testEndpoint('/');
        if (response.statusCode === 200) {
            console.log('✅ Test 1: Servidor responde correctamente');
            testsPassed++;
        } else {
            console.log(`❌ Test 1: Servidor responde con código ${response.statusCode}`);
        }
    } catch (error) {
        console.log(`❌ Test 1: Error conectando al servidor: ${error.message}`);
    }
    
    // Test 2: Endpoint de ejemplos
    totalTests++;
    try {
        const response = await testEndpoint('/examples');
        if (response.statusCode === 200 && response.body.success) {
            console.log('✅ Test 2: Endpoint de ejemplos funciona');
            console.log(`   📋 Ejemplos disponibles: ${response.body.examples.length}`);
            testsPassed++;
        } else {
            console.log(`❌ Test 2: Endpoint de ejemplos falló`);
        }
    } catch (error) {
        console.log(`❌ Test 2: Error en endpoint de ejemplos: ${error.message}`);
    }
    
    // Test 3: Generación de diagrama básico
    totalTests++;
    try {
        const testDescription = 'Una aplicación web con base de datos y storage';
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log('✅ Test 3: Generación de diagrama funciona');
            console.log(`   🎨 Elementos generados: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones generadas: ${data.metadata.totalConnections}`);
            console.log(`   🏷️  Servicios detectados: ${data.metadata.detectedServices.join(', ')}`);
            testsPassed++;
        } else {
            console.log(`❌ Test 3: Generación de diagrama falló`);
            console.log(`   Error: ${response.body.error || 'Desconocido'}`);
        }
    } catch (error) {
        console.log(`❌ Test 3: Error en generación de diagrama: ${error.message}`);
    }
    
    // Test 4: Generación con servicios específicos
    totalTests++;
    try {
        const testDescription = 'Arquitectura de microservicios con API Gateway, Service Bus, Redis Cache y Application Insights';
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log('✅ Test 4: Generación con servicios específicos funciona');
            console.log(`   🎨 Elementos generados: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones generadas: ${data.metadata.totalConnections}`);
            console.log(`   🏷️  Servicios detectados: ${data.metadata.detectedServices.join(', ')}`);
            testsPassed++;
        } else {
            console.log(`❌ Test 4: Generación con servicios específicos falló`);
        }
    } catch (error) {
        console.log(`❌ Test 4: Error en generación con servicios específicos: ${error.message}`);
    }
    
    // Test 5: Validación de entrada vacía
    totalTests++;
    try {
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: ''
        });
        
        if (response.statusCode === 400 && !response.body.success) {
            console.log('✅ Test 5: Validación de entrada vacía funciona');
            testsPassed++;
        } else {
            console.log(`❌ Test 5: Validación de entrada vacía falló`);
        }
    } catch (error) {
        console.log(`❌ Test 5: Error en validación de entrada: ${error.message}`);
    }
    
    // Test 6: Generación con descripción en español
    totalTests++;
    try {
        const testDescription = 'Necesito una arquitectura con dos máquinas virtuales, una base de datos SQL y un storage account para archivos';
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log('✅ Test 6: Generación con descripción en español funciona');
            console.log(`   🎨 Elementos generados: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones generadas: ${data.metadata.totalConnections}`);
            testsPassed++;
        } else {
            console.log(`❌ Test 6: Generación con descripción en español falló`);
        }
    } catch (error) {
        console.log(`❌ Test 6: Error en generación con español: ${error.message}`);
    }
    
    console.log('\n' + '=' .repeat(60));
    console.log(`🎯 RESUMEN DE PRUEBAS: ${testsPassed}/${totalTests} pasaron`);
    
    if (testsPassed === totalTests) {
        console.log('🎉 ¡Todas las pruebas pasaron! La aplicación está funcionando correctamente.');
        console.log('\n🌐 Para usar la aplicación:');
        console.log('   1. Abre tu navegador en http://localhost:3001');
        console.log('   2. Escribe una descripción de tu arquitectura Azure');
        console.log('   3. Haz clic en "Generar Diagrama"');
        console.log('   4. ¡Disfruta tu diagrama interactivo!');
    } else {
        console.log('⚠️  Algunas pruebas fallaron. Revisa los errores arriba.');
    }
    
    console.log('\n📝 Funcionalidades disponibles:');
    console.log('   • Generación automática de diagramas desde descripción en lenguaje natural');
    console.log('   • Reconocimiento de servicios Azure en español e inglés');
    console.log('   • Posicionamiento inteligente de elementos');
    console.log('   • Conexiones automáticas basadas en patrones comunes');
    console.log('   • Interfaz web interactiva con elementos arrastrables');
    console.log('   • Exportación y guardado de diagramas');
    console.log('   • Ejemplos predefinidos de arquitecturas');
}

// Ejecutar las pruebas
runTests().catch(console.error);
