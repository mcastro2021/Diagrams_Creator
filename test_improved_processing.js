#!/usr/bin/env node
/**
 * Script de prueba para verificar el procesamiento mejorado de lenguaje natural
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

async function testImprovedProcessing() {
    console.log('🧠 PRUEBAS DE PROCESAMIENTO MEJORADO');
    console.log('=' .repeat(60));
    
    let testsPassed = 0;
    let totalTests = 0;
    
    // Test 1: Descripción específica con servicios Azure
    totalTests++;
    try {
        const testDescription = 'Necesito una aplicación web con App Service, SQL Database y Storage Account para archivos';
        console.log(`\n🔍 Test 1: "${testDescription}"`);
        
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log(`✅ Test 1: Generación exitosa`);
            console.log(`   🎨 Elementos: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones: ${data.metadata.totalConnections}`);
            console.log(`   🏷️  Servicios: ${data.metadata.detectedServices.join(', ')}`);
            
            // Verificar que se detectaron los servicios específicos
            const expectedServices = ['azure-app-service', 'azure-sql', 'azure-storage'];
            const detectedServices = data.metadata.detectedServices;
            const hasExpectedServices = expectedServices.every(service => detectedServices.includes(service));
            
            if (hasExpectedServices) {
                console.log(`   ✅ Servicios específicos detectados correctamente`);
                testsPassed++;
            } else {
                console.log(`   ⚠️  Servicios detectados: ${detectedServices.join(', ')}`);
            }
        } else {
            console.log(`❌ Test 1: Error en generación`);
        }
    } catch (error) {
        console.log(`❌ Test 1: Error: ${error.message}`);
    }
    
    // Test 2: Descripción en español con términos técnicos
    totalTests++;
    try {
        const testDescription = 'Sistema de microservicios con Redis Cache, Service Bus para mensajería y Application Insights para monitoreo';
        console.log(`\n🔍 Test 2: "${testDescription}"`);
        
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log(`✅ Test 2: Generación exitosa`);
            console.log(`   🎨 Elementos: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones: ${data.metadata.totalConnections}`);
            console.log(`   🏷️  Servicios: ${data.metadata.detectedServices.join(', ')}`);
            
            // Verificar que se detectaron los servicios específicos
            const expectedServices = ['azure-redis', 'azure-service-bus', 'azure-monitor'];
            const detectedServices = data.metadata.detectedServices;
            const hasExpectedServices = expectedServices.every(service => detectedServices.includes(service));
            
            if (hasExpectedServices) {
                console.log(`   ✅ Servicios de microservicios detectados correctamente`);
                testsPassed++;
            } else {
                console.log(`   ⚠️  Servicios detectados: ${detectedServices.join(', ')}`);
            }
        } else {
            console.log(`❌ Test 2: Error en generación`);
        }
    } catch (error) {
        console.log(`❌ Test 2: Error: ${error.message}`);
    }
    
    // Test 3: Descripción genérica que debería inferir servicios
    totalTests++;
    try {
        const testDescription = 'Sistema de gestión de usuarios con base de datos y almacenamiento de archivos';
        console.log(`\n🔍 Test 3: "${testDescription}"`);
        
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log(`✅ Test 3: Generación exitosa`);
            console.log(`   🎨 Elementos: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones: ${data.metadata.totalConnections}`);
            console.log(`   🏷️  Servicios: ${data.metadata.detectedServices.join(', ')}`);
            
            // Verificar que se detectaron servicios básicos
            const detectedServices = data.metadata.detectedServices;
            if (detectedServices.length >= 2) {
                console.log(`   ✅ Servicios inferidos correctamente`);
                testsPassed++;
            } else {
                console.log(`   ⚠️  Pocos servicios detectados: ${detectedServices.length}`);
            }
        } else {
            console.log(`❌ Test 3: Error en generación`);
        }
    } catch (error) {
        console.log(`❌ Test 3: Error: ${error.message}`);
    }
    
    // Test 4: Descripción con términos de AWS que debería mapear a Azure
    totalTests++;
    try {
        const testDescription = 'Aplicación serverless con Lambda functions, RDS database y S3 storage';
        console.log(`\n🔍 Test 4: "${testDescription}"`);
        
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log(`✅ Test 4: Generación exitosa`);
            console.log(`   🎨 Elementos: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones: ${data.metadata.totalConnections}`);
            console.log(`   🏷️  Servicios: ${data.metadata.detectedServices.join(', ')}`);
            
            // Verificar que se detectaron servicios equivalentes
            const detectedServices = data.metadata.detectedServices;
            if (detectedServices.length >= 2) {
                console.log(`   ✅ Servicios equivalentes detectados`);
                testsPassed++;
            } else {
                console.log(`   ⚠️  Pocos servicios detectados: ${detectedServices.length}`);
            }
        } else {
            console.log(`❌ Test 4: Error en generación`);
        }
    } catch (error) {
        console.log(`❌ Test 4: Error: ${error.message}`);
    }
    
    // Test 5: Descripción muy específica con múltiples servicios
    totalTests++;
    try {
        const testDescription = 'Arquitectura completa con Virtual Machines, App Service, SQL Database, Storage Account, Redis Cache, Service Bus, Azure Functions, Cosmos DB, Key Vault y Application Insights';
        console.log(`\n🔍 Test 5: "${testDescription}"`);
        
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log(`✅ Test 5: Generación exitosa`);
            console.log(`   🎨 Elementos: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones: ${data.metadata.totalConnections}`);
            console.log(`   🏷️  Servicios: ${data.metadata.detectedServices.join(', ')}`);
            
            // Verificar que se detectaron múltiples servicios
            const detectedServices = data.metadata.detectedServices;
            if (detectedServices.length >= 8) {
                console.log(`   ✅ Múltiples servicios detectados correctamente`);
                testsPassed++;
            } else {
                console.log(`   ⚠️  Pocos servicios detectados: ${detectedServices.length}`);
            }
        } else {
            console.log(`❌ Test 5: Error en generación`);
        }
    } catch (error) {
        console.log(`❌ Test 5: Error: ${error.message}`);
    }
    
    // Test 6: Descripción con términos técnicos específicos
    totalTests++;
    try {
        const testDescription = 'Sistema de procesamiento de datos con NoSQL database, message queues y distributed caching';
        console.log(`\n🔍 Test 6: "${testDescription}"`);
        
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200 && response.body.success) {
            const data = response.body.data;
            console.log(`✅ Test 6: Generación exitosa`);
            console.log(`   🎨 Elementos: ${data.metadata.totalElements}`);
            console.log(`   🔗 Conexiones: ${data.metadata.totalConnections}`);
            console.log(`   🏷️  Servicios: ${data.metadata.detectedServices.join(', ')}`);
            
            // Verificar que se detectaron servicios específicos
            const detectedServices = data.metadata.detectedServices;
            if (detectedServices.length >= 2) {
                console.log(`   ✅ Servicios técnicos detectados`);
                testsPassed++;
            } else {
                console.log(`   ⚠️  Pocos servicios detectados: ${detectedServices.length}`);
            }
        } else {
            console.log(`❌ Test 6: Error en generación`);
        }
    } catch (error) {
        console.log(`❌ Test 6: Error: ${error.message}`);
    }
    
    console.log('\n' + '=' .repeat(60));
    console.log(`🎯 RESUMEN DE PRUEBAS: ${testsPassed}/${totalTests} pasaron`);
    
    if (testsPassed === totalTests) {
        console.log('🎉 ¡Todas las pruebas pasaron! El procesamiento mejorado funciona correctamente.');
        console.log('\n🌐 Para probar en la interfaz:');
        console.log('   1. Abre tu navegador en http://localhost:3001');
        console.log('   2. Prueba con estas descripciones:');
        console.log('      • "Aplicación web con App Service, SQL Database y Storage Account"');
        console.log('      • "Sistema de microservicios con Redis Cache y Service Bus"');
        console.log('      • "Arquitectura serverless con Azure Functions y Cosmos DB"');
        console.log('   3. Verifica que los servicios se detectan correctamente');
    } else {
        console.log('⚠️  Algunas pruebas fallaron. Revisa los errores arriba.');
    }
    
    console.log('\n📝 Mejoras implementadas:');
    console.log('   • Reconocimiento de patrones más flexible');
    console.log('   • Análisis por palabras clave y contexto');
    console.log('   • Mapeo de servicios equivalentes (AWS → Azure)');
    console.log('   • Detección inteligente de tipos de aplicación');
    console.log('   • Fallback inteligente para descripciones genéricas');
}

// Ejecutar las pruebas
testImprovedProcessing().catch(console.error);
