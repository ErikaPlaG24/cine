-- Usar base de datos cine
CREATE DATABASE IF NOT EXISTS cine;
USE cine;

-- Tabla de usuarios (admin, empleado, cliente)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'employee', 'customer') NOT NULL,
    phone VARCHAR(20),
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    password_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- Nueva columna
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Trigger para actualizar la fecha de actualización de la contraseña
DELIMITER //

CREATE TRIGGER update_password_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    -- Actualiza solo si el campo password cambia y no es NULL
    IF (NEW.password <> OLD.password OR (NEW.password IS NULL AND OLD.password IS NOT NULL) 
        OR (NEW.password IS NOT NULL AND OLD.password IS NULL)) 
        AND NEW.password IS NOT NULL THEN
        SET NEW.password_updated_at = CURRENT_TIMESTAMP;
    END IF;
END//

DELIMITER ;

-- Tabla de membresías
CREATE TABLE memberships (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    monthly_price DECIMAL(8,2) DEFAULT 0,
    benefits TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insertar membresías
INSERT INTO memberships (name, description, discount_percentage, monthly_price, benefits) VALUES
('Bronce', 'Descuento básico para clientes ocasionales', 5.00, 200.00, '5% de descuento en boletos'),
('Plata', 'Ideal para clientes frecuentes', 10.00, 350.00, '10% de descuento en boletos'),
('Oro', 'Para amantes del cine premium', 15.00, 550.00, '15% de descuento en boletos'),
('Platino', 'Membresía VIP con beneficios exclusivos', 20.00, 750.00, '20% de descuento en boletos'),
('Diamante', 'Máxima experiencia para los cinéfilos', 25.00, 1000.00, '25% de descuento en boletos');


-- Tabla de clientes con membresía
CREATE TABLE customer_memberships (
    customer_membership_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    membership_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (membership_id) REFERENCES memberships(membership_id)
);

-- Nueva tabla de películas compatible con TMDB
CREATE TABLE movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    original_title VARCHAR(255),
    original_language VARCHAR(10),
    overview TEXT,
    release_date DATE,
    vote_average FLOAT,
    vote_count INT,
    popularity FLOAT,
    poster_url TEXT,
    wallpaper_url TEXT,
    is_adult BOOLEAN,
    created_by_user_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
);

-- Tabla de géneros
CREATE TABLE genres (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Insertar géneros TMDB traducidos
INSERT INTO genres (id, name) VALUES
(28, 'Acción'),
(12, 'Aventura'),
(16, 'Animación'),
(35, 'Comedia'),
(80, 'Crimen'),
(99, 'Documental'),
(18, 'Drama'),
(10751, 'Familiar'),
(14, 'Fantasía'),
(36, 'Historia'),
(27, 'Terror'),
(10402, 'Música'),
(9648, 'Misterio'),
(10749, 'Romance'),
(878, 'Ciencia ficción'),
(10770, 'Película de TV'),
(53, 'Suspenso'),
(10752, 'Guerra'),
(37, 'Western');

-- Tabla puente muchos a muchos para películas y géneros
CREATE TABLE movie_genres (
    movie_id INT,
    genre_id INT,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id)
);

-- Tabla de salas
CREATE TABLE theaters (
    theater_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    capacity INT NOT NULL,
    has_3d BOOLEAN DEFAULT FALSE,
    has_dolby BOOLEAN DEFAULT FALSE,
    is_imax BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de horarios de proyección
CREATE TABLE showtimes (
    showtime_id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    theater_id INT NOT NULL,
    datetime DATETIME NOT NULL,
    base_price DECIMAL(8,2) NOT NULL,
    available_seats INT NOT NULL,
    is_3d BOOLEAN DEFAULT FALSE,
    is_imax BOOLEAN DEFAULT FALSE,
    created_by_user_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies(id),
    FOREIGN KEY (theater_id) REFERENCES theaters(theater_id),
    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id)
);

-- Tabla de ventas
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    showtime_id INT NOT NULL,
    customer_user_id INT,
    employee_user_id INT,
    ticket_quantity INT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,
    sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    payment_method ENUM('cash', 'credit_card', 'debit_card', 'membership') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (showtime_id) REFERENCES showtimes(showtime_id),
    FOREIGN KEY (customer_user_id) REFERENCES users(user_id),
    FOREIGN KEY (employee_user_id) REFERENCES users(user_id)
);

-- Tabla de asientos reservados
CREATE TABLE reserved_seats (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id)
);

-- Triggers para manejo de asientos
DELIMITER //
CREATE TRIGGER after_sale_insert
AFTER INSERT ON sales
FOR EACH ROW
BEGIN
    UPDATE showtimes 
    SET available_seats = available_seats - NEW.ticket_quantity,
        updated_at = CURRENT_TIMESTAMP
    WHERE showtime_id = NEW.showtime_id;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER before_sale_insert
BEFORE INSERT ON sales
FOR EACH ROW
BEGIN
    DECLARE available INT;
    SELECT available_seats INTO available FROM showtimes WHERE showtime_id = NEW.showtime_id;
    
    IF available < NEW.ticket_quantity THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'No hay suficientes asientos disponibles para esta función';
    END IF;
END//
DELIMITER ;

-- Insertar usuario administrador ejemplo (contraseña bcrypt)
INSERT INTO users (
    username, password, first_name, last_name, role, phone, is_active
) VALUES (
    'admin', 
    '$2b$12$OLtFD1NLSSZETrkTPmQiZ.jOgsBhko6mCc0R3z3FjsWt3PYNvoouG', 
    'Administrador', 
    'Del Sistema', 
    'admin', 
    '+1234567890',
    1
);


-- TRIGGERS PARA ACTUALIZAR LOS UPDATED AT

DELIMITER //

-- Trigger para la tabla users (incluyendo password_updated_at)
CREATE TRIGGER update_users_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
    
    -- Actualiza password_updated_at solo si cambia la contraseña
    IF (NEW.password <> OLD.password OR 
       (NEW.password IS NULL AND OLD.password IS NOT NULL) OR 
       (NEW.password IS NOT NULL AND OLD.password IS NULL)) THEN
        SET NEW.password_updated_at = CURRENT_TIMESTAMP;
    END IF;
END//

-- Trigger para la tabla memberships
CREATE TRIGGER update_memberships_timestamp
BEFORE UPDATE ON memberships
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

-- Trigger para la tabla customer_memberships
CREATE TRIGGER update_customer_memberships_timestamp
BEFORE UPDATE ON customer_memberships
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

-- Trigger para la tabla movies
CREATE TRIGGER update_movies_timestamp
BEFORE UPDATE ON movies
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

-- Trigger para la tabla theaters
CREATE TRIGGER update_theaters_timestamp
BEFORE UPDATE ON theaters
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

-- Trigger para la tabla showtimes
CREATE TRIGGER update_showtimes_timestamp
BEFORE UPDATE ON showtimes
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

-- Trigger para la tabla sales
CREATE TRIGGER update_sales_timestamp
BEFORE UPDATE ON sales
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

-- Trigger para la tabla reserved_seats
CREATE TRIGGER update_reserved_seats_timestamp
BEFORE UPDATE ON reserved_seats
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

DELIMITER ;