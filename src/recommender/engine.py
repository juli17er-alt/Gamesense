"""
GameSense - Motor de Recomendación Personalizada de Videojuegos
Corporación Universitaria Minuto de Dios - UNIMINUTO
Ingeniería en Ciencia de Datos e Inteligencia Artificial

Fase 3 de la propuesta: Seleccionar, validar y ejecutar técnicas básicas de recomendación:
1. Filtrado Basado en Contenido con Ponderación Conductual (Calificación + Horas Logarítmicas)
2. Filtrado Colaborativo Básico entre Usuarios (para comparación académica y análisis de dispersión)
"""

import math
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from src.database.db_manager import DatabaseManager
from src.analysis.player_eda import PlayerBehaviorEDA
from src.recommender.explainer import RecommendationExplainer


class ContentBasedRecommender:
    """
    Sistema de recomendación basado en contenido ponderado por comportamiento.
    Construye un perfil vectorial del jugador considerando:
    - Calificación explícita (1.0 a 5.0)
    - Horas de juego implícitas (transformación logarítmica para atenuar outliers)
    - Preferencia de plataforma
    """

    def __init__(self, db_manager: DatabaseManager, weight_genre: float = 0.70, weight_platform: float = 0.30):
        self.db = db_manager
        self.eda = PlayerBehaviorEDA(db_manager)
        self.weight_genre = weight_genre
        self.weight_platform = weight_platform

    def recommend(self, player_id: int, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Genera el top N de videojuegos recomendados para el jugador especificado,
        con puntuación de afinidad normalizada [0 - 100%] y explicación detallada.
        """
        interactions = self.db.get_player_interactions(player_id)
        candidate_games = self.db.get_unplayed_games(player_id)

        # Caso de arranque en frío (Cold-Start): el jugador no tiene juegos registrados
        if not interactions:
            return self._cold_start_recommendations(candidate_games, top_n)

        # 1. Obtener métricas de comportamiento por género y plataforma
        genre_df = self.eda.get_genre_breakdown(player_id)
        plat_df = self.eda.get_platform_breakdown(player_id)

        genre_stats_map = {row["genre_name"]: row for _, row in genre_df.iterrows()}
        plat_stats_map = {row["platform_name"]: row for _, row in plat_df.iterrows()}

        # Diccionarios de afinidad normalizados
        genre_affinities = {row["genre_name"]: row["affinity_score"] for _, row in genre_df.iterrows()}
        platform_affinities = {
            row["platform_name"]: (row["share_hours_pct"] / 100.0) for _, row in plat_df.iterrows()
        }

        recommendations = []

        for game in candidate_games:
            g_name = game["genre_name"]
            p_name = game["platform_name"]

            # Afinidad de género (70% del peso)
            score_genre = genre_affinities.get(g_name, 0.0)

            # Afinidad de plataforma (30% del peso)
            score_platform = platform_affinities.get(p_name, 0.0)

            # Puntuación combinada ponderada
            final_score = (self.weight_genre * score_genre) + (self.weight_platform * score_platform)

            # Generar explicación transparente
            explanation = RecommendationExplainer.explain_content_recommendation(
                game=game,
                player_genre_stats=genre_stats_map,
                player_platform_stats=plat_stats_map,
                player_interactions=interactions
            )

            recommendations.append({
                "game_id": game["game_id"],
                "title": game["title"],
                "genre_name": g_name,
                "platform_name": p_name,
                "release_year": game["release_year"],
                "description": game["description"],
                "match_score": round(final_score * 100, 1),
                "genre_affinity": round(score_genre * 100, 1),
                "platform_affinity": round(score_platform * 100, 1),
                "explanation": explanation["summary"],
                "details": explanation
            })

        # Ordenar por puntuación de afinidad descendente
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return recommendations[:top_n]

    def _cold_start_recommendations(self, candidate_games: List[Dict[str, Any]], top_n: int) -> List[Dict[str, Any]]:
        """Recomendaciones por defecto para jugadores sin historial registrado."""
        cold_explanation = RecommendationExplainer.explain_cold_start()
        results = []
        for g in candidate_games[:top_n]:
            results.append({
                "game_id": g["game_id"],
                "title": g["title"],
                "genre_name": g["genre_name"],
                "platform_name": g["platform_name"],
                "release_year": g["release_year"],
                "description": g["description"],
                "match_score": 50.0,
                "genre_affinity": 0.0,
                "platform_affinity": 0.0,
                "explanation": cold_explanation["summary"],
                "details": cold_explanation
            })
        return results


class CollaborativeFilteringRecommender:
    """
    Filtrado colaborativo basado en similitud de usuarios (User-Based Collaborative Filtering).
    Permite demostrar la comparación académica entre ambos enfoques y analizar el reto
    de dispersión de matriz (sparsity) cuando los encuestados reportan pocos títulos.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def recommend(self, player_id: int, top_n: int = 5) -> Dict[str, Any]:
        """
        Calcula similitud de Pearson/Coseno entre el usuario y otros jugadores con juegos compartidos.
        Retorna las recomendaciones y un reporte del estado de dispersión de la matriz.
        """
        with self.db.get_connection() as conn:
            query = """
                SELECT player_id, game_id, rating, hours_played
                FROM player_game_interactions
            """
            rows = [dict(r) for r in conn.execute(query).fetchall()]

        if not rows:
            return {"recommendations": [], "status": "Sin datos de interacción en el sistema."}

        df = pd.DataFrame(rows)
        # Crear matriz Usuario-Juego de calificaciones
        matrix = df.pivot_table(index="player_id", columns="game_id", values="rating")

        if player_id not in matrix.index:
            return {"recommendations": [], "status": "El jugador objetivo no tiene calificaciones registradas."}

        target_ratings = matrix.loc[player_id].dropna()
        if target_ratings.empty:
            return {"recommendations": [], "status": "El jugador objetivo no tiene calificaciones."}

        # Calcular similitud con otros jugadores basados en juegos en común
        similarities = {}
        for other_id in matrix.index:
            if other_id == player_id:
                continue
            other_ratings = matrix.loc[other_id].dropna()
            common_games = target_ratings.index.intersection(other_ratings.index)
            
            if len(common_games) >= 1:
                # Similitud Coseno sobre los juegos compartidos
                v1 = target_ratings[common_games].values
                v2 = other_ratings[common_games].values
                norm1 = np.linalg.norm(v1)
                norm2 = np.linalg.norm(v2)
                sim = float(np.dot(v1, v2) / (norm1 * norm2)) if norm1 > 0 and norm2 > 0 else 0.0
                if sim > 0:
                    similarities[other_id] = sim

        if not similarities:
            return {
                "recommendations": [],
                "status": "No se encontraron otros jugadores con juegos en común (Matriz dispersa / Sparsity). Se aconseja utilizar el Filtrado Basado en Contenido."
            }

        # Predecir calificación ponderada para juegos no jugados por el usuario
        unplayed_game_ids = [gid for gid in matrix.columns if pd.isna(matrix.loc[player_id, gid])]
        scored_games = []

        with self.db.get_connection() as conn:
            games_catalog = {
                r["game_id"]: dict(r)
                for r in conn.execute(
                    "SELECT g.game_id, g.title, gen.name as genre_name, plat.name as platform_name "
                    "FROM games g JOIN genres gen ON g.genre_id = gen.genre_id JOIN platforms plat ON g.platform_id = plat.platform_id"
                ).fetchall()
            }

        for gid in unplayed_game_ids:
            num = 0.0
            denom = 0.0
            contributors = []
            for other_id, sim in similarities.items():
                rating = matrix.loc[other_id, gid]
                if not pd.isna(rating):
                    num += sim * rating
                    denom += sim
                    contributors.append(other_id)

            if denom > 0:
                pred_rating = float(num / denom)
                g_info = games_catalog.get(gid, {})
                scored_games.append({
                    "game_id": gid,
                    "title": g_info.get("title", f"Juego {gid}"),
                    "genre_name": g_info.get("genre_name", "Desconocido"),
                    "platform_name": g_info.get("platform_name", "Desconocido"),
                    "predicted_rating": round(pred_rating, 2),
                    "contributors_count": len(contributors),
                    "explanation": f"Recomendado colaborativamente porque otros jugadores con gustos afines lo calificaron con un promedio predicho de {pred_rating:.1f}/5.0."
                })

        scored_games.sort(key=lambda x: x["predicted_rating"], reverse=True)
        return {
            "recommendations": scored_games[:top_n],
            "status": f"Modelo colaborativo ejecutado con éxito ({len(similarities)} usuarios similares identificados)."
        }
