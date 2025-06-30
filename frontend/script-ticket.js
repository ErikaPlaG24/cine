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

function cargarTicket() {
    const ticketDataStr = localStorage.getItem('ticketData');
    if (!ticketDataStr) {
        showNotification('No se encontraron datos del ticket', 'error');
        window.location.href = 'reservas.html';
        return;
    }
    
    try {
        ticketData = JSON.parse(ticketDataStr);
        mostrarTicket();
    } catch (error) {
        console.error('Error cargando datos del ticket:', error);
        showNotification('Error cargando el ticket', 'error');
        window.location.href = 'reservas.html';
    }
}

function mostrarTicket() {
    if (!ticketData) return;
    
    let detalles = `<strong>Usuario:</strong> ${ticketData.usuario}<br>`;
    detalles += `<strong>Película:</strong> ${ticketData.pelicula}<br>`;
    detalles += `<strong>Género:</strong> ${ticketData.genero}<br>`;
    detalles += `<strong>Duración:</strong> ${ticketData.duracion} minutos<br>`;
    detalles += `<strong>Horario:</strong> ${ticketData.horario}<br>`;
    detalles += `<strong>Fecha:</strong> ${ticketData.fecha}<br>`;
    detalles += `<strong>Sala:</strong> ${ticketData.sala}<br>`;
    detalles += `<strong>Asientos:</strong><br>`;
    
    ticketData.asientos.forEach(idAsiento => {
        const fila = idAsiento.charAt(0);
        const numero = idAsiento.substring(1);
        detalles += `&nbsp;&nbsp;&nbsp;&nbsp;Fila ${fila}, Asiento ${numero}<br>`;
    });
    
    detalles += `<br><strong>Fecha de compra:</strong> ${ticketData.fechaCompra}<br>`;
    detalles += `<strong>Hora de compra:</strong> ${ticketData.horaCompra}`;
    
    document.getElementById("detallesBoleto").innerHTML = detalles;
    document.getElementById("totalPago").textContent = `Total Pagado: $${ticketData.total}`;
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
