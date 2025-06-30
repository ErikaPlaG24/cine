# Sistema de Cine - Frontend

Este frontend ha sido adaptado para trabajar con la API FastAPI del sistema de cine.

## Archivos Principales

### 1. `api.js`
Contiene todas las funciones para comunicarse con la API del backend:
- **AuthAPI**: Funciones de autenticación (login, refresh, logout)
- **MoviesAPI**: Funciones para gestionar películas
- **TheatersAPI**: Funciones para gestionar salas
- **ShowtimesAPI**: Funciones para gestionar horarios
- **ReservedSeatsAPI**: Funciones para gestionar asientos reservados
- **SalesAPI**: Funciones para gestionar ventas

### 2. `script-api.js`
Script principal que maneja la lógica de la interfaz de usuario:
- Autenticación de usuarios
- Carga de películas desde la API
- Gestión de horarios y salas
- Reserva de asientos
- Procesamiento de compras

### 3. `config.js`
Configuraciones y utilidades:
- Configuración de entornos (desarrollo/producción)
- Funciones de notificación
- Validaciones de entrada
- Formateo de fechas y horas
- Manejo de estados de carga

### 4. `index.html`
Interfaz de usuario con:
- Formulario de login
- Selector de películas
- Selector de horarios
- Visualización de asientos
- Sistema de compra

## Funcionalidades

### Autenticación
- Login con usuario y contraseña
- Almacenamiento seguro de tokens JWT
- Manejo automático de expiración de sesión

### Gestión de Películas
- Carga automática de películas desde la API
- Filtrado de horarios por película seleccionada

### Reserva de Asientos
- Visualización en tiempo real de asientos disponibles/ocupados
- Sincronización con la base de datos
- Prevención de doble reserva

### Compras
- Creación de ventas en la base de datos
- Registro de asientos reservados
- Generación de tickets

## Configuración

### Desarrollo
- La URL base de la API está configurada para `http://localhost:8000`
- Logging habilitado para depuración

### Producción
- La URL base cambia a `/api` para usar el mismo dominio
- Logging deshabilitado

## Uso

1. **Iniciar el backend**: Asegúrate de que la API FastAPI esté corriendo en el puerto 8000
2. **Abrir el frontend**: Abre `index.html` en un navegador web
3. **Iniciar sesión**: Usa las credenciales configuradas en la base de datos
4. **Seleccionar película**: Elige una película del dropdown
5. **Seleccionar horario**: Elige un horario disponible
6. **Reservar asientos**: Haz clic en los asientos disponibles (verdes)
7. **Comprar**: Haz clic en "Comprar" para finalizar la transacción

## Endpoints Utilizados

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/refresh` - Renovar token

### Películas
- `GET /movies/all` - Obtener todas las películas

### Horarios
- `GET /showtimes/all` - Obtener todos los horarios

### Asientos Reservados
- `GET /reserved_seats/all` - Obtener todos los asientos reservados
- `POST /reserved_seats/create` - Crear nueva reserva

### Ventas
- `POST /sales/create` - Crear nueva venta

## Manejo de Errores

El sistema incluye:
- Notificaciones visuales para errores y éxito
- Reintentos automáticos para llamadas a la API
- Manejo de tokens expirados
- Validación de entrada de usuario

## Características Técnicas

- **Responsive**: Adaptable a diferentes tamaños de pantalla
- **Offline-ready**: Manejo de errores de conectividad
- **Secure**: Uso de JWT tokens para autenticación
- **Real-time**: Sincronización en tiempo real con la base de datos
- **User-friendly**: Interfaz intuitiva con notificaciones claras

## Dependencias

- Navegador web moderno con soporte para ES6+
- FastAPI backend corriendo
- Base de datos MySQL configurada
