"""
GameSense - Importador de Datos de Encuestas (Google Forms / CSV)
Corporación Universitaria Minuto de Dios - UNIMINUTO
Ingeniería en Ciencia de Datos e Inteligencia Artificial
"""

import csv
import io
from pathlib import Path
from typing import Dict, Any, List, Union

from src.database.db_manager import DatabaseManager


class SurveyDataImporter:
    """Permite importar respuestas tabulares provenientes de encuestas de Google Forms / Sheets."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def import_from_csv(self, file_path_or_buffer: Union[str, Path, io.StringIO, io.BytesIO]) -> Dict[str, Any]:
        """
        Importa un archivo CSV con las columnas esperadas:
        player_code, game_title, genre, platform, rating, hours_played
        """
        results = {
            "total_rows": 0,
            "imported_interactions": 0,
            "new_players": 0,
            "new_games": 0,
            "errors": []
        }

        # Manejo de entrada como ruta o buffer de Streamlit/memoria
        if isinstance(file_path_or_buffer, (str, Path)):
            with open(file_path_or_buffer, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        elif isinstance(file_path_or_buffer, io.BytesIO):
            content = file_path_or_buffer.getvalue().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))
            rows = list(reader)
        elif isinstance(file_path_or_buffer, io.StringIO):
            reader = csv.DictReader(file_path_or_buffer)
            rows = list(reader)
        else:
            raise ValueError("Formato de entrada no soportado para importación.")

        results["total_rows"] = len(rows)

        with self.db.get_connection() as conn:
            for idx, row in enumerate(rows, start=2): # Fila 1 es cabecera
                try:
                    # Normalización de claves (insensible a mayúsculas/espacios)
                    norm_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
                    
                    # Buscar campos requeridos
                    player_code = norm_row.get("player_code") or norm_row.get("jugador") or norm_row.get("id_jugador") or norm_row.get("player_id")
                    game_title = norm_row.get("game_title") or norm_row.get("juego") or norm_row.get("videojuego")
                    genre_name = norm_row.get("genre") or norm_row.get("genero") or norm_row.get("género")
                    platform_name = norm_row.get("platform") or norm_row.get("plataforma")
                    rating_val = norm_row.get("rating") or norm_row.get("calificacion") or norm_row.get("calificación")
                    hours_val = norm_row.get("hours_played") or norm_row.get("horas") or norm_row.get("horas_jugadas")

                    if not all([player_code, game_title, genre_name, platform_name, rating_val, hours_val]):
                        results["errors"].append(f"Fila {idx}: Faltan campos requeridos.")
                        continue

                    rating = float(rating_val)
                    hours = float(hours_val)

                    if not (1.0 <= rating <= 5.0):
                        results["errors"].append(f"Fila {idx}: Calificación fuera de rango [1.0 - 5.0]: {rating}")
                        continue
                    if hours < 0:
                        results["errors"].append(f"Fila {idx}: Horas no pueden ser negativas: {hours}")
                        continue

                    # 1. Gestionar Jugador (marcado como dato real: is_demo = 0)
                    p_row = conn.execute("SELECT player_id FROM players WHERE player_code = ?", (player_code,)).fetchone()
                    if p_row:
                        player_id = p_row["player_id"]
                    else:
                        cur = conn.execute("INSERT INTO players (player_code, is_demo) VALUES (?, 0)", (player_code,))
                        player_id = cur.lastrowid
                        results["new_players"] += 1

                    # 2. Gestionar Género
                    g_row = conn.execute("SELECT genre_id FROM genres WHERE name = ? COLLATE NOCASE", (genre_name,)).fetchone()
                    if g_row:
                        genre_id = g_row["genre_id"]
                    else:
                        cur = conn.execute("INSERT INTO genres (name) VALUES (?)", (genre_name.capitalize(),))
                        genre_id = cur.lastrowid

                    # 3. Gestionar Plataforma
                    plat_row = conn.execute("SELECT platform_id FROM platforms WHERE name = ? COLLATE NOCASE", (platform_name,)).fetchone()
                    if plat_row:
                        platform_id = plat_row["platform_id"]
                    else:
                        cur = conn.execute("INSERT INTO platforms (name) VALUES (?)", (platform_name,))
                        platform_id = cur.lastrowid

                    # 4. Gestionar Videojuego
                    game_row = conn.execute("SELECT game_id FROM games WHERE title = ? COLLATE NOCASE", (game_title,)).fetchone()
                    if game_row:
                        game_id = game_row["game_id"]
                    else:
                        cur = conn.execute(
                            "INSERT INTO games (title, genre_id, platform_id, is_demo) VALUES (?, ?, ?, 0)",
                            (game_title, genre_id, platform_id)
                        )
                        game_id = cur.lastrowid
                        results["new_games"] += 1

                    # 5. Insertar o actualizar interacción
                    conn.execute(
                        """
                        INSERT INTO player_game_interactions (player_id, game_id, rating, hours_played)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(player_id, game_id) DO UPDATE SET
                            rating = excluded.rating,
                            hours_played = excluded.hours_played,
                            created_at = CURRENT_TIMESTAMP
                        """,
                        (player_id, game_id, rating, hours)
                    )
                    results["imported_interactions"] += 1

                except Exception as e:
                    results["errors"].append(f"Fila {idx}: Excepción ({str(e)})")

            conn.commit()

        return results
