// Iconos SVG de Azure para el diagramador
const AzureIcons = {
    // Red y Seguridad
    azure_vnet: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#0078d4" stroke="#005a9e" stroke-width="2"/>
        <path d="M7 7h10v10H7z" fill="#ffffff" opacity="0.8"/>
        <path d="M9 9h6v6H9z" fill="#0078d4"/>
        <circle cx="12" cy="12" r="2" fill="#ffffff"/>
    </svg>`,
    
    azure_subnet: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="3" y="3" width="18" height="18" rx="2" fill="#40a9ff" stroke="#1890ff" stroke-width="2"/>
        <path d="M6 6h12v12H6z" fill="#ffffff" opacity="0.6"/>
        <path d="M8 8h8v8H8z" fill="#40a9ff"/>
        <circle cx="12" cy="12" r="1.5" fill="#ffffff"/>
    </svg>`,
    
    azure_firewall: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#ff4d4f" stroke="#cf1322" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#ff4d4f"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <circle cx="12" cy="12" r="2" fill="#ff4d4f"/>
        <path d="M10 10l4 4M14 10l-4 4" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    
    azure_load_balancer: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#40a9ff" stroke="#1890ff" stroke-width="2"/>
        <circle cx="7" cy="12" r="2" fill="#ffffff"/>
        <circle cx="12" cy="12" r="2" fill="#ffffff"/>
        <circle cx="17" cy="12" r="2" fill="#ffffff"/>
        <path d="M9 12h6" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
        <path d="M12 8v8" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
    </svg>`,
    
    // Aplicaciones
    azure_app_service: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#52c41a" stroke="#389e0d" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#52c41a"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v4h-4z" fill="#52c41a"/>
        <path d="M12 12v2" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    
    azure_web_app: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#73d13d" stroke="#52c41a" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#73d13d"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v2h-4z" fill="#73d13d"/>
        <path d="M10 14h4v2h-4z" fill="#73d13d"/>
    </svg>`,
    
    azure_api_app: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#faad14" stroke="#d48806" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#faad14"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#faad14"/>
        <path d="M10 12h4v1h-4z" fill="#faad14"/>
        <path d="M10 14h4v1h-4z" fill="#faad14"/>
        <path d="M10 16h4v1h-4z" fill="#faad14"/>
    </svg>`,
    
    azure_function: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#eb2f96" stroke="#c41d7f" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#eb2f96"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10l4 4M14 10l-4 4" stroke="#eb2f96" stroke-width="2" stroke-linecap="round"/>
    </svg>`,
    
    // Datos y Almacenamiento
    azure_sql: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#722ed1" stroke="#531dab" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#722ed1"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#722ed1"/>
        <path d="M10 12h4v1h-4z" fill="#722ed1"/>
        <path d="M10 14h4v1h-4z" fill="#722ed1"/>
        <path d="M10 16h4v1h-4z" fill="#722ed1"/>
        <circle cx="12" cy="18" r="1" fill="#722ed1"/>
    </svg>`,
    
    azure_storage: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#ff4d4f" stroke="#cf1322" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#ff4d4f"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#ff4d4f"/>
        <path d="M10 12h4v1h-4z" fill="#ff4d4f"/>
        <path d="M10 14h4v1h-4z" fill="#ff4d4f"/>
        <path d="M10 16h4v1h-4z" fill="#ff4d4f"/>
        <rect x="9" y="9" width="6" height="6" fill="#ff4d4f" opacity="0.5"/>
    </svg>`,
    
    azure_key_vault: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#722ed1" stroke="#531dab" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#722ed1"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#722ed1"/>
        <path d="M10 12h4v1h-4z" fill="#722ed1"/>
        <path d="M10 14h4v1h-4z" fill="#722ed1"/>
        <path d="M10 16h4v1h-4z" fill="#722ed1"/>
        <circle cx="12" cy="12" r="1" fill="#ffffff"/>
        <path d="M11 11h2v2h-2z" fill="#722ed1"/>
    </svg>`,
    
    azure_monitoring: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#52c41a" stroke="#389e0d" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#52c41a"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10l2 2 2-2 2 2" stroke="#52c41a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        <circle cx="10" cy="10" r="1" fill="#52c41a"/>
        <circle cx="14" cy="12" r="1" fill="#52c41a"/>
        <circle cx="18" cy="14" r="1" fill="#52c41a"/>
    </svg>`,
    
    // Conectividad
    azure_cdn: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#73d13d" stroke="#52c41a" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#73d13d"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#73d13d"/>
        <path d="M10 12h4v1h-4z" fill="#73d13d"/>
        <path d="M10 14h4v1h-4z" fill="#73d13d"/>
        <path d="M10 16h4v1h-4z" fill="#73d13d"/>
        <path d="M12 8v8" stroke="#73d13d" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    
    azure_vpn_gateway: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#faad14" stroke="#d48806" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#faad14"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#faad14"/>
        <path d="M10 12h4v1h-4z" fill="#faad14"/>
        <path d="M10 14h4v1h-4z" fill="#faad14"/>
        <path d="M10 16h4v1h-4z" fill="#faad14"/>
        <path d="M12 8v8" stroke="#faad14" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M8 12h8" stroke="#faad14" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    
    azure_express_route: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#eb2f96" stroke="#c41d7f" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#eb2f96"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#eb2f96"/>
        <path d="M10 12h4v1h-4z" fill="#eb2f96"/>
        <path d="M10 14h4v1h-4z" fill="#eb2f96"/>
        <path d="M10 16h4v1h-4z" fill="#eb2f96"/>
        <path d="M12 8v8" stroke="#eb2f96" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M8 12h8" stroke="#eb2f96" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="12" cy="12" r="1" fill="#ffffff"/>
    </svg>`,
    
    azure_bastion: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#faad14" stroke="#d48806" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#faad14"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#faad14"/>
        <path d="M10 12h4v1h-4z" fill="#faad14"/>
        <path d="M10 14h4v1h-4z" fill="#faad14"/>
        <path d="M10 16h4v1h-4z" fill="#faad14"/>
        <path d="M12 8v8" stroke="#faad14" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M8 12h8" stroke="#faad14" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="12" cy="12" r="1" fill="#ffffff"/>
        <path d="M11 11h2v2h-2z" fill="#faad14"/>
    </svg>`,
    
    azure_shared_services: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#722ed1" stroke="#531dab" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#722ed1"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#722ed1"/>
        <path d="M10 12h4v1h-4z" fill="#722ed1"/>
        <path d="M10 14h4v1h-4z" fill="#722ed1"/>
        <path d="M10 16h4v1h-4z" fill="#722ed1"/>
        <path d="M12 8v8" stroke="#722ed1" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M8 12h8" stroke="#722ed1" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="12" cy="12" r="1" fill="#ffffff"/>
        <path d="M11 11h2v2h-2z" fill="#722ed1"/>
        <path d="M9 9h6v6H9z" fill="#722ed1" opacity="0.3"/>
    </svg>`,
    
    // Nodos especiales
    internet: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#40a9ff" stroke="#1890ff" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#40a9ff"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#40a9ff"/>
        <path d="M10 12h4v1h-4z" fill="#40a9ff"/>
        <path d="M10 14h4v1h-4z" fill="#40a9ff"/>
        <path d="M10 16h4v1h-4z" fill="#40a9ff"/>
        <path d="M12 8v8" stroke="#40a9ff" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M8 12h8" stroke="#40a9ff" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="12" cy="12" r="1" fill="#ffffff"/>
        <path d="M11 11h2v2h-2z" fill="#40a9ff"/>
        <path d="M9 9h6v6H9z" fill="#40a9ff" opacity="0.3"/>
        <path d="M7 7h10v10H7z" fill="#40a9ff" opacity="0.1"/>
    </svg>`,
    
    on_premises: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#ff4d4f" stroke="#cf1322" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#ff4d4f"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#ff4d4f"/>
        <path d="M10 12h4v1h-4z" fill="#ff4d4f"/>
        <path d="M10 14h4v1h-4z" fill="#ff4d4f"/>
        <path d="M10 16h4v1h-4z" fill="#ff4d4f"/>
        <path d="M12 8v8" stroke="#ff4d4f" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M8 12h8" stroke="#ff4d4f" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="12" cy="12" r="1" fill="#ffffff"/>
        <path d="M11 11h2v2h-2z" fill="#ff4d4f"/>
        <path d="M9 9h6v6H9z" fill="#ff4d4f" opacity="0.3"/>
        <path d="M7 7h10v10H7z" fill="#ff4d4f" opacity="0.1"/>
        <path d="M5 5h14v14H5z" fill="#ff4d4f" opacity="0.05"/>
    </svg>`,
    
    diagram_title: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#1e293b" stroke="#475569" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.1"/>
        <path d="M6 6h12v12H6z" fill="#1e293b"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.2"/>
        <path d="M10 10h4v1h-4z" fill="#ffffff"/>
        <path d="M10 12h4v1h-4z" fill="#ffffff"/>
        <path d="M10 14h4v1h-4z" fill="#ffffff"/>
        <path d="M10 16h4v1h-4z" fill="#ffffff"/>
        <path d="M12 8v8" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M8 12h8" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
        <circle cx="12" cy="12" r="1" fill="#ffffff"/>
        <path d="M11 11h2v2h-2z" fill="#ffffff"/>
        <path d="M9 9h6v6H9z" fill="#ffffff" opacity="0.3"/>
        <path d="M7 7h10v10H7z" fill="#ffffff" opacity="0.1"/>
        <path d="M5 5h14v14H5z" fill="#ffffff" opacity="0.05"/>
        <path d="M3 3h18v18H3z" fill="#ffffff" opacity="0.02"/>
    </svg>`,
    
    // Nodos genéricos para otros tipos de diagramas
    start: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" fill="#52c41a" stroke="#389e0d" stroke-width="2"/>
        <path d="M8 12l3 3 5-5" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    
    end: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" fill="#ff4d4f" stroke="#cf1322" stroke-width="2"/>
        <path d="M8 8l8 8M16 8l-8 8" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
    </svg>`,
    
    process: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#40a9ff" stroke="#1890ff" stroke-width="2"/>
        <path d="M6 6h12v12H6z" fill="#ffffff" opacity="0.2"/>
        <path d="M8 8h8v8H8z" fill="#40a9ff"/>
        <path d="M10 10h4v1h-4z" fill="#ffffff"/>
        <path d="M10 12h4v1h-4z" fill="#ffffff"/>
        <path d="M10 14h4v1h-4z" fill="#ffffff"/>
        <path d="M10 16h4v1h-4z" fill="#ffffff"/>
    </svg>`,
    
    decision: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <polygon points="12,2 22,12 12,22 2,12" fill="#faad14" stroke="#d48806" stroke-width="2"/>
        <path d="M6 12l6 6 6-6" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        <path d="M12 6v6" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
    </svg>`,
    
    database: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="12" cy="6" rx="8" ry="3" fill="#722ed1" stroke="#531dab" stroke-width="2"/>
        <rect x="4" y="6" width="16" height="12" rx="3" fill="#722ed1" stroke="#531dab" stroke-width="2"/>
        <ellipse cx="12" cy="18" rx="8" ry="3" fill="#722ed1" stroke="#531dab" stroke-width="2"/>
        <path d="M12 6v12" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M8 9h8" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M8 12h8" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
        <path d="M8 15h8" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round"/>
    </svg>`,
    
    // Iconos específicos para el diagrama de Azure Hub and Spoke
    internet: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" fill="#40a9ff" stroke="#1890ff" stroke-width="2"/>
        <path d="M2 12h20" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
        <path d="M12 2c2.5 2.5 4 6 4 10s-1.5 7.5-4 10" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
        <path d="M12 2c-2.5 2.5-4 6-4 10s1.5 7.5 4 10" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
    </svg>`,
    
    azure_vnet: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#0078d4" stroke="#005a9e" stroke-width="2"/>
        <path d="M7 7h10v10H7z" fill="#ffffff" opacity="0.8"/>
        <path d="M9 9h6v6H9z" fill="#0078d4"/>
        <circle cx="12" cy="12" r="2" fill="#ffffff"/>
    </svg>`,
    
    azure_bastion: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#faad14" stroke="#d48806" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#faad14"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#faad14"/>
        <path d="M10 12h4v1h-4z" fill="#faad14"/>
        <path d="M10 14h4v1h-4z" fill="#faad14"/>
        <path d="M10 16h4v1h-4z" fill="#faad14"/>
        <circle cx="12" cy="18" r="1" fill="#faad14"/>
    </svg>`,
    
    azure_express_route: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#13c2c2" stroke="#08979c" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#13c2c2"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 12h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 14h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 16h4v1h-4z" fill="#13c2c2"/>
        <circle cx="12" cy="18" r="1" fill="#13c2c2"/>
    </svg>`,
    
    azure_shared_services: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#eb2f96" stroke="#c41d7f" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#eb2f96"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#eb2f96"/>
        <path d="M10 12h4v1h-4z" fill="#eb2f96"/>
        <path d="M10 14h4v1h-4z" fill="#eb2f96"/>
        <path d="M10 16h4v1h-4z" fill="#eb2f96"/>
        <circle cx="12" cy="18" r="1" fill="#eb2f96"/>
    </svg>`,
    
    diagram_title: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#f5222d" stroke="#cf1322" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#f5222d"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#f5222d"/>
        <path d="M10 12h4v1h-4z" fill="#f5222d"/>
        <path d="M10 14h4v1h-4z" fill="#f5222d"/>
        <path d="M10 16h4v1h-4z" fill="#f5222d"/>
        <circle cx="12" cy="18" r="1" fill="#f5222d"/>
    </svg>`,
    
    // Iconos genéricos para tipos no específicos
    azure_vm: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#52c41a" stroke="#389e0d" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#52c41a"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#52c41a"/>
        <path d="M10 12h4v1h-4z" fill="#52c41a"/>
        <path d="M10 14h4v1h-4z" fill="#52c41a"/>
        <path d="M10 16h4v1h-4z" fill="#52c41a"/>
        <circle cx="12" cy="18" r="1" fill="#52c41a"/>
    </svg>`,
    
    azure_monitoring: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#13c2c2" stroke="#08979c" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#13c2c2"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 12h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 14h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 16h4v1h-4z" fill="#13c2c2"/>
        <circle cx="12" cy="18" r="1" fill="#13c2c2"/>
    </svg>`,
    
    azure_vpn_gateway: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#faad14" stroke="#d48806" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#faad14"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#faad14"/>
        <path d="M10 12h4v1h-4z" fill="#faad14"/>
        <path d="M10 14h4v1h-4z" fill="#faad14"/>
        <path d="M10 16h4v1h-4z" fill="#faad14"/>
        <circle cx="12" cy="18" r="1" fill="#faad14"/>
    </svg>`,
    
    // Iconos adicionales que faltan
    azure_key_vault: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#722ed1" stroke="#531dab" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#722ed1"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#722ed1"/>
        <path d="M10 12h4v1h-4z" fill="#722ed1"/>
        <path d="M10 14h4v1h-4z" fill="#722ed1"/>
        <path d="M10 16h4v1h-4z" fill="#722ed1"/>
        <circle cx="12" cy="18" r="1" fill="#722ed1"/>
    </svg>`,
    
    azure_monitoring: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#13c2c2" stroke="#08979c" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#13c2c2"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 12h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 14h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 16h4v1h-4z" fill="#13c2c2"/>
        <circle cx="12" cy="18" r="1" fill="#13c2c2"/>
    </svg>`,
    
    azure_express_route: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#13c2c2" stroke="#08979c" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#13c2c2"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 12h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 14h4v1h-4z" fill="#13c2c2"/>
        <path d="M10 16h4v1h-4z" fill="#13c2c2"/>
        <circle cx="12" cy="18" r="1" fill="#13c2c2"/>
    </svg>`,
    
    azure_shared_services: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#eb2f96" stroke="#c41d7f" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#eb2f96"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#eb2f96"/>
        <path d="M10 12h4v1h-4z" fill="#eb2f96"/>
        <path d="M10 14h4v1h-4z" fill="#eb2f96"/>
        <path d="M10 16h4v1h-4z" fill="#eb2f96"/>
        <circle cx="12" cy="18" r="1" fill="#eb2f96"/>
    </svg>`,
    
    diagram_title: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="20" height="20" rx="2" fill="#f5222d" stroke="#cf1322" stroke-width="2"/>
        <path d="M4 4h16v16H4z" fill="#ffffff" opacity="0.2"/>
        <path d="M6 6h12v12H6z" fill="#f5222d"/>
        <path d="M8 8h8v8H8z" fill="#ffffff" opacity="0.8"/>
        <path d="M10 10h4v1h-4z" fill="#f5222d"/>
        <path d="M10 12h4v1h-4z" fill="#f5222d"/>
        <path d="M10 14h4v1h-4z" fill="#f5222d"/>
        <path d="M10 16h4v1h-4z" fill="#f5222d"/>
        <circle cx="12" cy="18" r="1" fill="#f5222d"/>
    </svg>`
};

// Función para obtener el icono SVG según el tipo de nodo
function getAzureIcon(type) {
    return AzureIcons[type] || AzureIcons['process']; // Default fallback
}

// Función para crear flechas de conexión con SVG
function createArrowConnection(fromElement, toElement, connectionType = 'default') {
    const fromRect = fromElement.getBoundingClientRect();
    const toRect = toElement.getBoundingClientRect();
    const canvasRect = document.getElementById('canvas').getBoundingClientRect();
    
    const fromX = fromRect.left - canvasRect.left + fromRect.width / 2;
    const fromY = fromRect.top - canvasRect.top + fromRect.height / 2;
    const toX = toRect.left - canvasRect.left + toRect.width / 2;
    const toY = toRect.top - canvasRect.top + toRect.height / 2;
    
    // Crear SVG para la conexión
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', '100%');
    svg.style.position = 'absolute';
    svg.style.left = '0';
    svg.style.top = '0';
    svg.style.pointerEvents = 'none';
    svg.style.zIndex = '1';
    
    // Crear línea principal con mejor estilo
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', fromX);
    line.setAttribute('y1', fromY);
    line.setAttribute('x2', toX);
    line.setAttribute('y2', toY);
    line.setAttribute('stroke', '#2563eb');
    line.setAttribute('stroke-width', '3');
    line.setAttribute('marker-end', 'url(#arrowhead)');
    line.setAttribute('stroke-linecap', 'round');
    
    // Crear marcador de flecha más visible
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'arrowhead');
    marker.setAttribute('markerWidth', '12');
    marker.setAttribute('markerHeight', '8');
    marker.setAttribute('refX', '10');
    marker.setAttribute('refY', '4');
    marker.setAttribute('orient', 'auto');
    
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', '0 0, 12 4, 0 8');
    polygon.setAttribute('fill', '#2563eb');
    
    marker.appendChild(polygon);
    defs.appendChild(marker);
    svg.appendChild(defs);
    svg.appendChild(line);
    
    return svg;
}

// Función para actualizar todas las conexiones
function updateAllConnections() {
    // Limpiar conexiones existentes
    const existingConnections = document.querySelectorAll('.connection-svg');
    existingConnections.forEach(conn => conn.remove());
    
    // Recrear conexiones
    if (window.currentDiagram && window.currentDiagram.data && window.currentDiagram.data.edges) {
        console.log('Actualizando conexiones:', window.currentDiagram.data.edges);
        window.currentDiagram.data.edges.forEach(edge => {
            console.log('Buscando elementos:', edge.from, '->', edge.to);
            const fromElement = document.getElementById(edge.from);
            const toElement = document.getElementById(edge.to);
            
            console.log('Elementos encontrados:', fromElement, toElement);
            
            if (fromElement && toElement) {
                const connection = createArrowConnection(fromElement, toElement);
                connection.classList.add('connection-svg');
                document.getElementById('canvas').appendChild(connection);
                console.log('Conexión creada entre', edge.from, 'y', edge.to);
            } else {
                console.warn('No se pudieron encontrar los elementos para la conexión:', edge.from, '->', edge.to);
            }
        });
    } else {
        console.warn('No hay diagrama actual o datos de conexiones');
    }
}
