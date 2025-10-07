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
    
    // Update field names to include index
    const index = container.children.length;
    const inputs = newSection.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        const baseName = input.name.replace(/\[\d+\]/, '');
        input.name = baseName.replace(/\[\]/, `[${index}]`);
        input.value = '';
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
}

function updateFieldIndices(sectionType) {
    const container = document.getElementById(sectionType + '-container');
    const sections = container.children;
    
    Array.from(sections).forEach((section, index) => {
        const inputs = section.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            const baseName = input.name.replace(/\[\d+\]/, '');
            input.name = baseName.replace(/\[\]/, `[${index}]`);
        });
    });
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
    const requiredFields = document.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#e74c3c';
            isValid = false;
        } else {
            field.style.borderColor = '#ddd';
        }
    });
    
    // Validate email format
    const emailField = document.querySelector('input[type="email"]');
    if (emailField && emailField.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(emailField.value)) {
            emailField.style.borderColor = '#e74c3c';
            isValid = false;
        }
    }
    
    if (!isValid) {
        showMessage('Por favor, complete todos los campos requeridos correctamente.', 'error');
    }
    
    return isValid;
}

function submitForm() {
    const form = document.getElementById('docente-form');
    const submitButton = document.querySelector('.submit-button');
    const loading = document.querySelector('.loading');
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.textContent = 'Enviando...';
    loading.style.display = 'block';
    
    // Collect form data
    const formData = new FormData(form);
    const jsonData = formDataToJSON(formData);
    
    // Submit to API
    fetch('/api/formulario/enviar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showMessage('¡Formulario enviado exitosamente! Será revisado por la administradora.', 'success');
            form.reset();
            // Remove dynamic sections except the first one
            resetDynamicSections();
        } else {
            showMessage('Error al enviar el formulario: ' + (data.message || 'Error desconocido'), 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Error de conexión. Por favor, intente nuevamente.', 'error');
    })
    .finally(() => {
        // Reset button state
        submitButton.disabled = false;
        submitButton.textContent = 'Enviar Formulario';
        loading.style.display = 'none';
    });
}

function formDataToJSON(formData) {
    const json = {};
    
    // Handle regular fields
    for (let [key, value] of formData.entries()) {
        if (key.includes('[')) {
            // Handle array fields
            const match = key.match(/^(.+)\[(\d+)\]\.(.+)$/);
            if (match) {
                const [, arrayName, index, fieldName] = match;
                if (!json[arrayName]) json[arrayName] = [];
                if (!json[arrayName][index]) json[arrayName][index] = {};
                json[arrayName][index][fieldName] = value;
            }
        } else {
            json[key] = value;
        }
    }
    
    return json;
}

function resetDynamicSections() {
    const containers = document.querySelectorAll('[id$="-container"]');
    containers.forEach(container => {
        // Keep only the first child (template)
        while (container.children.length > 1) {
            container.removeChild(container.lastChild);
        }
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