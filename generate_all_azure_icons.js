const fs = require('fs');
const path = require('path');

// Función para obtener todos los archivos SVG de una carpeta recursivamente
function getAllSvgFiles(dir, basePath = '') {
  let svgFiles = [];
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const relativePath = path.join(basePath, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      svgFiles = svgFiles.concat(getAllSvgFiles(fullPath, relativePath));
    } else if (item.endsWith('.svg')) {
      svgFiles.push(relativePath.replace(/\\/g, '/'));
    }
  }
  
  return svgFiles;
}

// Función para extraer el nombre del servicio del nombre del archivo
function extractServiceName(filename) {
  // Remover la extensión .svg
  const nameWithoutExt = filename.replace('.svg', '');
  
  // Extraer el nombre del servicio después del último guión
  const parts = nameWithoutExt.split('-');
  const serviceName = parts.slice(3).join('-'); // Saltar los primeros 3 elementos (número, icon, service)
  
  // Convertir a formato de clave (azure-service-name)
  return `azure-${serviceName.toLowerCase().replace(/\s+/g, '-').replace(/[()]/g, '')}`;
}

// Función para generar un nombre legible
function generateReadableName(filename) {
  const nameWithoutExt = filename.replace('.svg', '');
  const parts = nameWithoutExt.split('-');
  const serviceName = parts.slice(3).join(' ');
  
  // Capitalizar cada palabra
  return serviceName.split(' ').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
  ).join(' ');
}

// Función para determinar la categoría basada en la carpeta
function getCategory(folderPath) {
  const categoryMap = {
    'compute': 'Compute',
    'databases': 'Database',
    'networking': 'Networking',
    'storage': 'Storage',
    'security': 'Security',
    'monitor': 'Monitoring',
    'ai + machine learning': 'AI & ML',
    'analytics': 'Analytics',
    'app services': 'App Services',
    'containers': 'Containers',
    'identity': 'Identity',
    'integration': 'Integration',
    'iot': 'IoT',
    'management + governance': 'Management',
    'web': 'Web',
    'mobile': 'Mobile',
    'blockchain': 'Blockchain',
    'devops': 'DevOps',
    'migrate': 'Migration',
    'mixed reality': 'Mixed Reality',
    'general': 'General'
  };
  
  const firstFolder = folderPath.split('/')[0];
  return categoryMap[firstFolder] || 'Other';
}

// Obtener todos los archivos SVG
const iconsDir = './icons';
const allSvgFiles = getAllSvgFiles(iconsDir);

console.log(`📁 Encontrados ${allSvgFiles.length} iconos SVG`);

// Generar el objeto de iconos
const azureIconsReal = {};

allSvgFiles.forEach(filePath => {
  const serviceKey = extractServiceName(path.basename(filePath));
  const readableName = generateReadableName(path.basename(filePath));
  const category = getCategory(filePath);
  
  azureIconsReal[serviceKey] = {
    name: readableName,
    path: `/icons/${filePath}`,
    color: '#0078D4',
    category: category
  };
});

// Generar el contenido del archivo
const fileContent = `/**
 * Iconos oficiales de Azure - Generados automáticamente
 * Total de iconos: ${allSvgFiles.length}
 * Generado el: ${new Date().toISOString()}
 */

const azureIconsReal = ${JSON.stringify(azureIconsReal, null, 2)};

// Función para obtener el icono real de Azure
function getAzureIconReal(serviceType) {
  return azureIconsReal[serviceType] || {
    name: 'Azure Service',
    path: '/icons/general/10001-icon-service-All-Resources.svg',
    color: '#0078D4',
    category: 'General'
  };
}

// Función para cargar un icono de Azure
async function loadAzureIcon(serviceType) {
  const iconData = getAzureIconReal(serviceType);
  try {
    const response = await fetch(iconData.path);
    if (response.ok) {
      const svgContent = await response.text();
      return { 
        name: iconData.name, 
        svg: svgContent, 
        color: iconData.color,
        category: iconData.category 
      };
    } else {
      throw new Error(\`Failed to load icon: \${response.status} \${response.statusText}\`);
    }
  } catch (error) {
    console.error(\`Error fetching icon \${iconData.path}:\`, error);
    return {
      name: iconData.name,
      svg: \`<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><rect width="32" height="32" rx="4" fill="\${iconData.color}"/><text x="16" y="20" font-family="Segoe UI, sans-serif" font-size="12" fill="white" text-anchor="middle">\${iconData.name.charAt(0)}</text></svg>\`,
      color: iconData.color,
      category: iconData.category
    };
  }
}

// Función para obtener todos los iconos por categoría
function getIconsByCategory() {
  const categories = {};
  Object.entries(azureIconsReal).forEach(([key, icon]) => {
    if (!categories[icon.category]) {
      categories[icon.category] = [];
    }
    categories[icon.category].push({ key, ...icon });
  });
  return categories;
}

// Función para buscar iconos por nombre
function searchIcons(query) {
  const results = [];
  const searchTerm = query.toLowerCase();
  
  Object.entries(azureIconsReal).forEach(([key, icon]) => {
    if (icon.name.toLowerCase().includes(searchTerm) || 
        key.toLowerCase().includes(searchTerm)) {
      results.push({ key, ...icon });
    }
  });
  
  return results;
}

// Exportar funciones si es un módulo
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    azureIconsReal,
    getAzureIconReal,
    loadAzureIcon,
    getIconsByCategory,
    searchIcons
  };
}
`;

// Escribir el archivo
fs.writeFileSync('azure-icons-real.js', fileContent);

console.log('✅ Archivo azure-icons-real.js generado exitosamente');
console.log(`📊 Total de iconos incluidos: ${Object.keys(azureIconsReal).length}`);

// Mostrar estadísticas por categoría
const categories = {};
Object.values(azureIconsReal).forEach(icon => {
  categories[icon.category] = (categories[icon.category] || 0) + 1;
});

console.log('\n📋 Estadísticas por categoría:');
Object.entries(categories).forEach(([category, count]) => {
  console.log(`  ${category}: ${count} iconos`);
});

console.log('\n🎯 Algunos ejemplos de iconos generados:');
const examples = Object.entries(azureIconsReal).slice(0, 10);
examples.forEach(([key, icon]) => {
  console.log(`  ${key}: ${icon.name} (${icon.category})`);
});
