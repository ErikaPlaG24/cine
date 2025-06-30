let nombreUsuario = "";
let currentUser = null;
let peliculasData = [];
let horariosData = [];
let asientosReservadosData = [];

// Variable para almacenar los datos del ticket actual para el PDF
let ticketData = null;

// Función para verificar el estado de las librerías PDF
function checkPDFLibraries() {
    console.log('=== Estado de librerías PDF ===');
    console.log('html2canvasLoaded:', window.html2canvasLoaded);
    console.log('jsPDFLoaded:', window.jsPDFLoaded);
    console.log('window.html2canvas:', typeof window.html2canvas);
    console.log('window.jsPDF:', typeof window.jsPDF);
    console.log('html2canvas global:', typeof html2canvas);
    console.log('jsPDF global:', typeof jsPDF);
    console.log('window.jspdf:', typeof window.jspdf);
    
    const html2canvasAvailable = window.html2canvasLoaded || window.html2canvas || (typeof html2canvas !== 'undefined');
    const jsPDFAvailable = window.jsPDFLoaded || window.jsPDF || (typeof jsPDF !== 'undefined') || (typeof window.jspdf !== 'undefined');
    
    console.log('html2canvas disponible:', html2canvasAvailable);
    console.log('jsPDF disponible:', jsPDFAvailable);
    console.log('window.jspdf:', typeof window.jspdf);
    console.log('==============================');
    
    return html2canvasAvailable && jsPDFAvailable;
}

// Función para formatear tiempo
function formatTime(timeString) {
    try {
        const date = new Date(timeString);
        return date.toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
        });
    } catch (error) {
        // Si no se puede parsear, devolver el string original
        return timeString || 'Horario no disponible';
    }
}

// Objeto para guardar asientos seleccionados temporalmente (para UI)
const asientosSeleccionados = {
  1: new Set(),
  2: new Set(),
  3: new Set()
};

// Función de inicialización cuando se carga la página
window.addEventListener('DOMContentLoaded', function() {
    // Verificar si el usuario ya está autenticado
    if (isAuthenticated()) {
        const userData = getUserData();
        if (userData) {
            nombreUsuario = userData.username || "Usuario";
            mostrarInterfazPrincipal();
        }
    }
});

async function iniciarSesion() {
    const user = document.getElementById("usuario").value;
    const pass = document.getElementById("contrasena").value;
    
    // Validar entrada
    const userValidation = validateUserInput(user, 'username');
    if (!userValidation.valid) {
        showNotification(userValidation.message, 'error');
        return;
    }
    
    const passValidation = validateUserInput(pass, 'password');
    if (!passValidation.valid) {
        showNotification(passValidation.message, 'error');
        return;
    }

    const loginButton = document.querySelector('.btn-login');
    
    try {
        setLoading(loginButton, true);

        const response = await AuthAPI.login(user, pass);
        
        if (response.access_token) {
            nombreUsuario = user;
            currentUser = response.user || { username: user };
            mostrarInterfazPrincipal();
            await cargarDatosIniciales();
            showNotification('¡Bienvenido al sistema de cine!', 'success');
        }
    } catch (error) {
        showNotification("Error al iniciar sesión: " + error.message, 'error');
        log('Login error:', error);
    } finally {
        setLoading(loginButton, false);
    }
}

function mostrarInterfazPrincipal() {
    document.getElementById("login").style.display = "none";
    document.getElementById("salas").style.display = "block";
    document.getElementById("logout").style.display = "block";
}

async function cargarDatosIniciales() {
    try {
        await cargarPeliculas();
        // Seleccionar la primera sala por defecto
        document.getElementById("salaSeleccion").value = "1";
    } catch (error) {
        console.error('Error cargando datos iniciales:', error);
        alert('Error cargando datos: ' + error.message);
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
        
        log('Películas cargadas:', peliculasData);
        showNotification(`${peliculasData.length} películas cargadas`, 'success');
    } catch (error) {
        log('Error cargando películas:', error);
        showNotification('Error cargando películas: ' + error.message, 'error');
    }
}

async function cargarHorarios() {
    const peliculaId = document.getElementById("peliculaSeleccion").value;
    const horarioSelect = document.getElementById("horarioSeleccion");
    
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
            option.textContent = `${formatTime(horario.start_time)} - Sala ${horario.theater_id}`;
            option.dataset.theaterId = horario.theater_id;
            horarioSelect.appendChild(option);
        });
        
        log('Horarios cargados:', horariosPelicula);
        if (horariosPelicula.length === 0) {
            showNotification('No hay horarios disponibles para esta película', 'info');
        }
    } catch (error) {
        log('Error cargando horarios:', error);
        showNotification('Error cargando horarios: ' + error.message, 'error');
    }
}

async function cargarAsientosReservados() {
    const horarioId = document.getElementById("horarioSeleccion").value;
    
    if (!horarioId) {
        generarAsientos();
        return;
    }

    try {
        const asientosReservados = await ReservedSeatsAPI.getByShowtime(parseInt(horarioId));
        asientosReservadosData = asientosReservados;
        
        // Debug: Log de asientos reservados
        console.log('Asientos reservados para horario', horarioId, ':', asientosReservados);
        
        // Actualizar la sala seleccionada basada en el horario
        const horarioSelect = document.getElementById("horarioSeleccion");
        const selectedOption = horarioSelect.options[horarioSelect.selectedIndex];
        if (selectedOption && selectedOption.dataset.theaterId) {
            document.getElementById("salaSeleccion").value = selectedOption.dataset.theaterId;
        }
        
        generarAsientos();
        console.log('Asientos reservados cargados:', asientosReservados);
    } catch (error) {
        console.error('Error cargando asientos reservados:', error);
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
            const estaReservado = asientosReservadosData.some(asiento => {
                // Verificar por seat_number completo (ej: "A1") o por seat_row + número
                return (asiento.seat_number === idAsiento) || 
                       (asiento.seat_row === fila && asiento.seat_number == i) ||
                       (asiento.seat_row === fila && String(asiento.seat_number) === String(i));
            });
            
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

async function comprar() {
    const horarioId = document.getElementById("horarioSeleccion").value;
    const peliculaId = document.getElementById("peliculaSeleccion").value;
    const sala = document.getElementById("salaSeleccion").value;
    
    if (!horarioId || !peliculaId) {
        showNotification("Seleccione una película y un horario.", 'error');
        return;
    }
    
    const seleccionados = asientosSeleccionados[sala];
    if (seleccionados.size === 0) {
        showNotification("Seleccione al menos un asiento.", 'error');
        return;
    }

    const comprarButton = document.querySelector('button[onclick="comprar()"]');
    
    try {
        setLoading(comprarButton, true);
        
        // Crear la venta
        const saleData = {
            user_id: currentUser.id || 1, // Si no tenemos el ID del usuario, usar 1 como default
            showtime_id: parseInt(horarioId),
            total_amount: seleccionados.size * 75,
            sale_date: new Date().toISOString().split('T')[0]
        };
        
        const saleResponse = await SalesAPI.create(saleData);
        log('Venta creada:', saleResponse);
        
        // Crear reservas de asientos
        const reservasPromises = [];
        seleccionados.forEach(idAsiento => {
            const fila = idAsiento.charAt(0);
            const numero = parseInt(idAsiento.substring(1));
            
            const reservaData = {
                showtime_id: parseInt(horarioId),
                seat_row: fila,
                seat_number: numero,
                reservation_date: new Date().toISOString().split('T')[0]
            };
            
            reservasPromises.push(ReservedSeatsAPI.create(reservaData));
        });
        
        await Promise.all(reservasPromises);
        
        // Mostrar ticket
        mostrarTicket(peliculaId, horarioId, sala, seleccionados);
        showNotification('¡Compra realizada exitosamente!', 'success');
        
        // Limpiar selección y recargar asientos
        seleccionados.clear();
        await cargarAsientosReservados();
        
    } catch (error) {
        log('Error procesando compra:', error);
        showNotification('Error procesando la compra: ' + error.message, 'error');
    } finally {
        setLoading(comprarButton, false);
    }
}

function mostrarTicket(peliculaId, horarioId, sala, asientosComprados) {
    const pelicula = peliculasData.find(p => p.id == peliculaId);
    const horario = horariosData.find(h => h.id == horarioId);
    
    // Guardar datos del ticket para el PDF
    ticketData = {
        usuario: nombreUsuario,
        pelicula: pelicula ? pelicula.title : 'Película seleccionada',
        genero: pelicula ? pelicula.genre : 'N/A',
        duracion: pelicula ? pelicula.duration : 'N/A',
        horario: horario ? formatTime(horario.start_time) : 'Horario seleccionado',
        fecha: horario ? new Date(horario.start_time).toLocaleDateString('es-ES') : new Date().toLocaleDateString('es-ES'),
        sala: sala,
        asientos: Array.from(asientosComprados),
        total: asientosComprados.size * 75,
        fechaCompra: new Date().toLocaleDateString('es-ES'),
        horaCompra: new Date().toLocaleTimeString('es-ES')
    };
    
    let detalles = `<strong>Usuario:</strong> ${ticketData.usuario}<br>`;
    detalles += `<strong>Película:</strong> ${ticketData.pelicula}<br>`;
    detalles += `<strong>Horario:</strong> ${ticketData.horario}<br>`;
    detalles += `<strong>Fecha:</strong> ${ticketData.fecha}<br>`;
    detalles += `<strong>Sala:</strong> ${ticketData.sala}<br>`;
    detalles += `<strong>Asientos:</strong><br>`;
    
    ticketData.asientos.forEach(idAsiento => {
        const fila = idAsiento.charAt(0);
        const numero = idAsiento.substring(1);
        detalles += `&nbsp;&nbsp;&nbsp;&nbsp;Fila ${fila}, Asiento ${numero}<br>`;
    });
    
    document.getElementById("detallesBoleto").innerHTML = detalles;
    document.getElementById("totalPago").textContent = `Total: $${ticketData.total}`;
    document.getElementById("ticket").style.display = "block";
}

function cerrarSesion() {
    AuthAPI.logout();
    nombreUsuario = "";
    currentUser = null;
    peliculasData = [];
    horariosData = [];
    asientosReservadosData = [];
    
    // Limpiar selecciones
    Object.values(asientosSeleccionados).forEach(set => set.clear());
    
    document.getElementById("login").style.display = "block";
    document.getElementById("salas").style.display = "none";
    document.getElementById("logout").style.display = "none";
    document.getElementById("ticket").style.display = "none";
    document.getElementById("usuario").value = "";
    document.getElementById("contrasena").value = "";
    
    // Limpiar selectores
    document.getElementById("peliculaSeleccion").innerHTML = '<option value="">Seleccione una película</option>';
    document.getElementById("horarioSeleccion").innerHTML = '<option value="">Seleccione un horario</option>';
    document.getElementById("asientosContainer").innerHTML = "";
}

// Función para generar PDF usando html2canvas + jsPDF
function descargarPDF() {
    if (!ticketData) {
        showNotification('No hay datos del ticket para generar PDF', 'error');
        return;
    }

    // Verificar estado de las librerías
    if (!checkPDFLibraries()) {
        showNotification('Las librerías PDF no están disponibles. Reintentando...', 'warning');
        
        // Intentar de nuevo después de un momento
        setTimeout(() => {
            if (!checkPDFLibraries()) {
                showNotification('Error: No se pudieron cargar las librerías PDF. Recargue la página.', 'error');
            } else {
                descargarPDF();
            }
        }, 2000);
        return;
    }

    try {
        showNotification('Generando PDF... Por favor espere.', 'info');
        console.log('Iniciando generación de PDF...');
        
        // Obtener las funciones de las librerías
        const html2canvasFunc = window.html2canvas || html2canvas;
        let jsPDFFunc = window.jsPDF || jsPDF;
        
        // Si jsPDF no está disponible directamente, intentar obtenerlo de window.jspdf
        if (!jsPDFFunc && window.jspdf) {
            jsPDFFunc = window.jspdf;
        }
        
        // También intentar desde el objeto global jspdf
        if (!jsPDFFunc && typeof window.jspdf !== 'undefined') {
            jsPDFFunc = window.jspdf.jsPDF || window.jspdf;
        }
        
        console.log('html2canvasFunc:', typeof html2canvasFunc);
        console.log('jsPDFFunc:', typeof jsPDFFunc);
        
        if (!html2canvasFunc || !jsPDFFunc) {
            throw new Error('Las librerías PDF no están disponibles correctamente');
        }
        
        // Crear elemento temporal para el ticket
        const ticketElement = document.createElement('div');
        ticketElement.style.cssText = `
            position: absolute;
            top: -9999px;
            left: -9999px;
            width: 600px;
            font-family: Arial, sans-serif;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        `;
        
        ticketElement.innerHTML = `
            <div style="text-align: center; border-bottom: 2px solid #667eea; padding-bottom: 20px; margin-bottom: 30px;">
                <h1 style="font-size: 28px; color: #667eea; margin: 0;">🎬 CINE PREMIUM</h1>
                <p style="font-size: 16px; color: #666; margin: 5px 0;">Boleto de Entrada</p>
            </div>

            <div style="margin-bottom: 25px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                <h3 style="color: #667eea; margin-bottom: 10px; font-size: 16px;">📽️ INFORMACIÓN DE LA PELÍCULA</h3>
                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dotted #ddd;">
                    <span style="font-weight: bold;">Película:</span>
                    <span>${ticketData.pelicula}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dotted #ddd;">
                    <span style="font-weight: bold;">Género:</span>
                    <span>${ticketData.genero}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 5px 0;">
                    <span style="font-weight: bold;">Duración:</span>
                    <span>${ticketData.duracion} minutos</span>
                </div>
            </div>

            <div style="margin-bottom: 25px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                <h3 style="color: #667eea; margin-bottom: 10px; font-size: 16px;">🕒 INFORMACIÓN DE LA FUNCIÓN</h3>
                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dotted #ddd;">
                    <span style="font-weight: bold;">Fecha:</span>
                    <span>${ticketData.fecha}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dotted #ddd;">
                    <span style="font-weight: bold;">Horario:</span>
                    <span>${ticketData.horario}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 5px 0;">
                    <span style="font-weight: bold;">Sala:</span>
                    <span>Sala ${ticketData.sala}</span>
                </div>
            </div>

            <div style="margin-bottom: 25px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                <h3 style="color: #667eea; margin-bottom: 10px; font-size: 16px;">🪑 ASIENTOS RESERVADOS</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                    ${ticketData.asientos.map(asiento => {
                        const fila = asiento.charAt(0);
                        const numero = asiento.substring(1);
                        return `<div style="background: #667eea; color: white; padding: 8px 12px; border-radius: 5px; font-weight: bold;">Fila ${fila}, Asiento ${numero}</div>`;
                    }).join('')}
                </div>
            </div>

            <div style="margin-bottom: 25px; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea;">
                <h3 style="color: #667eea; margin-bottom: 10px; font-size: 16px;">👤 INFORMACIÓN DEL CLIENTE</h3>
                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dotted #ddd;">
                    <span style="font-weight: bold;">Cliente:</span>
                    <span>${ticketData.usuario}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px dotted #ddd;">
                    <span style="font-weight: bold;">Fecha de compra:</span>
                    <span>${ticketData.fechaCompra}</span>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 5px 0;">
                    <span style="font-weight: bold;">Hora de compra:</span>
                    <span>${ticketData.horaCompra}</span>
                </div>
            </div>

            <div style="background: #667eea; color: white; text-align: center; padding: 20px; border-radius: 8px; font-size: 20px; font-weight: bold; margin-bottom: 20px;">
                💰 TOTAL PAGADO: $${ticketData.total}
            </div>

            <div style="text-align: center; padding-top: 20px; border-top: 2px solid #e0e0e0; color: #666;">
                <p style="margin: 5px 0;"><strong>¡Gracias por elegir nuestro cine!</strong></p>
                <p style="margin: 5px 0;">Conserve este boleto para ingresar a la sala</p>
                <p style="margin: 5px 0;">🎟️ Ticket #${Date.now().toString().slice(-8)}</p>
            </div>
        `;
        
        document.body.appendChild(ticketElement);
        
        console.log('Elemento del ticket agregado al DOM');
        
        // Usar html2canvas para convertir a imagen
        html2canvasFunc(ticketElement, {
            scale: 2,
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff',
            logging: false // Desactivar logs de html2canvas
        }).then(canvas => {
            console.log('Canvas generado exitosamente');
            // Limpiar elemento temporal
            document.body.removeChild(ticketElement);
            
            // Crear PDF con la sintaxis correcta
            let pdf;
            try {
                if (jsPDFFunc.jsPDF) {
                    pdf = new jsPDFFunc.jsPDF('p', 'mm', 'a4');
                } else if (typeof jsPDFFunc === 'function') {
                    pdf = new jsPDFFunc('p', 'mm', 'a4');
                } else if (jsPDFFunc.default) {
                    pdf = new jsPDFFunc.default('p', 'mm', 'a4');
                } else {
                    // Último recurso: intentar crear directamente
                    pdf = new jsPDFFunc('p', 'mm', 'a4');
                }
                console.log('PDF inicializado exitosamente');
            } catch (pdfError) {
                console.error('Error inicializando PDF:', pdfError);
                throw new Error('No se pudo inicializar jsPDF: ' + pdfError.message);
            }
            
            const imgData = canvas.toDataURL('image/png');
            const imgWidth = 210; // A4 width in mm
            const pageHeight = 295; // A4 height in mm
            const imgHeight = (canvas.height * imgWidth) / canvas.width;
            let heightLeft = imgHeight;
            
            let position = 0;
            
            // Agregar imagen al PDF
            pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
            heightLeft -= pageHeight;
            
            // Si la imagen es más grande que una página, agregar páginas adicionales
            while (heightLeft >= 0) {
                position = heightLeft - imgHeight;
                pdf.addPage();
                pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
                heightLeft -= pageHeight;
            }
            
            // Generar nombre del archivo
            const fileName = `Ticket_${ticketData.pelicula.replace(/[^a-zA-Z0-9]/g, '_')}_${ticketData.fechaCompra.replace(/\//g, '-')}.pdf`;
            console.log('Guardando PDF como:', fileName);
            
            // Descargar PDF
            pdf.save(fileName);
            
            console.log('PDF generado y descargado exitosamente');
            showNotification('¡PDF generado exitosamente!', 'success');
            
        }).catch(error => {
            console.error('Error en html2canvas:', error);
            // Limpiar elemento temporal si hay error
            if (document.body.contains(ticketElement)) {
                document.body.removeChild(ticketElement);
            }
            
            showNotification('Error al generar el canvas. Intente nuevamente.', 'error');
        });
        
    } catch (error) {
        console.error('Error en función descargarPDF:', error);
        showNotification('Error al generar PDF. Intente nuevamente.', 'error');
    }
}

// Función para volver a la interfaz principal desde el ticket
function mostrarInterfazPrincipal() {
    document.getElementById("ticket").style.display = "none";
    document.getElementById("salas").style.display = "block";
    
    // Limpiar selecciones
    const sala = document.getElementById("salaSeleccion").value;
    if (sala && asientosSeleccionados[sala]) {
        asientosSeleccionados[sala].clear();
    }
    
    // Recargar datos para mostrar los nuevos asientos reservados
    cargarAsientosReservados();
}

// Función simple para probar jsPDF
function testJsPDF() {
    console.log('=== Probando jsPDF ===');
    
    try {
        let pdf;
        
        // Probar diferentes formas de acceso
        if (window.jsPDF) {
            console.log('Intentando window.jsPDF...');
            pdf = new window.jsPDF('p', 'mm', 'a4');
        } else if (typeof jsPDF !== 'undefined') {
            console.log('Intentando jsPDF global...');
            pdf = new jsPDF('p', 'mm', 'a4');
        } else if (window.jspdf) {
            console.log('Intentando window.jspdf...');
            if (window.jspdf.jsPDF) {
                pdf = new window.jspdf.jsPDF('p', 'mm', 'a4');
            } else {
                pdf = new window.jspdf('p', 'mm', 'a4');
            }
        }
        
        if (pdf) {
            console.log('✅ jsPDF funciona correctamente');
            pdf.text('Test', 10, 10);
            console.log('✅ Método text() funciona');
            showNotification('jsPDF funciona correctamente', 'success');
        } else {
            console.log('❌ No se pudo crear instancia de jsPDF');
            showNotification('Error: No se pudo crear instancia de jsPDF', 'error');
        }
        
    } catch (error) {
        console.error('❌ Error probando jsPDF:', error);
        showNotification('Error probando jsPDF: ' + error.message, 'error');
    }
    
    console.log('===================');
}
