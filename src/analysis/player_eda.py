"""
GameSense - Módulo de Análisis Exploratorio de Datos (EDA)
Corporación Universitaria Minuto de Dios - UNIMINUTO
Ingeniería en Ciencia de Datos e Inteligencia Artificial

Fase 2 de la propuesta: Analizar los datos recopilados para descubrir patrones
relacionados con los hábitos de juego, preferencias y comportamiento del jugador.
"""

import math
from typing import Dict, Any, List, Optional
import pandas as pd
from src.database.db_manager import DatabaseManager


class PlayerBehaviorEDA:
    """Calcula métricas y análisis de comportamiento para jugadores y cohortes globales."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def get_player_summary(self, player_id: int) -> Dict[str, Any]:
        """
        Retorna indicadores clave de rendimiento (KPIs) del jugador:
        - Total de juegos registrados
        - Horas totales invertidas
        - Calificación promedio otorgada
        - Promedio de horas por juego
        - Género y plataforma predominantes
        """
        interactions = self.db.get_player_interactions(player_id)
        if not interactions:
            return {
                "has_data": False,
                "total_games": 0,
                "total_hours": 0.0,
                "avg_rating": 0.0,
                "avg_hours_per_game": 0.0,
                "top_genre": "N/A",
                "top_platform": "N/A"
            }

        df = pd.DataFrame(interactions)
        total_games = len(df)
        total_hours = float(df["hours_played"].sum())
        avg_rating = float(df["rating"].mean())
        avg_hours = total_hours / total_games if total_games > 0 else 0.0

        # Género con más horas
        genre_hours = df.groupby("genre_name")["hours_played"].sum()
        top_genre = genre_hours.idxmax() if not genre_hours.empty else "N/A"

        # Plataforma con más horas
        plat_hours = df.groupby("platform_name")["hours_played"].sum()
        top_plat = plat_hours.idxmax() if not plat_hours.empty else "N/A"

        return {
            "has_data": True,
            "total_games": total_games,
            "total_hours": round(total_hours, 1),
            "avg_rating": round(avg_rating, 2),
            "avg_hours_per_game": round(avg_hours, 1),
            "top_genre": top_genre,
            "top_platform": top_plat
        }

    def get_genre_breakdown(self, player_id: int) -> pd.DataFrame:
        """
        Analiza la distribución del tiempo y calificaciones por género para el jugador.
        Calcula el puntaje de afinidad conductual combinando calificación y horas logarítmicas.
        """
        interactions = self.db.get_player_interactions(player_id)
        if not interactions:
            return pd.DataFrame(columns=["genre_name", "games_count", "total_hours", "avg_rating", "share_hours_pct", "affinity_score"])

        df = pd.DataFrame(interactions)
        total_hours_all = df["hours_played"].sum()

        grouped = df.groupby("genre_name").agg(
            games_count=("game_id", "count"),
            total_hours=("hours_played", "sum"),
            avg_rating=("rating", "mean")
        ).reset_index()

        # Afinidad conductual = Calificación * ln(1 + horas)
        df["interaction_weight"] = df["rating"] * df["hours_played"].apply(lambda h: math.log(1.0 + float(h)))
        weights_by_genre = df.groupby("genre_name")["interaction_weight"].sum()
        total_weight = weights_by_genre.sum()

        grouped["share_hours_pct"] = grouped["total_hours"].apply(
            lambda h: round((h / total_hours_all) * 100, 1) if total_hours_all > 0 else 0.0
        )
        grouped["avg_rating"] = grouped["avg_rating"].round(2)
        grouped["total_hours"] = grouped["total_hours"].round(1)

        grouped["affinity_score"] = grouped["genre_name"].apply(
            lambda g: round((weights_by_genre.get(g, 0.0) / total_weight), 3) if total_weight > 0 else 0.0
        )

        return grouped.sort_values(by="total_hours", ascending=False).reset_index(drop=True)

    def get_platform_breakdown(self, player_id: int) -> pd.DataFrame:
        """Analiza el desglose de horas y títulos por plataforma."""
        interactions = self.db.get_player_interactions(player_id)
        if not interactions:
            return pd.DataFrame(columns=["platform_name", "games_count", "total_hours", "avg_rating", "share_hours_pct"])

        df = pd.DataFrame(interactions)
        total_hours_all = df["hours_played"].sum()

        grouped = df.groupby("platform_name").agg(
            games_count=("game_id", "count"),
            total_hours=("hours_played", "sum"),
            avg_rating=("rating", "mean")
        ).reset_index()

        grouped["share_hours_pct"] = grouped["total_hours"].apply(
            lambda h: round((h / total_hours_all) * 100, 1) if total_hours_all > 0 else 0.0
        )
        grouped["avg_rating"] = grouped["avg_rating"].round(2)
        grouped["total_hours"] = grouped["total_hours"].round(1)

        return grouped.sort_values(by="total_hours", ascending=False).reset_index(drop=True)

    def get_global_catalog_eda(self) -> Dict[str, Any]:
        """
        Retorna estadísticas globales del sistema para visualización de cohorte general:
        - Distribución de juegos por género en el catálogo
        - Géneros con mayores horas acumuladas entre todos los jugadores
        - Correlación general entre horas jugadas y calificación
        """
        with self.db.get_connection() as conn:
            # Juegos por género en catálogo
            cat_query = """
                SELECT gen.name AS genre_name, COUNT(g.game_id) AS total_games
                FROM games g
                JOIN genres gen ON g.genre_id = gen.genre_id
                GROUP BY gen.name
                ORDER BY total_games DESC
            """
            catalog_genres = pd.DataFrame([dict(r) for r in conn.execute(cat_query).fetchall()])

            # Interacciones globales acumuladas
            int_query = """
                SELECT gen.name AS genre_name,
                       COUNT(i.interaction_id) AS total_ratings,
                       ROUND(AVG(i.rating), 2) AS avg_rating,
                       ROUND(SUM(i.hours_played), 1) AS total_hours
                FROM player_game_interactions i
                JOIN games g ON i.game_id = g.game_id
                JOIN genres gen ON g.genre_id = gen.genre_id
                GROUP BY gen.name
                ORDER BY total_hours DESC
            """
            interactions_by_genre = pd.DataFrame([dict(r) for r in conn.execute(int_query).fetchall()])

            # Plataformas globales
            plat_query = """
                SELECT plat.name AS platform_name,
                       COUNT(i.interaction_id) AS total_ratings,
                       ROUND(SUM(i.hours_played), 1) AS total_hours
                FROM player_game_interactions i
                JOIN games g ON i.game_id = g.game_id
                JOIN platforms plat ON g.platform_id = plat.platform_id
                GROUP BY plat.name
                ORDER BY total_hours DESC
            """
            platforms_summary = pd.DataFrame([dict(r) for r in conn.execute(plat_query).fetchall()])

            # Estadísticas generales
            tot_players = conn.execute("SELECT COUNT(*) AS c FROM players").fetchone()["c"]
            tot_games = conn.execute("SELECT COUNT(*) AS c FROM games").fetchone()["c"]
            tot_inter = conn.execute("SELECT COUNT(*) AS c FROM player_game_interactions").fetchone()["c"]

            return {
                "total_players": tot_players,
                "total_games": tot_games,
                "total_interactions": tot_inter,
                "catalog_genres": catalog_genres,
                "interactions_by_genre": interactions_by_genre,
                "platforms_summary": platforms_summary
            }
