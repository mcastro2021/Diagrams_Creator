#!/usr/bin/env node
/**
 * Script de prueba para verificar las conexiones mejoradas
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

async function testImprovedConnections() {
    console.log('🔗 PRUEBAS DE CONEXIONES MEJORADAS');
    console.log('=' .repeat(60));
    
    const testCases = [
        {
            description: 'Tres virtual machines conectadas a una base de datos',
            expectedElements: 4, // 3 VMs + 1 DB
            expectedConnections: 3, // Cada VM conectada a la DB
            expectedConnectionLabels: ['Database Access']
        },
        {
            description: 'Dos virtual machines en una red virtual con balanceador de carga',
            expectedElements: 4, // 2 VMs + 1 VNet + 1 LB
            expectedConnections: 5, // LB→VM1, LB→VM2, VM1→VNet, VM2→VNet, LB→VNet
            expectedConnectionLabels: ['Load Distribution', 'Network Connection']
        },
        {
            description: 'Aplicación web con App Service, SQL Database y Storage Account',
            expectedElements: 3, // 1 App Service + 1 DB + 1 Storage
            expectedConnections: 2, // App Service → DB, App Service → Storage
            expectedConnectionLabels: ['Data Access', 'File Storage']
        },
        {
            description: 'Cuatro virtual machines con Redis Cache y Service Bus',
            expectedElements: 6, // 4 VMs + 1 Redis + 1 Service Bus
            expectedConnections: 4, // Service Bus → VM1, VM2, VM3, VM4
            expectedConnectionLabels: ['Message Queue']
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
                const connections = data.data.connections;
                
                console.log(`✅ Respuesta exitosa`);
                console.log(`📊 Elementos: ${elements.length} (esperados: ${testCase.expectedElements})`);
                console.log(`🔗 Conexiones: ${connections.length} (esperadas: ${testCase.expectedConnections})`);
                
                // Mostrar elementos generados
                console.log('📋 Elementos generados:');
                elements.forEach((elem, index) => {
                    console.log(`  ${index + 1}. ${elem.text} (${elem.type})`);
                });
                
                // Mostrar conexiones generadas
                console.log('🔗 Conexiones generadas:');
                connections.forEach((conn, index) => {
                    const source = elements.find(e => e.id === conn.source);
                    const target = elements.find(e => e.id === conn.target);
                    console.log(`  ${index + 1}. ${source?.text} → ${target?.text} (${conn.label})`);
                });
                
                // Verificar cantidad de elementos
                const elementsMatch = elements.length >= testCase.expectedElements;
                console.log(`✅ Elementos: ${elementsMatch ? 'CORRECTO' : 'INCORRECTO'}`);
                
                // Verificar cantidad de conexiones
                const connectionsMatch = connections.length >= testCase.expectedConnections;
                console.log(`✅ Conexiones: ${connectionsMatch ? 'CORRECTO' : 'INCORRECTO'}`);
                
                // Verificar etiquetas de conexión
                const connectionLabels = connections.map(c => c.label);
                const labelsMatch = testCase.expectedConnectionLabels.some(expectedLabel => 
                    connectionLabels.includes(expectedLabel)
                );
                console.log(`✅ Etiquetas: ${labelsMatch ? 'CORRECTO' : 'INCORRECTO'}`);
                
                if (elementsMatch && connectionsMatch && labelsMatch) {
                    testsPassed++;
                    console.log('🎉 Test PASÓ');
                } else {
                    console.log('❌ Test FALLÓ');
                }
                
            } else {
                console.log(`❌ Error del servidor: ${response.statusCode}`);
            }
        } catch (error) {
            console.log(`❌ Error: ${error.message}`);
        }
    }
    
    console.log('\n' + '=' .repeat(60));
    console.log(`🎯 RESUMEN: ${testsPassed}/${totalTests} pruebas pasaron`);
    
    if (testsPassed === totalTests) {
        console.log('🎉 ¡TODAS LAS CONEXIONES FUNCIONAN CORRECTAMENTE!');
        console.log('\n🌐 Para verificar en el navegador:');
        console.log('   1. Abre http://localhost:3001');
        console.log('   2. Prueba con las descripciones de arriba');
        console.log('   3. Verifica que:');
        console.log('      • Se generan la cantidad correcta de elementos');
        console.log('      • Las conexiones son lógicas y claras');
        console.log('      • Las etiquetas de conexión son descriptivas');
        console.log('      • Los elementos múltiples se conectan correctamente');
    } else {
        console.log('⚠️  Algunas pruebas fallaron. Revisa los errores arriba.');
    }
    
    console.log('\n🔧 Mejoras implementadas:');
    console.log('   • Detección de cantidades (dos, tres, cuatro, etc.)');
    console.log('   • Generación de múltiples elementos del mismo tipo');
    console.log('   • Conexiones inteligentes basadas en patrones');
    console.log('   • Conexiones contextuales para múltiples elementos');
    console.log('   • Etiquetas descriptivas para cada conexión');
    console.log('   • Agrupación lógica de elementos por tipo');
}

// Ejecutar las pruebas
testImprovedConnections().catch(console.error);
