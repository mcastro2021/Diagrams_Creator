/**
 * Iconos oficiales de Azure en formato SVG
 * Basados en los diseños oficiales de Microsoft Azure
 */

const azureIconsOfficial = {
  'azure-vm': {
    name: 'Virtual Machine',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="4" width="20" height="16" rx="2" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <rect x="4" y="6" width="16" height="12" fill="white"/>
      <rect x="6" y="8" width="12" height="1" fill="#0078D4"/>
      <rect x="6" y="10" width="8" height="1" fill="#0078D4"/>
      <rect x="6" y="12" width="10" height="1" fill="#0078D4"/>
      <rect x="6" y="14" width="6" height="1" fill="#0078D4"/>
      <circle cx="8" cy="16" r="1" fill="#0078D4"/>
      <circle cx="12" cy="16" r="1" fill="#0078D4"/>
      <circle cx="16" cy="16" r="1" fill="#0078D4"/>
    </svg>`,
    color: '#0078D4'
  },
  
  'azure-app-service': {
    name: 'App Service',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="3" width="20" height="14" rx="2" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <rect x="4" y="5" width="16" height="10" fill="white"/>
      <rect x="6" y="7" width="12" height="1" fill="#0078D4"/>
      <rect x="6" y="9" width="8" height="1" fill="#0078D4"/>
      <rect x="6" y="11" width="10" height="1" fill="#0078D4"/>
      <rect x="6" y="13" width="6" height="1" fill="#0078D4"/>
      <circle cx="8" cy="15" r="1" fill="#0078D4"/>
      <circle cx="12" cy="15" r="1" fill="#0078D4"/>
      <circle cx="16" cy="15" r="1" fill="#0078D4"/>
    </svg>`,
    color: '#0078D4'
  },
  
  'azure-sql': {
    name: 'SQL Database',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="12" cy="6" rx="8" ry="3" fill="#0078D4"/>
      <path d="M4 6v12c0 1.66 3.58 3 8 3s8-1.34 8-3V6" fill="#0078D4"/>
      <ellipse cx="12" cy="18" rx="8" ry="3" fill="#0078D4"/>
      <rect x="8" y="8" width="8" height="8" fill="white" rx="1"/>
      <path d="M10 10h4v1h-4v-1zm0 2h4v1h-4v-1zm0 2h3v1h-3v-1z" fill="#0078D4"/>
    </svg>`,
    color: '#0078D4'
  },
  
  'azure-storage': {
    name: 'Storage Account',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="4" width="20" height="16" rx="2" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <rect x="4" y="6" width="16" height="12" fill="white"/>
      <rect x="6" y="8" width="12" height="2" fill="#0078D4"/>
      <rect x="6" y="11" width="12" height="2" fill="#0078D4"/>
      <rect x="6" y="14" width="12" height="2" fill="#0078D4"/>
      <rect x="6" y="17" width="8" height="2" fill="#0078D4"/>
    </svg>`,
    color: '#0078D4'
  },
  
  'azure-vnet': {
    name: 'Virtual Network',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <circle cx="12" cy="12" r="8" fill="white"/>
      <circle cx="8" cy="8" r="2" fill="#0078D4"/>
      <circle cx="16" cy="8" r="2" fill="#0078D4"/>
      <circle cx="8" cy="16" r="2" fill="#0078D4"/>
      <circle cx="16" cy="16" r="2" fill="#0078D4"/>
      <circle cx="12" cy="12" r="1" fill="#0078D4"/>
      <line x1="8" y1="8" x2="12" y2="12" stroke="#0078D4" stroke-width="1"/>
      <line x1="16" y1="8" x2="12" y2="12" stroke="#0078D4" stroke-width="1"/>
      <line x1="8" y1="16" x2="12" y2="12" stroke="#0078D4" stroke-width="1"/>
      <line x1="16" y1="16" x2="12" y2="12" stroke="#0078D4" stroke-width="1"/>
    </svg>`,
    color: '#0078D4'
  },
  
  'azure-load-balancer': {
    name: 'Load Balancer',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="6" width="20" height="12" rx="2" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <rect x="4" y="8" width="16" height="8" fill="white"/>
      <rect x="6" y="10" width="12" height="1" fill="#0078D4"/>
      <rect x="6" y="12" width="12" height="1" fill="#0078D4"/>
      <rect x="6" y="14" width="12" height="1" fill="#0078D4"/>
      <circle cx="8" cy="16" r="1" fill="#0078D4"/>
      <circle cx="12" cy="16" r="1" fill="#0078D4"/>
      <circle cx="16" cy="16" r="1" fill="#0078D4"/>
    </svg>`,
    color: '#0078D4'
  },
  
  'azure-redis': {
    name: 'Redis Cache',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="4" width="18" height="16" rx="2" fill="#DC382D" stroke="#DC382D" stroke-width="1"/>
      <rect x="5" y="6" width="14" height="12" fill="white"/>
      <rect x="7" y="8" width="10" height="1" fill="#DC382D"/>
      <rect x="7" y="10" width="8" height="1" fill="#DC382D"/>
      <rect x="7" y="12" width="10" height="1" fill="#DC382D"/>
      <rect x="7" y="14" width="6" height="1" fill="#DC382D"/>
      <circle cx="9" cy="16" r="1" fill="#DC382D"/>
      <circle cx="13" cy="16" r="1" fill="#DC382D"/>
    </svg>`,
    color: '#DC382D'
  },
  
  'azure-service-bus': {
    name: 'Service Bus',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="6" width="20" height="12" rx="2" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <rect x="4" y="8" width="16" height="8" fill="white"/>
      <rect x="6" y="10" width="12" height="1" fill="#0078D4"/>
      <rect x="6" y="12" width="12" height="1" fill="#0078D4"/>
      <rect x="6" y="14" width="12" height="1" fill="#0078D4"/>
      <circle cx="8" cy="16" r="1" fill="#0078D4"/>
      <circle cx="12" cy="16" r="1" fill="#0078D4"/>
      <circle cx="16" cy="16" r="1" fill="#0078D4"/>
    </svg>`,
    color: '#0078D4'
  },
  
  'azure-functions': {
    name: 'Azure Functions',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 4h18v16H3V4z" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <path d="M5 6h14v12H5V6z" fill="white"/>
      <path d="M8 8h8v1H8V8zm0 2h6v1H8v-1zm0 2h8v1H8v-1zm0 2h5v1H8v-1z" fill="#0078D4"/>
      <circle cx="10" cy="16" r="1" fill="#0078D4"/>
      <circle cx="14" cy="16" r="1" fill="#0078D4"/>
    </svg>`,
    color: '#0078D4'
  },
  
  'azure-cosmos': {
    name: 'Cosmos DB',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <circle cx="12" cy="12" r="8" fill="white"/>
      <path d="M12 4l4 8-4 8-4-8 4-8z" fill="#0078D4"/>
      <circle cx="12" cy="12" r="2" fill="white"/>
    </svg>`,
    color: '#0078D4'
  },
  
  'azure-key-vault': {
    name: 'Key Vault',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="4" width="18" height="16" rx="2" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <rect x="5" y="6" width="14" height="12" fill="white"/>
      <rect x="7" y="8" width="10" height="1" fill="#0078D4"/>
      <rect x="7" y="10" width="8" height="1" fill="#0078D4"/>
      <rect x="7" y="12" width="10" height="1" fill="#0078D4"/>
      <rect x="7" y="14" width="6" height="1" fill="#0078D4"/>
      <circle cx="9" cy="16" r="1" fill="#0078D4"/>
      <circle cx="13" cy="16" r="1" fill="#0078D4"/>
    </svg>`,
    color: '#0078D4'
  },
  
  'azure-monitor': {
    name: 'Application Insights',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="4" width="20" height="16" rx="2" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <rect x="4" y="6" width="16" height="12" fill="white"/>
      <path d="M6 8h12v1H6V8zm0 2h10v1H6v-1zm0 2h12v1H6v-1zm0 2h8v1H6v-1z" fill="#0078D4"/>
      <circle cx="8" cy="16" r="1" fill="#0078D4"/>
      <circle cx="12" cy="16" r="1" fill="#0078D4"/>
      <circle cx="16" cy="16" r="1" fill="#0078D4"/>
    </svg>`,
    color: '#0078D4'
  }
};

// Función para obtener el icono SVG
function getAzureIconOfficial(serviceType) {
  return azureIconsOfficial[serviceType] || {
    name: 'Azure Service',
    svg: `<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="4" width="18" height="16" rx="2" fill="#0078D4" stroke="#0078D4" stroke-width="1"/>
      <rect x="5" y="6" width="14" height="12" fill="white"/>
      <text x="12" y="14" text-anchor="middle" font-family="Arial" font-size="8" fill="#0078D4">AZURE</text>
    </svg>`,
    color: '#0078D4'
  };
}

// Exportar para uso en el navegador
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { azureIconsOfficial, getAzureIconOfficial };
} else {
  window.azureIconsOfficial = azureIconsOfficial;
  window.getAzureIconOfficial = getAzureIconOfficial;
}
