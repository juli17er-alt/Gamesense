"""
GameSense - Gestor de Base de Datos Relacional (SQLite)
Corporación Universitaria Minuto de Dios - UNIMINUTO
Ingeniería en Ciencia de Datos e Inteligencia Artificial
"""

import sqlite3
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from src.database.sample_data import GENRES, PLATFORMS, INITIAL_GAMES, SAMPLE_PLAYERS_INTERACTIONS

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "gamesense.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


class DatabaseManager:
    """Administra la conexión y operaciones sobre la base de datos relacional SQLite."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión con soporte para llaves foráneas y filas como diccionarios."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self) -> None:
        """Inicializa las tablas del esquema si aún no existen."""
        with self.get_connection() as conn:
            if SCHEMA_PATH.exists():
                with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            else:
                raise FileNotFoundError(f"No se encontró el archivo de esquema en: {SCHEMA_PATH}")

    def seed_initial_data(self, force: bool = False) -> None:
        """
        Pobla la base de datos con géneros, plataformas, catálogo de videojuegos
        y los perfiles de jugadores de demostración académica.
        """
        with self.get_connection() as conn:
            # Verificar si ya existen videojuegos en el catálogo
            cursor = conn.execute("SELECT COUNT(*) as count FROM games")
            count = cursor.fetchone()["count"]
            if count > 0 and not force:
                return

            if force:
                conn.execute("DELETE FROM player_game_interactions")
                conn.execute("DELETE FROM games")
                conn.execute("DELETE FROM players")
                conn.execute("DELETE FROM genres")
                conn.execute("DELETE FROM platforms")

            # 1. Insertar Géneros
            for g in GENRES:
                conn.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (g.strip(),))

            # 2. Insertar Plataformas
            for p in PLATFORMS:
                conn.execute("INSERT OR IGNORE INTO platforms (name) VALUES (?)", (p.strip(),))

            # Mapear nombres a IDs
            genre_map = {row["name"].lower(): row["genre_id"] for row in conn.execute("SELECT * FROM genres")}
            plat_map = {row["name"].lower(): row["platform_id"] for row in conn.execute("SELECT * FROM platforms")}

            # 3. Insertar Catálogo de Videojuegos
            for title, genre_name, plat_name, year, desc in INITIAL_GAMES:
                g_id = genre_map.get(genre_name.lower())
                p_id = plat_map.get(plat_name.lower())
                if g_id and p_id:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO games (title, genre_id, platform_id, release_year, description, is_demo)
                        VALUES (?, ?, ?, ?, ?, 1)
                        """,
                        (title.strip(), g_id, p_id, year, desc)
                    )

            # Mapear títulos de juegos a IDs
            game_map = {row["title"].lower(): row["game_id"] for row in conn.execute("SELECT * FROM games")}

            # 4. Insertar Jugadores de Demostración y sus Interacciones
            for player_data in SAMPLE_PLAYERS_INTERACTIONS:
                p_code = player_data["player_code"]
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO players (player_code, is_demo) VALUES (?, 1)",
                    (p_code,)
                )
                # Obtener el ID del jugador
                p_row = conn.execute("SELECT player_id FROM players WHERE player_code = ?", (p_code,)).fetchone()
                player_id = p_row["player_id"]

                for game_title, rating, hours in player_data["games"]:
                    g_id = game_map.get(game_title.lower())
                    if g_id:
                        conn.execute(
                            """
                            INSERT OR REPLACE INTO player_game_interactions
                            (player_id, game_id, rating, hours_played)
                            VALUES (?, ?, ?, ?)
                            """,
                            (player_id, g_id, float(rating), float(hours))
                        )
            conn.commit()

    # =========================================================================
    # Métodos de Acceso y Modificación de Datos (CRUD)
    # =========================================================================

    def get_all_players(self, include_demo: bool = True) -> List[Dict[str, Any]]:
        """Retorna todos los jugadores registrados."""
        query = "SELECT * FROM players"
        params = ()
        if not include_demo:
            query += " WHERE is_demo = 0"
        query += " ORDER BY player_id ASC"
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_player_by_id(self, player_id: int) -> Optional[Dict[str, Any]]:
        """Busca un jugador por su ID."""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM players WHERE player_id = ?", (player_id,)).fetchone()
            return dict(row) if row else None

    def create_player(self, player_code: str, is_demo: int = 0) -> int:
        """Registra un nuevo jugador y retorna su player_id."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO players (player_code, is_demo) VALUES (?, ?)",
                (player_code.strip(), is_demo)
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_genres(self) -> List[Dict[str, Any]]:
        """Lista todos los géneros disponibles."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM genres ORDER BY name ASC").fetchall()
            return [dict(r) for r in rows]

    def get_all_platforms(self) -> List[Dict[str, Any]]:
        """Lista todas las plataformas disponibles."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM platforms ORDER BY name ASC").fetchall()
            return [dict(r) for r in rows]

    def get_all_games(self) -> List[Dict[str, Any]]:
        """Retorna todos los juegos en el catálogo con sus nombres de género y plataforma."""
        query = """
            SELECT g.game_id, g.title, g.release_year, g.description, g.is_demo,
                   gen.name AS genre_name,
                   plat.name AS platform_name
            FROM games g
            JOIN genres gen ON g.genre_id = gen.genre_id
            JOIN platforms plat ON g.platform_id = plat.platform_id
            ORDER BY g.title ASC
        """
        with self.get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]

    def add_game(self, title: str, genre_id: int, platform_id: int, release_year: Optional[int] = None, description: str = "") -> int:
        """Agrega un nuevo juego al catálogo."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO games (title, genre_id, platform_id, release_year, description, is_demo)
                VALUES (?, ?, ?, ?, ?, 0)
                """,
                (title.strip(), genre_id, platform_id, release_year, description.strip())
            )
            conn.commit()
            return cursor.lastrowid

    def add_or_update_interaction(self, player_id: int, game_id: int, rating: float, hours_played: float) -> None:
        """Registra o actualiza la interacción de un jugador con un juego."""
        if not (1.0 <= rating <= 5.0):
            raise ValueError("La calificación debe estar entre 1.0 y 5.0.")
        if hours_played < 0:
            raise ValueError("Las horas jugadas no pueden ser negativas.")

        with self.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO player_game_interactions (player_id, game_id, rating, hours_played)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(player_id, game_id) DO UPDATE SET
                    rating = excluded.rating,
                    hours_played = excluded.hours_played,
                    created_at = CURRENT_TIMESTAMP
                """,
                (player_id, game_id, float(rating), float(hours_played))
            )
            conn.commit()

    def get_player_interactions(self, player_id: int) -> List[Dict[str, Any]]:
        """Retorna el historial completo de juegos reportados por un jugador."""
        query = """
            SELECT i.interaction_id, i.player_id, i.game_id, i.rating, i.hours_played, i.created_at,
                   g.title AS game_title,
                   gen.name AS genre_name,
                   plat.name AS platform_name
            FROM player_game_interactions i
            JOIN games g ON i.game_id = g.game_id
            JOIN genres gen ON g.genre_id = gen.genre_id
            JOIN platforms plat ON g.platform_id = plat.platform_id
            WHERE i.player_id = ?
            ORDER BY i.hours_played DESC, i.rating DESC
        """
        with self.get_connection() as conn:
            rows = conn.execute(query, (player_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_unplayed_games(self, player_id: int) -> List[Dict[str, Any]]:
        """Retorna los juegos del catálogo que el jugador aún NO ha calificado/jugado."""
        query = """
            SELECT g.game_id, g.title, g.release_year, g.description,
                   gen.name AS genre_name,
                   plat.name AS platform_name
            FROM games g
            JOIN genres gen ON g.genre_id = gen.genre_id
            JOIN platforms plat ON g.platform_id = plat.platform_id
            WHERE g.game_id NOT IN (
                SELECT game_id FROM player_game_interactions WHERE player_id = ?
            )
            ORDER BY g.title ASC
        """
        with self.get_connection() as conn:
            rows = conn.execute(query, (player_id,)).fetchall()
            return [dict(r) for r in rows]
