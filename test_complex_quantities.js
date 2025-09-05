#!/usr/bin/env node
/**
 * Script de prueba para verificar la detección de cantidades complejas
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

async function testComplexQuantities() {
    console.log('🔢 PRUEBAS DE CANTIDADES COMPLEJAS');
    console.log('=' .repeat(60));
    
    const testCases = [
        {
            description: 'cinco virtual machines conectadas a una base de datos y tres virtual machines mas conectadas a otra base de datos',
            expectedVMs: 8, // 5 + 3
            expectedDBs: 2, // una + otra
            expectedTotal: 10 // 8 VMs + 2 DBs
        },
        {
            description: 'dos virtual machines conectadas a una base de datos',
            expectedVMs: 2,
            expectedDBs: 1,
            expectedTotal: 3
        },
        {
            description: 'tres virtual machines en una red virtual con balanceador de carga',
            expectedVMs: 3,
            expectedVNet: 1,
            expectedLB: 1,
            expectedTotal: 5
        },
        {
            description: 'cuatro virtual machines con Redis Cache y Service Bus',
            expectedVMs: 4,
            expectedRedis: 1,
            expectedSB: 1,
            expectedTotal: 6
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
                console.log(`📊 Total elementos: ${elements.length} (esperados: ${testCase.expectedTotal})`);
                console.log(`🔗 Conexiones: ${connections.length}`);
                
                // Contar elementos por tipo
                const elementCounts = {};
                elements.forEach(element => {
                    elementCounts[element.type] = (elementCounts[element.type] || 0) + 1;
                });
                
                console.log('📋 Elementos por tipo:');
                Object.entries(elementCounts).forEach(([type, count]) => {
                    console.log(`  ${type}: ${count}`);
                });
                
                // Verificar cantidades específicas
                let testPassed = true;
                
                if (testCase.expectedVMs) {
                    const vmCount = elementCounts['azure-vm'] || 0;
                    const vmCorrect = vmCount === testCase.expectedVMs;
                    console.log(`✅ VMs: ${vmCount} (esperadas: ${testCase.expectedVMs}) ${vmCorrect ? 'CORRECTO' : 'INCORRECTO'}`);
                    if (!vmCorrect) testPassed = false;
                }
                
                if (testCase.expectedDBs) {
                    const dbCount = elementCounts['azure-sql'] || 0;
                    const dbCorrect = dbCount === testCase.expectedDBs;
                    console.log(`✅ DBs: ${dbCount} (esperadas: ${testCase.expectedDBs}) ${dbCorrect ? 'CORRECTO' : 'INCORRECTO'}`);
                    if (!dbCorrect) testPassed = false;
                }
                
                if (testCase.expectedVNet) {
                    const vnetCount = elementCounts['azure-vnet'] || 0;
                    const vnetCorrect = vnetCount === testCase.expectedVNet;
                    console.log(`✅ VNets: ${vnetCount} (esperadas: ${testCase.expectedVNet}) ${vnetCorrect ? 'CORRECTO' : 'INCORRECTO'}`);
                    if (!vnetCorrect) testPassed = false;
                }
                
                if (testCase.expectedLB) {
                    const lbCount = elementCounts['azure-load-balancer'] || 0;
                    const lbCorrect = lbCount === testCase.expectedLB;
                    console.log(`✅ LBs: ${lbCount} (esperados: ${testCase.expectedLB}) ${lbCorrect ? 'CORRECTO' : 'INCORRECTO'}`);
                    if (!lbCorrect) testPassed = false;
                }
                
                if (testCase.expectedRedis) {
                    const redisCount = elementCounts['azure-redis'] || 0;
                    const redisCorrect = redisCount === testCase.expectedRedis;
                    console.log(`✅ Redis: ${redisCount} (esperados: ${testCase.expectedRedis}) ${redisCorrect ? 'CORRECTO' : 'INCORRECTO'}`);
                    if (!redisCorrect) testPassed = false;
                }
                
                if (testCase.expectedSB) {
                    const sbCount = elementCounts['azure-service-bus'] || 0;
                    const sbCorrect = sbCount === testCase.expectedSB;
                    console.log(`✅ Service Bus: ${sbCount} (esperados: ${testCase.expectedSB}) ${sbCorrect ? 'CORRECTO' : 'INCORRECTO'}`);
                    if (!sbCorrect) testPassed = false;
                }
                
                // Verificar total
                const totalCorrect = elements.length === testCase.expectedTotal;
                console.log(`✅ Total: ${elements.length} (esperado: ${testCase.expectedTotal}) ${totalCorrect ? 'CORRECTO' : 'INCORRECTO'}`);
                if (!totalCorrect) testPassed = false;
                
                if (testPassed) {
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
        console.log('🎉 ¡TODAS LAS CANTIDADES COMPLEJAS FUNCIONAN CORRECTAMENTE!');
        console.log('\n🌐 Para verificar en el navegador:');
        console.log('   1. Abre http://localhost:3001');
        console.log('   2. Prueba con las descripciones de arriba');
        console.log('   3. Verifica que:');
        console.log('      • Se generan las cantidades correctas de elementos');
        console.log('      • Las conexiones son lógicas entre todos los elementos');
        console.log('      • Los elementos múltiples se conectan correctamente');
    } else {
        console.log('⚠️  Algunas pruebas fallaron. Revisa los errores arriba.');
    }
    
    console.log('\n🔧 Mejoras implementadas:');
    console.log('   • Detección de cantidades con patrones específicos');
    console.log('   • Soporte para múltiples grupos de elementos');
    console.log('   • Mapeo directo de tipos de servicio');
    console.log('   • Generación de cantidades exactas');
    console.log('   • Conexiones inteligentes entre todos los elementos');
}

// Ejecutar las pruebas
testComplexQuantities().catch(console.error);
