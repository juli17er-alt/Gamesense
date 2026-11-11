-- ============================================================================
-- GameSense: Sistema Inteligente de Recomendación de Videojuegos
-- Esquema de Base de Datos Relacional (SQLite / ANSI SQL)
-- Corporación Universitaria Minuto de Dios - UNIMINUTO
-- Ingeniería en Ciencia de Datos e Inteligencia Artificial
-- ============================================================================

PRAGMA foreign_keys = ON;

-- 1. Tabla de Géneros de Videojuegos
CREATE TABLE IF NOT EXISTS genres (
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE
);

-- 2. Tabla de Plataformas de Videojuegos
CREATE TABLE IF NOT EXISTS platforms (
    platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE
);

-- 3. Tabla de Jugadores
-- player_code almacena identificadores anónimos como 'Jugador 1' según la propuesta
-- is_demo permite diferenciar datos de prueba académica de encuestas reales
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_code TEXT NOT NULL UNIQUE COLLATE NOCASE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_demo INTEGER NOT NULL DEFAULT 0 CHECK(is_demo IN (0, 1))
);

-- 4. Catálogo de Videojuegos
CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE COLLATE NOCASE,
    genre_id INTEGER NOT NULL,
    platform_id INTEGER NOT NULL,
    release_year INTEGER,
    description TEXT,
    is_demo INTEGER NOT NULL DEFAULT 1 CHECK(is_demo IN (0, 1)),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id) ON DELETE RESTRICT,
    FOREIGN KEY (platform_id) REFERENCES platforms(platform_id) ON DELETE RESTRICT
);

-- 5. Interacciones de Jugadores con Videojuegos (Comportamiento)
-- Captura las 3 variables conductuales clave: Identidad, Calificación (1-5), Horas de juego
CREATE TABLE IF NOT EXISTS player_game_interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    rating REAL NOT NULL CHECK(rating >= 1.0 AND rating <= 5.0),
    hours_played REAL NOT NULL CHECK(hours_played >= 0.0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(player_id, game_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE RESTRICT
);

-- Índices para optimizar consultas de análisis y filtrado de recomendación
CREATE INDEX IF NOT EXISTS idx_interactions_player ON player_game_interactions(player_id);
CREATE INDEX IF NOT EXISTS idx_interactions_game ON player_game_interactions(game_id);
CREATE INDEX IF NOT EXISTS idx_games_genre ON games(genre_id);
CREATE INDEX IF NOT EXISTS idx_games_platform ON games(platform_id);
