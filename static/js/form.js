// JavaScript for dynamic form functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form functionality
    initializeDynamicSections();
    initializeFormSubmission();
});

function initializeDynamicSections() {
    // Add event listeners for "add more" buttons
    const addButtons = document.querySelectorAll('.add-button');
    addButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionType = this.dataset.section;
            addDynamicSection(sectionType);
        });
    });
}

function addDynamicSection(sectionType) {
    const container = document.getElementById(sectionType + '-container');
    const template = document.getElementById(sectionType + '-template');
    
    if (!container || !template) return;
    
    // Clone the template
    const newSection = template.cloneNode(true);
    newSection.style.display = 'block';
    newSection.removeAttribute('id');
    newSection.classList.add('dynamic-item');
    
    // Update field names to include index
    const index = container.querySelectorAll('.dynamic-item').length;
    const inputs = newSection.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        if (input.name.includes('[]')) {
            input.name = input.name.replace('[]', `[${index}]`);
        }
        input.value = '';
        
        // Add change event listener for validation
        input.addEventListener('change', validateField);
        input.addEventListener('blur', validateField);
    });
    
    // Add remove button functionality
    const removeButton = newSection.querySelector('.remove-button');
    if (removeButton) {
        removeButton.addEventListener('click', function(e) {
            e.preventDefault();
            newSection.remove();
            updateFieldIndices(sectionType);
        });
    }
    
    container.appendChild(newSection);
    
    // Focus on first input of new section
    const firstInput = newSection.querySelector('input, textarea, select');
    if (firstInput) {
        firstInput.focus();
    }
}

function updateFieldIndices(sectionType) {
    const container = document.getElementById(sectionType + '-container');
    const sections = container.querySelectorAll('.dynamic-item');
    
    sections.forEach((section, index) => {
        const inputs = section.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            const baseName = input.name.replace(/\[\d+\]/, '');
            input.name = baseName.replace(/\[\]/, `[${index}]`);
        });
    });
}

function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    
    // Reset previous validation state
    field.style.borderColor = '#ddd';
    
    // Validate based on field type
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            field.style.borderColor = '#e74c3c';
            return false;
        }
    }
    
    if (field.type === 'number' && value) {
        const numValue = parseInt(value);
        if (isNaN(numValue) || numValue <= 0) {
            field.style.borderColor = '#e74c3c';
            return false;
        }
    }
    
    if (field.type === 'date' && value) {
        const date = new Date(value);
        const today = new Date();
        // Allow dates up to 1 year in the future
        const maxDate = new Date();
        maxDate.setFullYear(today.getFullYear() + 1);
        
        if (date > maxDate) {
            field.style.borderColor = '#e74c3c';
            return false;
        }
    }
    
    return true;
}

function initializeFormSubmission() {
    const form = document.getElementById('docente-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!validateForm()) {
            return;
        }
        
        submitForm();
    });
}

function validateForm() {
    let isValid = true;
    const errors = [];
    
    // Validate required fields
    const requiredFields = document.querySelectorAll('input[required], textarea[required]');
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#e74c3c';
            isValid = false;
            
            const label = field.closest('.form-group')?.querySelector('label')?.textContent || field.name;
            errors.push(`${label.replace(' *', '')} es requerido`);
        } else {
            field.style.borderColor = '#ddd';
        }
    });
    
    // Validate email format
    const emailField = document.querySelector('input[type="email"]');
    if (emailField && emailField.value) {
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailRegex.test(emailField.value.trim())) {
            emailField.style.borderColor = '#e74c3c';
            isValid = false;
            errors.push('El formato del correo electrónico no es válido');
        }
    }
    
    // Validate dynamic sections have at least some data
    const hasAnyActivity = validateActivitySections();
    if (!hasAnyActivity) {
        errors.push('Debe agregar al menos una actividad (curso, publicación, evento, etc.)');
        isValid = false;
    }
    
    // Validate specific field formats
    const numberFields = document.querySelectorAll('input[type="number"]');
    numberFields.forEach(field => {
        if (field.value && (isNaN(field.value) || parseInt(field.value) <= 0)) {
            field.style.borderColor = '#e74c3c';
            isValid = false;
            errors.push('Los números deben ser valores positivos');
        }
    });
    
    // Validate dates
    const dateFields = document.querySelectorAll('input[type="date"]');
    dateFields.forEach(field => {
        if (field.value) {
            const date = new Date(field.value);
            const today = new Date();
            const maxDate = new Date();
            maxDate.setFullYear(today.getFullYear() + 1);
            
            if (date > maxDate) {
                field.style.borderColor = '#e74c3c';
                isValid = false;
                errors.push('Las fechas no pueden ser más de un año en el futuro');
            }
        }
    });
    
    if (!isValid) {
        const errorMessage = errors.length > 0 ? 
            'Errores encontrados:\n• ' + [...new Set(errors)].join('\n• ') :
            'Por favor, complete todos los campos requeridos correctamente.';
        showMessage(errorMessage, 'error');
    }
    
    return isValid;
}

function validateActivitySections() {
    const sections = [
        'cursos_capacitacion', 'publicaciones', 'eventos_academicos',
        'diseno_curricular', 'movilidad', 'reconocimientos', 'certificaciones'
    ];
    
    for (const section of sections) {
        const container = document.getElementById(section + '-container');
        const dynamicItems = container?.querySelectorAll('.dynamic-item');
        
        if (dynamicItems && dynamicItems.length > 0) {
            // Check if any item has meaningful data
            for (const item of dynamicItems) {
                const inputs = item.querySelectorAll('input, textarea, select');
                const hasData = Array.from(inputs).some(input => 
                    input.value && input.value.trim() !== ''
                );
                if (hasData) {
                    return true;
                }
            }
        }
    }
    
    return false;
}

function submitForm() {
    const form = document.getElementById('docente-form');
    const submitButton = document.querySelector('.submit-button');
    const loading = document.querySelector('.loading');
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.textContent = 'Enviando...';
    loading.style.display = 'block';
    
    // Hide any existing messages
    hideMessages();
    
    // Collect form data
    const formData = new FormData(form);
    const jsonData = formDataToJSON(formData);
    
    // Log data for debugging (remove in production)
    console.log('Sending form data:', jsonData);
    
    // Submit to API
    fetch('/api/formulario/enviar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData)
    })
    .then(async response => {
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Success case
            showMessage(
                `¡Formulario enviado exitosamente! 
                ID de seguimiento: ${data.formulario_id}. 
                Será revisado por la administradora.`, 
                'success'
            );
            
            // Store form ID for future reference
            localStorage.setItem('lastFormId', data.formulario_id);
            
            // Reset form
            form.reset();
            resetDynamicSections();
            
            // Scroll to top to show success message
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
        } else {
            // Handle API errors
            handleSubmissionError(data, response.status);
        }
    })
    .catch(error => {
        console.error('Network error:', error);
        showMessage(
            'Error de conexión. Verifique su conexión a internet e intente nuevamente.', 
            'error'
        );
    })
    .finally(() => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar Formulario';
        loading.style.display = 'none';
    });
}

function handleSubmissionError(data, statusCode) {
    let errorMessage = 'Error al enviar el formulario.';
    
    if (statusCode === 400) {
        // Validation errors
        if (data.detail && data.detail.errors) {
            errorMessage = 'Errores de validación:\n• ' + data.detail.errors.join('\n• ');
        } else if (data.detail && data.detail.message) {
            errorMessage = data.detail.message;
        } else if (data.detail) {
            errorMessage = data.detail;
        }
    } else if (statusCode === 409) {
        // Conflict (duplicate email)
        errorMessage = data.detail || 'Ya existe un formulario con este correo electrónico.';
    } else if (statusCode === 500) {
        // Server error
        errorMessage = 'Error interno del servidor. Por favor, intente más tarde.';
    } else {
        // Other errors
        errorMessage = data.detail || data.message || 'Error desconocido.';
    }
    
    showMessage(errorMessage, 'error');
    
    // If validation errors, scroll to first invalid field
    if (statusCode === 400) {
        scrollToFirstError();
    }
}

function scrollToFirstError() {
    const invalidField = document.querySelector('input[style*="border-color: rgb(231, 76, 60)"], textarea[style*="border-color: rgb(231, 76, 60)"], select[style*="border-color: rgb(231, 76, 60)"]');
    if (invalidField) {
        invalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        invalidField.focus();
    }
}

function hideMessages() {
    const messages = document.querySelectorAll('.message');
    messages.forEach(msg => msg.style.display = 'none');
}

function formDataToJSON(formData) {
    const json = {};
    
    // Handle regular fields
    for (let [key, value] of formData.entries()) {
        if (key.includes('[')) {
            // Handle array fields - updated regex to handle empty brackets
            const match = key.match(/^(.+)\[(\d*)\]\.(.+)$/);
            if (match) {
                const [, arrayName, indexStr, fieldName] = match;
                if (!json[arrayName]) json[arrayName] = [];
                
                // Find the actual index by counting existing items
                let index = indexStr === '' ? json[arrayName].length : parseInt(indexStr);
                if (!json[arrayName][index]) json[arrayName][index] = {};
                json[arrayName][index][fieldName] = value;
            }
        } else {
            json[key] = value;
        }
    }
    
    // Clean up arrays - remove empty objects and null values
    Object.keys(json).forEach(key => {
        if (Array.isArray(json[key])) {
            json[key] = json[key].filter(item => {
                if (typeof item === 'object' && item !== null) {
                    // Remove empty strings and keep only objects with meaningful data
                    const hasData = Object.values(item).some(val => val && val.trim && val.trim() !== '');
                    return hasData;
                }
                return item !== null && item !== '';
            });
        }
    });
    
    return json;
}

function resetDynamicSections() {
    const containers = document.querySelectorAll('[id$="-container"]');
    containers.forEach(container => {
        // Remove all dynamic items, keep only the template
        const dynamicItems = container.querySelectorAll('.dynamic-item');
        dynamicItems.forEach(item => item.remove());
    });
}

function showMessage(text, type) {
    // Hide any existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.style.display = 'none');
    
    // Create or show message
    let messageDiv = document.querySelector('.message.' + type);
    if (!messageDiv) {
        messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + type;
        document.querySelector('.container').appendChild(messageDiv);
    }
    
    messageDiv.textContent = text;
    messageDiv.style.display = 'block';
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
}

// Form status checking functionality
function initializeStatusCheck() {
    // Check if there's a stored form ID
    const lastFormId = localStorage.getItem('lastFormId');
    if (lastFormId) {
        addStatusCheckButton(lastFormId);
    }
}

function addStatusCheckButton(formId) {
    const container = document.querySelector('.container');
    if (!container || document.querySelector('.status-check')) return;
    
    const statusDiv = document.createElement('div');
    statusDiv.className = 'status-check';
    statusDiv.innerHTML = `
        <div class="status-info">
            <h3>Estado de su último formulario</h3>
            <p>ID de seguimiento: <strong>${formId}</strong></p>
            <button type="button" class="status-button" onclick="checkFormStatus(${formId})">
                Verificar Estado
            </button>
            <div class="status-result" style="display: none;"></div>
        </div>
    `;
    
    container.insertBefore(statusDiv, container.firstChild);
}

async function checkFormStatus(formId) {
    const button = document.querySelector('.status-button');
    const resultDiv = document.querySelector('.status-result');
    
    if (!button || !resultDiv) return;
    
    // Show loading state
    button.disabled = true;
    button.textContent = 'Verificando...';
    resultDiv.style.display = 'none';
    
    try {
        const response = await fetch(`/api/formulario/status/${formId}`);
        const data = await response.json();
        
        if (response.ok) {
            displayFormStatus(data, resultDiv);
        } else {
            resultDiv.innerHTML = `
                <div class="status-error">
                    <p>Error: ${data.detail || 'No se pudo obtener el estado'}</p>
                </div>
            `;
        }
        
        resultDiv.style.display = 'block';
        
    } catch (error) {
        console.error('Error checking status:', error);
        resultDiv.innerHTML = `
            <div class="status-error">
                <p>Error de conexión. Intente nuevamente.</p>
            </div>
        `;
        resultDiv.style.display = 'block';
    } finally {
        button.disabled = false;
        button.textContent = 'Verificar Estado';
    }
}

function displayFormStatus(data, container) {
    const statusColors = {
        'PENDIENTE': '#f39c12',
        'APROBADO': '#27ae60',
        'RECHAZADO': '#e74c3c'
    };
    
    const statusTexts = {
        'PENDIENTE': 'Pendiente de revisión',
        'APROBADO': 'Aprobado',
        'RECHAZADO': 'Rechazado'
    };
    
    const color = statusColors[data.estado] || '#95a5a6';
    const statusText = statusTexts[data.estado] || data.estado;
    
    let html = `
        <div class="status-success">
            <div class="status-badge" style="background-color: ${color};">
                ${statusText}
            </div>
            <p><strong>Fecha de envío:</strong> ${formatDate(data.fecha_envio)}</p>
    `;
    
    if (data.fecha_revision) {
        html += `<p><strong>Fecha de revisión:</strong> ${formatDate(data.fecha_revision)}</p>`;
    }
    
    if (data.revisado_por) {
        html += `<p><strong>Revisado por:</strong> ${data.revisado_por}</p>`;
    }
    
    if (data.comentarios) {
        html += `<p><strong>Comentarios:</strong> ${data.comentarios}</p>`;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function formatDate(dateString) {
    if (!dateString) return 'No disponible';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Auto-save functionality
let autoSaveTimer;
const AUTOSAVE_DELAY = 30000; // 30 seconds

function initializeAutoSave() {
    const form = document.getElementById('docente-form');
    if (!form) return;
    
    // Add event listeners for auto-save
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('input', scheduleAutoSave);
        input.addEventListener('change', scheduleAutoSave);
    });
    
    // Load saved data on page load
    loadSavedData();
}

function scheduleAutoSave() {
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(autoSaveForm, AUTOSAVE_DELAY);
}

function autoSaveForm() {
    const form = document.getElementById('docente-form');
    if (!form) return;
    
    const formData = new FormData(form);
    const jsonData = formDataToJSON(formData);
    
    // Only save if there's meaningful data
    if (jsonData.nombre_completo || jsonData.correo_institucional) {
        localStorage.setItem('formDraft', JSON.stringify(jsonData));
        showAutoSaveIndicator();
    }
}

function loadSavedData() {
    const savedData = localStorage.getItem('formDraft');
    if (!savedData) return;
    
    try {
        const data = JSON.parse(savedData);
        populateFormWithData(data);
        showMessage('Se ha restaurado un borrador guardado automáticamente.', 'info');
    } catch (error) {
        console.error('Error loading saved data:', error);
        localStorage.removeItem('formDraft');
    }
}

function populateFormWithData(data) {
    // Populate basic fields
    Object.keys(data).forEach(key => {
        if (typeof data[key] === 'string') {
            const field = document.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = data[key];
            }
        }
    });
    
    // Populate dynamic sections
    const arrayFields = [
        'cursos_capacitacion', 'publicaciones', 'eventos_academicos',
        'diseno_curricular', 'movilidad', 'reconocimientos', 'certificaciones'
    ];
    
    arrayFields.forEach(fieldName => {
        if (data[fieldName] && Array.isArray(data[fieldName])) {
            data[fieldName].forEach((item, index) => {
                addDynamicSection(fieldName);
                
                // Populate the newly added section
                Object.keys(item).forEach(itemKey => {
                    const field = document.querySelector(`[name="${fieldName}[${index}].${itemKey}"]`);
                    if (field) {
                        field.value = item[itemKey];
                    }
                });
            });
        }
    });
}

function showAutoSaveIndicator() {
    let indicator = document.querySelector('.autosave-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'autosave-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 14px;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s;
        `;
        document.body.appendChild(indicator);
    }
    
    indicator.textContent = 'Borrador guardado';
    indicator.style.opacity = '1';
    
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

function clearSavedData() {
    localStorage.removeItem('formDraft');
}

// Initialize all functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDynamicSections();
    initializeFormSubmission();
    initializeStatusCheck();
    initializeAutoSave();
});