-- =====================================================
-- BASE DE DATOS STYLEPIN
-- =====================================================

CREATE DATABASE IF NOT EXISTS stylepin 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE stylepin;

-- =====================================================
-- TABLA: users
-- =====================================================

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(30) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Información personal
    full_name VARCHAR(100) NOT NULL,
    bio TEXT,
    avatar_url VARCHAR(500),
    
    -- Preferencias
    gender ENUM('male', 'female', 'non_binary', 'prefer_not_to_say') DEFAULT 'prefer_not_to_say',
    preferred_styles JSON,
    
    -- Estado y verificación
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    role ENUM('user', 'admin', 'moderator') DEFAULT 'user',
    email_verified_at TIMESTAMP NULL,
    
    -- Seguridad
    login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP NULL,
    password_reset_token VARCHAR(255) NULL,
    password_reset_token_expiry TIMESTAMP NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    
    -- Indices
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_created_at (created_at),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- TABLA: pins (Para Corte 2)
-- =====================================================

CREATE TABLE IF NOT EXISTS pins (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    
    -- Contenido
    image_url VARCHAR(500) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Categorización
    category ENUM('outfit_completo', 'prenda_individual', 'accesorio', 'calzado') NOT NULL,
    styles JSON,
    occasions JSON,
    season ENUM('primavera', 'verano', 'otono', 'invierno', 'todo_el_ano') DEFAULT 'todo_el_ano',
    
    -- Shopping
    brands JSON,
    price_range ENUM('bajo_500', '500_1000', '1000_2000', 'mas_2000') DEFAULT 'bajo_500',
    where_to_buy VARCHAR(200),
    purchase_link VARCHAR(500),
    
    -- Engagement
    likes_count INT DEFAULT 0,
    saves_count INT DEFAULT 0,
    comments_count INT DEFAULT 0,
    views_count INT DEFAULT 0,
    
    -- Metadata
    colors JSON,
    tags JSON,
    is_private BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indices
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_season (season),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;