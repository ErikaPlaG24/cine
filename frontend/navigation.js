// Componente de navegación unificado para todas las páginas
function createUnifiedNavigation() {
    return `
        <header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
                <div style="display: flex; align-items: center; gap: 20px;">
                    <h1 style="margin: 0; font-size: 24px; font-weight: bold;">🎬 Cine Premium</h1>
                    <nav style="display: flex; gap: 15px; align-items: center;">
                        <a href="reservas.html" style="color: white; text-decoration: none; padding: 8px 16px; border-radius: 5px; transition: background 0.3s; display: flex; align-items: center; gap: 5px;" onmouseover="this.style.background='rgba(255,255,255,0.2)'" onmouseout="this.style.background='transparent'">
                            🎟️ Reservas
                        </a>
                        <a href="ticket.html" style="color: white; text-decoration: none; padding: 8px 16px; border-radius: 5px; transition: background 0.3s; display: flex; align-items: center; gap: 5px;" onmouseover="this.style.background='rgba(255,255,255,0.2)'" onmouseout="this.style.background='transparent'">
                            🎫 Mis Tickets
                        </a>
                        <!-- Enlaces de administrador (solo visible para admins) -->
                        <a id="adminReportsLink" href="reportes.html" style="display: none; background: rgba(40, 167, 69, 0.9); color: white; text-decoration: none; padding: 8px 16px; border-radius: 5px; font-size: 14px; font-weight: bold; transition: all 0.3s; display: flex; align-items: center; gap: 5px;" onmouseover="this.style.background='#28a745'" onmouseout="this.style.background='rgba(40, 167, 69, 0.9)'">
                            📊 Reportes
                        </a>
                        <a id="adminPanelLink" href="admin.html" style="display: none; background: rgba(111, 66, 193, 0.9); color: white; text-decoration: none; padding: 8px 16px; border-radius: 5px; font-size: 14px; font-weight: bold; transition: all 0.3s; display: flex; align-items: center; gap: 5px;" onmouseover="this.style.background='#6f42c1'" onmouseout="this.style.background='rgba(111, 66, 193, 0.9)'">
                            🛠️ Administrar
                        </a>
                    </nav>
                </div>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <span id="welcomeMessage" style="font-size: 16px; opacity: 0.9;">Bienvenido</span>
                    <div id="userInfo" style="display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.1); padding: 8px 12px; border-radius: 8px;"></div>
                    <button onclick="cerrarSesion()" style="background: #e74c3c; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: all 0.3s; display: flex; align-items: center; gap: 5px;" onmouseover="this.style.background='#c0392b'" onmouseout="this.style.background='#e74c3c'">
                        🚪 Cerrar Sesión
                    </button>
                </div>
            </div>
        </header>
    `;
}

// Función para inicializar la navegación en cualquier página
function initializeNavigation() {
    // Insertar la navegación al inicio del body
    const body = document.body;
    const navContainer = document.createElement('div');
    navContainer.innerHTML = createUnifiedNavigation();
    body.insertBefore(navContainer.firstElementChild, body.firstChild);
    
    // Verificar autenticación y mostrar enlaces de admin si corresponde
    checkAuthAndShowAdminLinks();
    
    // Mostrar información del usuario
    showUserInfo();
}

// Función para verificar autenticación y mostrar enlaces de admin
function checkAuthAndShowAdminLinks() {
    try {
        if (!isAuthenticated()) {
            // Si no está autenticado, redirigir al login
            if (window.location.pathname !== '/frontend/login.html' && 
                window.location.pathname !== '/frontend/index.html' &&
                !window.location.pathname.includes('login.html') &&
                !window.location.pathname.includes('index.html')) {
                window.location.href = 'login.html';
                return;
            }
        }
        
        // Obtener información del usuario del token
        const token = localStorage.getItem('authToken');
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                
                // Mostrar enlaces de admin si es administrador
                if (payload.role === 'admin') {
                    const adminReportsLink = document.getElementById('adminReportsLink');
                    const adminPanelLink = document.getElementById('adminPanelLink');
                    
                    if (adminReportsLink) adminReportsLink.style.display = 'flex';
                    if (adminPanelLink) adminPanelLink.style.display = 'flex';
                }
                
                // Actualizar mensaje de bienvenida
                const welcomeMessage = document.getElementById('welcomeMessage');
                if (welcomeMessage) {
                    welcomeMessage.textContent = `Hola, ${payload.username || 'Usuario'}`;
                }
                
            } catch (error) {
                console.error('Error decodificando token:', error);
            }
        }
    } catch (error) {
        console.error('Error en checkAuthAndShowAdminLinks:', error);
    }
}

// Función para mostrar información del usuario
function showUserInfo() {
    try {
        const token = localStorage.getItem('authToken');
        if (token) {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const userInfo = document.getElementById('userInfo');
            
            if (userInfo) {
                const roleColor = payload.role === 'admin' ? '#e74c3c' : '#28a745';
                const roleText = payload.role === 'admin' ? 'ADMIN' : 'CLIENTE';
                
                userInfo.innerHTML = `
                    <span style="font-size: 14px;">${payload.username || 'Usuario'}</span>
                    <span style="background: ${roleColor}; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">${roleText}</span>
                `;
            }
        }
    } catch (error) {
        console.error('Error mostrando info del usuario:', error);
    }
}

// Función unificada para cerrar sesión
function cerrarSesion() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userId');
    localStorage.removeItem('cinemaUser');
    
    // Mostrar mensaje y redirigir
    if (window.showNotification) {
        window.showNotification('Sesión cerrada correctamente', 'success');
    }
    
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 1000);
}

// Función para resaltar la página actual en la navegación
function highlightCurrentPage() {
    const currentPage = window.location.pathname.split('/').pop();
    const navLinks = document.querySelectorAll('header nav a');
    
    navLinks.forEach(link => {
        const linkPage = link.getAttribute('href');
        if (linkPage === currentPage) {
            link.style.background = 'rgba(255,255,255,0.3)';
            link.style.fontWeight = 'bold';
        }
    });
}

// Auto-inicializar cuando se carga el DOM
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si no estamos en login o index
    const currentPage = window.location.pathname.split('/').pop();
    if (currentPage !== 'login.html' && currentPage !== 'index.html' && currentPage !== '') {
        initializeNavigation();
        highlightCurrentPage();
    }
});
