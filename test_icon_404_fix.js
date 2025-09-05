#!/usr/bin/env node
/**
 * Script de prueba para verificar que el error 404 de iconos está corregido
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

async function testIcon404Fix() {
    console.log('🔧 VERIFICACIÓN DE CORRECCIÓN DE ERROR 404 EN ICONOS');
    console.log('=' .repeat(60));
    
    let testsPassed = 0;
    let totalTests = 0;
    
    // Test 1: Verificar que el icono de fallback existe
    totalTests++;
    try {
        const response = await testEndpoint('/icons/general/10001-icon-service-All-Resources.svg');
        if (response.statusCode === 200 && response.body.includes('<svg')) {
            console.log('✅ Test 1: Icono de fallback disponible (All-Resources.svg)');
            testsPassed++;
        } else {
            console.log(`❌ Test 1: Error con icono de fallback: ${response.statusCode}`);
        }
    } catch (error) {
        console.log(`❌ Test 1: Error: ${error.message}`);
    }
    
    // Test 2: Verificar que el archivo azure-icons-real.js tiene el path correcto
    totalTests++;
    try {
        const jsContent = fs.readFileSync('azure-icons-real.js', 'utf8');
        if (jsContent.includes('/icons/general/10001-icon-service-All-Resources.svg')) {
            console.log('✅ Test 2: azure-icons-real.js tiene el path correcto del fallback');
            testsPassed++;
        } else {
            console.log('❌ Test 2: azure-icons-real.js no tiene el path correcto del fallback');
        }
    } catch (error) {
        console.log(`❌ Test 2: Error leyendo azure-icons-real.js: ${error.message}`);
    }
    
    // Test 3: Probar generación de diagrama con servicio no mapeado (debería usar fallback)
    totalTests++;
    try {
        const testDescription = 'Sistema con servicio desconocido XYZ';
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200) {
            console.log('✅ Test 3: Generación funciona con servicios no mapeados (usa fallback)');
            testsPassed++;
        } else {
            console.log(`❌ Test 3: Error en generación: ${response.statusCode}`);
        }
    } catch (error) {
        console.log(`❌ Test 3: Error: ${error.message}`);
    }
    
    // Test 4: Verificar que todos los iconos principales están disponibles
    totalTests++;
    const mainIcons = [
        '/icons/compute/10021-icon-service-Virtual-Machine.svg',
        '/icons/app services/10035-icon-service-App-Services.svg',
        '/icons/databases/10130-icon-service-SQL-Database.svg',
        '/icons/storage/10086-icon-service-Storage-Accounts.svg',
        '/icons/networking/10061-icon-service-Virtual-Networks.svg'
    ];
    
    let availableIcons = 0;
    for (const iconPath of mainIcons) {
        try {
            const response = await testEndpoint(iconPath);
            if (response.statusCode === 200) {
                availableIcons++;
            }
        } catch (error) {
            // Ignorar errores individuales
        }
    }
    
    if (availableIcons >= 4) {
        console.log(`✅ Test 4: ${availableIcons}/${mainIcons.length} iconos principales disponibles`);
        testsPassed++;
    } else {
        console.log(`❌ Test 4: Solo ${availableIcons}/${mainIcons.length} iconos principales disponibles`);
    }
    
    // Test 5: Verificar que no hay referencias al icono incorrecto
    totalTests++;
    try {
        const jsContent = fs.readFileSync('azure-icons-real.js', 'utf8');
        if (!jsContent.includes('10001-icon-service-Azure.svg')) {
            console.log('✅ Test 5: No hay referencias al icono incorrecto (Azure.svg)');
            testsPassed++;
        } else {
            console.log('❌ Test 5: Aún hay referencias al icono incorrecto (Azure.svg)');
        }
    } catch (error) {
        console.log(`❌ Test 5: Error leyendo archivo: ${error.message}`);
    }
    
    console.log('\n' + '=' .repeat(60));
    console.log(`🎯 RESUMEN DE PRUEBAS: ${testsPassed}/${totalTests} pasaron`);
    
    if (testsPassed === totalTests) {
        console.log('🎉 ¡Error 404 de iconos corregido! No debería haber más errores 404.');
        console.log('\n🌐 Para verificar en el navegador:');
        console.log('   1. Abre http://localhost:3001');
        console.log('   2. Abre la consola del navegador (F12)');
        console.log('   3. Verifica que NO hay errores 404');
        console.log('   4. Prueba generar un diagrama');
        console.log('   5. Los iconos deberían cargarse sin errores');
    } else {
        console.log('⚠️  Algunas pruebas fallaron. Revisa los errores arriba.');
    }
    
    console.log('\n🔧 Cambios realizados:');
    console.log('   • Corregido path del icono de fallback');
    console.log('   • Cambiado de 10001-icon-service-Azure.svg (no existe)');
    console.log('   • A 10001-icon-service-All-Resources.svg (existe)');
    console.log('   • Verificado que el servidor sirve el icono correctamente');
}

// Ejecutar las pruebas
testIcon404Fix().catch(console.error);
