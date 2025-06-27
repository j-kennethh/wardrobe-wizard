document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('fitting-room-canvas');
    let selectedElement = null;
    let zIndexCounter = 1;
    let currentRotation = 0;
    let currentScale = 1;
    
    // Initialize interact.js on the canvas
    interact(canvas).dropzone({
        accept: '.draggable-item',
        ondrop: function(event) {
            // This will handle dropping items (if needed)
        }
    });
    
    // Handle clothing selection from modal
    document.getElementById('add-selected-items').addEventListener('click', function() {
        const checkboxes = document.querySelectorAll('#clothing-selection-form input[name="items"]:checked');
        
        checkboxes.forEach(checkbox => {
            const itemId = checkbox.value;
            const itemCard = checkbox.closest('.card');
            const itemImg = itemCard.querySelector('.card-img-top').src;
            const itemTitle = itemCard.querySelector('.form-check-label').textContent.trim();
            
            addItemToCanvas(itemId, itemImg, itemTitle);
        });
        
        // Close the modal
        bootstrap.Modal.getInstance(document.getElementById('clothingSelectorModal')).hide();
    });
    
    // Add an item to the canvas
    function addItemToCanvas(itemId, itemImg, itemTitle) {
        const itemElement = document.createElement('div');
        itemElement.className = 'draggable-item';
        itemElement.dataset.itemId = itemId;
        itemElement.style.position = 'absolute';
        itemElement.style.left = '100px';
        itemElement.style.top = '100px';
        itemElement.style.width = '150px';
        itemElement.style.zIndex = zIndexCounter++;
        itemElement.style.transform = 'rotate(0deg) scale(1)';
        itemElement.style.cursor = 'move';
        
        itemElement.innerHTML = `
            <img src="${itemImg}" alt="${itemTitle}" style="width: 100%; height: auto; pointer-events: none;">
            <div class="item-controls" style="position: absolute; top: -25px; left: 0; display: none;">
                <button class="btn btn-sm btn-danger delete-item">×</button>
            </div>
        `;
        
        canvas.appendChild(itemElement);
        
        // Make the item draggable and resizable
        setupInteract(itemElement);
        
        // Add event listeners for the item
        itemElement.addEventListener('click', function(e) {
            if (e.target.classList.contains('delete-item')) return;
            
            // Select this item
            selectItem(itemElement);
        });
        
        itemElement.querySelector('.delete-item').addEventListener('click', function() {
            itemElement.remove();
        });
        
        // Show controls on hover
        itemElement.addEventListener('mouseenter', function() {
            this.querySelector('.item-controls').style.display = 'block';
        });
        
        itemElement.addEventListener('mouseleave', function() {
            if (this !== selectedElement) {
                this.querySelector('.item-controls').style.display = 'none';
            }
        });
        
        // Select this item by default
        selectItem(itemElement);
    }
    
    // Set up interact.js for an item
    function setupInteract(element) {
        interact(element)
            .draggable({
                inertia: true,
                modifiers: [
                    interact.modifiers.restrictRect({
                        restriction: 'parent',
                        endOnly: true
                    })
                ],
                autoScroll: true,
                listeners: {
                    move: dragMoveListener
                }
            })
            .resizable({
                edges: { left: true, right: true, bottom: true, top: true },
                modifiers: [
                    interact.modifiers.restrictEdges({
                        outer: 'parent'
                    }),
                    interact.modifiers.aspectRatio({
                        ratio: 'preserve'
                    })
                ],
                listeners: {
                    move: function (event) {
                        let { x, y } = event.target.dataset;
                        
                        x = (parseFloat(x) || 0) + event.deltaRect.left;
                        y = (parseFloat(y) || 0) + event.deltaRect.top;
                        
                        Object.assign(event.target.style, {
                            width: `${event.rect.width}px`,
                            height: `${event.rect.height}px`,
                            transform: `rotate(${currentRotation}deg) scale(${currentScale})`
                        });
                        
                        Object.assign(event.target.dataset, { x, y });
                    }
                }
            });
    }
    
    // Drag move listener
    function dragMoveListener(event) {
        const target = event.target;
        const x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
        const y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;
        
        target.style.transform = `translate(${x}px, ${y}px) rotate(${currentRotation}deg) scale(${currentScale})`;
        
        target.setAttribute('data-x', x);
        target.setAttribute('data-y', y);
    }
    
    // Select an item
    function selectItem(element) {
        if (selectedElement) {
            selectedElement.querySelector('.item-controls').style.display = 'none';
            selectedElement.style.boxShadow = 'none';
        }
        
        selectedElement = element;
        element.querySelector('.item-controls').style.display = 'block';
        element.style.boxShadow = '0 0 0 2px #0d6efd';
        element.style.zIndex = zIndexCounter++;
        
        // Get current transform values
        const transform = element.style.transform;
        const rotationMatch = transform.match(/rotate\((\d+)deg\)/);
        const scaleMatch = transform.match(/scale\(([\d.]+)\)/);
        
        currentRotation = rotationMatch ? parseInt(rotationMatch[1]) : 0;
        currentScale = scaleMatch ? parseFloat(scaleMatch[1]) : 1;
        
        // Update sliders
        document.getElementById('rotation-slider').value = currentRotation;
        document.getElementById('rotation-value').textContent = currentRotation;
        document.getElementById('scale-slider').value = currentScale * 100;
        document.getElementById('scale-value').textContent = Math.round(currentScale * 100);
    }
    
    // Rotation slider
    document.getElementById('rotation-slider').addEventListener('input', function() {
        if (!selectedElement) return;
        
        currentRotation = this.value;
        document.getElementById('rotation-value').textContent = currentRotation;
        
        const x = parseFloat(selectedElement.getAttribute('data-x')) || 0;
        const y = parseFloat(selectedElement.getAttribute('data-y')) || 0;
        
        selectedElement.style.transform = `translate(${x}px, ${y}px) rotate(${currentRotation}deg) scale(${currentScale})`;
    });
    
    // Scale slider
    document.getElementById('scale-slider').addEventListener('input', function() {
        if (!selectedElement) return;
        
        currentScale = this.value / 100;
        document.getElementById('scale-value').textContent = this.value;
        
        const x = parseFloat(selectedElement.getAttribute('data-x')) || 0;
        const y = parseFloat(selectedElement.getAttribute('data-y')) || 0;
        
        selectedElement.style.transform = `translate(${x}px, ${y}px) rotate(${currentRotation}deg) scale(${currentScale})`;
    });
    
    // Bring forward button
    document.getElementById('bring-forward').addEventListener('click', function() {
        if (!selectedElement) return;
        
        const currentZIndex = parseInt(selectedElement.style.zIndex);
        selectedElement.style.zIndex = currentZIndex + 1;
    });
    
    // Send backward button
    document.getElementById('send-backward').addEventListener('click', function() {
        if (!selectedElement) return;
        
        const currentZIndex = parseInt(selectedElement.style.zIndex);
        if (currentZIndex > 1) {
            selectedElement.style.zIndex = currentZIndex - 1;
        }
    });
    
    // Form submission - collect all items and their positions
    document.getElementById('look-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const items = Array.from(document.querySelectorAll('.draggable-item')).map(item => {
            const x = parseFloat(item.getAttribute('data-x')) || 0;
            const y = parseFloat(item.getAttribute('data-y')) || 0;
            
            // Get rotation and scale from transform
            const transform = item.style.transform;
            const rotationMatch = transform.match(/rotate\((\d+)deg\)/);
            const scaleMatch = transform.match(/scale\(([\d.]+)\)/);
            
            const rotation = rotationMatch ? parseInt(rotationMatch[1]) : 0;
            const scale = scaleMatch ? parseFloat(scaleMatch[1]) : 1;
            
            return {
                id: item.dataset.itemId,
                x: x,
                y: y,
                rotation: rotation,
                scale: scale,
                zIndex: parseInt(item.style.zIndex)
            };
        });
        
        // Create a hidden input with the canvas data
        const canvasDataInput = document.createElement('input');
        canvasDataInput.type = 'hidden';
        canvasDataInput.name = 'canvas_data';
        canvasDataInput.value = JSON.stringify({ items: items });
        
        this.appendChild(canvasDataInput);
        this.submit();
    });
});