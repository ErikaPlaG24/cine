// Script para la administración CRUD
console.log('🔧 script-admin.js loaded');

// Variables globales
let currentUser = null;
let moviesData = [];
let theatersData = [];

// Función para limpiar sesión y redirigir al login
function clearSessionAndRedirect(message = 'Sesión expirada. Redirigiendo al login...') {
    console.log('🧹 Limpiando sesión...');
    console.log('🔍 Causa del redirect:', message);
    
    localStorage.removeItem('authToken');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userId');
    showError(message);
    console.log('⏰ Redirigiendo en 3 segundos...');
    setTimeout(() => {
        console.log('🔄 Redirigiendo a login.html');
        window.location.href = 'login.html';
    }, 3000);
}

// Función para inicializar la página
async function initAdmin() {
    console.log('🚀 Inicializando página de administración...');
    
    try {
        // Verificar autenticación (igual que en reportes)
        if (!isAuthenticated()) {
            console.log('❌ Usuario no autenticado, redirigiendo...');
            window.location.href = 'login.html';
            return;
        }

        // Obtener datos del usuario
        try {
            currentUser = await getCurrentUserData();
            console.log('👤 Usuario actual:', currentUser);
        } catch (error) {
            console.log('❌ Error obteniendo datos del usuario, redirigiendo al login...');
            window.location.href = 'login.html';
            return;
        }

        // Verificar si es administrador
        if (!isAdmin(currentUser)) {
            console.log('❌ Usuario no es administrador');
            showError('No tienes permisos para acceder a esta sección. Solo los administradores pueden acceder al panel de administración.');
            setTimeout(() => {
                window.location.href = 'reservas.html';
            }, 3000);
            return;
        }

        console.log('✅ Usuario administrador verificado');
        
        // Cargar datos iniciales
        await loadInitialData();

    } catch (error) {
        console.error('❌ Error inicializando admin:', error);
        showError('Error al cargar el panel de administración: ' + error.message);
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 3000);
    }
}

// Función para obtener datos del usuario actual decodificando el token
async function getCurrentUserData() {
    try {
        const token = localStorage.getItem('authToken');
        if (!token) {
            console.log('❌ No se encontró token de autenticación en localStorage');
            // Intentar obtener de cinemaUser como respaldo
            const storedUser = localStorage.getItem('cinemaUser');
            if (storedUser) {
                const userData = JSON.parse(storedUser);
                if (userData.token) {
                    console.log('✅ Token encontrado en cinemaUser');
                    return userData;
                }
            }
            throw new Error('No se encontró token de autenticación');
        }

        // Decodificar el JWT para obtener los datos del usuario
        const payload = JSON.parse(atob(token.split('.')[1]));
        
        return {
            id: payload.user_id || payload.id,
            username: payload.username,
            role: payload.role,
            token: token
        };
    } catch (error) {
        console.error('Error obteniendo datos del usuario:', error);
        // Limpiar cualquier token corrupto
        localStorage.removeItem('authToken');
        localStorage.removeItem('cinemaUser');
        throw new Error('Error al obtener datos del usuario');
    }
}

// Función para verificar si el usuario es administrador
function isAdmin(userData) {
    return userData && userData.role === 'admin';
}

// Función para actualizar la información del usuario en la navbar
function updateUserInfo(user) {
    const userInfo = document.getElementById('userInfo');
    if (userInfo && user) {
        userInfo.innerHTML = `
            <span class="me-2">${user.username || user.email || 'Usuario'}</span>
            <span class="badge badge-admin">ADMIN</span>
        `;
    }
}

// Función para cerrar sesión
function logout() {
    cerrarSesion();
}

// Función para cargar datos iniciales
async function loadInitialData() {
    console.log('📊 Cargando datos iniciales...');
    
    try {
        // Cargar datos necesarios para los formularios
        await Promise.all([
            loadMoviesData(),
            loadTheatersData()
        ]);
        
        // Cargar las tablas
        await Promise.all([
            loadUsersTable(),
            loadMoviesTable(),
            loadShowtimesTable()
        ]);
        
        console.log('✅ Datos iniciales cargados');
        
    } catch (error) {
        console.error('❌ Error cargando datos iniciales:', error);
        showError('Error al cargar los datos: ' + error.message);
    }
}

// ===========================================
// GESTIÓN DE USUARIOS
// ===========================================

async function loadUsersTable() {
    console.log('👥 Cargando tabla de usuarios...');
    
    try {
        const users = await UsersAPI.getAll();
        displayUsersTable(users);
    } catch (error) {
        console.error('❌ Error cargando usuarios:', error);
        document.getElementById('usersTable').innerHTML = `
            <div class="alert alert-danger">
                Error al cargar usuarios: ${error.message}
            </div>
        `;
    }
}

function displayUsersTable(users) {
    const container = document.getElementById('usersTable');
    
    if (!users || users.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No hay usuarios registrados.</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Usuario</th>
                        <th>Rol</th>
                        <th>Fecha Registro</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${user.user_id}</td>
                            <td>${user.username || 'N/A'}</td>
                            <td>
                                <span class="badge ${user.role === 'admin' ? 'bg-danger' : 'bg-primary'}">
                                    ${user.role === 'admin' ? 'Administrador' : 'Cliente'}
                                </span>
                            </td>
                            <td>${new Date(user.created_at || user.registration_date).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary me-1" 
                                        onclick="editUser(${user.user_id})">
                                    ✏️ Editar
                                </button>
                                <button class="btn btn-sm btn-outline-danger" 
                                        onclick="deleteUser(${user.user_id}, '${user.username}')">
                                    🗑️ Eliminar
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function showCreateUserModal() {
    document.getElementById('userModalTitle').textContent = 'Nuevo Usuario';
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    document.getElementById('userPassword').required = true;
    
    const modal = new bootstrap.Modal(document.getElementById('userModal'));
    modal.show();
}

async function editUser(userId) {
    try {
        const user = await UsersAPI.getById(userId);
        
        document.getElementById('userModalTitle').textContent = 'Editar Usuario';
        document.getElementById('userId').value = user.user_id;
        document.getElementById('userUsername').value = user.username;
        document.getElementById('userRole').value = user.role;
        document.getElementById('userPassword').required = false;
        document.getElementById('userPassword').placeholder = 'Dejar vacío para mantener la contraseña actual';
        
        const modal = new bootstrap.Modal(document.getElementById('userModal'));
        modal.show();
    } catch (error) {
        console.error('❌ Error cargando usuario:', error);
        showError('Error al cargar los datos del usuario: ' + error.message);
    }
}

async function saveUser() {
    try {
        const userId = document.getElementById('userId').value;
        const username = document.getElementById('userUsername').value;
        const password = document.getElementById('userPassword').value;
        const role = document.getElementById('userRole').value;
        
        if (!username || !role) {
            showError('Usuario y rol son obligatorios');
            return;
        }
        
        if (!userId && !password) {
            showError('La contraseña es obligatoria para nuevos usuarios');
            return;
        }
        
        const userData = { username, role };
        if (password) {
            userData.password = password;
        }
        
        if (userId) {
            // Actualizar usuario existente
            await UsersAPI.update(parseInt(userId), userData);
            showSuccess('Usuario actualizado correctamente');
        } else {
            // Crear nuevo usuario
            await UsersAPI.create(userData);
            showSuccess('Usuario creado correctamente');
        }
        
        // Cerrar modal y recargar tabla
        bootstrap.Modal.getInstance(document.getElementById('userModal')).hide();
        await loadUsersTable();
        
    } catch (error) {
        console.error('❌ Error guardando usuario:', error);
        showError('Error al guardar el usuario: ' + error.message);
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`¿Estás seguro de que quieres eliminar al usuario "${username}"?`)) {
        return;
    }
    
    try {
        await UsersAPI.delete(userId);
        showSuccess('Usuario eliminado correctamente');
        await loadUsersTable();
    } catch (error) {
        console.error('❌ Error eliminando usuario:', error);
        showError('Error al eliminar el usuario: ' + error.message);
    }
}

// ===========================================
// GESTIÓN DE PELÍCULAS
// ===========================================

async function loadMoviesData() {
    try {
        const response = await MoviesAPI.getAll();
        moviesData = response.movies || [];
        
        // Actualizar selector de películas en el modal de funciones
        const selector = document.getElementById('showtimeMovie');
        selector.innerHTML = '<option value="">Seleccionar película</option>' +
            moviesData.map(movie => `<option value="${movie.id}">${movie.title}</option>`).join('');
            
    } catch (error) {
        console.error('❌ Error cargando películas:', error);
        moviesData = [];
    }
}

async function loadMoviesTable() {
    console.log('🎬 Cargando tabla de películas...');
    
    try {
        const response = await MoviesAPI.getAll();
        const movies = response.movies || [];
        displayMoviesTable(movies);
    } catch (error) {
        console.error('❌ Error cargando películas:', error);
        document.getElementById('moviesTable').innerHTML = `
            <div class="alert alert-danger">
                Error al cargar películas: ${error.message}
            </div>
        `;
    }
}

function displayMoviesTable(movies) {
    const container = document.getElementById('moviesTable');
    
    if (!movies || movies.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No hay películas registradas.</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Título</th>
                        <th>Duración</th>
                        <th>Fecha Estreno</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${movies.map(movie => `
                        <tr>
                            <td>${movie.id}</td>
                            <td>${movie.title}</td>
                            <td>${movie.duration_minutes} min</td>
                            <td>${new Date(movie.release_date).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary me-1" 
                                        onclick="editMovie(${movie.id})">
                                    ✏️ Editar
                                </button>
                                <button class="btn btn-sm btn-outline-danger" 
                                        onclick="deleteMovie(${movie.id}, '${movie.title}')">
                                    🗑️ Eliminar
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function showCreateMovieModal() {
    document.getElementById('movieModalTitle').textContent = 'Nueva Película';
    document.getElementById('movieForm').reset();
    document.getElementById('movieId').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('movieModal'));
    modal.show();
}

async function editMovie(movieId) {
    try {
        const movie = await MoviesAPI.getById(movieId);
        
        document.getElementById('movieModalTitle').textContent = 'Editar Película';
        document.getElementById('movieId').value = movie.id;
        document.getElementById('movieTitle').value = movie.title || '';
        document.getElementById('movieOriginalTitle').value = movie.original_title || '';
        document.getElementById('movieDuration').value = movie.duration_minutes || '';
        document.getElementById('movieReleaseDate').value = movie.release_date || '';
        document.getElementById('movieOverview').value = movie.overview || '';
        document.getElementById('moviePosterUrl').value = movie.poster_url || '';
        document.getElementById('movieWallpaperUrl').value = movie.wallpaper_url || '';
        
        const modal = new bootstrap.Modal(document.getElementById('movieModal'));
        modal.show();
    } catch (error) {
        console.error('❌ Error cargando película:', error);
        showError('Error al cargar los datos de la película: ' + error.message);
    }
}

async function saveMovie() {
    try {
        const movieId = document.getElementById('movieId').value;
        const title = document.getElementById('movieTitle').value;
        const originalTitle = document.getElementById('movieOriginalTitle').value;
        const duration = document.getElementById('movieDuration').value;
        const releaseDate = document.getElementById('movieReleaseDate').value;
        const overview = document.getElementById('movieOverview').value;
        const posterUrl = document.getElementById('moviePosterUrl').value;
        const wallpaperUrl = document.getElementById('movieWallpaperUrl').value;
        
        if (!title || !duration || !releaseDate) {
            showError('Título, duración y fecha de estreno son obligatorios');
            return;
        }
        
        const movieData = {
            title,
            original_title: originalTitle,
            duration_minutes: parseInt(duration),
            release_date: releaseDate,
            overview,
            poster_url: posterUrl,
            wallpaper_url: wallpaperUrl
        };
        
        if (movieId) {
            // Actualizar película existente
            await MoviesAPI.update(parseInt(movieId), movieData);
            showSuccess('Película actualizada correctamente');
        } else {
            // Crear nueva película
            await MoviesAPI.create(movieData);
            showSuccess('Película creada correctamente');
        }
        
        // Cerrar modal y recargar tabla
        bootstrap.Modal.getInstance(document.getElementById('movieModal')).hide();
        await loadMoviesTable();
        await loadMoviesData(); // Actualizar datos para el selector de funciones
        
    } catch (error) {
        console.error('❌ Error guardando película:', error);
        showError('Error al guardar la película: ' + error.message);
    }
}

async function deleteMovie(movieId, title) {
    if (!confirm(`¿Estás seguro de que quieres eliminar la película "${title}"?`)) {
        return;
    }
    
    try {
        await MoviesAPI.delete(movieId);
        showSuccess('Película eliminada correctamente');
        await loadMoviesTable();
        await loadMoviesData(); // Actualizar datos para el selector de funciones
    } catch (error) {
        console.error('❌ Error eliminando película:', error);
        showError('Error al eliminar la película: ' + error.message);
    }
}

// ===========================================
// GESTIÓN DE FUNCIONES (SHOWTIMES)
// ===========================================

async function loadTheatersData() {
    try {
        console.log('🏛️ Cargando datos de salas...');
        const theaters = await TheatersAPI.getAll();
        theatersData = theaters || [];
        console.log('🏛️ Salas cargadas:', theatersData);
        
        // Actualizar selector de salas en el modal de funciones
        const selector = document.getElementById('showtimeTheater');
        if (selector) {
            selector.innerHTML = '<option value="">Seleccionar sala</option>' +
                theatersData.map(theater => `<option value="${theater.theater_id}">${theater.name}</option>`).join('');
            console.log('🏛️ Selector de salas actualizado con', theatersData.length, 'opciones');
        }
            
    } catch (error) {
        console.error('❌ Error cargando salas:', error);
        theatersData = [];
    }
}

async function loadShowtimesTable() {
    console.log('📅 Cargando tabla de funciones...');
    
    try {
        const response = await ShowtimesAPI.getAll();
        const showtimes = response.showtimes || [];
        displayShowtimesTable(showtimes);
    } catch (error) {
        console.error('❌ Error cargando funciones:', error);
        document.getElementById('showtimesTable').innerHTML = `
            <div class="alert alert-danger">
                Error al cargar funciones: ${error.message}
            </div>
        `;
    }
}

function displayShowtimesTable(showtimes) {
    const container = document.getElementById('showtimesTable');
    
    if (!showtimes || showtimes.length === 0) {
        container.innerHTML = '<div class="alert alert-info">No hay funciones programadas.</div>';
        return;
    }
    
    container.innerHTML = `
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Película</th>
                        <th>Sala</th>
                        <th>Fecha</th>
                        <th>Hora</th>
                        <th>Asientos Disp.</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${showtimes.map(showtime => {
                        // Parsear la fecha y hora del campo datetime
                        const datetime = new Date(showtime.datetime);
                        const isValidDate = !isNaN(datetime.getTime());
                        
                        return `
                        <tr>
                            <td>${showtime.showtime_id}</td>
                            <td>${showtime.movie_title || 'N/A'}</td>
                            <td>${showtime.theater_name || 'Sala ' + showtime.theater_id}</td>
                            <td>${isValidDate ? datetime.toLocaleDateString() : 'Fecha inválida'}</td>
                            <td>${isValidDate ? datetime.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : 'Hora inválida'}</td>
                            <td>${showtime.available_seats}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary me-1" 
                                        onclick="editShowtime(${showtime.showtime_id})">
                                    ✏️ Editar
                                </button>
                                <button class="btn btn-sm btn-outline-danger" 
                                        onclick="deleteShowtime(${showtime.showtime_id}, '${showtime.movie_title || 'esta función'}')">
                                    🗑️ Eliminar
                                </button>
                            </td>
                        </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function showCreateShowtimeModal() {
    // Asegurar que los datos de películas y salas estén cargados
    await Promise.all([
        loadMoviesData(),
        loadTheatersData()
    ]);
    
    document.getElementById('showtimeModalTitle').textContent = 'Nueva Función';
    document.getElementById('showtimeForm').reset();
    document.getElementById('showtimeId').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('showtimeModal'));
    modal.show();
}

async function editShowtime(showtimeId) {
    try {
        // Asegurar que los datos de películas y salas estén cargados
        await Promise.all([
            loadMoviesData(),
            loadTheatersData()
        ]);
        
        const showtime = await ShowtimesAPI.getById(showtimeId);
        
        document.getElementById('showtimeModalTitle').textContent = 'Editar Función';
        document.getElementById('showtimeId').value = showtime.showtime_id;
        document.getElementById('showtimeMovie').value = showtime.movie_id || '';
        document.getElementById('showtimeTheater').value = showtime.theater_id || '';
        
        // Parsear el datetime para separar fecha y hora
        if (showtime.datetime) {
            const datetime = new Date(showtime.datetime);
            if (!isNaN(datetime.getTime())) {
                // Formatear fecha para input date (YYYY-MM-DD)
                const dateStr = datetime.toISOString().split('T')[0];
                // Formatear hora para input time (HH:MM)
                const timeStr = datetime.toLocaleTimeString('en-GB', {hour: '2-digit', minute: '2-digit'});
                
                document.getElementById('showtimeDate').value = dateStr;
                document.getElementById('showtimeTime').value = timeStr;
            }
        }
        
        document.getElementById('showtimeAvailableSeats').value = showtime.available_seats || '';
        
        const modal = new bootstrap.Modal(document.getElementById('showtimeModal'));
        modal.show();
    } catch (error) {
        console.error('❌ Error cargando función:', error);
        showError('Error al cargar los datos de la función: ' + error.message);
    }
}

async function saveShowtime() {
    try {
        const showtimeId = document.getElementById('showtimeId').value;
        const movieId = document.getElementById('showtimeMovie').value;
        const theaterId = document.getElementById('showtimeTheater').value;
        const date = document.getElementById('showtimeDate').value;
        const time = document.getElementById('showtimeTime').value;
        const availableSeats = document.getElementById('showtimeAvailableSeats').value;
        
        if (!movieId || !theaterId || !date || !time || !availableSeats) {
            showError('Todos los campos son obligatorios');
            return;
        }
        
        // Combinar fecha y hora en formato datetime
        const datetime = `${date} ${time}:00`; // Agregar segundos
        
        const showtimeData = {
            movie_id: parseInt(movieId),
            theater_id: parseInt(theaterId),
            datetime: datetime,
            available_seats: parseInt(availableSeats),
            base_price: 75.00 // Precio base por defecto
        };
        
        if (showtimeId) {
            // Actualizar función existente
            await ShowtimesAPI.update(parseInt(showtimeId), showtimeData);
            showSuccess('Función actualizada correctamente');
        } else {
            // Crear nueva función
            await ShowtimesAPI.create(showtimeData);
            showSuccess('Función creada correctamente');
        }
        
        // Cerrar modal y recargar tabla
        bootstrap.Modal.getInstance(document.getElementById('showtimeModal')).hide();
        await loadShowtimesTable();
        
    } catch (error) {
        console.error('❌ Error guardando función:', error);
        showError('Error al guardar la función: ' + error.message);
    }
}

async function deleteShowtime(showtimeId, movieTitle) {
    if (!confirm(`¿Estás seguro de que quieres eliminar la función de "${movieTitle}"?`)) {
        return;
    }
    
    try {
        await ShowtimesAPI.delete(showtimeId);
        showSuccess('Función eliminada correctamente');
        await loadShowtimesTable();
    } catch (error) {
        console.error('❌ Error eliminando función:', error);
        showError('Error al eliminar la función: ' + error.message);
    }
}

// ===========================================
// FUNCIONES DE UTILIDAD
// ===========================================

function showSuccess(message) {
    console.log('✅', message);
    // Crear y mostrar una notificación de éxito
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}

function showError(message) {
    console.error('❌', message);
    // Crear y mostrar una notificación de error
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    
    // Auto-remover después de 8 segundos
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 8000);
}

// Función para limpiar sesión corrupta y redirigir al login
function cleanSessionAndRedirect() {
    console.log('🧹 Limpiando sesión corrupta...');
    localStorage.removeItem('authToken');
    localStorage.removeItem('cinemaUser');
    localStorage.removeItem('userRole');
    
    showError('Sesión corrupta detectada. Por favor, inicia sesión nuevamente.');
    setTimeout(() => {
        window.location.href = 'login.html';
    }, 2000);
}

// Función para debuggear token
function debugToken() {
    console.log('🔍 === DEBUG TOKEN ===');
    const token = localStorage.getItem('authToken');
    
    if (!token) {
        console.log('❌ No hay token en localStorage');
        return false;
    }
    
    console.log('📝 Token completo (primeros 50 chars):', token.substring(0, 50) + '...');
    console.log('📏 Longitud del token:', token.length);
    console.log('📝 Tipo de token:', typeof token);
    
    // Verificar caracteres extraños
    const hasWeirdChars = /[^\w\.\-_]/.test(token);
    console.log('⚠️ Tiene caracteres extraños:', hasWeirdChars);
    
    // Intentar split por puntos
    const parts = token.split('.');
    console.log('🔢 Número de partes separadas por punto:', parts.length);
    
    if (parts.length === 3) {
        console.log('✅ Formato JWT válido');
        try {
            // Intentar decodificar solo el payload
            const payload = atob(parts[1]);
            console.log('📄 Payload decodificado:', payload);
            
            try {
                const parsedPayload = JSON.parse(payload);
                console.log('✅ Payload parseado exitosamente:', parsedPayload);
                console.log('🔍 === FIN DEBUG TOKEN ===');
                return true;
            } catch (parseError) {
                console.error('❌ Error parseando payload:', parseError);
                console.log('🔍 === FIN DEBUG TOKEN ===');
                return false;
            }
        } catch (decodeError) {
            console.error('❌ Error decodificando base64:', decodeError);
            console.log('🔍 === FIN DEBUG TOKEN ===');
            return false;
        }
    } else {
        console.log('❌ No es un JWT válido');
        console.log('🔍 Partes:', parts.map((part, index) => `${index}: ${part.substring(0, 20)}...`));
        console.log('🔍 === FIN DEBUG TOKEN ===');
        return false;
    }
}

// Inicializar cuando se carga la página
document.addEventListener('DOMContentLoaded', initAdmin);
