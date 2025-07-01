// Script para la página de reportes administrativos
console.log('🔧 script-reportes.js loaded');

// Variables globales
let currentUser = null;

// Función para inicializar la página
async function initReports() {
    console.log('🚀 Inicializando página de reportes...');
    
    try {
        // Verificar autenticación
        if (!isAuthenticated()) {
            console.log('❌ Usuario no autenticado, redirigiendo...');
            window.location.href = 'login.html';
            return;
        }

        // Obtener datos del usuario
        currentUser = await getCurrentUserData();
        console.log('👤 Usuario actual:', currentUser);

        // Verificar si es administrador
        if (!isAdmin(currentUser)) {
            console.log('❌ Usuario no es administrador');
            showError('No tienes permisos para acceder a esta sección. Solo los administradores pueden ver reportes.');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 3000);
            return;
        }

        console.log('✅ Usuario administrador verificado');
        
        // Mostrar información del usuario
        updateUserInfo(currentUser);
        
        // Cargar reportes iniciales
        await loadAllReports();

    } catch (error) {
        console.error('❌ Error inicializando reportes:', error);
        showError('Error al cargar la página de reportes: ' + error.message);
    }
}

// Función para obtener datos del usuario actual decodificando el token
async function getCurrentUserData() {
    try {
        const token = localStorage.getItem('authToken');
        if (!token) {
            throw new Error('No hay token de acceso');
        }

        // Intentar decodificar como JWT primero
        try {
            if (token.includes('.')) {
                // Es un JWT, intentar decodificar
                const payload = JSON.parse(atob(token.split('.')[1]));
                console.log('🔍 Payload del JWT:', payload);
                
                return {
                    username: payload.username || 'Usuario',
                    role: payload.role || 'customer'
                };
            } else {
                // Es un token de prueba, obtener datos de otro lugar
                console.log('🔍 Token de prueba detectado, buscando datos del usuario...');
                
                // Intentar obtener de userData
                const userData = localStorage.getItem('userData');
                if (userData) {
                    const parsedUserData = JSON.parse(userData);
                    return {
                        username: parsedUserData.username || 'Usuario',
                        role: parsedUserData.role || 'customer'
                    };
                }
                
                // Como fallback, verificar usuarios admin conocidos
                const storedUser = localStorage.getItem('cinemaUser');
                if (storedUser) {
                    const user = JSON.parse(storedUser);
                    return {
                        username: user.username || 'Usuario',
                        role: (user.username === 'admin' || user.username === 'Isaura') ? 'admin' : 'customer'
                    };
                }
                
                throw new Error('No se pudo determinar la información del usuario');
            }
        } catch (decodeError) {
            console.warn('⚠️ Error decodificando token:', decodeError);
            
            // Fallback final
            const storedUser = localStorage.getItem('cinemaUser');
            if (storedUser) {
                const user = JSON.parse(storedUser);
                return {
                    username: user.username || 'Usuario',
                    role: (user.username === 'admin' || user.username === 'Isaura') ? 'admin' : 'customer'
                };
            }
            
            throw new Error('No se pudo obtener información del usuario');
        }
        
    } catch (error) {
        console.error('❌ Error decodificando token:', error);
        // Como fallback, intentar obtener de userData
        const userData = localStorage.getItem('userData');
        if (userData) {
            return JSON.parse(userData);
        }
        throw new Error('No se pudo obtener información del usuario');
    }
}

// Función para verificar si el usuario es administrador
function isAdmin(user) {
    return user && user.role === 'admin';
}

// Función para actualizar la información del usuario en la UI
function updateUserInfo(user) {
    const userInfo = document.getElementById('userInfo');
    if (userInfo && user) {
        userInfo.innerHTML = `
            <strong>Usuario:</strong> ${user.username} 
            <span class="badge badge-admin">ADMIN</span>
        `;
    }
}

// Función para cargar todos los reportes
async function loadAllReports() {
    console.log('📊 Cargando todos los reportes...');
    
    try {
        // Mostrar indicador de carga
        showLoading(true);
        
        // Cargar reportes en paralelo
        await Promise.all([
            loadSalesSummary(),
            loadDetailedSales()
        ]);
        
        console.log('✅ Todos los reportes cargados exitosamente');
        
    } catch (error) {
        console.error('❌ Error cargando reportes:', error);
        showError('Error al cargar los reportes: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Función para cargar resumen de ventas
async function loadSalesSummary() {
    console.log('📈 Cargando resumen de ventas...');
    
    try {
        const response = await ReportsAPI.getSalesSummary();
        
        console.log('📈 Resumen de ventas recibido:', response);
        displaySalesSummary(response);
        
    } catch (error) {
        console.error('❌ Error cargando resumen de ventas:', error);
        document.getElementById('salesSummary').innerHTML = `
            <div class="alert alert-danger">
                Error al cargar resumen de ventas: ${error.message}
            </div>
        `;
    }
}

// Función para cargar ventas detalladas
async function loadDetailedSales() {
    console.log('📋 Cargando ventas detalladas...');
    
    try {
        const response = await ReportsAPI.getDetailedSales();
        
        console.log('📋 Ventas detalladas recibidas:', response);
        displayDetailedSales(response);
        
    } catch (error) {
        console.error('❌ Error cargando ventas detalladas:', error);
        document.getElementById('detailedSales').innerHTML = `
            <div class="alert alert-danger">
                Error al cargar ventas detalladas: ${error.message}
            </div>
        `;
    }
}

// Función para mostrar el resumen de ventas
function displaySalesSummary(data) {
    const container = document.getElementById('salesSummary');
    
    if (!data || !data.summary) {
        container.innerHTML = '<div class="alert alert-info">No hay datos de resumen disponibles.</div>';
        return;
    }
    
    const summary = data.summary;
    
    container.innerHTML = `
        <div class="row">
            <div class="col-md-3">
                <div class="card bg-primary text-white">
                    <div class="card-body">
                        <h5 class="card-title">Total de Ventas</h5>
                        <h3 class="card-text">$${(summary.total_amount || 0).toLocaleString()}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white">
                    <div class="card-body">
                        <h5 class="card-title">Boletos Vendidos</h5>
                        <h3 class="card-text">${summary.total_tickets || 0}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-info text-white">
                    <div class="card-body">
                        <h5 class="card-title">Transacciones</h5>
                        <h3 class="card-text">${summary.total_transactions || 0}</h3>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white">
                    <div class="card-body">
                        <h5 class="card-title">Promedio por Venta</h5>
                        <h3 class="card-text">$${(summary.average_sale || 0).toFixed(2)}</h3>
                    </div>
                </div>
            </div>
        </div>
        
        ${summary.sales_by_movie && summary.sales_by_movie.length > 0 ? `
        <div class="mt-4">
            <h5>Ventas por Película</h5>
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Película</th>
                            <th>Boletos Vendidos</th>
                            <th>Ingresos</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${summary.sales_by_movie.map(movie => `
                            <tr>
                                <td>${movie.title || 'Sin título'}</td>
                                <td>${movie.tickets_sold || 0}</td>
                                <td>$${(movie.total_revenue || 0).toLocaleString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
        ` : ''}
        
        ${summary.sales_by_theater && summary.sales_by_theater.length > 0 ? `
        <div class="mt-4">
            <h5>Ventas por Sala</h5>
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Sala</th>
                            <th>Boletos Vendidos</th>
                            <th>Ingresos</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${summary.sales_by_theater.map(theater => `
                            <tr>
                                <td>${theater.theater_name || 'Sin nombre'}</td>
                                <td>${theater.tickets_sold || 0}</td>
                                <td>$${(theater.total_revenue || 0).toLocaleString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
        ` : ''}
    `;
}

// Función para mostrar las ventas detalladas
function displayDetailedSales(data) {
    const container = document.getElementById('detailedSales');
    
    if (!data || !data.sales || data.sales.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No hay ventas registradas.</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="thead-dark">
                    <tr>
                        <th>ID Venta</th>
                        <th>Usuario</th>
                        <th>Película</th>
                        <th>Sala</th>
                        <th>Función</th>
                        <th>Asientos</th>
                        <th>Total</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.sales.map(sale => `
                        <tr>
                            <td>${sale.sale_id || '-'}</td>
                            <td>${sale.username || '-'}</td>
                            <td>${sale.movie_title || '-'}</td>
                            <td>${sale.theater_name || '-'}</td>
                            <td>${sale.showtime ? formatDateTime(sale.showtime) : '-'}</td>
                            <td>
                                <span class="badge badge-secondary">
                                    ${sale.seats_count || 0} asientos
                                </span>
                            </td>
                            <td><strong>$${(sale.total_amount || 0).toLocaleString()}</strong></td>
                            <td>${sale.sale_date ? formatDateTime(sale.sale_date) : '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
        
        <div class="mt-3">
            <p class="text-muted">
                Total de registros: <strong>${data.sales.length}</strong>
            </p>
        </div>
    `;
}

// Función para formatear fechas
function formatDateTime(dateString) {
    if (!dateString) return '-';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return dateString;
    }
}

// Función para refrescar todos los reportes
async function refreshReports() {
    console.log('🔄 Refrescando reportes...');
    await loadAllReports();
}

// Función para exportar reporte (funcionalidad futura)
function exportReport(type) {
    showInfo(`Funcionalidad de exportar ${type} estará disponible próximamente.`);
}

// Función para mostrar/ocultar indicador de carga
function showLoading(show) {
    const loader = document.getElementById('loadingIndicator');
    if (loader) {
        loader.style.display = show ? 'block' : 'none';
    }
}

// Funciones de notificación
function showError(message) {
    console.error('❌', message);
    if (window.showNotification) {
        window.showNotification(message, 'error');
    } else {
        alert('Error: ' + message);
    }
}

function showSuccess(message) {
    console.log('✅', message);
    if (window.showNotification) {
        window.showNotification(message, 'success');
    } else {
        alert('Éxito: ' + message);
    }
}

function showInfo(message) {
    console.log('ℹ️', message);
    if (window.showNotification) {
        window.showNotification(message, 'info');
    } else {
        alert('Info: ' + message);
    }
}

// Función para cerrar sesión
function logout() {
    if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
        cerrarSesion();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initReports);
