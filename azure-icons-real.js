/**
 * Mapeo de iconos oficiales de Azure
 * Basado en los iconos descargados de Microsoft
 */

const azureIconsReal = {
  'azure-vm': {
    name: 'Virtual Machine',
    path: '/icons/compute/10021-icon-service-Virtual-Machine.svg',
    color: '#0078D4'
  },
  
  'azure-app-service': {
    name: 'App Service',
    path: '/icons/app services/10035-icon-service-App-Services.svg',
    color: '#0078D4'
  },
  
  'azure-sql': {
    name: 'SQL Database',
    path: '/icons/databases/10130-icon-service-SQL-Database.svg',
    color: '#0078D4'
  },
  
  'azure-storage': {
    name: 'Storage Account',
    path: '/icons/storage/10086-icon-service-Storage-Accounts.svg',
    color: '#0078D4'
  },
  
  'azure-vnet': {
    name: 'Virtual Network',
    path: '/icons/networking/10061-icon-service-Virtual-Networks.svg',
    color: '#0078D4'
  },
  
  'azure-load-balancer': {
    name: 'Load Balancer',
    path: '/icons/networking/10062-icon-service-Load-Balancers.svg',
    color: '#0078D4'
  },
  
  'azure-redis': {
    name: 'Redis Cache',
    path: '/icons/databases/10137-icon-service-Cache-Redis.svg',
    color: '#DC382D'
  },
  
  'azure-service-bus': {
    name: 'Service Bus',
    path: '/icons/integration/10836-icon-service-Azure-Service-Bus.svg',
    color: '#0078D4'
  },
  
  'azure-functions': {
    name: 'Azure Functions',
    path: '/icons/compute/10029-icon-service-Function-Apps.svg',
    color: '#0078D4'
  },
  
  'azure-cosmos': {
    name: 'Cosmos DB',
    path: '/icons/databases/10121-icon-service-Azure-Cosmos-DB.svg',
    color: '#0078D4'
  },
  
  'azure-key-vault': {
    name: 'Key Vault',
    path: '/icons/security/10245-icon-service-Key-Vaults.svg',
    color: '#0078D4'
  },
  
  'azure-monitor': {
    name: 'Application Insights',
    path: '/icons/monitor/00012-icon-service-Application-Insights.svg',
    color: '#0078D4'
  }
};

// Función para obtener el icono real de Azure
function getAzureIconReal(serviceType) {
  return azureIconsReal[serviceType] || {
    name: 'Azure Service',
    path: '/icons/general/10001-icon-service-All-Resources.svg',
    color: '#0078D4'
  };
}

// Función para cargar el contenido SVG del icono
async function loadAzureIcon(serviceType) {
  const iconData = getAzureIconReal(serviceType);
  
  try {
    const response = await fetch(iconData.path);
    if (response.ok) {
      const svgContent = await response.text();
      return {
        name: iconData.name,
        svg: svgContent,
        color: iconData.color
      };
    } else {
      // Fallback a icono SVG básico si no se puede cargar
      return {
        name: iconData.name,
        svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="3" y="4" width="18" height="16" rx="2" fill="${iconData.color}" stroke="${iconData.color}" stroke-width="1"/>
          <rect x="5" y="6" width="14" height="12" fill="white"/>
          <text x="12" y="14" text-anchor="middle" font-family="Arial" font-size="8" fill="${iconData.color}">${iconData.name}</text>
        </svg>`,
        color: iconData.color
      };
    }
  } catch (error) {
    console.error('Error loading icon:', error);
    // Fallback a icono SVG básico
    return {
      name: iconData.name,
      svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="4" width="18" height="16" rx="2" fill="${iconData.color}" stroke="${iconData.color}" stroke-width="1"/>
        <rect x="5" y="6" width="14" height="12" fill="white"/>
        <text x="12" y="14" text-anchor="middle" font-family="Arial" font-size="8" fill="${iconData.color}">${iconData.name}</text>
      </svg>`,
      color: iconData.color
    };
  }
}

// Exportar para uso en el navegador
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { azureIconsReal, getAzureIconReal, loadAzureIcon };
} else {
  window.azureIconsReal = azureIconsReal;
  window.getAzureIconReal = getAzureIconReal;
  window.loadAzureIcon = loadAzureIcon;
}
