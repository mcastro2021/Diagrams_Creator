// Panel de iconos dinámico
class IconsPanel {
    constructor() {
        this.icons = {};
        this.currentProvider = 'all';
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.isVisible = false;
        
        this.init();
    }
    
    async init() {
        await this.loadIcons();
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
            }
        } catch (error) {
            console.error('Error cargando iconos:', error);
        }
    }
    
    createPanel() {
        // Crear panel flotante de iconos
        const panel = document.createElement('div');
        panel.id = 'iconsPanel';
        panel.className = 'icons-panel';
        panel.innerHTML = `
            <div class="icons-panel-header">
                <h6 class="mb-0">
                    <i class="fas fa-icons me-2"></i>Biblioteca de Iconos
                </h6>
                <button class="btn btn-sm btn-outline-secondary" onclick="iconsPanel.toggle()">
                    <i class="fas fa-times"></i>
                </button>
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
                    <input type="text" class="form-control form-control-sm" 
                           id="iconSearch" placeholder="Buscar iconos...">
                </div>
            </div>
            
            <div class="icons-panel-content">
                <div id="iconsGrid" class="icons-grid">
                    <!-- Los iconos se cargarán aquí -->
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
        
        // Búsqueda
        document.getElementById('iconSearch').addEventListener('input', (e) => {
            this.searchQuery = e.target.value.toLowerCase();
            this.renderIcons();
        });
        
        // Inicializar filtros
        this.updateCategoryFilter();
        this.renderIcons();
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
        
        // Añadir opciones de categoría
        Array.from(categories).sort().forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category.replace(/-/g, ' ');
            categorySelect.appendChild(option);
        });
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
            grid.innerHTML = '<div class="text-center text-muted py-3">No se encontraron iconos</div>';
            return;
        }
        
        // Renderizar iconos
        iconsToShow.slice(0, 100).forEach(icon => { // Limitar a 100 para rendimiento
            const iconElement = this.createIconElement(icon);
            grid.appendChild(iconElement);
        });
        
        // Mostrar contador
        if (iconsToShow.length > 100) {
            const moreElement = document.createElement('div');
            moreElement.className = 'text-center text-muted py-2';
            moreElement.textContent = `Mostrando 100 de ${iconsToShow.length} iconos`;
            grid.appendChild(moreElement);
        }
    }
    
    createIconElement(icon) {
        const iconDiv = document.createElement('div');
        iconDiv.className = 'icon-item';
        iconDiv.title = `${icon.name} (${icon.provider}/${icon.category})`;
        
        iconDiv.innerHTML = `
            <div class="icon-preview">
                <img src="${icon.path}" alt="${icon.name}" onerror="this.style.display='none'">
            </div>
            <div class="icon-name">${icon.name.replace(/-/g, ' ')}</div>
        `;
        
        // Evento de clic para añadir icono al diagrama
        iconDiv.addEventListener('click', () => {
            this.addIconToCanvas(icon);
        });
        
        return iconDiv;
    }
    
    addIconToCanvas(icon) {
        if (!currentDiagram) {
            showError('Primero crea o carga un diagrama');
            return;
        }
        
        // Generar posición aleatoria en el canvas
        const canvas = document.getElementById('diagramCanvas');
        const canvasRect = canvas.getBoundingClientRect();
        
        const x = Math.random() * (canvasRect.width - 120);
        const y = Math.random() * (canvasRect.height - 80);
        
        const nodeData = {
            id: `icon_${Date.now()}`,
            type: 'icon',
            text: icon.name.replace(/-/g, ' '),
            x: x,
            y: y,
            width: 80,
            height: 80,
            icon: icon.path,
            provider: icon.provider,
            category: icon.category
        };
        
        // Añadir nodo al diagrama actual
        currentDiagram.data.nodes.push(nodeData);
        
        // Crear elemento visual
        createNodeElement(nodeData);
        
        // Guardar cambios
        saveDiagramChanges();
        
        showSuccess(`Icono ${icon.name} añadido al diagrama`);
        
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
