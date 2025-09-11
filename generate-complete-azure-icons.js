const fs = require('fs');
const path = require('path');

// Función para convertir nombre de archivo a nombre de servicio
function filenameToServiceName(filename) {
  // Remover prefijo numérico y extensiones
  let name = filename
    .replace(/^\d+-icon-service-/, '')
    .replace(/\.svg$/, '')
    .replace(/[()]/g, '')
    .replace(/\s+/g, '-')
    .toLowerCase();
  
  // Mapeos especiales
  const specialMappings = {
    'machine-learning-studio-classic-web-services': 'machine-learning-studio-classic',
    'log-analytics-workspaces': 'log-analytics',
    'stream-analytics-jobs': 'stream-analytics',
    'azure-synapse-analytics': 'synapse-analytics',
    'power-bi-embedded': 'power-bi-embedded',
    'power-platform': 'power-platform',
    'data-factories': 'data-factory',
    'hd-insight-clusters': 'hd-insight',
    'data-lake-analytics': 'data-lake-analytics',
    'azure-data-explorer-clusters': 'data-explorer',
    'analysis-services': 'analysis-services',
    'event-hub-clusters': 'event-hub-clusters',
    'data-lake-store-gen1': 'data-lake-store',
    'azure-databricks': 'databricks',
    'app-service-plans': 'app-service-plan',
    'app-service-certificates': 'app-service-certificate',
    'app-service-domains': 'app-service-domain',
    'cdn-profiles': 'cdn-profile',
    'cognitive-search': 'cognitive-search',
    'notification-hubs': 'notification-hub',
    'app-service-environments': 'app-service-environment',
    'app-services': 'app-service'
  };
  
  return specialMappings[name] || name;
}

// Función para obtener categoría basada en la carpeta
function getCategoryFromFolder(folderName) {
  const categoryMap = {
    'ai + machine learning': 'AI & ML',
    'analytics': 'Analytics',
    'app services': 'App Services',
    'azure ecosystem': 'Azure Ecosystem',
    'azure stack': 'Azure Stack',
    'blockchain': 'Blockchain',
    'compute': 'Compute',
    'containers': 'Containers',
    'databases': 'Databases',
    'devops': 'DevOps',
    'general': 'General',
    'hybrid + multicloud': 'Hybrid & Multicloud',
    'identity': 'Identity',
    'integration': 'Integration',
    'intune': 'Intune',
    'iot': 'IoT',
    'management + governance': 'Management & Governance',
    'menu': 'Menu',
    'migrate': 'Migrate',
    'migration': 'Migration',
    'mixed reality': 'Mixed Reality',
    'mobile': 'Mobile',
    'monitor': 'Monitor',
    'networking': 'Networking',
    'new icons': 'New Icons',
    'other': 'Other',
    'security': 'Security',
    'storage': 'Storage',
    'web': 'Web'
  };
  
  return categoryMap[folderName] || 'Other';
}

// Función para obtener color basado en categoría
function getColorFromCategory(category) {
  const colorMap = {
    'AI & ML': '#0078D4',
    'Analytics': '#0078D4',
    'App Services': '#0078D4',
    'Azure Ecosystem': '#0078D4',
    'Azure Stack': '#0078D4',
    'Blockchain': '#0078D4',
    'Compute': '#0078D4',
    'Containers': '#0078D4',
    'Databases': '#0078D4',
    'DevOps': '#0078D4',
    'General': '#0078D4',
    'Hybrid & Multicloud': '#0078D4',
    'Identity': '#0078D4',
    'Integration': '#0078D4',
    'Intune': '#0078D4',
    'IoT': '#0078D4',
    'Management & Governance': '#0078D4',
    'Menu': '#0078D4',
    'Migrate': '#0078D4',
    'Migration': '#0078D4',
    'Mixed Reality': '#0078D4',
    'Mobile': '#0078D4',
    'Monitor': '#0078D4',
    'Networking': '#0078D4',
    'New Icons': '#0078D4',
    'Other': '#0078D4',
    'Security': '#0078D4',
    'Storage': '#0078D4',
    'Web': '#0078D4'
  };
  
  return colorMap[category] || '#0078D4';
}

// Función para obtener nombre legible
function getReadableName(filename) {
  let name = filename
    .replace(/^\d+-icon-service-/, '')
    .replace(/\.svg$/, '')
    .replace(/[()]/g, '')
    .replace(/-/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
  
  return name;
}

// Función principal
function generateCompleteAzureIcons() {
  const iconsDir = path.join(__dirname, 'Icons');
  const azureIcons = {};
  
  // Leer todas las carpetas
  const folders = fs.readdirSync(iconsDir, { withFileTypes: true })
    .filter(dirent => dirent.isDirectory())
    .map(dirent => dirent.name);
  
  folders.forEach(folder => {
    const folderPath = path.join(iconsDir, folder);
    const files = fs.readdirSync(folderPath)
      .filter(file => file.endsWith('.svg'));
    
    files.forEach(file => {
      const serviceName = filenameToServiceName(file);
      const category = getCategoryFromFolder(folder);
      const color = getColorFromCategory(category);
      const readableName = getReadableName(file);
      
      azureIcons[`azure-${serviceName}`] = {
        name: readableName,
        path: `/icons/${folder}/${file}`,
        color: color,
        category: category
      };
    });
  });
  
  return azureIcons;
}

// Generar el archivo
const completeIcons = generateCompleteAzureIcons();
const output = `// Azure Icons Complete Mapping - Generated automatically
const azureIconsComplete = ${JSON.stringify(completeIcons, null, 2)};

// Make it globally available
if (typeof window !== 'undefined') {
  window.azureIconsComplete = azureIconsComplete;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = azureIconsComplete;
}`;

fs.writeFileSync('azure-icons-complete.js', output);
console.log(`Generated azure-icons-complete.js with ${Object.keys(completeIcons).length} icons`);
console.log('Categories:', [...new Set(Object.values(completeIcons).map(icon => icon.category))]);
