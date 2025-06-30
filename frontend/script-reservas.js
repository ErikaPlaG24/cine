let nombreUsuario = "";
let currentUser = null;
let peliculasData = [];
let horariosData = [];
let asientosReservadosData = [];

// Objeto para guardar asientos seleccionados temporalmente (para UI)
const asientosSeleccionados = {
  1: new Set(),
  2: new Set(),
  3: new Set()
};

// Función para formatear tiempo
function formatTime(timeString, dateString = null) {
    try {
        // Si timeString ya está en formato HH:MM, devolverlo directamente
        if (timeString && /^\d{1,2}:\d{2}$/.test(timeString)) {
            return timeString;
        }
        
        // Si es una fecha completa, extraer solo la hora
        if (timeString && timeString.includes('T')) {
            const date = new Date(timeString);
            return date.toLocaleTimeString('es-ES', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: false 
            });
        }
        
        // Si tenemos fecha y hora por separado, combinarlas
        if (dateString && timeString) {
            const fullDateTime = `${dateString}T${timeString}:00`;
            const date = new Date(fullDateTime);
            return date.toLocaleTimeString('es-ES', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: false 
            });
        }
        
        // Si no se puede parsear, devolver el string original
        return timeString || 'Horario no disponible';
    } catch (error) {
        // Si hay error, devolver el string original
        return timeString || 'Horario no disponible';
    }
}

// Función para formatear fechas
function formatDate(dateString) {
    try {
        if (!dateString) return 'Fecha no disponible';
        
        // Si ya está en formato YYYY-MM-DD, convertir a formato legible
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
            const date = new Date(dateString + 'T00:00:00');
            return date.toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
        
        // Si es una fecha completa, formatearla
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'long', 
            day: 'numeric'
        });
    } catch (error) {
        return dateString || 'Fecha no disponible';
    }
}

async function cargarDatosIniciales() {
    try {
        // Obtener datos del usuario
        const userData = getUserData();
        if (userData) {
            nombreUsuario = userData.username;
            currentUser = userData.user || { username: userData.username };
        }
        
        await cargarPeliculas();
        // Seleccionar la primera sala por defecto
        document.getElementById("salaSeleccion").value = "1";
        generarAsientos();
        
        // Si hay un horario previamente seleccionado, cargar sus asientos reservados
        const horarioSeleccionado = document.getElementById("horarioSeleccion").value;
        if (horarioSeleccionado) {
            await cargarAsientosReservados();
        }
    } catch (error) {
        console.error('Error cargando datos iniciales:', error);
        showNotification('Error cargando datos: ' + error.message, 'error');
    }
}

async function cargarPeliculas() {
    try {
        const response = await retryApiCall(() => MoviesAPI.getAll());
        // El API devuelve directamente el array de películas
        peliculasData = Array.isArray(response) ? response : (response.movies || []);
        
        const select = document.getElementById("peliculaSeleccion");
        select.innerHTML = '<option value="">Seleccione una película</option>';
        
        peliculasData.forEach(pelicula => {
            const option = document.createElement("option");
            option.value = pelicula.id;
            option.textContent = pelicula.title || `Película ${pelicula.id}`;
            select.appendChild(option);
        });
        
        console.log('Películas cargadas:', peliculasData);
    } catch (error) {
        console.log('Error cargando películas:', error);
        showNotification('Error cargando películas: ' + error.message, 'error');
    }
}

async function cargarHorarios() {
    const peliculaId = document.getElementById("peliculaSeleccion").value;
    const horarioSelect = document.getElementById("horarioSeleccion");
    const salaSelector = document.getElementById("salaSeleccion");
    
    // Desbloquear selector de sala al cambiar de película
    salaSelector.disabled = false;
    salaSelector.style.opacity = "1";
    
    if (!peliculaId) {
        horarioSelect.innerHTML = '<option value="">Seleccione un horario</option>';
        return;
    }

    try {
        const response = await retryApiCall(() => ShowtimesAPI.getAll());
        // El API devuelve directamente el array de horarios
        horariosData = Array.isArray(response) ? response : (response.showtimes || []);
        
        // Filtrar horarios por película seleccionada
        const horariosPelicula = horariosData.filter(horario => 
            horario.movie_id == peliculaId
        );
        
        horarioSelect.innerHTML = '<option value="">Seleccione un horario</option>';
        
        horariosPelicula.forEach(horario => {
            const option = document.createElement("option");
            option.value = horario.id;
            // Mostrar hora, fecha y sala de forma más clara
            const fechaFormateada = formatDate(horario.date);
            const horaFormateada = formatTime(horario.start_time);
            option.textContent = `${horaFormateada} - ${fechaFormateada} - Sala ${horario.theater_id}`;
            option.dataset.theaterId = horario.theater_id;
            horarioSelect.appendChild(option);
        });
        
        console.log('Horarios cargados:', horariosPelicula);
        if (horariosPelicula.length === 0) {
            showNotification('No hay horarios disponibles para esta película', 'info');
        }
    } catch (error) {
        console.log('Error cargando horarios:', error);
        showNotification('Error cargando horarios: ' + error.message, 'error');
    }
}

async function cargarAsientosReservados() {
    const horarioId = document.getElementById("horarioSeleccion").value;
    const salaSelector = document.getElementById("salaSeleccion");
    
    if (!horarioId) {
        console.log('⚠️ No hay horario seleccionado, generando asientos vacíos');
        // Desbloquear selector de sala si no hay horario seleccionado
        salaSelector.disabled = false;
        salaSelector.style.opacity = "1";
        generarAsientos();
        return;
    }

    // Bloquear selector de sala una vez que se selecciona un horario
    salaSelector.disabled = true;
    salaSelector.style.opacity = "0.6";

    try {
        console.log('🔄 Cargando asientos reservados para horario:', horarioId);
        console.log('🌐 Llamando al endpoint:', `/reserved_seats/showtime/${horarioId}`);
        
        const asientosReservados = await ReservedSeatsAPI.getByShowtime(parseInt(horarioId));
        asientosReservadosData = asientosReservados;
        
        // Debug: Log MUY detallado de asientos reservados
        console.log('📋 RESPUESTA COMPLETA del servidor:', asientosReservados);
        console.log('📋 Tipo de respuesta:', typeof asientosReservados);
        console.log('📋 Es array:', Array.isArray(asientosReservados));
        console.log('📋 Cantidad de asientos reservados:', asientosReservados.length);
        
        if (asientosReservados.length > 0) {
            console.log('🪑 DETALLES DE CADA ASIENTO RESERVADO:');
            asientosReservados.forEach((asiento, index) => {
                console.log(`   Asiento ${index + 1}:`, {
                    id: asiento.id,
                    seat_number: asiento.seat_number,
                    seat_row: asiento.seat_row,
                    seat_number_parsed: asiento.seat_number_parsed,
                    showtime_id: asiento.showtime_id,
                    sale_id: asiento.sale_id,
                    reservation_date: asiento.reservation_date,
                    OBJETO_COMPLETO: asiento
                });
            });
        } else {
            console.log('⚠️ NO SE ENCONTRARON ASIENTOS RESERVADOS para este horario');
        }
        
        // Actualizar la sala seleccionada basada en el horario
        const horarioSelect = document.getElementById("horarioSeleccion");
        const selectedOption = horarioSelect.options[horarioSelect.selectedIndex];
        if (selectedOption && selectedOption.dataset.theaterId) {
            document.getElementById("salaSeleccion").value = selectedOption.dataset.theaterId;
        }
        
        // Limpiar selecciones previas antes de generar asientos
        const sala = document.getElementById("salaSeleccion").value;
        if (sala && asientosSeleccionados[sala]) {
            asientosSeleccionados[sala].clear();
            console.log('🧹 Asientos seleccionados limpiados para sala:', sala);
        }
        
        generarAsientos();
        console.log('✅ Asientos reservados cargados y vista actualizada');
    } catch (error) {
        console.error('❌ ERROR COMPLETO cargando asientos reservados:', error);
        console.error('❌ Stack trace:', error.stack);
        asientosReservadosData = [];
        generarAsientos();
    }
}

function generarAsientos() {
    const cont = document.getElementById("asientosContainer");
    cont.innerHTML = "";
    
    const filas = ["A", "B", "C", "D"];
    const sala = document.getElementById("salaSeleccion").value;
    
    if (!sala) {
        cont.innerHTML = "<p>Seleccione una sala</p>";
        return;
    }
    
    const seleccionados = asientosSeleccionados[sala];
    
    // Crear título de pantalla
    const pantalla = document.createElement("div");
    pantalla.style.cssText = "text-align: center; margin-bottom: 20px; padding: 10px; background: #f0f0f0; border-radius: 10px; font-weight: bold;";
    pantalla.textContent = "🎬 PANTALLA 🎬";
    cont.appendChild(pantalla);

    for (let fila of filas) {
        const filaDiv = document.createElement("div");
        filaDiv.style.cssText = "display: flex; justify-content: center; margin-bottom: 10px; gap: 5px;";
        
        for (let i = 1; i <= 5; i++) {
            const idAsiento = `${fila}${i}`;
            const div = document.createElement("div");
            div.className = "asiento";
            div.dataset.fila = fila;
            div.dataset.numero = i;
            div.textContent = idAsiento;
            
            // Verificar si el asiento está reservado en el backend
            console.log(`🔍 Verificando asiento ${idAsiento}...`);
            console.log(`🔍 asientosReservadosData tiene ${asientosReservadosData.length} asientos`);
            
            const estaReservado = asientosReservadosData.some(asiento => {
                // La estructura actual del backend devuelve seat_number completo (ej: "A1")
                const coincideAsientoCompleto = asiento.seat_number === idAsiento;
                
                // También verificar por fila y número parseados si están disponibles
                const coincideFilaYNumero = asiento.seat_row === fila && 
                                           String(asiento.seat_number_parsed) === String(i);
                
                const resultado = coincideAsientoCompleto || coincideFilaYNumero;
                
                console.log(`🔍 Comparando ${idAsiento} con asiento reservado:`, {
                    asientoReservado: asiento,
                    idAsiento: idAsiento,
                    fila: fila,
                    numero: i,
                    'asiento.seat_number': asiento.seat_number,
                    'asiento.seat_row': asiento.seat_row,
                    'asiento.seat_number_parsed': asiento.seat_number_parsed,
                    coincideAsientoCompleto,
                    coincideFilaYNumero,
                    resultado
                });
                
                if (resultado) {
                    console.log(`🔒 ¡ASIENTO ${idAsiento} ESTÁ RESERVADO!`);
                }
                
                return resultado;
            });
            
            console.log(`🔍 Resultado final para ${idAsiento}: ${estaReservado ? 'RESERVADO' : 'DISPONIBLE'}`);
            
            if (estaReservado) {
                div.classList.add("ocupado");
                div.title = "Asiento ocupado";
            } else if (seleccionados.has(idAsiento)) {
                div.classList.add("reservado");
                div.title = "Asiento seleccionado";
                div.onclick = () => {
                    div.classList.remove("reservado");
                    div.classList.add("disponible");
                    seleccionados.delete(idAsiento);
                };
            } else {
                div.classList.add("disponible");
                div.title = "Asiento disponible";
                div.onclick = () => {
                    div.classList.remove("disponible");
                    div.classList.add("reservado");
                    seleccionados.add(idAsiento);
                };
            }
            
            filaDiv.appendChild(div);
        }
        cont.appendChild(filaDiv);
    }
    
    // Agregar leyenda
    const leyenda = document.createElement("div");
    leyenda.style.cssText = "margin-top: 20px; text-align: center; font-size: 14px;";
    leyenda.innerHTML = `
        <div style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
            <span>🟢 Disponible</span>
            <span>🔵 Seleccionado</span>
            <span>🔴 Ocupado</span>
        </div>
    `;
    cont.appendChild(leyenda);
}

async function comprar(event) {
    // Prevenir cualquier comportamiento por defecto
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    
    console.log('🚀 Iniciando proceso de compra...');
    
    const horarioId = document.getElementById("horarioSeleccion").value;
    const peliculaId = document.getElementById("peliculaSeleccion").value;
    const sala = document.getElementById("salaSeleccion").value;
    
    if (!horarioId || !peliculaId) {
        showNotification("Seleccione una película y un horario.", 'error');
        return false;
    }
    
    const seleccionados = asientosSeleccionados[sala];
    if (seleccionados.size === 0) {
        showNotification("Seleccione al menos un asiento.", 'error');
        return false;
    }

    const comprarButton = document.querySelector('button[onclick*="comprar"]');
    
    try {
        setLoading(comprarButton, true);
        
        // Crear la venta
        const asientosSeleccionadosArray = Array.from(seleccionados);
        const saleData = {
            customer_user_id: currentUser.id || 1, // Si no tenemos el ID del usuario, usar 1 como default
            showtime_id: parseInt(horarioId),
            ticket_quantity: seleccionados.size,
            total: seleccionados.size * 75,
            payment_method: "cash",
            seats: asientosSeleccionadosArray
        };
        
        console.log('📤 Enviando datos de venta:', saleData);
        const saleResponse = await SalesAPI.create(saleData);
        console.log('✅ Venta creada exitosamente:', saleResponse);
        
        // Los asientos ya se reservan automáticamente en el endpoint de crear venta
        
        // Preparar datos del ticket
        const pelicula = peliculasData.find(p => p.id == peliculaId);
        const horario = horariosData.find(h => h.id == horarioId);
        
        const ticketData = {
            usuario: nombreUsuario,
            pelicula: pelicula ? pelicula.title : 'Película seleccionada',
            genero: pelicula ? pelicula.genre : 'N/A',
            duracion: pelicula ? pelicula.duration : 'N/A',
            horario: horario ? formatTime(horario.start_time) : 'Horario seleccionado',
            fecha: horario ? formatDate(horario.date) : new Date().toLocaleDateString('es-ES'),
            sala: sala,
            asientos: Array.from(seleccionados),
            total: seleccionados.size * 75,
            fechaCompra: new Date().toLocaleDateString('es-ES'),
            horaCompra: new Date().toLocaleTimeString('es-ES')
        };
        
        // Guardar datos del ticket en localStorage
        localStorage.setItem('ticketData', JSON.stringify(ticketData));
        console.log('🎫 Datos del ticket guardados en localStorage:', ticketData);
        
        // Verificar que los datos se guardaron correctamente
        const verificarTicket = localStorage.getItem('ticketData');
        console.log('✅ Verificación de datos guardados:', !!verificarTicket);
        
        // Limpiar asientos seleccionados
        seleccionados.clear();
        
        // Mostrar mensaje de éxito
        console.log('🎉 ¡Compra realizada exitosamente!');
        showNotification('¡Compra realizada exitosamente!', 'success');
        
        // Verificar autenticación antes de redirigir
        console.log('🔐 Verificando autenticación antes de redirigir...');
        console.log('🔐 isAuthenticated():', isAuthenticated());
        console.log('🔐 localStorage cinemaUser:', !!localStorage.getItem('cinemaUser'));
        
        // Redireccionar inmediatamente a la página del ticket
        console.log('🔄 Redirigiendo a ticket.html...');
        console.log('🔄 URL actual:', window.location.href);
        console.log('🔄 Ejecutando redirección...');
        window.location.href = 'ticket.html';
        
    } catch (error) {
        console.error('❌ Error procesando compra:', error);
        showNotification('Error procesando la compra: ' + error.message, 'error');
    } finally {
        setLoading(comprarButton, false);
    }
    
    return false; // Prevenir cualquier envío de formulario
}

// Función para actualizar asientos después de una compra exitosa
async function actualizarAsientosDespuesCompra() {
    try {
        console.log('🔄 Actualizando asientos después de compra...');
        // Recargar asientos reservados para mostrar los nuevos asientos ocupados
        await cargarAsientosReservados();
        console.log('✅ Asientos actualizados después de la compra');
    } catch (error) {
        console.error('❌ Error actualizando asientos después de compra:', error);
    }
}

// Función para forzar recarga de datos cuando se regresa a la página
function forzarRecargaDatos() {
    const horarioSeleccionado = document.getElementById("horarioSeleccion").value;
    if (horarioSeleccionado) {
        console.log('🔄 Forzando recarga de asientos para horario:', horarioSeleccionado);
        cargarAsientosReservados();
    }
}

// Función de inicialización para establecer el estado inicial
function inicializarEstadoSelectores() {
    const salaSelector = document.getElementById("salaSeleccion");
    const horarioSelector = document.getElementById("horarioSeleccion");
    
    // Si no hay horario seleccionado, asegurar que el selector de sala esté desbloqueado
    if (!horarioSelector.value) {
        salaSelector.disabled = false;
        salaSelector.style.opacity = "1";
    }
}

// Ejecutar inicialización cuando la página cargue
document.addEventListener('DOMContentLoaded', function() {
    inicializarEstadoSelectores();
    
    // También verificar autenticación
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    
    // Cargar datos iniciales
    cargarPeliculas();
});
