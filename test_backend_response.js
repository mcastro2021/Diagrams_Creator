#!/usr/bin/env node
/**
 * Script de prueba para verificar la respuesta del backend
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

async function testBackendResponse() {
    console.log('🔍 VERIFICACIÓN DE RESPUESTA DEL BACKEND');
    console.log('=' .repeat(60));
    
    // Test 1: Probar con descripción simple
    try {
        console.log('Test 1: "Dos virtual machines conectadas a una base de datos"');
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: 'Dos virtual machines conectadas a una base de datos'
        });
        
        console.log(`Status: ${response.statusCode}`);
        if (response.statusCode === 200) {
            try {
                const data = JSON.parse(response.body);
                console.log('✅ Respuesta JSON válida');
                console.log('Elementos generados:');
                data.data.elements.forEach((elem, index) => {
                    console.log(`  ${index + 1}. Tipo: ${elem.type}, Texto: ${elem.text}`);
                });
                console.log('Servicios detectados:', data.data.metadata.detectedServices);
            } catch (parseError) {
                console.log('❌ Error parseando JSON:', parseError.message);
                console.log('Respuesta raw:', response.body.substring(0, 200) + '...');
            }
        } else {
            console.log('❌ Error del servidor:', response.body);
        }
    } catch (error) {
        console.log('❌ Error de conexión:', error.message);
    }
    
    console.log('\n' + '-'.repeat(40) + '\n');
    
    // Test 2: Probar con descripción en inglés
    try {
        console.log('Test 2: "Two virtual machines connected to a database"');
        const response = await testEndpoint('/generate-diagram', 'POST', {
            description: 'Two virtual machines connected to a database'
        });
        
        console.log(`Status: ${response.statusCode}`);
        if (response.statusCode === 200) {
            try {
                const data = JSON.parse(response.body);
                console.log('✅ Respuesta JSON válida');
                console.log('Elementos generados:');
                data.data.elements.forEach((elem, index) => {
                    console.log(`  ${index + 1}. Tipo: ${elem.type}, Texto: ${elem.text}`);
                });
                console.log('Servicios detectados:', data.data.metadata.detectedServices);
            } catch (parseError) {
                console.log('❌ Error parseando JSON:', parseError.message);
                console.log('Respuesta raw:', response.body.substring(0, 200) + '...');
            }
        } else {
            console.log('❌ Error del servidor:', response.body);
        }
    } catch (error) {
        console.log('❌ Error de conexión:', error.message);
    }
    
    console.log('\n' + '-'.repeat(40) + '\n');
    
    // Test 3: Verificar que los tipos coinciden con azure-icons-real.js
    console.log('Test 3: Verificando mapeo de tipos');
    const azureIconsReal = require('./azure-icons-real.js');
    
    const testTypes = ['azure-vm', 'azure-sql', 'azure-storage', 'azure-app-service'];
    testTypes.forEach(type => {
        const iconData = azureIconsReal.getAzureIconReal(type);
        console.log(`  ${type}: ${iconData.name} -> ${iconData.path}`);
    });
}

// Ejecutar las pruebas
testBackendResponse().catch(console.error);
