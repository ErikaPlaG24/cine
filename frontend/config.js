// Configuración para desarrollo y producción
const CONFIG = {
    development: {
        API_BASE_URL: 'http://localhost:8000',  // Backend está en puerto 8000 
        ENABLE_LOGGING: true
    },
    production: {
        API_BASE_URL: '/api',
        ENABLE_LOGGING: false
    }
};

// Detectar entorno (por defecto development)
const ENVIRONMENT = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') ? 'development' : 'production';
const APP_CONFIG = CONFIG[ENVIRONMENT];

// Hacer que la configuración esté disponible globalmente
window.APP_CONFIG = APP_CONFIG;

// Debug: Log environment detection
console.log('Current hostname:', window.location.hostname);
console.log('Detected environment:', ENVIRONMENT);
console.log('API Config:', APP_CONFIG);

// Función de logging condicional
function log(...args) {
    if (APP_CONFIG.ENABLE_LOGGING) {
        console.log('[CINE APP]:', ...args);
    }
}

// Función para mostrar notificaciones de usuario
function showNotification(message, type = 'info') {
    // Crear elemento de notificación si no existe
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 300px;
        `;
        document.body.appendChild(notificationContainer);
    }

    // Crear notificación
    const notification = document.createElement('div');
    notification.style.cssText = `
        background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4caf50' : '#2196f3'};
        color: white;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease-out;
        cursor: pointer;
    `;
    notification.textContent = message;
    
    // Agregar animación CSS
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideIn {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            @keyframes slideOut {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    // Agregar al contenedor
    notificationContainer.appendChild(notification);

    // Auto-remover después de 5 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);

    // Permitir cerrar al hacer click
    notification.addEventListener('click', () => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    });
}

// Función para formatear fechas
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Función para formatear tiempo
function formatTime(timeString) {
    // Si viene en formato HH:MM:SS, tomar solo HH:MM
    if (timeString && timeString.includes(':')) {
        const parts = timeString.split(':');
        return `${parts[0]}:${parts[1]}`;
    }
    return timeString;
}

// Función para validar entrada de usuario
function validateUserInput(input, type = 'text') {
    if (!input || input.trim() === '') {
        return { valid: false, message: 'Este campo es requerido' };
    }

    switch (type) {
        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(input)) {
                return { valid: false, message: 'Email inválido' };
            }
            break;
        case 'password':
            if (input.length < 6) {
                return { valid: false, message: 'La contraseña debe tener al menos 6 caracteres' };
            }
            break;
        case 'username':
            if (input.length < 3) {
                return { valid: false, message: 'El usuario debe tener al menos 3 caracteres' };
            }
            break;
    }

    return { valid: true };
}

// Función para mostrar/ocultar loading
function setLoading(element, isLoading, originalText = null) {
    if (isLoading) {
        element.disabled = true;
        element.dataset.originalText = originalText || element.innerHTML;
        element.innerHTML = '<span>⏳</span> Cargando...';
    } else {
        element.disabled = false;
        element.innerHTML = element.dataset.originalText || originalText || element.innerHTML;
    }
}

// Función para retries automáticos de API
async function retryApiCall(apiFunction, maxRetries = 3, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await apiFunction();
        } catch (error) {
            log(`Intento ${i + 1} falló:`, error.message);
            
            if (i === maxRetries - 1) {
                throw error;
            }
            
            // Esperar antes del siguiente intento
            await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
        }
    }
}

// Exportar configuración para uso global
window.APP_CONFIG = APP_CONFIG;
window.log = log;
window.showNotification = showNotification;
window.formatDate = formatDate;
window.formatTime = formatTime;
window.validateUserInput = validateUserInput;
window.setLoading = setLoading;
window.retryApiCall = retryApiCall;
