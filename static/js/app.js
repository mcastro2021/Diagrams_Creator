// Diagrams Creator - JavaScript Application

class DiagramsCreator {
    constructor() {
        this.currentDiagramId = null;
        this.libraries = [];
        this.selectedIcons = [];
        this.allIcons = []; // Cache de todos los iconos para búsqueda
        this.searchTimeout = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadLibraries();
        this.setupTooltips();
    }
    
    bindEvents() {
        // Generate diagram from text
        document.getElementById('generateFromText').addEventListener('click', () => {
            this.generateFromText();
        });
        
        // Generate diagram from file
        document.getElementById('generateFromFile').addEventListener('click', () => {
            this.generateFromFile();
        });
        
        // Export buttons
        document.getElementById('exportXML')?.addEventListener('click', () => {
            this.exportDiagram('xml');
        });
        
        document.getElementById('exportSVG')?.addEventListener('click', () => {
            this.exportDiagram('svg');
        });
        
        document.getElementById('exportPNG')?.addEventListener('click', () => {
            this.exportDiagram('png');
        });
        
        document.getElementById('exportPDF')?.addEventListener('click', () => {
            this.exportDiagram('pdf');
        });
        
        // View in Draw.io
        document.getElementById('viewDrawio')?.addEventListener('click', () => {
            this.openInDrawio();
        });
        
        // File input change
        document.getElementById('documentFile').addEventListener('change', (e) => {
            this.handleFileSelection(e);
        });
        
        // Enter key in textarea
        document.getElementById('architectureText').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.generateFromText();
            }
        });
        
        // Search and filter events
        document.getElementById('iconSearch').addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });
        
        document.getElementById('clearSearch').addEventListener('click', () => {
            this.clearSearch();
        });
        
        document.getElementById('librarySelect').addEventListener('change', (e) => {
            this.filterByLibrary(e.target.value);
        });
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleQuickFilter(e.target.dataset.filter);
            });
        });
    }
    
    setupTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    async loadLibraries() {
        try {
            this.showMessage('Cargando librerías de iconos...', 'info');
            
            const response = await fetch('/api/libraries');
            const data = await response.json();
            
            if (data.success) {
                this.libraries = data.libraries;
                this.populateLibrarySelector();
                this.hideMessage();
                this.showMessage(`${data.libraries.length} librerías cargadas exitosamente`, 'success', 3000);
            } else {
                this.showMessage('Error cargando librerías: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error loading libraries:', error);
            this.showMessage('Error de conexión al cargar librerías', 'error');
        }
    }
    
    populateLibrarySelector() {
        const selector = document.getElementById('librarySelect');
        selector.innerHTML = '<option value="">Todas las librerías</option>';
        
        // Agrupar librerías por categoría
        const categories = {
            'Azure': this.libraries.filter(lib => lib.name.includes('azure')),
            'AWS': this.libraries.filter(lib => lib.name.includes('aws')),
            'General': this.libraries.filter(lib => lib.name.includes('general')),
            'Connections': this.libraries.filter(lib => lib.name.includes('connections')),
            'Other': this.libraries.filter(lib => !['azure', 'aws', 'general', 'connections'].some(cat => lib.name.includes(cat)))
        };
        
        Object.entries(categories).forEach(([category, libs]) => {
            if (libs.length > 0) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = `${category} (${libs.length})`;
                
                libs.sort((a, b) => a.name.localeCompare(b.name)).forEach(lib => {
                    const option = document.createElement('option');
                    option.value = lib.name;
                    option.textContent = `${lib.name} (${lib.count} iconos)`;
                    optgroup.appendChild(option);
                });
                
                selector.appendChild(optgroup);
            }
        });
    }
    
    renderLibraries() {
        const accordion = document.getElementById('librariesAccordion');
        accordion.innerHTML = '';
        
        this.libraries.forEach((library, index) => {
            const accordionItem = document.createElement('div');
            accordionItem.className = 'accordion-item';
            
            accordionItem.innerHTML = `
                <h2 class="accordion-header" id="heading${index}">
                    <button class="accordion-button collapsed" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#collapse${index}">
                        <i class="fas fa-folder me-2"></i>
                        ${library.name} 
                        <span class="badge bg-secondary ms-2">${library.count}</span>
                    </button>
                </h2>
                <div id="collapse${index}" class="accordion-collapse collapse" 
                     data-bs-parent="#librariesAccordion">
                    <div class="accordion-body">
                        <div class="icons-grid" id="icons-${library.name}">
                            <div class="text-center">
                                <div class="spinner-border spinner-border-sm" role="status">
                                    <span class="visually-hidden">Cargando...</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            accordion.appendChild(accordionItem);
            
            // Load icons when accordion is opened
            const collapseElement = accordionItem.querySelector(`#collapse${index}`);
            collapseElement.addEventListener('shown.bs.collapse', () => {
                this.loadLibraryIcons(library.name);
            });
        });
    }
    
    async loadLibraryIcons(libraryName) {
        const iconsContainer = document.getElementById(`icons-${libraryName}`);
        
        if (iconsContainer.dataset.loaded === 'true') {
            return; // Already loaded
        }
        
        try {
            const response = await fetch(`/api/icons/${libraryName}`);
            const data = await response.json();
            
            if (data.success && data.icons) {
                this.renderIcons(iconsContainer, data.icons);
                iconsContainer.dataset.loaded = 'true';
            } else {
                iconsContainer.innerHTML = `<div class="text-danger">Error: ${data.error || 'Error cargando iconos'}</div>`;
            }
        } catch (error) {
            console.error('Error loading icons:', error);
            iconsContainer.innerHTML = '<div class="text-danger">Error cargando iconos</div>';
        }
    }
    
    renderIcons(container, icons) {
        container.innerHTML = '';
        
        if (icons.length === 0) {
            container.innerHTML = '<div class="text-muted">No hay iconos disponibles</div>';
            return;
        }
        
        icons.slice(0, 50).forEach(icon => { // Limit to 50 icons for performance
            const iconElement = document.createElement('div');
            iconElement.className = 'icon-item';
            iconElement.title = icon.name;
            
            // Usar el endpoint del servidor para cargar el icono
            const iconUrl = `/api/icon/${encodeURIComponent(icon.library)}/${encodeURIComponent(icon.name)}`;
            
            iconElement.innerHTML = `
                <div class="icon-preview">
                    <img src="${iconUrl}" 
                         alt="${icon.name}" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <i class="fas fa-cube fallback-icon" style="display: none;"></i>
                </div>
                <div class="icon-name">${icon.name}</div>
            `;
            
            iconElement.addEventListener('click', () => {
                this.selectIcon(icon);
            });
            
            container.appendChild(iconElement);
        });
        
        if (icons.length > 50) {
            const moreElement = document.createElement('div');
            moreElement.className = 'text-center mt-2';
            moreElement.innerHTML = `<small class="text-muted">+${icons.length - 50} más iconos</small>`;
            container.appendChild(moreElement);
        }
    }
    
    selectIcon(icon) {
        // Add visual feedback
        const iconElements = document.querySelectorAll('.icon-item');
        iconElements.forEach(el => el.classList.remove('selected'));
        
        event.currentTarget.classList.add('selected');
        
        // Store selected icon
        this.selectedIcons.push(icon);
        
        // Show feedback
        this.showMessage(`Icono "${icon.name}" seleccionado`, 'success', 2000);
    }
    
    async generateFromText() {
        const text = document.getElementById('architectureText').value.trim();
        
        if (!text) {
            this.showMessage('Por favor, ingresa una descripción de la arquitectura', 'warning');
            return;
        }
        
        // Validar que no sea un mensaje de error de JavaScript
        if (text.includes('Uncaught') || text.includes('TypeError') || text.includes('app.js:') || text.includes('Cannot read properties')) {
            this.showMessage('Por favor, ingresa una descripción válida de la arquitectura', 'error');
            // Limpiar el campo de texto
            document.getElementById('architectureText').value = '';
            return;
        }
        
        const diagramType = document.getElementById('diagramType').value;
        
        this.showLoading();
        this.hideMessage();
        
        try {
            const response = await fetch('/api/generate-diagram', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    input_text: text,
                    diagram_type: diagramType
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentDiagramId = data.diagram_id;
                console.log('✅ Diagram generated successfully!');
                console.log('📊 Diagram ID:', data.diagram_id);
                console.log('🎯 Current ID set to:', this.currentDiagramId);
                this.showResults(data);
                this.showMessage('¡Diagrama generado exitosamente!', 'success');
            } else {
                this.showMessage('Error generando diagrama: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error generating diagram:', error);
            this.showMessage('Error de conexión al generar diagrama', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    async generateFromFile() {
        const fileInput = document.getElementById('documentFile');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showMessage('Por favor, selecciona un archivo', 'warning');
            return;
        }
        
        // Validar tipo de archivo
        const allowedTypes = ['txt', 'pdf', 'docx', 'doc', 'md', 'json'];
        const fileExt = file.name.split('.').pop().toLowerCase();
        
        if (!allowedTypes.includes(fileExt)) {
            this.showMessage(`Tipo de archivo no soportado: .${fileExt}. Formatos permitidos: ${allowedTypes.join(', ')}`, 'error');
            return;
        }
        
        // Validar tamaño
        const maxSize = 16 * 1024 * 1024; // 16MB
        if (file.size > maxSize) {
            this.showMessage(`Archivo demasiado grande (${(file.size / 1024 / 1024).toFixed(1)}MB). Máximo: 16MB`, 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        const diagramType = document.getElementById('diagramType').value;
        
        formData.append('diagram_type', diagramType);
        
        this.showLoading();
        this.hideMessage();
        
        try {
            this.showMessage(`Procesando archivo: ${file.name} (${(file.size / 1024).toFixed(1)}KB)...`, 'info');
            
            const response = await fetch('/api/upload-document', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentDiagramId = data.diagram_id;
                console.log('✅ Diagram generated successfully!');
                console.log('📊 Diagram ID:', data.diagram_id);
                console.log('🎯 Current ID set to:', this.currentDiagramId);
                this.showResults(data);
                this.showMessage(`¡Documento procesado exitosamente! Extraído: ${data.extracted_text.length} caracteres`, 'success');
            } else {
                this.showMessage('Error procesando documento: ' + data.error, 'error');
                console.error('Document processing error:', data);
            }
        } catch (error) {
            console.error('Error processing document:', error);
            this.showMessage('Error de conexión al procesar documento. Verifica que el archivo sea válido.', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    showResults(data) {
        const resultsCard = document.getElementById('resultsCard');
        resultsCard.style.display = 'block';
        resultsCard.classList.add('slide-in-up');
        
        // Show diagram preview
        this.showDiagramPreview(data.diagram_url);
        
        // Show components
        this.showComponents(data.analysis.components || []);
        
        // Show connections
        this.showConnections(data.analysis.connections || []);
        
        // Show suggestions if available
        if (data.suggestions && data.suggestions.length > 0) {
            this.showSuggestions(data.suggestions);
        }
        
        // Scroll to results
        resultsCard.scrollIntoView({ behavior: 'smooth' });
    }
    
    showDiagramPreview(diagramUrl) {
        const preview = document.getElementById('diagramPreview');
        preview.innerHTML = `
            <div class="diagram-preview">
                <div class="text-center">
                    <i class="fas fa-project-diagram fa-3x text-primary mb-3"></i>
                    <h5>Diagrama generado exitosamente</h5>
                    <p class="text-muted">Haz clic en "Abrir en Draw.io" para ver y editar el diagrama completo</p>
                    <div class="btn-group" role="group">
                        <button class="btn btn-primary" onclick="openInDrawioDesktop()">
                            <i class="fas fa-desktop me-2"></i>
                            Abrir en Draw.io Desktop
                        </button>
                        <button class="btn btn-outline-primary" onclick="app.downloadDiagram()">
                            <i class="fas fa-download me-2"></i>
                            Descargar XML
                        </button>
                        <button class="btn btn-outline-secondary" onclick="app.copyDiagramUrl()">
                            <i class="fas fa-copy me-2"></i>
                            Copiar URL
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    showComponents(components) {
        const container = document.getElementById('componentsList');
        container.innerHTML = '';
        
        if (components.length === 0) {
            container.innerHTML = '<div class="text-muted">No se identificaron componentes</div>';
            return;
        }
        
        components.forEach(component => {
            const item = document.createElement('div');
            item.className = 'component-item';
            
            item.innerHTML = `
                <div class="component-icon">
                    <i class="fas fa-cube text-primary"></i>
                </div>
                <div class="component-info">
                    <h6>${component.name}</h6>
                    <small>${component.type} - ${component.technology}</small>
                </div>
            `;
            
            container.appendChild(item);
        });
    }
    
    showConnections(connections) {
        const container = document.getElementById('connectionsList');
        container.innerHTML = '';
        
        if (connections.length === 0) {
            container.innerHTML = '<div class="text-muted">No se identificaron conexiones</div>';
            return;
        }
        
        connections.forEach(connection => {
            const item = document.createElement('div');
            item.className = 'connection-item';
            
            item.innerHTML = `
                <div class="d-flex align-items-center w-100">
                    <span class="text-truncate">${connection.from}</span>
                    <i class="fas fa-arrow-right connection-arrow"></i>
                    <span class="text-truncate">${connection.to}</span>
                </div>
                ${connection.label ? `<small class="text-muted ms-2">${connection.label}</small>` : ''}
            `;
            
            container.appendChild(item);
        });
    }
    
    showSuggestions(suggestions) {
        const section = document.getElementById('suggestionsSection');
        const list = document.getElementById('suggestionsList');
        
        list.innerHTML = '';
        suggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.innerHTML = `<i class="fas fa-lightbulb me-2"></i>${suggestion}`;
            list.appendChild(item);
        });
        
        section.style.display = 'block';
    }
    
    async exportDiagram(format) {
        if (!this.currentDiagramId) {
            this.showMessage('No hay diagrama para exportar', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`/api/export/${this.currentDiagramId}/${format}`);
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `diagram_${this.currentDiagramId}.${format}`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                this.showMessage(`Diagrama exportado como ${format.toUpperCase()}`, 'success');
            } else {
                const data = await response.json();
                this.showMessage('Error exportando: ' + data.error, 'error');
            }
        } catch (error) {
            console.error('Error exporting diagram:', error);
            this.showMessage('Error de conexión al exportar', 'error');
        }
    }
    
    async openInDrawio() {
        if (!this.currentDiagramId) {
            this.showMessage('No hay diagrama para abrir', 'warning');
            return;
        }
        
        try {
            // Primero verificar que el diagrama existe
            const diagramUrl = `${window.location.origin}/api/diagram/${this.currentDiagramId}`;
            const response = await fetch(diagramUrl);
            
            if (!response.ok) {
                const errorData = await response.json();
                this.showMessage(`Error: ${errorData.error}`, 'error');
                return;
            }
            
            // Obtener el contenido XML
            const xmlContent = await response.text();
            
            // Limpiar y validar el XML
            const cleanXml = xmlContent.trim();
            
            if (!cleanXml.startsWith('<')) {
                this.showMessage('El archivo no contiene XML válido', 'error');
                return;
            }
            
            try {
                // Método más seguro para codificar en base64
                const encoder = new TextEncoder();
                const data = encoder.encode(cleanXml);
                const base64Content = btoa(String.fromCharCode(...data));
                
                // Abrir en Draw.io con el contenido
                const drawioUrl = `https://app.diagrams.net/#R${base64Content}`;
                
                window.open(drawioUrl, '_blank');
                
            } catch (encodingError) {
                console.error('Encoding error:', encodingError);
                
                // Método alternativo: usar URL directa
                const diagramUrl = `${window.location.origin}/api/diagram/${this.currentDiagramId}`;
                const drawioUrl = `https://app.diagrams.net/?url=${encodeURIComponent(diagramUrl)}`;
                
                window.open(drawioUrl, '_blank');
            }
            
            this.showMessage('Diagrama abierto en Draw.io', 'success', 3000);
            
        } catch (error) {
            console.error('Error opening in Draw.io:', error);
            this.showMessage('Error abriendo diagrama en Draw.io', 'error');
        }
    }
    
    handleFileSelection(event) {
        const file = event.target.files[0];
        if (file) {
            const fileSize = (file.size / 1024 / 1024).toFixed(2); // MB
            const maxSize = 16; // MB
            
            if (file.size > maxSize * 1024 * 1024) {
                this.showMessage(`El archivo es demasiado grande (${fileSize}MB). Máximo permitido: ${maxSize}MB`, 'warning');
                event.target.value = '';
                return;
            }
            
            this.showMessage(`Archivo seleccionado: ${file.name} (${fileSize}MB)`, 'info', 3000);
        }
    }
    
    showLoading() {
        document.getElementById('loadingCard').style.display = 'block';
        document.getElementById('loadingCard').classList.add('fade-in');
    }
    
    hideLoading() {
        document.getElementById('loadingCard').style.display = 'none';
    }
    
    showMessage(message, type = 'info', duration = 5000) {
        const alertElement = document.getElementById('errorAlert');
        const messageElement = document.getElementById('errorMessage');
        
        // Update classes based on type
        alertElement.className = 'alert mt-3';
        switch (type) {
            case 'success':
                alertElement.classList.add('alert-success');
                break;
            case 'warning':
                alertElement.classList.add('alert-warning');
                break;
            case 'error':
                alertElement.classList.add('alert-danger');
                break;
            default:
                alertElement.classList.add('alert-info');
        }
        
        messageElement.textContent = message;
        alertElement.style.display = 'block';
        alertElement.classList.add('fade-in');
        
        if (duration > 0) {
            setTimeout(() => {
                this.hideMessage();
            }, duration);
        }
    }
    
    hideMessage() {
        const alertElement = document.getElementById('errorAlert');
        alertElement.style.display = 'none';
    }
    
    openInDrawioSimple() {
        console.log('🔍 Opening diagram in Draw.io...');
        console.log('📊 Current diagram ID:', this.currentDiagramId);
        
        if (!this.currentDiagramId) {
            console.log('❌ No current diagram ID found!');
            this.showMessage('No hay diagrama para abrir', 'warning');
            return;
        }
        
        // Método simple usando URL directa
        const diagramUrl = `${window.location.origin}/api/diagram/${this.currentDiagramId}`;
        const drawioUrl = `https://app.diagrams.net/?url=${encodeURIComponent(diagramUrl)}`;
        
        console.log('🌐 Diagram URL:', diagramUrl);
        console.log('🎯 Draw.io URL:', drawioUrl);
        
        window.open(drawioUrl, '_blank');
        this.showMessage('Abriendo en Draw.io...', 'info', 2000);
    }
    
    copyDiagramUrl() {
        if (!this.currentDiagramId) {
            this.showMessage('No hay diagrama para copiar', 'warning');
            return;
        }
        
        const diagramUrl = `${window.location.origin}/api/diagram/${this.currentDiagramId}`;
        
        navigator.clipboard.writeText(diagramUrl).then(() => {
            this.showMessage('URL copiada al portapapeles', 'success', 2000);
        }).catch(err => {
            console.error('Error copying URL:', err);
            // Fallback para navegadores que no soportan clipboard API
            const textArea = document.createElement('textarea');
            textArea.value = diagramUrl;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showMessage('URL copiada al portapapeles', 'success', 2000);
        });
    }
    
    openInDrawioSimple() {
        console.log('🔍 Opening diagram in Draw.io...');
        console.log('📊 Current diagram ID:', this.currentDiagramId);
        
        if (!this.currentDiagramId) {
            console.log('❌ No current diagram ID found!');
            this.showMessage('No hay diagrama para abrir', 'warning');
            return;
        }
        
        // Método simple usando URL directa
        const diagramUrl = `${window.location.origin}/api/diagram/${this.currentDiagramId}`;
        const drawioUrl = `https://app.diagrams.net/?url=${encodeURIComponent(diagramUrl)}`;
        
        console.log('🌐 Diagram URL:', diagramUrl);
        console.log('🎯 Draw.io URL:', drawioUrl);
        
        window.open(drawioUrl, '_blank');
        this.showMessage('Abriendo en Draw.io...', 'info', 2000);
    }
    
    copyDiagramUrl() {
        if (!this.currentDiagramId) {
            this.showMessage('No hay diagrama para copiar', 'warning');
            return;
        }
        
        const diagramUrl = `${window.location.origin}/api/diagram/${this.currentDiagramId}`;
        
        navigator.clipboard.writeText(diagramUrl).then(() => {
            this.showMessage('URL copiada al portapapeles', 'success', 2000);
        }).catch(err => {
            console.error('Error copying URL:', err);
            // Fallback para navegadores que no soportan clipboard API
            const textArea = document.createElement('textarea');
            textArea.value = diagramUrl;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showMessage('URL copiada al portapapeles', 'success', 2000);
        });
    }
    
    async downloadDiagram() {
        if (!this.currentDiagramId) {
            this.showMessage('No hay diagrama para descargar', 'warning');
            return;
        }
        
        try {
            const diagramUrl = `${window.location.origin}/api/diagram/${this.currentDiagramId}`;
            const response = await fetch(diagramUrl);
            
            if (!response.ok) {
                const errorData = await response.json();
                this.showMessage(`Error descargando: ${errorData.error}`, 'error');
                return;
            }
            
            const xmlContent = await response.text();
            const blob = new Blob([xmlContent], { type: 'application/xml' });
            const url = window.URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `diagram_${this.currentDiagramId}.xml`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showMessage('Diagrama descargado exitosamente', 'success', 3000);
            
        } catch (error) {
            console.error('Error downloading diagram:', error);
            this.showMessage('Error descargando diagrama', 'error');
        }
    }
    
    // Search and Filter Functions
    handleSearch(query) {
        clearTimeout(this.searchTimeout);
        
        this.searchTimeout = setTimeout(() => {
            this.performSearch(query);
        }, 300); // Debounce 300ms
    }
    
    async performSearch(query) {
        const searchResults = document.getElementById('searchResults');
        const searchGrid = document.getElementById('searchResultsGrid');
        const searchCount = document.getElementById('searchResultsCount');
        const iconsStatus = document.getElementById('iconsStatus');
        const librariesAccordion = document.getElementById('librariesAccordion');
        
        if (!query.trim()) {
            searchResults.style.display = 'none';
            librariesAccordion.style.display = 'none';
            iconsStatus.style.display = 'block';
            return;
        }
        
        // Show loading
        searchGrid.innerHTML = '<div class="search-loading"><i class="fas fa-spinner fa-spin me-2"></i>Buscando...</div>';
        searchResults.style.display = 'block';
        librariesAccordion.style.display = 'none';
        iconsStatus.style.display = 'none';
        
        try {
            const results = await this.searchIcons(query);
            
            if (results.length === 0) {
                searchGrid.innerHTML = `
                    <div class="search-empty">
                        <i class="fas fa-search"></i>
                        <p>No se encontraron iconos para "${query}"</p>
                        <small>Intenta con términos como: firewall, azure, database, network</small>
                    </div>
                `;
            } else {
                searchCount.textContent = results.length;
                this.renderSearchResults(results, searchGrid);
            }
        } catch (error) {
            console.error('Search error:', error);
            searchGrid.innerHTML = `
                <div class="search-empty">
                    <i class="fas fa-exclamation-triangle text-warning"></i>
                    <p>Error en la búsqueda</p>
                </div>
            `;
        }
    }
    
    async searchIcons(query) {
        const results = [];
        const queryLower = query.toLowerCase();
        
        // Buscar en todas las librerías
        for (const library of this.libraries) {
            try {
                const response = await fetch(`/api/icons/${library.name}`);
                const data = await response.json();
                
                if (data.success) {
                    const matchingIcons = data.icons.filter(icon => 
                        icon.name.toLowerCase().includes(queryLower) ||
                        library.name.toLowerCase().includes(queryLower)
                    );
                    
                    matchingIcons.forEach(icon => {
                        results.push({
                            ...icon,
                            library: library.name,
                            libraryType: library.type
                        });
                    });
                }
            } catch (error) {
                console.error(`Error searching in library ${library.name}:`, error);
            }
        }
        
        return results.slice(0, 100); // Limitar a 100 resultados
    }
    
    renderSearchResults(results, container) {
        container.innerHTML = '';
        
        results.forEach(icon => {
            const iconElement = document.createElement('div');
            iconElement.className = 'icon-item search-result';
            iconElement.title = `${icon.name} (${icon.library})`;
            
            // Usar el endpoint del servidor para cargar el icono
            const iconUrl = `/api/icon/${encodeURIComponent(icon.library)}/${encodeURIComponent(icon.name)}`;
            
            iconElement.innerHTML = `
                <div class="icon-preview">
                    <img src="${iconUrl}" 
                         alt="${icon.name}" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <i class="fas fa-cube fallback-icon" style="display: none;"></i>
                </div>
                <div class="icon-name">${icon.name}</div>
                <div class="library-badge">${icon.library.split('_').pop()}</div>
            `;
            
            iconElement.addEventListener('click', () => {
                this.selectIcon(icon);
            });
            
            container.appendChild(iconElement);
        });
    }
    
    clearSearch() {
        document.getElementById('iconSearch').value = '';
        document.getElementById('searchResults').style.display = 'none';
        document.getElementById('librariesAccordion').style.display = 'none';
        document.getElementById('iconsStatus').style.display = 'block';
        
        // Clear active filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        document.getElementById('librarySelect').value = '';
    }
    
    filterByLibrary(libraryName) {
        if (!libraryName) {
            this.clearSearch();
            return;
        }
        
        // Simulate search with library name
        document.getElementById('iconSearch').value = libraryName;
        this.performSearch(libraryName);
    }
    
    handleQuickFilter(filter) {
        // Toggle active state
        const button = document.querySelector(`[data-filter="${filter}"]`);
        const isActive = button.classList.contains('active');
        
        // Clear all active filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        if (!isActive) {
            button.classList.add('active');
            document.getElementById('iconSearch').value = filter;
            this.performSearch(filter);
        } else {
            this.clearSearch();
        }
    }
}

// Global error handler to prevent JavaScript errors from being displayed
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // Don't let the error bubble up to avoid confusion
    e.preventDefault();
});

// Initialize application when DOM is loaded
let app; // Global instance
document.addEventListener('DOMContentLoaded', () => {
    app = new DiagramsCreator();
});

// Global utility functions
window.DiagramsCreator = {
    // Health check
    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            console.log('Health check:', data);
            return data;
        } catch (error) {
            console.error('Health check failed:', error);
            return null;
        }
    },
    
    // Copy diagram URL to clipboard
    copyDiagramUrl(diagramId) {
        const url = `${window.location.origin}/api/diagram/${diagramId}`;
        navigator.clipboard.writeText(url).then(() => {
            alert('URL copiada al portapapeles');
        }).catch(err => {
            console.error('Error copying URL:', err);
        });
    }
};

// Función para abrir con Draw.io Desktop
async function openInDrawioDesktop() {
    console.log('🖥️ Opening diagram in Draw.io Desktop...');
    
    if (!app.currentDiagramId) {
        alert('No hay diagrama para abrir');
        return;
    }
    
    try {
        // Descargar el archivo automáticamente
        const diagramUrl = `${window.location.origin}/api/diagram/${app.currentDiagramId}`;
        console.log('📥 Downloading diagram from:', diagramUrl);
        
        const response = await fetch(diagramUrl);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const xmlContent = await response.text();
        console.log('✅ XML content downloaded:', xmlContent.length, 'characters');
        
        // Crear blob y descargar
        const blob = new Blob([xmlContent], { type: 'application/xml' });
        const downloadUrl = window.URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `diagram_${app.currentDiagramId}.drawio`;
        
        // Agregar al DOM temporalmente y hacer clic
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Limpiar URL objeto
        window.URL.revokeObjectURL(downloadUrl);
        
        // Mostrar instrucciones
        showDrawioDesktopInstructions();
        
    } catch (error) {
        console.error('❌ Error downloading diagram:', error);
        alert(`Error descargando diagrama: ${error.message}`);
    }
}

function showDrawioDesktopInstructions() {
    const instructions = `
        <div class="alert alert-success alert-dismissible fade show" role="alert" style="position: fixed; top: 20px; right: 20px; z-index: 1050; max-width: 400px;">
            <h6><i class="fas fa-check-circle"></i> ¡Archivo descargado!</h6>
            <p><strong>Para abrir en Draw.io Desktop:</strong></p>
            <ol class="mb-2" style="font-size: 0.9em;">
                <li>📥 Se descargó el archivo <code>.drawio</code></li>
                <li>🖥️ Abre Draw.io Desktop</li>
                <li>📂 File → Open → selecciona el archivo</li>
                <li>🎨 ¡Edita sin problemas!</li>
            </ol>
            <small>
                <strong>¿No tienes Draw.io Desktop?</strong> 
                <a href="https://github.com/jgraph/drawio-desktop/releases" target="_blank" class="alert-link">
                    Descárgalo aquí →
                </a>
            </small>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Mostrar instrucciones
    document.body.insertAdjacentHTML('beforeend', instructions);
    
    // Auto-eliminar después de 15 segundos
    setTimeout(() => {
        const alert = document.querySelector('.alert-success');
        if (alert) alert.remove();
    }, 15000);
}
