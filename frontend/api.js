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
                errorMessage = errorData.detail || errorData.message || errorMessage;
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
                localStorage.setItem('userData', JSON.stringify(data.user || {}));
                console.log('Token saved successfully');
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
    }
};

// Funciones para películas
const MoviesAPI = {
    async getAll() {
        return await apiRequest('/movies/all', {
            method: 'GET'
        });
    },

    async getById(id) {
        return await apiRequest('/movies/by_id', {
            method: 'POST',
            body: JSON.stringify({ id })
        });
    },

    async search(query) {
        return await apiRequest('/movies/search', {
            method: 'POST',
            body: JSON.stringify({ query })
        });
    }
};

// Funciones para salas/teatros
const TheatersAPI = {
    async getAll() {
        return await apiRequest('/theaters/all', {
            method: 'GET'
        });
    },

    async getById(id) {
        return await apiRequest('/theaters/by_id', {
            method: 'POST',
            body: JSON.stringify({ id })
        });
    }
};

// Funciones para horarios
const ShowtimesAPI = {
    async getAll() {
        return await apiRequest('/showtimes/all', {
            method: 'GET'
        });
    },

    async getById(id) {
        return await apiRequest('/showtimes/by_id', {
            method: 'POST',
            body: JSON.stringify({ id })
        });
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
            console.log('📋 Es array:', Array.isArray(response));
            
            const result = Array.isArray(response) ? response : [];
            console.log('📋 Resultado final (array):', result);
            console.log('📋 Cantidad de asientos en resultado:', result.length);
            
            return result;
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

// Función para verificar si el token está válido
function isAuthenticated() {
    // Verificar tanto authToken como el localStorage
    const storedUser = localStorage.getItem('cinemaUser');
    const hasToken = !!authToken || (storedUser && JSON.parse(storedUser).token);
    console.log('isAuthenticated check:', { authToken: !!authToken, storedUser: !!storedUser, hasToken });
    return hasToken;
}

// Función para obtener datos del usuario
function getUserData() {
    const userData = localStorage.getItem('userData');
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
