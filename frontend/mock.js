// MODO MOCK COMPLETAMENTE DESACTIVADO
// Este archivo ya no se usa - solo datos reales de la API

console.log("🚫 Archivo mock.js desactivado - Solo se usarán datos reales de la API");

// Función vacía para evitar errores si se llama
function enableMockMode() {
    console.log("🚫 enableMockMode() ignorado - Modo mock desactivado");
}

// Función vacía para evitar errores si se llama  
function disableMockMode() {
    console.log("✅ Modo mock ya está desactivado");
}

// No hacer nada en el evento DOMContentLoaded
window.addEventListener('DOMContentLoaded', function() {
    console.log("✅ Solo usando datos reales de la API - Modo mock completamente desactivado");
});
    movies: [
        { id: 1, title: "Mad Max: Furia en la carretera", genre: "Acción" },
        { id: 2, title: "Un jefe en pañales", genre: "Comedia" },
        { id: 3, title: "El conjuro 3", genre: "Terror" }
    ],
    showtimes: [
        { id: 1, movie_id: 1, theater_id: 1, show_time: "14:00:00", show_date: "2024-01-15" },
        { id: 2, movie_id: 1, theater_id: 2, show_time: "17:00:00", show_date: "2024-01-15" },
        { id: 3, movie_id: 2, theater_id: 1, show_time: "15:30:00", show_date: "2024-01-15" },
        { id: 4, movie_id: 3, theater_id: 3, show_time: "19:00:00", show_date: "2024-01-15" }
    ],
    reserved_seats: [
        { id: 1, showtime_id: 1, seat_row: "A", seat_number: 1 },
        { id: 2, showtime_id: 1, seat_row: "A", seat_number: 2 },
        { id: 3, showtime_id: 2, seat_row: "B", seat_number: 3 }
    ]
};

// Mock API functions
const MockAuthAPI = {
    async login(username, password) {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Simular delay
        
        if (username === "admin" && password === "123456") {
            return {
                access_token: "mock_token_12345",
                user: { id: 1, username: username }
            };
        } else {
            throw new Error("Credenciales inválidas");
        }
    },

    logout() {
        // Mock logout
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
    }
};

const MockMoviesAPI = {
    async getAll() {
        await new Promise(resolve => setTimeout(resolve, 500));
        return { movies: MOCK_DATA.movies };
    }
};

const MockShowtimesAPI = {
    async getAll() {
        await new Promise(resolve => setTimeout(resolve, 500));
        return { showtimes: MOCK_DATA.showtimes };
    }
};

const MockReservedSeatsAPI = {
    async getAll() {
        await new Promise(resolve => setTimeout(resolve, 300));
        return { reserved_seats: MOCK_DATA.reserved_seats };
    },

    async getByShowtime(showtimeId) {
        await new Promise(resolve => setTimeout(resolve, 300));
        return MOCK_DATA.reserved_seats.filter(seat => seat.showtime_id === showtimeId);
    },

    async create(seatData) {
        await new Promise(resolve => setTimeout(resolve, 800));
        const newSeat = {
            id: MOCK_DATA.reserved_seats.length + 1,
            ...seatData
        };
        MOCK_DATA.reserved_seats.push(newSeat);
        return newSeat;
    }
};

const MockSalesAPI = {
    async create(saleData) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        return {
            id: Math.floor(Math.random() * 1000),
            ...saleData,
            created_at: new Date().toISOString()
        };
    }
};

// Función para activar el modo mock manualmente
function enableMockMode() {
    console.log("🧪 MODO MOCK ACTIVADO MANUALMENTE - Usando datos simulados");
    
    // Reemplazar APIs reales con mocks
    window.AuthAPI = MockAuthAPI;
    window.MoviesAPI = MockMoviesAPI;
    window.ShowtimesAPI = MockShowtimesAPI;
    window.ReservedSeatsAPI = MockReservedSeatsAPI;
    window.SalesAPI = MockSalesAPI;
    
    // Simular usuario autenticado si hay token
    if (localStorage.getItem('authToken') === 'mock_token_12345') {
        window.isAuthenticated = () => true;
        window.getUserData = () => ({ id: 1, username: "admin" });
    }
    
    // Mostrar indicador visual
    let indicator = document.getElementById('mock-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'mock-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: #ff9800;
            color: white;
            text-align: center;
            padding: 5px;
            font-size: 12px;
            z-index: 9999;
            font-weight: bold;
        `;
        indicator.textContent = '🧪 MODO MOCK ACTIVO - Credenciales: admin/123456';
        document.body.appendChild(indicator);
    }
    
    // Mostrar notificación
    if (window.showNotification) {
        window.showNotification('Modo mock activado. Use: admin/123456', 'success');
    } else {
        alert('Modo mock activado. Credenciales: admin/123456');
    }
}

// Auto-activar modo mock si no hay conexión con la API
window.addEventListener('DOMContentLoaded', function() {
    // FORZAR USO DE API REAL - DESACTIVAR MODO MOCK
    console.log("🔧 Modo mock DESACTIVADO - Usando solo API real");
    /*
    // Verificar si estamos en modo desarrollo
    const isDevelopment = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1' ||
                         window.location.protocol === 'file:';
    
    if (isDevelopment) {
        // Intentar hacer una petición simple para verificar conectividad
        fetch('http://localhost:8000/')
            .then(response => {
                if (!response.ok) throw new Error('API no disponible');
                console.log("✅ API disponible - Usando modo normal");
            })
            .catch(() => {
                console.log("❌ API no disponible - Activando modo mock");
                enableMockMode();
            });
    }
    */
});

// Exportar función para uso manual
window.enableMockMode = enableMockMode;
