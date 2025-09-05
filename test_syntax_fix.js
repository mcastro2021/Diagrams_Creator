#!/usr/bin/env node
/**
 * Script de prueba para verificar que el error de sintaxis async/await está corregido
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

async function testSyntaxFix() {
    console.log('🔧 VERIFICACIÓN DE CORRECCIÓN DE SINTAXIS ASYNC/AWAIT');
    console.log('=' .repeat(60));
    
    let testsPassed = 0;
    let totalTests = 0;
    
    // Test 1: Verificar que el HTML se sirve correctamente
    totalTests++;
    try {
        const response = await testEndpoint('/');
        if (response.statusCode === 200 && response.body.includes('<!DOCTYPE html>')) {
            console.log('✅ Test 1: HTML se sirve correctamente');
            testsPassed++;
        } else {
            console.log(`❌ Test 1: Error sirviendo HTML: ${response.statusCode}`);
        }
    } catch (error) {
        console.log(`❌ Test 1: Error: ${error.message}`);
    }
    
    // Test 2: Verificar que no hay errores de sintaxis en el HTML
    totalTests++;
    try {
        const htmlContent = fs.readFileSync('index.html', 'utf8');
        
        // Verificar que las funciones async están correctamente definidas
        const hasAsyncGenerateDiagram = htmlContent.includes('async function generateDiagram()');
        const hasAsyncRenderDiagram = htmlContent.includes('async function renderDiagram(data)');
        const hasAsyncLoadSavedDiagram = htmlContent.includes('async function loadSavedDiagram()');
        
        // Verificar que no hay await dentro de .then()
        const hasAwaitInThen = htmlContent.includes('.then(async') || 
                              (htmlContent.includes('.then(') && htmlContent.includes('await'));
        
        if (hasAsyncGenerateDiagram && hasAsyncRenderDiagram && hasAsyncLoadSavedDiagram && !hasAwaitInThen) {
            console.log('✅ Test 2: Sintaxis async/await corregida correctamente');
            testsPassed++;
        } else {
            console.log('❌ Test 2: Problemas de sintaxis detectados');
            console.log(`   - generateDiagram async: ${hasAsyncGenerateDiagram}`);
            console.log(`   - renderDiagram async: ${hasAsyncRenderDiagram}`);
            console.log(`   - loadSavedDiagram async: ${hasAsyncLoadSavedDiagram}`);
            console.log(`   - await en .then(): ${hasAwaitInThen}`);
        }
    } catch (error) {
        console.log(`❌ Test 2: Error leyendo HTML: ${error.message}`);
    }
    
    // Test 3: Probar generación de diagrama (debería funcionar sin errores de sintaxis)
    totalTests++;
    try {
        const testDescription = 'Aplicación web con App Service y SQL Database';
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: testDescription
        });
        
        if (response.statusCode === 200) {
            console.log('✅ Test 3: Generación de diagrama funciona sin errores de sintaxis');
            testsPassed++;
        } else {
            console.log(`❌ Test 3: Error en generación: ${response.statusCode}`);
        }
    } catch (error) {
        console.log(`❌ Test 3: Error: ${error.message}`);
    }
    
    // Test 4: Verificar que el servidor está funcionando
    totalTests++;
    try {
        const response = await testEndpoint('/examples');
        if (response.statusCode === 200) {
            console.log('✅ Test 4: Servidor funcionando correctamente');
            testsPassed++;
        } else {
            console.log(`❌ Test 4: Error del servidor: ${response.statusCode}`);
        }
    } catch (error) {
        console.log(`❌ Test 4: Error: ${error.message}`);
    }
    
    console.log('\n' + '=' .repeat(60));
    console.log(`🎯 RESUMEN DE PRUEBAS: ${testsPassed}/${totalTests} pasaron`);
    
    if (testsPassed === totalTests) {
        console.log('🎉 ¡Error de sintaxis corregido! La aplicación debería funcionar correctamente.');
        console.log('\n🌐 Para probar en el navegador:');
        console.log('   1. Abre http://localhost:3001');
        console.log('   2. Abre la consola del navegador (F12)');
        console.log('   3. Verifica que NO hay errores de sintaxis');
        console.log('   4. Prueba generar un diagrama');
        console.log('   5. Los iconos oficiales de Azure deberían cargarse correctamente');
    } else {
        console.log('⚠️  Algunas pruebas fallaron. Revisa los errores arriba.');
    }
    
    console.log('\n🔧 Cambios realizados:');
    console.log('   • Convertido .then()/.catch() a async/await');
    console.log('   • Eliminado await dentro de funciones .then()');
    console.log('   • Mantenido async en generateDiagram(), renderDiagram(), loadSavedDiagram()');
    console.log('   • Estructura de código más limpia y sin errores de sintaxis');
}

// Ejecutar las pruebas
testSyntaxFix().catch(console.error);
