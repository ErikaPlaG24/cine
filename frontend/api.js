// Configuración de la API
const API_BASE_URL = window.APP_CONFIG ? window.APP_CONFIG.API_BASE_URL : 'http://localhost:8000';

// Debug: Log the API base URL being used
console.log('API_BASE_URL being used:', API_BASE_URL);
console.log('window.APP_CONFIG:', window.APP_CONFIG);

// Token storage
let authToken = localStorage.getItem('authToken');

// Función para hacer peticiones HTTP con autenticación
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(authToken && { 'Authorization': `Bearer ${authToken}` })
        }
    };

    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };

    try {
        window.log && window.log(`API Request: ${options.method || 'GET'} ${url}`);
        
        const response = await fetch(url, finalOptions);
        
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData) {
                    // Manejar diferentes formatos de error
                    if (typeof errorData.detail === 'object') {
                        if (errorData.detail.missing_fields) {
                            errorMessage = `Faltan campos requeridos: ${errorData.detail.missing_fields.join(', ')}`;
                        } else if (errorData.detail.error) {
                            errorMessage = errorData.detail.error;
                        } else {
                            errorMessage = JSON.stringify(errorData.detail);
                        }
                    } else {
                        errorMessage = errorData.detail || errorData.message || errorMessage;
                    }
                }
            } catch (e) {
                // Si no se puede parsear el JSON del error, usar el status
                errorMessage = `HTTP ${response.status} - ${response.statusText}`;
            }
            
            // Errores específicos
            if (response.status === 405) {
                errorMessage += " - Método no permitido. Verifique la configuración del backend.";
            } else if (response.status === 404) {
                errorMessage += " - Endpoint no encontrado.";
            } else if (response.status === 500) {
                errorMessage += " - Error interno del servidor.";
            }
            
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        window.log && window.log(`API Response:`, data);
        return data;
    } catch (error) {
        console.error('API Error:', error);
        window.log && window.log('API Error:', error);
        
        // Si es un error de autenticación, limpiar token
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            AuthAPI.logout();
            window.showNotification && window.showNotification('Sesión expirada. Por favor, inicie sesión nuevamente.', 'error');
        }
        
        // Si es error de conectividad
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            error.message = 'No se puede conectar con el servidor. Verifique que la API esté ejecutándose.';
        }
        
        throw error;
    }
}

// Funciones de autenticación
const AuthAPI = {
    async login(username, password) {
        console.log('AuthAPI.login called with:', username, '(password hidden)');
        
        try {
            const data = await apiRequest('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            
            console.log('Login response received:', data);
            
            if (data && data.access_token) {
                authToken = data.access_token;
                localStorage.setItem('authToken', authToken);
                
                // Guardar datos del usuario incluyendo el rol
                const userData = data.user || {};
                localStorage.setItem('userData', JSON.stringify(userData));
                
                // También guardar en el formato legacy para compatibilidad
                localStorage.setItem('cinemaUser', JSON.stringify({
                    username: userData.username,
                    token: authToken,
                    role: userData.role
                }));
                
                console.log('Token y datos de usuario guardados exitosamente');
                console.log('Datos del usuario:', userData);
            } else {
                console.error('No access_token in response:', data);
            }
            
            return data;
        } catch (error) {
            console.error('AuthAPI.login error:', error);
            throw error;
        }
    },

    async refresh() {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) throw new Error('No refresh token available');
        
        const data = await apiRequest('/auth/refresh', {
            method: 'POST',
            body: JSON.stringify({ refresh_token: refreshToken })
        });
        
        if (data.access_token) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
        }
        
        return data;
    },

    logout() {
        authToken = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('userData');
        localStorage.removeItem('cinemaUser');
    }
};

// Funciones CRUD para usuarios
const UsersAPI = {
    async getAll() {
        console.log('👥 UsersAPI.getAll - Obteniendo todos los usuarios');
        try {
            const response = await apiRequest('/users/all', {
                method: 'GET'
            });
            console.log('👥 Usuarios obtenidos:', response);
            
            // El backend puede devolver directamente un array o un objeto con propiedad 'users'
            if (Array.isArray(response)) {
                return response;
            } else {
                return response.users || [];
            }
        } catch (error) {
            console.error('❌ Error obteniendo usuarios:', error);
            throw error;
        }
    },

    async getById(userId) {
        console.log('👤 UsersAPI.getById - Obteniendo usuario:', userId);
        try {
            const response = await apiRequest('/users/by_id', {
                method: 'POST',
                body: JSON.stringify({ user_id: userId })
            });
            console.log('👤 Usuario obtenido:', response);
            return response.user;
        } catch (error) {
            console.error('❌ Error obteniendo usuario:', error);
            throw error;
        }
    },

    async create(userData) {
        console.log('➕ UsersAPI.create - Creando usuario:', userData);
        try {
            const response = await apiRequest('/users/create', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            console.log('✅ Usuario creado:', response);
            return response;
        } catch (error) {
            console.error('❌ Error creando usuario:', error);
            throw error;
        }
    },

    async update(userId, userData) {
        console.log('✏️ UsersAPI.update - Actualizando usuario:', userId, userData);
        try {
            const response = await apiRequest('/users/update', {
                method: 'PUT',
                body: JSON.stringify({ user_id: userId, ...userData })
            });
            console.log('✅ Usuario actualizado:', response);
            return response;
        } catch (error) {
            console.error('❌ Error actualizando usuario:', error);
            throw error;
        }
    },

    async delete(userId) {
        console.log('🗑️ UsersAPI.delete - Eliminando usuario:', userId);
        try {
            const response = await apiRequest('/users/delete', {
                method: 'DELETE',
                body: JSON.stringify({ user_id: userId })
            });
            console.log('✅ Usuario eliminado:', response);
            return response;
        } catch (error) {
            console.error('❌ Error eliminando usuario:', error);
            throw error;
        }
    }
};

// Funciones CRUD para películas
const MoviesAPI = {
    async getAll() {
        console.log('🎬 MoviesAPI.getAll - Obteniendo todas las películas');
        try {
            const response = await apiRequest('/movies/all', {
                method: 'GET'
            });
            console.log('🎬 Películas obtenidas:', response);
            return response;
        } catch (error) {
            console.error('❌ Error obteniendo películas:', error);
            throw error;
        }
    },

    async getById(movieId) {
        console.log('🎭 MoviesAPI.getById - Obteniendo película:', movieId);
        try {
            const response = await apiRequest('/movies/by_id', {
                method: 'POST',
                body: JSON.stringify({ movie_id: movieId })
            });
            console.log('🎭 Película obtenida:', response);
            return response.movie;
        } catch (error) {
            console.error('❌ Error obteniendo película:', error);
            throw error;
        }
    },

    async create(movieData) {
        console.log('➕ MoviesAPI.create - Creando película:', movieData);
        try {
            const response = await apiRequest('/movies/create', {
                method: 'POST',
                body: JSON.stringify(movieData)
            });
            console.log('✅ Película creada:', response);
            return response;
        } catch (error) {
            console.error('❌ Error creando película:', error);
            throw error;
        }
    },

    async update(movieId, movieData) {
        console.log('✏️ MoviesAPI.update - Actualizando película:', movieId, movieData);
        try {
            const response = await apiRequest('/movies/update', {
                method: 'PUT',
                body: JSON.stringify({ movie_id: movieId, ...movieData })
            });
            console.log('✅ Película actualizada:', response);
            return response;
        } catch (error) {
            console.error('❌ Error actualizando película:', error);
            throw error;
        }
    },

    async delete(movieId) {
        console.log('🗑️ MoviesAPI.delete - Eliminando película:', movieId);
        try {
            const response = await apiRequest('/movies/delete', {
                method: 'DELETE',
                body: JSON.stringify({ movie_id: movieId })
            });
            console.log('✅ Película eliminada:', response);
            return response;
        } catch (error) {
            console.error('❌ Error eliminando película:', error);
            throw error;
        }
    }
};

// Funciones CRUD para funciones (showtimes)
const ShowtimesAPI = {
    async getAll() {
        console.log('📅 ShowtimesAPI.getAll - Obteniendo todas las funciones');
        try {
            const response = await apiRequest('/showtimes/all', {
                method: 'GET'
            });
            console.log('📅 Funciones obtenidas:', response);
            return response;
        } catch (error) {
            console.error('❌ Error obteniendo funciones:', error);
            throw error;
        }
    },

    async getById(showtimeId) {
        console.log('📅 ShowtimesAPI.getById - Obteniendo función:', showtimeId);
        try {
            const response = await apiRequest('/showtimes/by_id', {
                method: 'POST',
                body: JSON.stringify({ showtime_id: showtimeId })
            });
            console.log('📅 Función obtenida:', response);
            return response.showtime;
        } catch (error) {
            console.error('❌ Error obteniendo función:', error);
            throw error;
        }
    },

    async create(showtimeData) {
        console.log('➕ ShowtimesAPI.create - Creando función:', showtimeData);
        try {
            const response = await apiRequest('/showtimes/create', {
                method: 'POST',
                body: JSON.stringify(showtimeData)
            });
            console.log('✅ Función creada:', response);
            return response;
        } catch (error) {
            console.error('❌ Error creando función:', error);
            throw error;
        }
    },

    async update(showtimeId, showtimeData) {
        console.log('✏️ ShowtimesAPI.update - Actualizando función:', showtimeId, showtimeData);
        try {
            const response = await apiRequest('/showtimes/update', {
                method: 'PUT',
                body: JSON.stringify({ showtime_id: showtimeId, ...showtimeData })
            });
            console.log('✅ Función actualizada:', response);
            return response;
        } catch (error) {
            console.error('❌ Error actualizando función:', error);
            throw error;
        }
    },

    async delete(showtimeId) {
        console.log('🗑️ ShowtimesAPI.delete - Eliminando función:', showtimeId);
        try {
            const response = await apiRequest('/showtimes/delete', {
                method: 'DELETE',
                body: JSON.stringify({ showtime_id: showtimeId })
            });
            console.log('✅ Función eliminada:', response);
            return response;
        } catch (error) {
            console.error('❌ Error eliminando función:', error);
            throw error;
        }
    }
};

// Funciones para teatros/salas
const TheatersAPI = {
    async getAll() {
        console.log('🏛️ TheatersAPI.getAll - Obteniendo todas las salas');
        try {
            const response = await apiRequest('/theaters/all', {
                method: 'GET'
            });
            console.log('🏛️ Salas obtenidas:', response);
            return response.theaters || [];
        } catch (error) {
            console.error('❌ Error obteniendo salas:', error);
            throw error;
        }
    }
};

// Funciones para asientos reservados
const ReservedSeatsAPI = {
    async getAll() {
        return await apiRequest('/reserved_seats/all', {
            method: 'GET'
        });
    },

    async create(seatData) {
        return await apiRequest('/reserved_seats', {
            method: 'POST',
            body: JSON.stringify(seatData)
        });
    },

    async getByShowtime(showtimeId) {
        // Usar el endpoint específico para obtener asientos por showtime
        console.log('🔍 ReservedSeatsAPI.getByShowtime - Obteniendo asientos para showtime:', showtimeId);
        console.log('🌐 URL completa:', `${APP_CONFIG.API_BASE_URL}/reserved_seats/showtime/${showtimeId}`);
        
        try {
            const response = await apiRequest(`/reserved_seats/showtime/${showtimeId}`, {
                method: 'GET'
            });
            
            console.log('📋 RESPUESTA RAW del servidor:', response);
            console.log('📋 Tipo de respuesta:', typeof response);
            
            // El endpoint devuelve {showtime_id: X, reserved_seats: ["A1", "A2"]}
            if (response && response.reserved_seats && Array.isArray(response.reserved_seats)) {
                console.log('📋 Asientos reservados encontrados:', response.reserved_seats);
                return response.reserved_seats;
            } else {
                console.log('📋 No se encontraron asientos reservados o formato incorrecto');
                return [];
            }
        } catch (error) {
            console.error('❌ ERROR COMPLETO en ReservedSeatsAPI.getByShowtime:', error);
            console.error('❌ Error stack:', error.stack);
            return [];
        }
    }
};

// Funciones para ventas
const SalesAPI = {
    async create(saleData) {
        return await apiRequest('/sales/create', {
            method: 'POST',
            body: JSON.stringify(saleData)
        });
    },

    async getAll() {
        return await apiRequest('/sales/all', {
            method: 'GET'
        });
    },

    async getById(id) {
        return await apiRequest('/sales/by_id', {
            method: 'POST',
            body: JSON.stringify({ id })
        });
    }
};

// Funciones para reportes administrativos
const ReportsAPI = {
    async getSalesSummary() {
        console.log('📊 ReportsAPI.getSalesSummary - Obteniendo resumen de ventas');
        try {
            const response = await apiRequest('/reports/sales-summary', {
                method: 'GET'
            });
            console.log('📊 Resumen de ventas obtenido:', response);
            return response;
        } catch (error) {
            console.error('❌ Error obteniendo resumen de ventas:', error);
            throw error;
        }
    },

    async getDetailedSales() {
        console.log('📋 ReportsAPI.getDetailedSales - Obteniendo ventas detalladas');
        try {
            const response = await apiRequest('/reports/detailed-sales', {
                method: 'GET'
            });
            console.log('📋 Ventas detalladas obtenidas:', response);
            return response;
        } catch (error) {
            console.error('❌ Error obteniendo ventas detalladas:', error);
            throw error;
        }
    }
};

// Función para verificar si el token está válido
function isAuthenticated() {
    // Verificar token en localStorage
    const authToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('cinemaUser');
    
    console.log('isAuthenticated check:', { 
        authToken: !!authToken, 
        storedUser: !!storedUser,
        hasValidToken: !!(authToken || (storedUser && JSON.parse(storedUser).token))
    });
    
    return !!(authToken || (storedUser && JSON.parse(storedUser).token));
}

// Función para obtener datos del usuario
function getUserData() {
    const userData = localStorage.getItem('cinemaUser');
    return userData ? JSON.parse(userData) : null;
}

// Función de diagnóstico para verificar conectividad
async function diagnosticAPI() {
    const diagnostics = {
        baseUrl: API_BASE_URL,
        timestamp: new Date().toISOString(),
        tests: []
    };
    
    // Test 1: Verificar conectividad básica
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        diagnostics.tests.push({
            name: 'Conectividad básica',
            status: response.ok ? 'OK' : 'FAIL',
            details: `HTTP ${response.status} - ${response.statusText}`
        });
    } catch (error) {
        diagnostics.tests.push({
            name: 'Conectividad básica',
            status: 'FAIL',
            details: error.message
        });
    }
    
    // Test 2: Verificar endpoint de documentación
    try {
        const response = await fetch(`${API_BASE_URL}/docs`);
        diagnostics.tests.push({
            name: 'Documentación API',
            status: response.ok ? 'OK' : 'FAIL',
            details: `HTTP ${response.status}`
        });
    } catch (error) {
        diagnostics.tests.push({
            name: 'Documentación API',
            status: 'FAIL',
            details: error.message
        });
    }
    
    // Test 3: Verificar CORS
    try {
        const response = await fetch(`${API_BASE_URL}/`, {
            method: 'OPTIONS'
        });
        diagnostics.tests.push({
            name: 'CORS (OPTIONS)',
            status: response.ok ? 'OK' : 'FAIL',
            details: `HTTP ${response.status}`
        });
    } catch (error) {
        diagnostics.tests.push({
            name: 'CORS (OPTIONS)',
            status: 'FAIL',
            details: error.message
        });
    }
    
    console.table(diagnostics.tests);
    return diagnostics;
}

// Función para probar endpoints específicos
async function testEndpoints() {
    console.log("🔍 Probando endpoints...");
    const results = [];
    
    // Test 1: Verificar que el servidor esté corriendo
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        results.push({
            endpoint: 'GET /',
            status: response.status,
            statusText: response.statusText,
            success: response.ok
        });
    } catch (error) {
        results.push({
            endpoint: 'GET /',
            error: error.message,
            success: false
        });
    }
    
    // Test 2: Verificar documentación
    try {
        const response = await fetch(`${API_BASE_URL}/docs`);
        results.push({
            endpoint: 'GET /docs',
            status: response.status,
            statusText: response.statusText,
            success: response.ok
        });
    } catch (error) {
        results.push({
            endpoint: 'GET /docs',
            error: error.message,
            success: false
        });
    }
    
    // Test 3: Verificar ruta de login
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: 'test', password: 'test' })
        });
        results.push({
            endpoint: 'POST /auth/login',
            status: response.status,
            statusText: response.statusText,
            success: response.status !== 405
        });
    } catch (error) {
        results.push({
            endpoint: 'POST /auth/login',
            error: error.message,
            success: false
        });
    }
    
    // Test 4: Verificar CORS con OPTIONS
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'OPTIONS'
        });
        results.push({
            endpoint: 'OPTIONS /auth/login',
            status: response.status,
            statusText: response.statusText,
            success: response.ok
        });
    } catch (error) {
        results.push({
            endpoint: 'OPTIONS /auth/login',
            error: error.message,
            success: false
        });
    }
    
    console.table(results);
    
    // Mostrar resultado visual
    const successCount = results.filter(r => r.success).length;
    const message = `${successCount}/${results.length} endpoints funcionando. Ver consola para detalles.`;
    
    if (window.showNotification) {
        window.showNotification(message, successCount === results.length ? 'success' : 'error');
    } else {
        alert(message);
    }
    
    return results;
}
