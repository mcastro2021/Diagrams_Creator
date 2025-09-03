// Variables globales
let currentDiagram = null;
let selectedNode = null;
let isDragging = false;
let dragOffset = { x: 0, y: 0 };
let templates = [];
let diagrams = [];
let availableIcons = {};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando Diagramas Creator...');
    
    // Inicializar Mermaid
    mermaid.initialize({ 
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose'
    });
    
    // Cargar datos iniciales
    loadTemplates();
    loadDiagrams();
    loadAvailableIcons();
    
    // Configurar eventos
    setupEventListeners();
    
    console.log('✅ Aplicación inicializada correctamente');
});

// Configurar event listeners
function setupEventListeners() {
    const canvas = document.getElementById('diagramCanvas');
    
    // Canvas events
    canvas.addEventListener('click', handleCanvasClick);
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('contextmenu', handleContextMenu);
    
    // Keyboard events
    document.addEventListener('keydown', handleKeyDown);
    
    // Window events
    window.addEventListener('resize', handleWindowResize);
}

// Cargar plantillas disponibles
async function loadTemplates() {
    try {
        showLoading(true);
        const response = await fetch('/templates');
        const data = await response.json();
        
        if (data.success) {
            templates = data.templates;
            renderTemplates();
        } else {
            showError('Error cargando plantillas: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión al cargar plantillas');
    } finally {
        showLoading(false);
    }
}

// Renderizar plantillas en el sidebar
function renderTemplates() {
    const container = document.getElementById('templatesList');
    container.innerHTML = '';
    
    templates.forEach(template => {
        const templateElement = document.createElement('div');
        templateElement.className = 'template-item';
        templateElement.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${template.icon} template-icon"></i>
                <div>
                    <div class="fw-bold">${template.name}</div>
                    <small class="text-muted">${template.description}</small>
                </div>
            </div>
        `;
        
        templateElement.addEventListener('click', () => createDiagramFromTemplate(template.id));
        container.appendChild(templateElement);
    });
}

// Cargar diagramas existentes
async function loadDiagrams() {
    try {
        const response = await fetch('/diagrams');
        const data = await response.json();
        
        if (data.success) {
            diagrams = data.diagrams;
            renderDiagrams();
        }
    } catch (error) {
        console.error('Error cargando diagramas:', error);
    }
}

// Renderizar lista de diagramas
function renderDiagrams() {
    const container = document.getElementById('diagramsList');
    container.innerHTML = '';
    
    if (diagrams.length === 0) {
        container.innerHTML = '<p class="text-muted small">No hay diagramas guardados</p>';
        return;
    }
    
    diagrams.forEach(diagram => {
        const diagramElement = document.createElement('div');
        diagramElement.className = 'diagram-item';
        if (currentDiagram && currentDiagram.id === diagram.id) {
            diagramElement.classList.add('active');
        }
        
        const createdDate = new Date(diagram.created_at).toLocaleDateString();
        
        diagramElement.innerHTML = `
            <div class="diagram-title">${diagram.title}</div>
            <div class="diagram-meta">
                <small class="text-muted">
                    <i class="fas fa-calendar me-1"></i>${createdDate}
                    <i class="fas fa-tag ms-2 me-1"></i>${diagram.type}
                    ${diagram.ai_generated ? '<i class="fas fa-magic ms-2 text-success" title="Generado con IA"></i>' : ''}
                </small>
            </div>
        `;
        
        diagramElement.addEventListener('click', () => loadDiagram(diagram.id));
        container.appendChild(diagramElement);
    });
}

// Cargar iconos disponibles
async function loadAvailableIcons() {
    try {
        const response = await fetch('/api/icons');
        const data = await response.json();
        
        if (data.success) {
            availableIcons = data.icons;
            console.log('📦 Iconos cargados:', Object.keys(availableIcons).length, 'categorías');
        }
    } catch (error) {
        console.error('Error cargando iconos:', error);
        // Fallback: usar iconos básicos
        availableIcons = {
            'basic': ['rectangle', 'circle', 'diamond', 'ellipse'],
            'aws': ['ec2', 'lambda', 's3', 'rds'],
            'azure': ['vm', 'function', 'storage', 'sql']
        };
    }
}

// Crear diagrama desde plantilla
async function createDiagramFromTemplate(templateId) {
    try {
        showLoading(true);
        
        const response = await fetch('/create_diagram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: templateId,
                title: `Nuevo ${templates.find(t => t.id === templateId)?.name || 'Diagrama'}`
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentDiagram = data.diagram;
            renderDiagram(currentDiagram.data);
            loadDiagrams(); // Actualizar lista
            showSuccess('Diagrama creado exitosamente');
        } else {
            showError('Error creando diagrama: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión');
    } finally {
        showLoading(false);
    }
}

// Generar diagrama con IA
async function generateAIDiagram() {
    const title = document.getElementById('aiTitle').value.trim();
    const type = document.getElementById('aiType').value;
    const description = document.getElementById('aiDescription').value.trim();
    
    if (!description) {
        showError('Por favor, proporciona una descripción del diagrama');
        return;
    }
    
    try {
        showLoading(true, 'Generando diagrama con IA...');
        
        const response = await fetch('/generate_ai_diagram', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title || 'Diagrama Generado por IA',
                type: type,
                description: description
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentDiagram = data.diagram;
            renderDiagram(currentDiagram.data);
            loadDiagrams(); // Actualizar lista
            
            // Cerrar modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('aiModal'));
            modal.hide();
            
            // Limpiar formulario
            document.getElementById('aiTitle').value = '';
            document.getElementById('aiDescription').value = '';
            document.getElementById('aiType').value = 'auto';
            
            showSuccess('¡Diagrama generado exitosamente con IA!');
        } else {
            showError('Error generando diagrama: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión con el servidor');
    } finally {
        showLoading(false);
    }
}

// Renderizar diagrama en el canvas
function renderDiagram(diagramData) {
    const canvas = document.getElementById('diagramCanvas');
    canvas.innerHTML = '';
    canvas.classList.add('active');
    
    if (!diagramData || !diagramData.nodes) {
        console.error('Datos de diagrama inválidos:', diagramData);
        return;
    }
    
    // Renderizar nodos
    diagramData.nodes.forEach(node => {
        createNodeElement(node);
    });
    
    // Renderizar conexiones
    if (diagramData.edges) {
        diagramData.edges.forEach(edge => {
            createConnectionElement(edge, diagramData.nodes);
        });
    }
    
    console.log('📊 Diagrama renderizado:', diagramData.nodes.length, 'nodos,', (diagramData.edges || []).length, 'conexiones');
}

// Crear elemento de nodo
function createNodeElement(node) {
    const canvas = document.getElementById('diagramCanvas');
    const nodeElement = document.createElement('div');
    
    nodeElement.className = `diagram-node ${node.type || 'rectangle'}`;
    nodeElement.id = node.id;
    
    // Posición y tamaño
    nodeElement.style.left = (node.x || 100) + 'px';
    nodeElement.style.top = (node.y || 100) + 'px';
    nodeElement.style.width = (node.width || 120) + 'px';
    nodeElement.style.height = (node.height || 60) + 'px';
    nodeElement.style.position = 'absolute';
    nodeElement.style.zIndex = '100';
    
    // Aplicar estilos personalizados si existen
    if (node.style) {
        Object.keys(node.style).forEach(key => {
            nodeElement.style[key] = node.style[key];
        });
    }
    
    // Contenido del nodo según el tipo
    if (node.type === 'azure_icon' && node.icon) {
        // Nodo con icono Azure SVG
        nodeElement.innerHTML = `
            <div class="icon-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 8px;">
                <img src="${node.icon}" alt="${node.text}" style="max-width: 48px; max-height: 48px; object-fit: contain; margin-bottom: 4px;" onerror="this.style.display='none';">
                <div class="node-text" style="font-size: 10px; text-align: center; line-height: 1.1; font-weight: 500; color: #333;">${node.text || node.id}</div>
            </div>
        `;
        nodeElement.style.backgroundColor = '#ffffff';
        nodeElement.style.border = '2px solid #0078d4';
        nodeElement.style.borderRadius = '8px';
        nodeElement.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
    } else if (node.type === 'network_box') {
        // Caja de red (VNet, Subnet, etc.) - Mejorada para contener elementos
        nodeElement.innerHTML = `
            <div class="network-box-header" style="background: rgba(0,120,212,0.1); padding: 4px 8px; border-bottom: 1px solid #0078d4; font-size: 11px; font-weight: bold; color: #0078d4; text-align: center;">
                ${node.text || node.id}
            </div>
            <div class="network-box-content" style="padding: 8px; height: calc(100% - 24px); position: relative; overflow: hidden;">
                <!-- Los elementos internos se posicionarán aquí -->
            </div>
        `;
        nodeElement.style.backgroundColor = 'rgba(230, 243, 255, 0.3)';
        nodeElement.style.border = '2px solid #0078d4';
        nodeElement.style.borderRadius = '8px';
        nodeElement.style.position = 'absolute';
        nodeElement.style.overflow = 'visible';
        nodeElement.style.zIndex = '50';
        
        // Añadir clase CSS para estilos adicionales
        nodeElement.classList.add('network-container');
        
    } else if (node.type === 'text') {
        // Nodo de texto puro
        nodeElement.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; text-align: center; font-weight: bold; color: #333;">
                ${node.text || node.id}
            </div>
        `;
        nodeElement.style.backgroundColor = 'transparent';
        nodeElement.style.border = 'none';
    } else if (node.type === 'icon' && node.icon) {
        // Nodo con icono genérico
        nodeElement.innerHTML = `
            <div class="icon-container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 4px;">
                <img src="${node.icon}" alt="${node.text}" style="max-width: 60%; max-height: 60%; object-fit: contain; margin-bottom: 0.25rem;" onerror="this.style.display='none';">
                <div class="node-text" style="font-size: 0.75rem; text-align: center; line-height: 1.2;">${node.text || node.id}</div>
            </div>
        `;
    } else {
        // Nodo de texto normal
        nodeElement.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; text-align: center; padding: 4px;">
                ${node.text || node.id}
            </div>
        `;
        nodeElement.style.backgroundColor = '#ffffff';
        nodeElement.style.border = '1px solid #ccc';
        nodeElement.style.borderRadius = '4px';
    }
    
    // Estilos comunes para todos los nodos
    nodeElement.style.boxSizing = 'border-box';
    nodeElement.style.cursor = 'pointer';
    nodeElement.style.userSelect = 'none';
    
    // Eventos del nodo
    nodeElement.addEventListener('click', () => selectNode(nodeElement));
    nodeElement.addEventListener('mousedown', (e) => startDragging(nodeElement, e));
    
    canvas.appendChild(nodeElement);
    
    console.log(`📦 Nodo creado: ${node.id} (${node.type}) en (${node.x}, ${node.y})`);
}

// Crear elemento de conexión
function createConnectionElement(edge, nodes) {
    const canvas = document.getElementById('diagramCanvas');
    const fromNode = document.getElementById(edge.from);
    const toNode = document.getElementById(edge.to);
    
    if (!fromNode || !toNode) {
        console.warn('Nodos no encontrados para la conexión:', edge);
        return;
    }
    
    console.log(`🔗 Creando conexión: ${edge.from} -> ${edge.to}`);
    
    const connectionElement = document.createElement('div');
    connectionElement.className = 'diagram-connection';
    connectionElement.id = edge.id;
    
    // Calcular posiciones relativas al canvas
    const fromRect = fromNode.getBoundingClientRect();
    const toRect = toNode.getBoundingClientRect();
    const canvasRect = canvas.getBoundingClientRect();
    
    // Posiciones absolutas dentro del canvas
    const fromX = fromRect.left - canvasRect.left + fromRect.width / 2;
    const fromY = fromRect.top - canvasRect.top + fromRect.height / 2;
    const toX = toRect.left - canvasRect.left + toRect.width / 2;
    const toY = toRect.top - canvasRect.top + toRect.height / 2;
    
    console.log(`📍 Posiciones: desde (${fromX}, ${fromY}) hasta (${toX}, ${toY})`);
    
    // Crear SVG para la línea con flecha
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.style.position = 'absolute';
    svg.style.left = '0';
    svg.style.top = '0';
    svg.style.width = '100%';
    svg.style.height = '100%';
    svg.style.pointerEvents = 'none';
    svg.style.zIndex = '1000';
    
    // Calcular dimensiones del SVG para cubrir toda la conexión
    const svgWidth = Math.max(Math.abs(toX - fromX), 100);
    const svgHeight = Math.max(Math.abs(toY - fromY), 100);
    svg.setAttribute('width', svgWidth);
    svg.setAttribute('height', svgHeight);
    
    // Definiciones para la flecha
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', `arrowhead-${edge.id}`);
    marker.setAttribute('markerWidth', '10');
    marker.setAttribute('markerHeight', '7');
    marker.setAttribute('refX', '9');
    marker.setAttribute('refY', '3.5');
    marker.setAttribute('orient', 'auto');
    
    const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
    polygon.setAttribute('points', '0 0, 10 3.5, 0 7');
    polygon.setAttribute('fill', '#0d6efd');
    
    marker.appendChild(polygon);
    defs.appendChild(marker);
    svg.appendChild(defs);
    
    // Crear la línea de conexión
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', fromX);
    line.setAttribute('y1', fromY);
    line.setAttribute('x2', toX);
    line.setAttribute('y2', toY);
    line.setAttribute('stroke', '#0d6efd');
    line.setAttribute('stroke-width', '3');
    line.setAttribute('marker-end', `url(#arrowhead-${edge.id})`);
    line.setAttribute('stroke-dasharray', edge.type === 'dashed' ? '5,5' : 'none');
    
    svg.appendChild(line);
    
    // Añadir etiqueta de la conexión si existe
    if (edge.label) {
        const labelX = (fromX + toX) / 2;
        const labelY = (fromY + toY) / 2 - 15;
        
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', labelX);
        label.setAttribute('y', labelY);
        label.setAttribute('text-anchor', 'middle');
        label.setAttribute('font-family', 'Arial');
        label.setAttribute('font-size', '12');
        label.setAttribute('fill', '#333');
        label.setAttribute('font-weight', 'bold');
        
        // Dividir el texto en múltiples líneas si es necesario
        const lines = edge.label.split('\n');
        lines.forEach((lineText, index) => {
            const tspan = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
            tspan.setAttribute('x', labelX);
            tspan.setAttribute('dy', index === 0 ? '0' : '1.2em');
            tspan.textContent = lineText;
            label.appendChild(tspan);
        });
        
        // Fondo para la etiqueta
        const labelBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        const labelWidth = Math.max(...lines.map(l => l.length)) * 8;
        const labelHeight = lines.length * 16;
        labelBg.setAttribute('x', labelX - labelWidth / 2 - 5);
        labelBg.setAttribute('y', labelY - 12);
        labelBg.setAttribute('width', labelWidth + 10);
        labelBg.setAttribute('height', labelHeight + 8);
        labelBg.setAttribute('fill', 'white');
        labelBg.setAttribute('stroke', '#ccc');
        labelBg.setAttribute('stroke-width', '1');
        labelBg.setAttribute('rx', '3');
        
        svg.appendChild(labelBg);
        svg.appendChild(label);
    }
    
    connectionElement.appendChild(svg);
    
    // Posicionar el elemento de conexión
    connectionElement.style.position = 'absolute';
    connectionElement.style.left = '0';
    connectionElement.style.top = '0';
    connectionElement.style.width = '100%';
    connectionElement.style.height = '100%';
    connectionElement.style.pointerEvents = 'none';
    connectionElement.style.zIndex = '1000';
    
    canvas.appendChild(connectionElement);
    
    console.log(`✅ Conexión creada: ${edge.from} -> ${edge.to} (${edge.label || 'sin etiqueta'})`);
}

// Seleccionar nodo
function selectNode(nodeElement) {
    // Deseleccionar nodo anterior
    if (selectedNode) {
        selectedNode.classList.remove('selected');
    }
    
    // Seleccionar nuevo nodo
    selectedNode = nodeElement;
    nodeElement.classList.add('selected');
    
    console.log('Nodo seleccionado:', nodeElement.id);
}

// Iniciar arrastre
function startDragging(nodeElement, event) {
    isDragging = true;
    selectedNode = nodeElement;
    
    const rect = nodeElement.getBoundingClientRect();
    dragOffset.x = event.clientX - rect.left;
    dragOffset.y = event.clientY - rect.top;
    
    nodeElement.style.cursor = 'grabbing';
    document.body.style.cursor = 'grabbing';
}

// Manejar eventos del canvas
function handleCanvasClick(event) {
    if (selectedNode && !event.target.classList.contains('diagram-node')) {
        selectedNode.classList.remove('selected');
        selectedNode = null;
    }
}

function handleMouseDown(event) {
    if (event.target.classList.contains('diagram-node')) {
        startDragging(event.target, event);
    }
}

function handleMouseMove(event) {
    if (isDragging && selectedNode) {
        const canvas = document.getElementById('diagramCanvas');
        const canvasRect = canvas.getBoundingClientRect();
        
        const newX = event.clientX - canvasRect.left - dragOffset.x;
        const newY = event.clientY - canvasRect.top - dragOffset.y;
        
        selectedNode.style.left = Math.max(0, newX) + 'px';
        selectedNode.style.top = Math.max(0, newY) + 'px';
        
        // Actualizar conexiones
        updateConnections();
    }
}

function handleMouseUp(event) {
    if (isDragging) {
        isDragging = false;
        document.body.style.cursor = 'default';
        
        if (selectedNode) {
            selectedNode.style.cursor = 'move';
            
            // Guardar posición actualizada
            if (currentDiagram) {
                saveDiagramChanges();
            }
        }
    }
}

function handleContextMenu(event) {
    event.preventDefault();
    // Aquí se puede implementar un menú contextual
}

function handleKeyDown(event) {
    if (event.key === 'Delete' && selectedNode) {
        deleteSelectedNode();
    } else if (event.key === 'Escape') {
        if (selectedNode) {
            selectedNode.classList.remove('selected');
            selectedNode = null;
        }
    }
}

function handleWindowResize() {
    // Actualizar conexiones cuando cambie el tamaño de la ventana
    updateConnections();
}

// Actualizar conexiones
function updateConnections() {
    const connections = document.querySelectorAll('.diagram-connection');
    connections.forEach(connection => {
        // Reposicionar conexiones basado en las nuevas posiciones de los nodos
        // Esta es una implementación simplificada
        connection.remove();
    });
    
    // Recrear conexiones si hay datos del diagrama
    if (currentDiagram && currentDiagram.data && currentDiagram.data.edges) {
        currentDiagram.data.edges.forEach(edge => {
            createConnectionElement(edge, currentDiagram.data.nodes);
        });
    }
}

// Eliminar nodo seleccionado
function deleteSelectedNode() {
    if (!selectedNode || !currentDiagram) return;
    
    const nodeId = selectedNode.id;
    
    // Eliminar nodo del DOM
    selectedNode.remove();
    selectedNode = null;
    
    // Eliminar nodo de los datos
    currentDiagram.data.nodes = currentDiagram.data.nodes.filter(node => node.id !== nodeId);
    
    // Eliminar conexiones relacionadas
    currentDiagram.data.edges = currentDiagram.data.edges.filter(edge => 
        edge.from !== nodeId && edge.to !== nodeId
    );
    
    // Actualizar conexiones
    updateConnections();
    
    // Guardar cambios
    saveDiagramChanges();
    
    showSuccess('Nodo eliminado');
}

// Guardar cambios del diagrama
async function saveDiagramChanges() {
    if (!currentDiagram) return;
    
    try {
        // Actualizar posiciones de nodos
        const nodes = document.querySelectorAll('.diagram-node');
        nodes.forEach(nodeElement => {
            const nodeData = currentDiagram.data.nodes.find(n => n.id === nodeElement.id);
            if (nodeData) {
                nodeData.x = parseInt(nodeElement.style.left);
                nodeData.y = parseInt(nodeElement.style.top);
            }
        });
        
        const response = await fetch(`/diagram/${currentDiagram.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: currentDiagram.data,
                title: currentDiagram.title
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentDiagram = data.diagram;
            console.log('💾 Diagrama guardado');
        }
    } catch (error) {
        console.error('Error guardando diagrama:', error);
    }
}

// Cargar diagrama específico
async function loadDiagram(diagramId) {
    try {
        showLoading(true);
        
        const response = await fetch(`/diagram/${diagramId}`);
        const data = await response.json();
        
        if (data.success) {
            currentDiagram = data.diagram;
            renderDiagram(currentDiagram.data);
            renderDiagrams(); // Actualizar lista para mostrar el activo
            showSuccess(`Diagrama "${currentDiagram.title}" cargado`);
        } else {
            showError('Error cargando diagrama: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión');
    } finally {
        showLoading(false);
    }
}

// Subir archivo
async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Por favor, selecciona un archivo');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoading(true, 'Procesando archivo...');
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Crear nuevo diagrama con los datos procesados
            if (data.diagram_data) {
                currentDiagram = {
                    id: 'temp_' + Date.now(),
                    title: data.title || 'Diagrama desde Archivo',
                    type: data.type || 'flowchart',
                    data: data.diagram_data,
                    created_at: new Date().toISOString()
                };
                
                renderDiagram(currentDiagram.data);
                showSuccess('Archivo procesado exitosamente');
            }
        } else {
            showError('Error procesando archivo: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión');
    } finally {
        showLoading(false);
        fileInput.value = ''; // Limpiar input
    }
}

// Procesar texto libre
async function processText() {
    const textInput = document.getElementById('textInput');
    const text = textInput.value.trim();
    
    if (!text) {
        showError('Por favor, ingresa algún texto');
        return;
    }
    
    try {
        showLoading(true, 'Procesando texto...');
        
        const response = await fetch('/process_text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Crear nuevo diagrama con los datos procesados
            if (data.diagram_data) {
                currentDiagram = {
                    id: 'temp_' + Date.now(),
                    title: data.title || 'Diagrama desde Texto',
                    type: data.type || 'flowchart',
                    data: data.diagram_data,
                    created_at: new Date().toISOString()
                };
                
                renderDiagram(currentDiagram.data);
                showSuccess('Texto procesado exitosamente');
            }
        } else {
            showError('Error procesando texto: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión');
    } finally {
        showLoading(false);
        textInput.value = ''; // Limpiar input
    }
}

// Exportar diagrama
async function exportDiagram(format) {
    if (!currentDiagram) {
        showError('No hay diagrama para exportar');
        return;
    }
    
    try {
        showLoading(true, `Exportando como ${format.toUpperCase()}...`);
        
        const response = await fetch(`/export/${currentDiagram.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ format: format })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Crear enlace de descarga
            const link = document.createElement('a');
            link.href = data.download_url;
            link.download = data.filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showSuccess(`Diagrama exportado como ${format.toUpperCase()}`);
        } else {
            showError('Error exportando diagrama: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Error de conexión');
    } finally {
        showLoading(false);
    }
}

// Utilidades de UI
function showLoading(show, message = 'Cargando...') {
    const spinner = document.getElementById('loadingSpinner');
    const messageElement = spinner.querySelector('p');
    
    if (show) {
        messageElement.textContent = message;
        spinner.style.display = 'flex';
    } else {
        spinner.style.display = 'none';
    }
}

function showSuccess(message) {
    showToast(message, 'success');
}

function showError(message) {
    showToast(message, 'error');
    console.error('Error:', message);
}

function showToast(message, type = 'info') {
    // Crear toast dinámicamente
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toastElement = document.createElement('div');
    toastElement.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'primary'} border-0`;
    toastElement.setAttribute('role', 'alert');
    toastElement.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastElement);
    
    const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
    toast.show();
    
    // Eliminar toast después de que se oculte
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    return container;
}

// Editar texto del nodo
function editNodeText(nodeElement, nodeData) {
    if (!currentDiagram) return;
    
    const currentText = nodeData.text || nodeData.id;
    const newText = prompt('Editar texto del nodo:', currentText);
    
    if (newText !== null && newText.trim() !== '') {
        // Actualizar datos del nodo
        nodeData.text = newText.trim();
        
        // Actualizar elemento visual
        if (nodeData.type === 'icon' && nodeData.icon) {
            const textElement = nodeElement.querySelector('.node-text');
            if (textElement) {
                textElement.textContent = newText.trim();
            }
        } else {
            nodeElement.textContent = newText.trim();
        }
        
        // Guardar cambios
        saveDiagramChanges();
        
        showSuccess('Texto del nodo actualizado');
    }
}

// Añadir nuevo nodo al canvas
function addNodeToCanvas(type = 'rectangle', text = 'Nuevo Nodo') {
    if (!currentDiagram) {
        showError('Primero crea o carga un diagrama');
        return;
    }
    
    const canvas = document.getElementById('diagramCanvas');
    const canvasRect = canvas.getBoundingClientRect();
    
    // Posición aleatoria en el canvas
    const x = Math.random() * (canvasRect.width - 120);
    const y = Math.random() * (canvasRect.height - 80);
    
    const nodeData = {
        id: generateUniqueId(),
        type: type,
        text: text,
        x: x,
        y: y,
        width: 120,
        height: 60
    };
    
    // Añadir nodo al diagrama actual
    currentDiagram.data.nodes.push(nodeData);
    
    // Crear elemento visual
    createNodeElement(nodeData);
    
    // Guardar cambios
    saveDiagramChanges();
    
    showSuccess('Nodo añadido al diagrama');
}

// Conectar dos nodos
function connectNodes(fromNodeId, toNodeId, label = '') {
    if (!currentDiagram) return;
    
    // Verificar que los nodos existen
    const fromNode = currentDiagram.data.nodes.find(n => n.id === fromNodeId);
    const toNode = currentDiagram.data.nodes.find(n => n.id === toNodeId);
    
    if (!fromNode || !toNode) {
        showError('Nodos no encontrados');
        return;
    }
    
    // Crear conexión
    const connectionData = {
        id: `edge_${Date.now()}`,
        from: fromNodeId,
        to: toNodeId,
        text: label
    };
    
    // Inicializar edges si no existe
    if (!currentDiagram.data.edges) {
        currentDiagram.data.edges = [];
    }
    
    // Añadir conexión
    currentDiagram.data.edges.push(connectionData);
    
    // Crear elemento visual
    createConnectionElement(connectionData, currentDiagram.data.nodes);
    
    // Guardar cambios
    saveDiagramChanges();
    
    showSuccess('Conexión creada');
}

// Funciones de utilidad
function generateUniqueId() {
    return 'node_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function debounce(func, wait) {
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

// Exportar funciones globales para uso en HTML
window.generateAIDiagram = generateAIDiagram;
window.uploadFile = uploadFile;
window.processText = processText;
window.exportDiagram = exportDiagram;
