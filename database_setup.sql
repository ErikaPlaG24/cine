-- Script para crear/verificar las tablas necesarias para el sistema de cine
-- Ejecutar este script en MySQL Workbench o línea de comandos

USE cine;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de películas  
CREATE TABLE IF NOT EXISTS movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    duration INT NOT NULL,
    genre VARCHAR(100),
    rating VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de teatros/salas
CREATE TABLE IF NOT EXISTS theaters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    capacity INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de horarios de funciones
CREATE TABLE IF NOT EXISTS showtimes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    theater_id INT NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    FOREIGN KEY (theater_id) REFERENCES theaters(id)
);

-- Tabla de asientos reservados
CREATE TABLE IF NOT EXISTS reserved_seats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    showtime_id INT NOT NULL,
    seat_row VARCHAR(10) NOT NULL,
    seat_number INT NOT NULL,
    user_id INT,
    status ENUM('reserved', 'sold') DEFAULT 'reserved',
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (showtime_id) REFERENCES showtimes(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY unique_seat_showtime (showtime_id, seat_row, seat_number)
);

-- Tabla de ventas
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    showtime_id INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'completed',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (showtime_id) REFERENCES showtimes(id)
);

-- Insertar datos de prueba si las tablas están vacías

-- Usuarios de prueba
INSERT IGNORE INTO users (username, email, password) VALUES 
('admin', 'admin@cine.com', 'admin123'),
('test', 'test@cine.com', 'test123');

-- Películas de prueba
INSERT IGNORE INTO movies (title, description, duration, genre, rating) VALUES 
('Mad Max: Furia en la carretera', 'Película de acción post-apocalíptica', 120, 'Acción', 'R'),
('Un jefe en pañales', 'Comedia familiar animada', 97, 'Comedia', 'PG'),
('El conjuro 3', 'Película de terror sobrenatural', 112, 'Terror', 'R');

-- Teatros de prueba
INSERT IGNORE INTO theaters (name, capacity) VALUES 
('Sala 1', 20),
('Sala 2', 20),
('Sala 3', 20);

-- Horarios de prueba (solo si no existen)
INSERT IGNORE INTO showtimes (movie_id, theater_id, start_time, end_time, date) VALUES 
(1, 1, '14:00:00', '16:00:00', '2024-12-30'),
(1, 2, '16:30:00', '18:30:00', '2024-12-30'),
(2, 1, '15:00:00', '16:37:00', '2024-12-30'),
(2, 3, '17:00:00', '18:37:00', '2024-12-30'),
(3, 2, '19:00:00', '20:52:00', '2024-12-30'),
(3, 3, '20:00:00', '21:52:00', '2024-12-30');

-- Verificar que las tablas se crearon correctamente
SELECT 'Usuarios' as Tabla, COUNT(*) as Registros FROM users
UNION ALL
SELECT 'Películas', COUNT(*) FROM movies
UNION ALL
SELECT 'Teatros', COUNT(*) FROM theaters
UNION ALL
SELECT 'Horarios', COUNT(*) FROM showtimes
UNION ALL
SELECT 'Asientos Reservados', COUNT(*) FROM reserved_seats
UNION ALL
SELECT 'Ventas', COUNT(*) FROM sales;
