// Panel de iconos dinámico mejorado
class IconsPanel {
    constructor() {
        this.icons = {};
        this.currentProvider = 'all';
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.isVisible = false;
        this.searchHistory = [];
        this.favoriteIcons = [];
        this.recentIcons = [];
        
        this.init();
    }
    
    async init() {
        await this.loadIcons();
        this.loadUserPreferences();
        this.createPanel();
        this.setupEventListeners();
    }
    
    async loadIcons() {
        try {
            const response = await fetch('/api/icons');
            const data = await response.json();
            
            if (data.success) {
                this.icons = data.icons;
                console.log('📦 Panel de iconos inicializado:', data.total_icons, 'iconos');
                
                // Crear índice de búsqueda para búsqueda más rápida
                this.createSearchIndex();
            }
        } catch (error) {
            console.error('Error cargando iconos:', error);
        }
    }
    
    createSearchIndex() {
        // Crear índice de búsqueda para búsqueda más eficiente
        this.searchIndex = {};
        
        Object.entries(this.icons).forEach(([providerName, provider]) => {
            Object.entries(provider).forEach(([categoryName, categoryIcons]) => {
                categoryIcons.forEach(icon => {
                    // Indexar por nombre
                    const nameWords = icon.name.toLowerCase().split('-');
                    nameWords.forEach(word => {
                        if (!this.searchIndex[word]) this.searchIndex[word] = [];
                        this.searchIndex[word].push(icon);
                    });
                    
                    // Indexar por categoría
                    if (!this.searchIndex[categoryName.toLowerCase()]) {
                        this.searchIndex[categoryName.toLowerCase()] = [];
                    }
                    this.searchIndex[categoryName.toLowerCase()].push(icon);
                    
                    // Indexar por proveedor
                    if (!this.searchIndex[providerName.toLowerCase()]) {
                        this.searchIndex[providerName.toLowerCase()] = [];
                    }
                    this.searchIndex[providerName.toLowerCase()].push(icon);
                });
            });
        });
    }
    
    loadUserPreferences() {
        // Cargar preferencias del usuario desde localStorage
        try {
            this.favoriteIcons = JSON.parse(localStorage.getItem('favoriteIcons') || '[]');
            this.recentIcons = JSON.parse(localStorage.getItem('recentIcons') || '[]');
            this.searchHistory = JSON.parse(localStorage.getItem('searchHistory') || '[]');
        } catch (error) {
            console.error('Error cargando preferencias:', error);
        }
    }
    
    saveUserPreferences() {
        // Guardar preferencias del usuario en localStorage
        try {
            localStorage.setItem('favoriteIcons', JSON.stringify(this.favoriteIcons));
            localStorage.setItem('recentIcons', JSON.stringify(this.recentIcons));
            localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
        } catch (error) {
            console.error('Error guardando preferencias:', error);
        }
    }
    
    createPanel() {
        // Crear panel flotante de iconos mejorado
        const panel = document.createElement('div');
        panel.id = 'iconsPanel';
        panel.className = 'icons-panel';
        panel.innerHTML = `
            <div class="icons-panel-header">
                <h6 class="mb-0">
                    <i class="fas fa-icons me-2"></i>Biblioteca de Iconos
                </h6>
                <div class="header-controls">
                    <button class="btn btn-sm btn-outline-primary me-2" onclick="iconsPanel.showFavorites()" title="Iconos favoritos">
                        <i class="fas fa-heart"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="iconsPanel.toggle()" title="Cerrar panel">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            
            <div class="icons-panel-controls">
                <div class="row g-2 mb-3">
                    <div class="col-6">
                        <select class="form-select form-select-sm" id="providerFilter">
                            <option value="all">Todos los proveedores</option>
                            <option value="AWS">AWS</option>
                            <option value="Azure">Azure</option>
                        </select>
                    </div>
                    <div class="col-6">
                        <select class="form-select form-select-sm" id="categoryFilter">
                            <option value="all">Todas las categorías</option>
                        </select>
                    </div>
                </div>
                
                <div class="mb-3">
                    <div class="input-group">
                        <input type="text" class="form-control form-control-sm" 
                               id="iconSearch" placeholder="Buscar iconos...">
                        <button class="btn btn-outline-secondary btn-sm" type="button" onclick="iconsPanel.clearSearch()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div id="searchSuggestions" class="search-suggestions"></div>
                </div>
                
                <div class="mb-2">
                    <div class="btn-group btn-group-sm w-100" role="group">
                        <button type="button" class="btn btn-outline-primary" onclick="iconsPanel.showRecent()">
                            <i class="fas fa-clock me-1"></i>Recientes
                        </button>
                        <button type="button" class="btn btn-outline-primary" onclick="iconsPanel.showPopular()">
                            <i class="fas fa-star me-1"></i>Populares
                        </button>
                        <button type="button" class="btn btn-outline-primary" onclick="iconsPanel.showAll()">
                            <i class="fas fa-th me-1"></i>Todos
                        </button>
                    </div>
                </div>
            </div>
            
            <div class="icons-panel-content">
                <div id="iconsGrid" class="icons-grid">
                    <!-- Los iconos se cargarán aquí -->
                </div>
                
                <div id="iconsPagination" class="icons-pagination mt-3">
                    <!-- Paginación -->
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
        
        // Agregar botón para mostrar el panel
        this.createToggleButton();
    }
    
    createToggleButton() {
        const button = document.createElement('button');
        button.id = 'iconsToggleBtn';
        button.className = 'btn btn-primary icons-toggle-btn';
        button.innerHTML = '<i class="fas fa-icons"></i>';
        button.title = 'Mostrar biblioteca de iconos';
        button.onclick = () => this.toggle();
        
        document.body.appendChild(button);
    }
    
    setupEventListeners() {
        // Filtro de proveedor
        document.getElementById('providerFilter').addEventListener('change', (e) => {
            this.currentProvider = e.target.value;
            this.updateCategoryFilter();
            this.renderIcons();
        });
        
        // Filtro de categoría
        document.getElementById('categoryFilter').addEventListener('change', (e) => {
            this.currentCategory = e.target.value;
            this.renderIcons();
        });
        
        // Búsqueda mejorada con debounce
        const searchInput = document.getElementById('iconSearch');
        searchInput.addEventListener('input', this.debounce((e) => {
            this.searchQuery = e.target.value.toLowerCase();
            this.showSearchSuggestions();
            this.renderIcons();
        }, 300));
        
        // Búsqueda con Enter
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performAdvancedSearch();
            }
        });
        
        // Inicializar filtros
        this.updateCategoryFilter();
        this.renderIcons();
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    showSearchSuggestions() {
        const suggestionsContainer = document.getElementById('searchSuggestions');
        if (!this.searchQuery || this.searchQuery.length < 2) {
            suggestionsContainer.innerHTML = '';
            return;
        }
        
        // Generar sugerencias basadas en el índice de búsqueda
        const suggestions = this.generateSearchSuggestions(this.searchQuery);
        
        if (suggestions.length === 0) {
            suggestionsContainer.innerHTML = '';
            return;
        }
        
        suggestionsContainer.innerHTML = suggestions.map(suggestion => 
            `<div class="search-suggestion" onclick="iconsPanel.selectSuggestion('${suggestion}')">
                <i class="fas fa-search me-2"></i>${suggestion}
            </div>`
        ).join('');
    }
    
    generateSearchSuggestions(query) {
        const suggestions = new Set();
        const queryLower = query.toLowerCase();
        
        // Buscar en el índice de búsqueda
        Object.keys(this.searchIndex).forEach(key => {
            if (key.includes(queryLower) && key !== queryLower) {
                suggestions.add(key);
            }
        });
        
        // Sugerencias comunes
        const commonTerms = {
            'vm': ['virtual machine', 'ec2', 'compute', 'server'],
            'database': ['db', 'rds', 'sql', 'nosql', 'storage'],
            'network': ['vpc', 'vnet', 'subnet', 'gateway', 'router'],
            'security': ['firewall', 'waf', 'iam', 'security group'],
            'monitor': ['logging', 'analytics', 'insights', 'metrics'],
            'api': ['gateway', 'app service', 'function', 'lambda'],
            'container': ['kubernetes', 'docker', 'aks', 'ecs', 'eks'],
            'storage': ['s3', 'blob', 'file', 'backup', 'archive']
        };
        
        Object.entries(commonTerms).forEach(([term, related]) => {
            if (queryLower.includes(term)) {
                related.forEach(suggestion => suggestions.add(suggestion));
            }
        });
        
        return Array.from(suggestions).slice(0, 8);
    }
    
    selectSuggestion(suggestion) {
        document.getElementById('iconSearch').value = suggestion;
        this.searchQuery = suggestion.toLowerCase();
        document.getElementById('searchSuggestions').innerHTML = '';
        this.renderIcons();
    }
    
    clearSearch() {
        document.getElementById('iconSearch').value = '';
        this.searchQuery = '';
        document.getElementById('searchSuggestions').innerHTML = '';
        this.renderIcons();
    }
    
    async performAdvancedSearch() {
        if (!this.searchQuery || this.searchQuery.length < 2) return;
        
        try {
            // Guardar en historial de búsqueda
            if (!this.searchHistory.includes(this.searchQuery)) {
                this.searchHistory.unshift(this.searchQuery);
                this.searchHistory = this.searchHistory.slice(0, 10); // Mantener solo 10
                this.saveUserPreferences();
            }
            
            // Búsqueda avanzada en el servidor
            const params = new URLSearchParams({
                q: this.searchQuery,
                provider: this.currentProvider,
                category: this.currentCategory,
                limit: 200
            });
            
            const response = await fetch(`/api/search_icons?${params}`);
            const data = await response.json();
            
            if (data.success) {
                this.displaySearchResults(data.results, data.metadata);
            }
        } catch (error) {
            console.error('Error en búsqueda avanzada:', error);
        }
    }
    
    displaySearchResults(results, metadata) {
        const grid = document.getElementById('iconsGrid');
        grid.innerHTML = '';
        
        if (results.length === 0) {
            grid.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-search fa-2x mb-3"></i>
                    <h6>No se encontraron iconos</h6>
                    <p class="small">Intenta con otros términos de búsqueda</p>
                    ${metadata.suggestions ? `
                        <div class="mt-3">
                            <strong>Sugerencias:</strong><br>
                            ${metadata.suggestions.map(s => `<span class="badge bg-light text-dark me-1">${s}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
            return;
        }
        
        // Mostrar metadatos de búsqueda
        if (metadata) {
            const metadataDiv = document.createElement('div');
            metadataDiv.className = 'search-metadata mb-3 p-2 bg-light rounded';
            metadataDiv.innerHTML = `
                <small class="text-muted">
                    <i class="fas fa-info-circle me-1"></i>
                    Encontrados ${metadata.total_found} iconos para "${metadata.query}"
                    ${metadata.suggestions ? `<br>Sugerencias: ${metadata.suggestions.join(', ')}` : ''}
                </small>
            `;
            grid.appendChild(metadataDiv);
        }
        
        // Renderizar resultados
        results.forEach(icon => {
            const iconElement = this.createIconElement(icon);
            grid.appendChild(iconElement);
        });
    }
    
    updateCategoryFilter() {
        const categorySelect = document.getElementById('categoryFilter');
        categorySelect.innerHTML = '<option value="all">Todas las categorías</option>';
        
        const categories = new Set();
        
        if (this.currentProvider === 'all') {
            // Obtener todas las categorías de todos los proveedores
            Object.values(this.icons).forEach(provider => {
                Object.keys(provider).forEach(category => {
                    categories.add(category);
                });
            });
        } else {
            // Obtener categorías del proveedor seleccionado
            if (this.icons[this.currentProvider]) {
                Object.keys(this.icons[this.currentProvider]).forEach(category => {
                    categories.add(category);
                });
            }
        }
        
        // Añadir opciones de categoría ordenadas
        Array.from(categories).sort().forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = this.formatCategoryName(category);
            categorySelect.appendChild(option);
        });
    }
    
    formatCategoryName(category) {
        return category
            .replace(/-/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase())
            .replace(/\s+/g, ' ')
            .trim();
    }
    
    renderIcons() {
        const grid = document.getElementById('iconsGrid');
        grid.innerHTML = '';
        
        let iconsToShow = [];
        
        // Filtrar iconos según los criterios
        Object.entries(this.icons).forEach(([providerName, provider]) => {
            if (this.currentProvider !== 'all' && providerName !== this.currentProvider) {
                return;
            }
            
            Object.entries(provider).forEach(([categoryName, categoryIcons]) => {
                if (this.currentCategory !== 'all' && categoryName !== this.currentCategory) {
                    return;
                }
                
                categoryIcons.forEach(icon => {
                    if (this.searchQuery === '' || 
                        icon.name.toLowerCase().includes(this.searchQuery) ||
                        categoryName.toLowerCase().includes(this.searchQuery) ||
                        providerName.toLowerCase().includes(this.searchQuery)) {
                        iconsToShow.push(icon);
                    }
                });
            });
        });
        
        // Mostrar mensaje si no hay iconos
        if (iconsToShow.length === 0) {
            grid.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-search fa-2x mb-3"></i>
                    <h6>No se encontraron iconos</h6>
                    <p class="small">Ajusta los filtros o términos de búsqueda</p>
                </div>
            `;
            return;
        }
        
        // Ordenar iconos por relevancia y popularidad
        iconsToShow.sort((a, b) => {
            // Priorizar iconos favoritos
            const aIsFavorite = this.favoriteIcons.some(fav => fav.path === a.path);
            const bIsFavorite = this.favoriteIcons.some(fav => fav.path === b.path);
            
            if (aIsFavorite && !bIsFavorite) return -1;
            if (!aIsFavorite && bIsFavorite) return 1;
            
            // Luego por nombre alfabéticamente
            return a.name.localeCompare(b.name);
        });
        
        // Renderizar iconos con paginación
        const itemsPerPage = 50;
        const currentPage = 1;
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const pageIcons = iconsToShow.slice(startIndex, endIndex);
        
        pageIcons.forEach(icon => {
            const iconElement = this.createIconElement(icon);
            grid.appendChild(iconElement);
        });
        
        // Mostrar paginación si es necesario
        if (iconsToShow.length > itemsPerPage) {
            this.renderPagination(iconsToShow.length, itemsPerPage, currentPage);
        }
        
        // Mostrar contador
        const counterDiv = document.createElement('div');
        counterDiv.className = 'text-center text-muted py-2';
        counterDiv.textContent = `Mostrando ${pageIcons.length} de ${iconsToShow.length} iconos`;
        grid.appendChild(counterDiv);
    }
    
    renderPagination(totalItems, itemsPerPage, currentPage) {
        const paginationContainer = document.getElementById('iconsPagination');
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        
        if (totalPages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }
        
        let paginationHTML = '<nav><ul class="pagination pagination-sm justify-content-center">';
        
        // Botón anterior
        paginationHTML += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="iconsPanel.goToPage(${currentPage - 1})">Anterior</a>
            </li>
        `;
        
        // Números de página
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                paginationHTML += `
                    <li class="page-item ${i === currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="iconsPanel.goToPage(${i})">${i}</a>
                    </li>
                `;
            } else if (i === currentPage - 3 || i === currentPage + 3) {
                paginationHTML += '<li class="page-item disabled"><span class="page-link">...</span></li>';
            }
        }
        
        // Botón siguiente
        paginationHTML += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="iconsPanel.goToPage(${currentPage + 1})">Siguiente</a>
            </li>
        `;
        
        paginationHTML += '</ul></nav>';
        paginationContainer.innerHTML = paginationHTML;
    }
    
    goToPage(page) {
        // Implementar navegación entre páginas
        console.log('Navegando a página:', page);
    }
    
    createIconElement(icon) {
        const iconDiv = document.createElement('div');
        iconDiv.className = 'icon-item';
        iconDiv.title = `${icon.name} (${icon.provider}/${icon.category})`;
        
        const isFavorite = this.favoriteIcons.some(fav => fav.path === icon.path);
        
        iconDiv.innerHTML = `
            <div class="icon-preview">
                <img src="${icon.path}" alt="${icon.name}" onerror="this.style.display='none'">
                <button class="btn btn-sm btn-link favorite-btn ${isFavorite ? 'text-danger' : 'text-muted'}" 
                        onclick="iconsPanel.toggleFavorite(event, ${JSON.stringify(icon).replace(/"/g, '&quot;')})">
                    <i class="fas fa-heart"></i>
                </button>
            </div>
            <div class="icon-name">${this.formatIconName(icon.name)}</div>
            <div class="icon-meta">
                <small class="text-muted">${icon.provider} • ${this.formatCategoryName(icon.category)}</small>
            </div>
        `;
        
        // Evento de clic para añadir icono al diagrama
        iconDiv.addEventListener('click', (e) => {
            if (!e.target.closest('.favorite-btn')) {
                this.addIconToCanvas(icon);
            }
        });
        
        return iconDiv;
    }
    
    formatIconName(name) {
        return name
            .replace(/-/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase())
            .replace(/\s+/g, ' ')
            .trim();
    }
    
    toggleFavorite(event, icon) {
        event.stopPropagation();
        
        const existingIndex = this.favoriteIcons.findIndex(fav => fav.path === icon.path);
        
        if (existingIndex >= 0) {
            // Remover de favoritos
            this.favoriteIcons.splice(existingIndex, 1);
            event.target.classList.remove('text-danger');
            event.target.classList.add('text-muted');
        } else {
            // Añadir a favoritos
            this.favoriteIcons.push(icon);
            event.target.classList.remove('text-muted');
            event.target.classList.add('text-danger');
        }
        
        this.saveUserPreferences();
    }
    
    showFavorites() {
        const grid = document.getElementById('iconsGrid');
        grid.innerHTML = '';
        
        if (this.favoriteIcons.length === 0) {
            grid.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-heart fa-2x mb-3"></i>
                    <h6>No hay iconos favoritos</h6>
                    <p class="small">Haz clic en el corazón para marcar iconos como favoritos</p>
                </div>
            `;
            return;
        }
        
        this.favoriteIcons.forEach(icon => {
            const iconElement = this.createIconElement(icon);
            grid.appendChild(iconElement);
        });
    }
    
    showRecent() {
        const grid = document.getElementById('iconsGrid');
        grid.innerHTML = '';
        
        if (this.recentIcons.length === 0) {
            grid.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-clock fa-2x mb-3"></i>
                    <h6>No hay iconos recientes</h6>
                    <p class="small">Los iconos que uses aparecerán aquí</p>
                </div>
            `;
            return;
        }
        
        this.recentIcons.forEach(icon => {
            const iconElement = this.createIconElement(icon);
            grid.appendChild(iconElement);
        });
    }
    
    showPopular() {
        // Mostrar iconos más populares basados en uso
        this.showAll();
    }
    
    showAll() {
        this.renderIcons();
    }
    
    addIconToCanvas(icon) {
        if (!currentDiagram) {
            showError('Primero crea o carga un diagrama');
            return;
        }
        
        // Añadir a iconos recientes
        const existingIndex = this.recentIcons.findIndex(recent => recent.path === icon.path);
        if (existingIndex >= 0) {
            this.recentIcons.splice(existingIndex, 1);
        }
        this.recentIcons.unshift(icon);
        this.recentIcons = this.recentIcons.slice(0, 20); // Mantener solo 20
        this.saveUserPreferences();
        
        // Generar posición aleatoria en el canvas
        const canvas = document.getElementById('diagramCanvas');
        const canvasRect = canvas.getBoundingClientRect();
        
        const x = Math.random() * (canvasRect.width - 120);
        const y = Math.random() * (canvasRect.height - 80);
        
        const nodeData = {
            id: `icon_${Date.now()}`,
            type: 'icon',
            text: this.formatIconName(icon.name),
            x: x,
            y: y,
            width: 80,
            height: 80,
            icon: icon.path,
            provider: icon.provider,
            category: icon.category,
            metadata: {
                provider: icon.provider,
                category: icon.category,
                added_at: new Date().toISOString()
            }
        };
        
        // Añadir nodo al diagrama actual
        currentDiagram.data.nodes.push(nodeData);
        
        // Crear elemento visual
        createNodeElement(nodeData);
        
        // Guardar cambios
        saveDiagramChanges();
        
        showSuccess(`Icono ${this.formatIconName(icon.name)} añadido al diagrama`);
        
        // Cerrar panel si está en modo móvil
        if (window.innerWidth < 768) {
            this.hide();
        }
    }
    
    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    show() {
        const panel = document.getElementById('iconsPanel');
        const button = document.getElementById('iconsToggleBtn');
        
        panel.classList.add('visible');
        button.style.display = 'none';
        this.isVisible = true;
        
        // Recargar iconos si es necesario
        if (Object.keys(this.icons).length === 0) {
            this.loadIcons().then(() => {
                this.updateCategoryFilter();
                this.renderIcons();
            });
        }
    }
    
    hide() {
        const panel = document.getElementById('iconsPanel');
        const button = document.getElementById('iconsToggleBtn');
        
        panel.classList.remove('visible');
        button.style.display = 'block';
        this.isVisible = false;
    }
    
    async searchIcons(query, provider = 'all', category = 'all') {
        try {
            const params = new URLSearchParams({
                q: query,
                provider: provider,
                category: category
            });
            
            const response = await fetch(`/api/search_icons?${params}`);
            const data = await response.json();
            
            if (data.success) {
                return data.results;
            } else {
                console.error('Error buscando iconos:', data.error);
                return [];
            }
        } catch (error) {
            console.error('Error en búsqueda de iconos:', error);
            return [];
        }
    }
}

// Inicializar panel de iconos cuando se carga la página
let iconsPanel;
document.addEventListener('DOMContentLoaded', function() {
    iconsPanel = new IconsPanel();
});

// Exportar para uso global
window.IconsPanel = IconsPanel;
