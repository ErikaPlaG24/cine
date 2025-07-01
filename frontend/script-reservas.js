let nombreUsuario = "";
let currentUser = null;
let peliculasData = [];
let horariosData = [];
let asientosReservadosData = [];

// Objeto para guardar asientos seleccionados temporalmente (para UI)
const asientosSeleccionados = {
  1: new Set(),
  2: new Set(),
  3: new Set(),
  4: new Set(),
  5: new Set()
};

// Flag para prevenir eventos automáticos durante limpieza
let isClearing = false;

// Función wrapper para manejar cambios de horario
function onHorarioChange() {
    const horarioId = document.getElementById("horarioSeleccion").value;
    console.log('🎬 === CAMBIO DE HORARIO DETECTADO ===');
    console.log('🎬 Horario seleccionado:', horarioId);
    console.log('🎬 isClearing flag:', isClearing);
    
    if (isClearing) {
        console.log('⏭️ Ignorando evento onHorarioChange porque estamos limpiando');
        return;
    }
    
    console.log('✅ Procesando cambio de horario válido');
    
    if (horarioId) {
        console.log('🔄 Cargando asientos reservados para horario:', horarioId);
        cargarAsientosReservados();
    } else {
        console.log('⚠️ No hay horario seleccionado, limpiando asientos');
        asientosReservadosData = [];
        generarAsientos();
    }
}

// Función para limpiar completamente el estado de selección
async function limpiarEstadoCompleto(recargarHorarios = true) {
    console.log('🧹 === LIMPIEZA COMPLETA DEL ESTADO ===');
    
    isClearing = true;
    
    // Limpiar selecciones
    document.getElementById("horarioSeleccion").value = "";
    document.getElementById("horarioSeleccion").selectedIndex = 0;
    
    // Limpiar datos en memoria
    asientosReservadosData = [];
    
    // Limpiar asientos seleccionados
    const sala = document.getElementById("salaSeleccion").value;
    if (sala && asientosSeleccionados[sala]) {
        asientosSeleccionados[sala].clear();
    }
    
    // Regenerar asientos limpios
    generarAsientos();
    
    isClearing = false;
    
    // IMPORTANTE: Recargar horarios para la película actual después de limpiar (solo si no estamos ya en cargarHorarios)
    if (recargarHorarios) {
        const peliculaActual = document.getElementById("peliculaSeleccion").value;
        console.log('🔄 Verificando recarga de horarios...');
        console.log('🔄 Película actual seleccionada:', peliculaActual);
        console.log('🔄 ¿Debería recargar horarios?', !!peliculaActual);
        
        if (peliculaActual) {
            console.log('🔄 Recargando horarios para película actual:', peliculaActual);
            await cargarHorarios();
            console.log('🔄 Recarga de horarios completada');
        } else {
            console.log('⚠️ No hay película seleccionada para recargar horarios');
        }
    } else {
        console.log('⏭️ Salteando recarga de horarios (recargarHorarios = false)');
    }
    
    console.log('✅ Estado completamente limpiado');
}

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
        
        // Mostrar características de administrador si aplica
        toggleAdminFeatures();
        
        await cargarPeliculas();
        // Verificar y corregir cualquier inconsistencia entre película y horario seleccionados
        await verificarConsistenciaPeliculaHorario();
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

// Función para verificar y corregir inconsistencias entre película y horario
async function verificarConsistenciaPeliculaHorario() {
    try {
        const peliculaId = document.getElementById("peliculaSeleccion").value;
        const horarioId = document.getElementById("horarioSeleccion").value;
        
        // Si no hay película o horario seleccionado, no hay nada que verificar
        if (!peliculaId || !horarioId) {
            console.log('🔍 No hay película y horario para verificar consistencia');
            return;
        }
        
        // Cargar horarios si no están cargados
        if (horariosData.length === 0) {
            const response = await retryApiCall(() => ShowtimesAPI.getAll());
            horariosData = Array.isArray(response) ? response : (response.showtimes || []);
        }
        
        // Verificar si el horario seleccionado pertenece a la película seleccionada
        const horarioSeleccionado = horariosData.find(h => h.showtime_id == horarioId);
        if (horarioSeleccionado && horarioSeleccionado.movie_id != peliculaId) {
            console.warn('⚠️ INCONSISTENCIA DETECTADA al cargar: película/horario no coinciden');
            console.warn('Película seleccionada:', peliculaId);
            console.warn('Horario seleccionado:', horarioSeleccionado);
            
            // Usar la función de limpieza completa
            await limpiarEstadoCompleto();
            
            console.log('✅ Inconsistencia corregida automáticamente');
            showNotification('Se detectó una selección inconsistente que fue corregida automáticamente.', 'info');
        } else {
            console.log('✅ Verificación de consistencia: Todo correcto');
        }
    } catch (error) {
        console.error('Error verificando consistencia:', error);
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
    
    console.log('🎬 === CARGANDO HORARIOS ===');
    console.log('🎬 Película seleccionada:', peliculaId);
    console.log('🎬 isClearing flag:', isClearing);
    
    // Desbloquear selector de sala al cambiar de película
    salaSelector.disabled = false;
    salaSelector.style.opacity = "1";
    
    // Limpiar asientos reservados de la película anterior
    asientosReservadosData = [];
    console.log('🧹🧹🧹 ASIENTOS LIMPIADOS AL CAMBIAR PELÍCULA 🧹🧹🧹');
    console.log('🧹 asientosReservadosData.length después de limpiar:', asientosReservadosData.length);
    
    // Establecer flag para prevenir eventos automáticos
    isClearing = true;
    
    if (!peliculaId) {
        horarioSelect.innerHTML = '<option value="">Seleccione un horario</option>';
        horarioSelect.value = "";
        isClearing = false;
        // Regenerar asientos limpios cuando no hay película seleccionada
        generarAsientos();
        return;
    }

    try {
        const response = await retryApiCall(() => ShowtimesAPI.getAll());
        // El API devuelve directamente el array de horarios
        horariosData = Array.isArray(response) ? response : (response.showtimes || []);
        
        // Filtrar horarios por película seleccionada
        console.log('🎭 TODOS LOS HORARIOS del servidor:', horariosData);
        console.log('🎭 PELÍCULA SELECCIONADA ID:', peliculaId);
        console.log('🎭 TIPO de peliculaId:', typeof peliculaId);
        
        const horariosPelicula = horariosData.filter(horario => {
            const coincide = horario.movie_id == peliculaId;
            console.log(`🎭 Horario ID ${horario.showtime_id}: movie_id=${horario.movie_id} (tipo: ${typeof horario.movie_id}), coincide con película ${peliculaId}: ${coincide}`);
            return coincide;
        });
        
        console.log('🎭 HORARIOS FILTRADOS para película:', horariosPelicula);
        
        horarioSelect.innerHTML = '<option value="">Seleccione un horario</option>';
        
        // IMPORTANTE: Limpiar la selección de horario al cambiar de película
        // Esto previene que quede seleccionado un horario de otra película
        await limpiarEstadoCompleto(false); // false = no recargar horarios (ya estamos cargándolos)
        console.log('🧹 Estado limpiado al cambiar película');
        
        horariosPelicula.forEach(horario => {
            const option = document.createElement("option");
            option.value = horario.showtime_id; // Usar showtime_id en lugar de id
            // Usar datetime para extraer fecha y hora
            const fechaFormateada = formatDate(horario.datetime);
            const horaFormateada = formatTime(horario.datetime);
            option.textContent = `${horaFormateada} - ${fechaFormateada} - Sala ${horario.theater_id}`;
            option.dataset.theaterId = horario.theater_id;
            option.dataset.movieId = horario.movie_id; // Agregar movie_id para debug
            horarioSelect.appendChild(option);
            
            console.log(`🎭 Agregando horario: ID=${horario.showtime_id}, Movie_ID=${horario.movie_id}, Theater=${horario.theater_id}`);
        });
        
        console.log('Horarios cargados:', horariosPelicula);
        if (horariosPelicula.length === 0) {
            showNotification('No hay horarios disponibles para esta película', 'info');
        }
        
        // Regenerar asientos limpios después de cargar nuevos horarios
        // También limpiar asientos reservados porque ya no hay horario seleccionado
        asientosReservadosData = [];
        generarAsientos();
        
        // Limpiar flag al finalizar
        isClearing = false;
    } catch (error) {
        console.log('Error cargando horarios:', error);
        showNotification('Error cargando horarios: ' + error.message, 'error');
        isClearing = false; // Asegurar que se limpia el flag incluso en caso de error
    }
}

async function cargarAsientosReservados() {
    // Si estamos en proceso de limpieza, no ejecutar esta función
    if (isClearing) {
        console.log('⏭️ Saltando cargarAsientosReservados porque estamos limpiando');
        return;
    }
    
    const horarioId = document.getElementById("horarioSeleccion").value;
    const salaSelector = document.getElementById("salaSeleccion");
    
    console.log('🎯 === CARGANDO ASIENTOS RESERVADOS ===');
    console.log('🎯 Horario ID:', horarioId);
    console.log('🎯 isClearing flag:', isClearing);
    
    if (!horarioId) {
        console.log('⚠️ No hay horario seleccionado, generando asientos vacíos');
        // Desbloquear selector de sala si no hay horario seleccionado
        salaSelector.disabled = false;
        salaSelector.style.opacity = "1";
        // Limpiar completamente los asientos reservados
        asientosReservadosData = [];
        generarAsientos();
        return;
    }

    // VALIDACIÓN CRÍTICA: Verificar que el horario pertenece a la película actual
    const peliculaId = document.getElementById("peliculaSeleccion").value;
    if (peliculaId && horariosData.length > 0) {
        const horarioSeleccionado = horariosData.find(h => h.showtime_id == horarioId);
        if (horarioSeleccionado && horarioSeleccionado.movie_id != peliculaId) {
            console.error('❌ INCONSISTENCIA EN cargarAsientosReservados');
            console.error('Película actual:', peliculaId);
            console.error('Horario seleccionado:', horarioSeleccionado);
            
            // Usar la función de limpieza completa
            await limpiarEstadoCompleto();
            showNotification('Selección inconsistente detectada y corregida.', 'warning');
            return;
        }
    }

    // Bloquear selector de sala una vez que se selecciona un horario
    salaSelector.disabled = true;
    salaSelector.style.opacity = "0.6";

    // IMPORTANTE: Limpiar asientos reservados anteriores antes de cargar nuevos
    asientosReservadosData = [];
    console.log('🧹 Asientos reservados limpiados antes de cargar el horario:', horarioId);

    try {
        console.log('🔄 Cargando asientos reservados para horario:', horarioId);
        console.log('🌐 Llamando al endpoint:', `/reserved_seats/showtime/${horarioId}`);
        console.log('🎬 IMPORTANTE: Estos asientos son SOLO para el horario ID:', horarioId);
        
        // Verificar qué película corresponde a este horario
        const peliculaActual = document.getElementById("peliculaSeleccion").value;
        const horarioActual = horariosData.find(h => h.showtime_id == horarioId);
        console.log('🎭 VERIFICACIÓN: Película seleccionada:', peliculaActual);
        console.log('🎭 VERIFICACIÓN: Horario encontrado:', horarioActual);
        if (horarioActual) {
            console.log('🎭 VERIFICACIÓN: Movie_ID del horario:', horarioActual.movie_id);
            console.log('🎭 VERIFICACIÓN: ¿Coinciden?', horarioActual.movie_id == peliculaActual);
        }
        
        const asientosReservados = await ReservedSeatsAPI.getByShowtime(parseInt(horarioId));
        asientosReservadosData = asientosReservados;
        
        // Debug: Log MUY detallado de asientos reservados
        console.log('📋 RESPUESTA COMPLETA del servidor:', asientosReservados);
        console.log('📋 Tipo de respuesta:', typeof asientosReservados);
        console.log('📋 Es array:', Array.isArray(asientosReservados));
        console.log('📋 Cantidad de asientos reservados:', asientosReservados.length);
        console.log('📋 asientosReservadosData actualizado:', asientosReservadosData);
        
        if (asientosReservados.length > 0) {
            console.log('🪑 DETALLES DE CADA ASIENTO RESERVADO:');
            console.log('🚨 HORARIO_ID ACTUAL:', horarioId);
            asientosReservados.forEach((asiento, index) => {
                console.log(`   Asiento ${index + 1}:`, asiento);
                console.log(`   Tipo:`, typeof asiento);
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
    
    const filas = ["A", "B", "C", "D", "E", "F"];
    const sala = document.getElementById("salaSeleccion").value;
    const horarioId = document.getElementById("horarioSeleccion").value;
    
    // Log para debug del problema de asientos cruzados
    console.log('🎯 === GENERANDO ASIENTOS ===');
    console.log('🎯 Sala seleccionada:', sala);
    console.log('🎯 Horario seleccionado:', horarioId);
    console.log('🎯 Asientos reservados en memoria:', asientosReservadosData.length);
    console.log('🎯 Contenido de asientosReservadosData:', asientosReservadosData);
    if (asientosReservadosData.length > 0) {
        console.log('🎯 Primer asiento reservado (ejemplo):', asientosReservadosData[0]);
        console.log('🎯 Tipo del primer asiento:', typeof asientosReservadosData[0]);
    }
    
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
        
        for (let i = 1; i <= 10; i++) {
            const idAsiento = `${fila}${i}`;
            const div = document.createElement("div");
            div.className = "asiento";
            div.dataset.fila = fila;
            div.dataset.numero = i;
            div.textContent = idAsiento;
            
            // Verificar si el asiento está reservado en el backend
            const estaReservado = asientosReservadosData.some(asiento => {
                // El backend ahora devuelve un array de strings simples como ["A1", "A2"]
                // No objetos con propiedades
                if (typeof asiento === 'string') {
                    return asiento === idAsiento;
                }
                
                // Mantener compatibilidad con formato anterior por si acaso
                const coincideAsientoCompleto = asiento.seat_number === idAsiento;
                const coincideFilaYNumero = asiento.seat_row === fila && 
                                           String(asiento.seat_number_parsed) === String(i);
                
                return coincideAsientoCompleto || coincideFilaYNumero;
            });
            
            if (estaReservado) {
                console.log(`🔒 ¡ASIENTO ${idAsiento} ESTÁ RESERVADO!`);
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
    
    // VALIDACIÓN CRÍTICA: Verificar que el horario seleccionado pertenece a la película seleccionada
    if (horarioId && peliculaId) {
        const horarioSeleccionado = horariosData.find(h => h.showtime_id == horarioId);
        if (horarioSeleccionado && horarioSeleccionado.movie_id != peliculaId) {
            console.error('❌ BUG DETECTADO: Horario seleccionado no corresponde a la película');
            console.error('Película seleccionada:', peliculaId);
            console.error('Horario seleccionado:', horarioSeleccionado);
            showNotification("Error: El horario seleccionado no corresponde a la película. Por favor, seleccione un horario válido.", 'error');
            // Usar la función de limpieza completa
            await limpiarEstadoCompleto();
            return false;
        }
        console.log('✅ Validación horario-película CORRECTA');
    }
    
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
            customer_user_id: currentUser.id || 1, // Usar customer_user_id como está en la tabla
            showtime_id: parseInt(horarioId),
            ticket_quantity: seleccionados.size, // Usar ticket_quantity como está en la tabla
            subtotal: seleccionados.size * 75,
            total: seleccionados.size * 75, // Usar total como está en la tabla
            payment_method: "cash",
            seats: asientosSeleccionadosArray
        };
        
        console.log('📤 Enviando datos de venta:', saleData);
        console.log('📤 Detalles de los datos:');
        console.log('- customer_user_id:', saleData.customer_user_id, typeof saleData.customer_user_id);
        console.log('- showtime_id:', saleData.showtime_id, typeof saleData.showtime_id);
        console.log('- ticket_quantity:', saleData.ticket_quantity, typeof saleData.ticket_quantity);
        console.log('- total:', saleData.total, typeof saleData.total);
        console.log('- payment_method:', saleData.payment_method, typeof saleData.payment_method);
        console.log('- seats:', saleData.seats, Array.isArray(saleData.seats));
        
        const saleResponse = await SalesAPI.create(saleData);
        console.log('✅ Venta creada exitosamente:', saleResponse);
        
        // Los asientos ya se reservan automáticamente en el endpoint de crear venta
        
        // Preparar datos del ticket
        const pelicula = peliculasData.find(p => p.id == peliculaId);
        const horario = horariosData.find(h => h.showtime_id == horarioId);
        
        const ticketData = {
            usuario: nombreUsuario || 'Usuario',
            pelicula: pelicula ? pelicula.title : 'Película seleccionada',
            genero: pelicula ? (pelicula.original_language === 'en' ? 'Película Internacional' : 'Película Nacional') : 'N/A',
            duracion: pelicula && pelicula.duration_minutes ? pelicula.duration_minutes : 'N/A',
            horario: horario ? formatTime(horario.datetime) : 'Horario seleccionado',
            fecha: horario ? formatDate(horario.datetime) : new Date().toLocaleDateString('es-ES'),
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
        
        // Recargar asientos reservados inmediatamente para reflejar la compra
        console.log('🔄 Recargando asientos después de compra exitosa...');
        await cargarAsientosReservados();
        
        // Regenerar la visualización de asientos para mostrar los recién ocupados
        generarAsientos();
        
        // Mostrar mensaje de éxito
        console.log('🎉 ¡Compra realizada exitosamente!');
        showNotification('¡Compra realizada exitosamente!', 'success');
        
        // Agregar botón de backup para ir al ticket
        comprarButton.innerHTML = '🎫 Ver Ticket';
        comprarButton.onclick = () => window.location.href = './ticket.html';
        comprarButton.style.backgroundColor = '#28a745';
        comprarButton.disabled = false;
        
        // Verificar autenticación antes de redirigir
        console.log('🔐 Verificando autenticación antes de redirigir...');
        console.log('🔐 isAuthenticated():', isAuthenticated());
        console.log('🔐 localStorage cinemaUser:', !!localStorage.getItem('cinemaUser'));
        
        // Redirección inmediata y como backup después de un delay
        console.log('🔄 Intentando redirección inmediata...');
        try {
            window.location.href = './ticket.html';
        } catch (e) {
            console.error('❌ Redirección inmediata falló:', e);
        }
        
        // Esperar un momento para que el usuario vea los asientos actualizados
        setTimeout(() => {
            console.log('🔄 Iniciando redirección al ticket...');
            console.log('🔄 URL actual:', window.location.href);
            
            try {
                // Método simple y directo
                console.log('🔄 Redirigiendo a ticket.html...');
                
                // Intentar múltiples métodos de redirección
                if (window.location.replace) {
                    window.location.replace('./ticket.html');
                } else if (window.location.href) {
                    window.location.href = './ticket.html';
                } else {
                    // Método de último recurso
                    window.location = './ticket.html';
                }
                
                // Verificación adicional después de un delay
                setTimeout(() => {
                    if (!window.location.href.includes('ticket.html')) {
                        console.log('🔄 Redirección no detectada, intentando método alternativo...');
                        window.open('./ticket.html', '_self');
                    }
                }, 500);
                
            } catch (error) {
                console.error('❌ Error en redirección:', error);
                // Si falla la redirección, al menos mostrar los datos del ticket aquí
                alert('Compra realizada exitosamente. Por favor, navegue manualmente a la página del ticket.');
            }
        }, 1000); // Reducir a 1 segundo
        
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

// Función para verificar si el usuario es administrador
function isUserAdmin() {
    try {
        const token = localStorage.getItem('authToken');
        if (!token) return false;
        
        // Decodificar el token JWT
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.role === 'admin';
    } catch (error) {
        console.error('Error verificando rol de administrador:', error);
        return false;
    }
}

// Función para mostrar/ocultar enlaces de administrador
function toggleAdminFeatures() {
    const adminReportsLink = document.getElementById('adminReportsLink');
    const adminPanelLink = document.getElementById('adminPanelLink');
    
    if (isUserAdmin()) {
        if (adminReportsLink) {
            adminReportsLink.style.display = 'inline-block';
        }
        if (adminPanelLink) {
            adminPanelLink.style.display = 'inline-block';
        }
        console.log('✅ Usuario administrador detectado, mostrando enlaces de administración');
    } else {
        if (adminReportsLink) {
            adminReportsLink.style.display = 'none';
        }
        if (adminPanelLink) {
            adminPanelLink.style.display = 'none';
        }
        console.log('ℹ️ Usuario regular, ocultando enlaces de administración');
    }
}

// Función para mostrar/ocultar características de administrador
async function toggleAdminFeatures() {
    console.log('🔐 Verificando permisos de administrador...');
    
    try {
        // Obtener datos del usuario del token
        const token = localStorage.getItem('authToken');
        if (!token) {
            console.log('❌ No hay token disponible');
            return;
        }

        let userRole = 'customer'; // Valor por defecto
        
        // Intentar decodificar como JWT primero
        try {
            if (token.includes('.')) {
                // Es un JWT, intentar decodificar
                const payload = JSON.parse(atob(token.split('.')[1]));
                console.log('🔍 Payload del JWT:', payload);
                userRole = payload.role || 'customer';
            } else {
                // Es un token de prueba, verificar si es de admin
                console.log('🔍 Token de prueba detectado:', token);
                
                // Obtener datos del usuario guardados
                const userData = localStorage.getItem('userData');
                if (userData) {
                    const parsedUserData = JSON.parse(userData);
                    userRole = parsedUserData.role || 'customer';
                    console.log('🔍 Datos de usuario desde localStorage:', parsedUserData);
                } else {
                    // Como fallback, verificar en la base de datos el rol del usuario actual
                    const storedUser = localStorage.getItem('cinemaUser');
                    if (storedUser) {
                        const user = JSON.parse(storedUser);
                        // Para usuarios específicos conocidos, asignar rol admin
                        if (user.username === 'admin' || user.username === 'Isaura') {
                            userRole = 'admin';
                        }
                    }
                }
            }
        } catch (decodeError) {
            console.warn('⚠️ Error decodificando token:', decodeError);
            
            // Fallback: verificar usuarios admin conocidos
            const storedUser = localStorage.getItem('cinemaUser');
            if (storedUser) {
                const user = JSON.parse(storedUser);
                if (user.username === 'admin' || user.username === 'Isaura') {
                    userRole = 'admin';
                }
            }
        }
        
        console.log('👤 Rol del usuario determinado:', userRole);
        
        // Mostrar características de admin si el usuario es administrador
        const adminReportsLink = document.getElementById('adminReportsLink');
        const adminPanelLink = document.getElementById('adminPanelLink');
        const adminSection = document.getElementById('adminSection');
        
        if (userRole === 'admin') {
            if (adminReportsLink) {
                adminReportsLink.style.display = 'inline-block';
            }
            if (adminPanelLink) {
                adminPanelLink.style.display = 'inline-block';
            }
            if (adminSection) {
                adminSection.style.display = 'block';
            }
            console.log('✅ Características de administrador activadas');
        } else {
            if (adminReportsLink) {
                adminReportsLink.style.display = 'none';
            }
            if (adminPanelLink) {
                adminPanelLink.style.display = 'none';
            }
            if (adminSection) {
                adminSection.style.display = 'none';
            }
            console.log('❌ Usuario no es administrador');
        }
        
    } catch (error) {
        console.error('❌ Error verificando permisos de admin:', error);
    }
}

toggleAdminFeatures();

// Función para mostrar estadísticas rápidas en el panel de admin
async function showQuickStats() {
    console.log('📊 Mostrando estadísticas rápidas...');
    
    const quickStats = document.getElementById('quickStats');
    const quickStatsContent = document.getElementById('quickStatsContent');
    
    if (!quickStats || !quickStatsContent) {
        console.error('❌ Elementos de estadísticas no encontrados');
        return;
    }
    
    // Mostrar indicador de carga
    quickStatsContent.innerHTML = '<div style="text-align: center; padding: 20px; color: white;">🔄 Cargando estadísticas...</div>';
    quickStats.style.display = 'block';
    
    try {
        // Cargar resumen de ventas
        const response = await ReportsAPI.getSalesSummary();
        console.log('📊 Estadísticas recibidas:', response);
        
        // Procesar datos
        const summary = response.summary || {};
        const totalSales = summary.total_sales || 0;
        const totalAmount = summary.total_amount || 0;
        const uniqueCustomers = summary.unique_customers || 0;
        const mostSoldMovie = response.top_movies?.most_sold || { title: 'N/A', tickets_sold: 0 };
        
        // Mostrar estadísticas
        quickStatsContent.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; color: white;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; margin-bottom: 5px;">${totalSales}</div>
                    <div style="font-size: 14px; opacity: 0.9;">Ventas Totales</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; margin-bottom: 5px;">$${totalAmount.toLocaleString()}</div>
                    <div style="font-size: 14px; opacity: 0.9;">Ingresos</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; margin-bottom: 5px;">${uniqueCustomers}</div>
                    <div style="font-size: 14px; opacity: 0.9;">Clientes</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">${mostSoldMovie.title}</div>
                    <div style="font-size: 14px; opacity: 0.9;">Película más vendida (${mostSoldMovie.tickets_sold} boletos)</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 15px;">
                <button onclick="hideQuickStats()" style="background: rgba(255,255,255,0.2); color: white; border: 1px solid white; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                    Ocultar
                </button>
            </div>
        `;
        
    } catch (error) {
        console.error('❌ Error cargando estadísticas:', error);
        quickStatsContent.innerHTML = `
            <div style="text-align: center; padding: 20px; color: white;">
                ❌ Error al cargar estadísticas: ${error.message}
                <br><br>
                <button onclick="hideQuickStats()" style="background: rgba(255,255,255,0.2); color: white; border: 1px solid white; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                    Cerrar
                </button>
            </div>
        `;
    }
}

// Función para ocultar estadísticas rápidas
function hideQuickStats() {
    const quickStats = document.getElementById('quickStats');
    if (quickStats) {
        quickStats.style.display = 'none';
    }
}
