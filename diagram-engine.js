/**
 * Professional Diagram Engine - Draw.io Style
 * Replicates the professional look and feel of diagrams.net/draw.io
 */

class ProfessionalDiagramEngine {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.elements = [];
        this.connections = [];
        this.selectedElement = null;
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        
        this.init();
    }
    
    init() {
        this.setupContainer();
        this.setupEventListeners();
    }
    
    setupContainer() {
        this.container.innerHTML = '';
        this.container.style.cssText = `
            position: relative;
            width: 100%;
            height: 100%;
            background: #f8f9fa;
            background-image: 
                radial-gradient(circle, #e0e0e0 1px, transparent 1px);
            background-size: 20px 20px;
            overflow: auto;
            cursor: default;
        `;
        
        // Create SVG layer for connections
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        `;
        
        // Create diagram content wrapper
        this.contentWrapper = document.createElement('div');
        this.contentWrapper.className = 'diagram-content';
        this.contentWrapper.style.cssText = `
            position: relative;
            width: 100%;
            height: 100%;
            min-width: 3000px;
            min-height: 2000px;
            z-index: 1;
        `;
        
        // Create elements layer
        this.elementsLayer = document.createElement('div');
        this.elementsLayer.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2;
        `;
        
        this.contentWrapper.appendChild(this.svg);
        this.contentWrapper.appendChild(this.elementsLayer);
        this.container.appendChild(this.contentWrapper);
    }
    
    setupEventListeners() {
        this.container.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.container.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.container.addEventListener('mouseup', this.handleMouseUp.bind(this));
        this.container.addEventListener('click', this.handleClick.bind(this));
    }
    
    handleMouseDown(e) {
        if (e.target.classList.contains('diagram-element')) {
            this.selectedElement = e.target;
            this.isDragging = true;
            
            const rect = e.target.getBoundingClientRect();
            const containerRect = this.container.getBoundingClientRect();
            
            this.dragOffset = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
            
            e.target.style.zIndex = '1000';
            e.preventDefault();
        }
    }
    
    handleMouseMove(e) {
        if (this.isDragging && this.selectedElement) {
            const containerRect = this.container.getBoundingClientRect();
            
            // Get current zoom scale if applied
            let scale = 1;
            if (this.contentWrapper) {
                const transform = window.getComputedStyle(this.contentWrapper).transform;
                if (transform && transform !== 'none') {
                    const matrix = transform.match(/matrix\(([^)]+)\)/);
                    if (matrix) {
                        scale = parseFloat(matrix[1].split(',')[0]);
                    }
                }
            }
            
            const x = (e.clientX - containerRect.left - this.dragOffset.x) / scale;
            const y = (e.clientY - containerRect.top - this.dragOffset.y) / scale;
            
            this.selectedElement.style.left = Math.max(0, x) + 'px';
            this.selectedElement.style.top = Math.max(0, y) + 'px';
            
            this.updateConnections();
        }
    }
    
    handleMouseUp(e) {
        if (this.selectedElement) {
            this.selectedElement.style.zIndex = '10';
            this.selectedElement = null;
        }
        this.isDragging = false;
    }
    
    handleClick(e) {
        if (e.target === this.container) {
            this.clearSelection();
        }
    }
    
    clearSelection() {
        this.elementsLayer.querySelectorAll('.diagram-element').forEach(el => {
            el.classList.remove('selected');
        });
    }
    
    createElement(elementData) {
        const element = document.createElement('div');
        element.className = 'diagram-element';
        element.id = elementData.id;
        
        // Professional styling like draw.io
        element.style.cssText = `
            position: absolute;
            left: ${elementData.x}px;
            top: ${elementData.y}px;
            width: ${elementData.width || 200}px;
            height: ${elementData.height || 100}px;
            background: white;
            border: 2px solid #d0d7de;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            cursor: move;
            user-select: none;
            transition: all 0.2s ease;
            z-index: 10;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 12px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        // Create icon
        const icon = document.createElement('div');
        icon.className = 'element-icon';
        icon.style.cssText = `
            width: 36px;
            height: 36px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: ${elementData.iconPath ? 'transparent' : (elementData.color || '#0078d4')};
            border-radius: 6px;
            color: white;
            font-size: 16px;
            font-weight: bold;
        `;
        
        // Try to load icon, fallback to initial
        if (elementData.iconPath) {
            const img = document.createElement('img');
            img.src = elementData.iconPath;
            img.style.cssText = 'width: 28px; height: 28px; object-fit: contain;';
            img.onerror = () => {
                console.log('Failed to load icon:', elementData.iconPath);
                icon.style.background = elementData.color || '#0078d4';
                icon.textContent = (elementData.text || elementData.name || 'A').charAt(0);
            };
            img.onload = () => {
                console.log('Successfully loaded icon:', elementData.iconPath);
                icon.style.background = 'transparent';
            };
            icon.appendChild(img);
        } else {
            icon.style.background = elementData.color || '#0078d4';
            icon.textContent = (elementData.text || elementData.name || 'A').charAt(0);
        }
        
        // Create label
        const label = document.createElement('div');
        label.className = 'element-label';
        label.textContent = elementData.text || elementData.name || 'Element';
        label.style.cssText = `
            font-size: 12px;
            font-weight: 600;
            color: #24292f;
            text-align: center;
            line-height: 1.2;
            word-wrap: break-word;
        `;
        
        element.appendChild(icon);
        element.appendChild(label);
        
        // Hover effects
        element.addEventListener('mouseenter', () => {
            if (!this.isDragging) {
                element.style.borderColor = '#0078d4';
                element.style.boxShadow = '0 4px 12px rgba(0, 120, 212, 0.2)';
                element.style.transform = 'translateY(-2px)';
            }
        });
        
        element.addEventListener('mouseleave', () => {
            if (!this.isDragging) {
                element.style.borderColor = '#d0d7de';
                element.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                element.style.transform = 'translateY(0)';
            }
        });
        
        this.elementsLayer.appendChild(element);
        this.elements.push({
            id: elementData.id,
            element: element,
            data: elementData
        });
        
        return element;
    }
    
    createConnection(connectionData) {
        const sourceElement = this.elements.find(e => 
            e.id === connectionData.from || 
            e.id === connectionData.source ||
            e.data.id === connectionData.from ||
            e.data.id === connectionData.source
        );
        const targetElement = this.elements.find(e => 
            e.id === connectionData.to || 
            e.id === connectionData.target ||
            e.data.id === connectionData.to ||
            e.data.id === connectionData.target
        );
        
        console.log('Creating connection:', {
            connectionData,
            sourceElement: sourceElement ? sourceElement.id : 'NOT FOUND',
            targetElement: targetElement ? targetElement.id : 'NOT FOUND',
            availableElements: this.elements.map(e => e.id)
        });
        
        if (!sourceElement || !targetElement) {
            console.log('Connection skipped - missing elements');
            return;
        }
        
        const connection = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        connection.id = connectionData.id;
        
        // Create arrow marker if not exists
        if (!document.getElementById('arrow-marker')) {
            const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
            const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
            marker.id = 'arrow-marker';
            marker.setAttribute('markerWidth', '10');
            marker.setAttribute('markerHeight', '7');
            marker.setAttribute('refX', '9');
            marker.setAttribute('refY', '3.5');
            marker.setAttribute('orient', 'auto');
            marker.setAttribute('markerUnits', 'strokeWidth');
            
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', 'M0,0 L0,7 L10,3.5 z');
            path.setAttribute('fill', '#666');
            
            marker.appendChild(path);
            defs.appendChild(marker);
            this.svg.appendChild(defs);
        }
        
        // Create line
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.style.cssText = `
            stroke: #666;
            stroke-width: 2;
            marker-end: url(#arrow-marker);
            transition: stroke 0.2s ease;
        `;
        
        // Create label if exists
        let label = null;
        if (connectionData.label) {
            label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.textContent = connectionData.label;
            label.style.cssText = `
                font-size: 11px;
                fill: #666;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                text-anchor: middle;
                dominant-baseline: middle;
            `;
        }
        
        connection.appendChild(line);
        if (label) connection.appendChild(label);
        
        this.svg.appendChild(connection);
        this.connections.push({
            id: connectionData.id,
            connection: connection,
            line: line,
            label: label,
            data: {
                ...connectionData,
                source: connectionData.source || connectionData.from,
                target: connectionData.target || connectionData.to
            }
        });
        
        this.updateConnection(connectionData.id);
    }
    
    updateConnection(connectionId) {
        const conn = this.connections.find(c => c.id === connectionId);
        if (!conn) return;
        
        const sourceElement = this.elements.find(e => 
            e.id === conn.data.source || 
            e.id === conn.data.from ||
            e.data.id === conn.data.source ||
            e.data.id === conn.data.from
        );
        const targetElement = this.elements.find(e => 
            e.id === conn.data.target || 
            e.id === conn.data.to ||
            e.data.id === conn.data.target ||
            e.data.id === conn.data.to
        );
        
        if (!sourceElement || !targetElement) return;
        
        const sourceRect = sourceElement.element.getBoundingClientRect();
        const targetRect = targetElement.element.getBoundingClientRect();
        const containerRect = this.container.getBoundingClientRect();
        
        // Calculate connection points (center of elements)
        const sourceX = sourceRect.left - containerRect.left + sourceRect.width / 2;
        const sourceY = sourceRect.top - containerRect.top + sourceRect.height / 2;
        const targetX = targetRect.left - containerRect.left + targetRect.width / 2;
        const targetY = targetRect.top - containerRect.top + targetRect.height / 2;
        
        // Update line
        conn.line.setAttribute('x1', sourceX);
        conn.line.setAttribute('y1', sourceY);
        conn.line.setAttribute('x2', targetX);
        conn.line.setAttribute('y2', targetY);
        
        // Update label position
        if (conn.label) {
            const midX = (sourceX + targetX) / 2;
            const midY = (sourceY + targetY) / 2;
            conn.label.setAttribute('x', midX);
            conn.label.setAttribute('y', midY);
        }
    }
    
    updateConnections() {
        this.connections.forEach(conn => {
            this.updateConnection(conn.id);
        });
    }
    
    renderDiagram(diagramData) {
        // Clear existing elements
        if (this.elementsLayer) {
            this.elementsLayer.innerHTML = '';
        }
        if (this.svg) {
            this.svg.innerHTML = '';
        }
        this.elements = [];
        this.connections = [];
        
        // Create elements
        diagramData.elements.forEach(elementData => {
            this.createElement(elementData);
        });
        
        // Create connections
        console.log('Creating connections:', diagramData.connections);
        diagramData.connections.forEach(connectionData => {
            console.log('Creating connection:', connectionData);
            this.createConnection(connectionData);
        });
        
        // Update all connections
        this.updateConnections();
    }
    
    exportDiagram() {
        // Create a copy of the diagram data
        const exportData = {
            elements: this.elements.map(e => ({
                id: e.id,
                x: parseInt(e.element.style.left),
                y: parseInt(e.element.style.top),
                width: parseInt(e.element.style.width),
                height: parseInt(e.element.style.height),
                text: e.data.text,
                type: e.data.type,
                color: e.data.color
            })),
            connections: this.connections.map(c => ({
                id: c.id,
                source: c.data.source,
                target: c.data.target,
                label: c.data.label
            }))
        };
        
        return exportData;
    }
}

// Make it globally available
window.ProfessionalDiagramEngine = ProfessionalDiagramEngine;
