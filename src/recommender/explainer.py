"""
GameSense - Generador de Explicaciones de Recomendación
Corporación Universitaria Minuto de Dios - UNIMINUTO
Ingeniería en Ciencia de Datos e Inteligencia Artificial

Genera explicaciones claras, transparentes y comprensibles en lenguaje natural
sobre por qué el sistema sugiere cada videojuego a partir del historial del jugador.
"""

from typing import Dict, Any, List


class RecommendationExplainer:
    """Traduce las afinidades numéricas y métricas del modelo en explicaciones interpretables."""

    @staticmethod
    def explain_content_recommendation(
        game: Dict[str, Any],
        player_genre_stats: Dict[str, Any],
        player_platform_stats: Dict[str, Any],
        player_interactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Genera una explicación estructurada y una frase explicativa para una recomendación
        basada en contenido con ponderación conductual.
        """
        genre_name = game["genre_name"]
        platform_name = game["platform_name"]

        genre_info = player_genre_stats.get(genre_name)
        platform_info = player_platform_stats.get(platform_name)

        reasons = []
        similar_games_played = [
            i["game_title"] for i in player_interactions if i["genre_name"] == genre_name
        ]

        if genre_info is not None:
            hours = genre_info["total_hours"]
            avg_rating = genre_info["avg_rating"]
            share_pct = genre_info["share_hours_pct"]
            
            if similar_games_played:
                examples_str = ", ".join(f"'{title}'" for title in similar_games_played[:2])
                reasons.append(
                    f"Otorgaste una alta calificación promedio de **{avg_rating}/5.0** y acumulaste "
                    f"**{hours} horas** ({share_pct}% de tu tiempo) en títulos de **{genre_name}** como {examples_str}."
                )
            else:
                reasons.append(
                    f"Presentas una afinidad del **{share_pct}%** en el género **{genre_name}** con calificación de **{avg_rating}/5.0**."
                )

        if platform_info is not None:
            plat_hours = platform_info["total_hours"]
            reasons.append(
                f"El juego está disponible en tu plataforma frecuente (**{platform_name}**), donde registras **{plat_hours} horas** de juego."
            )
        elif genre_info is None:
            # Caso de exploración o juego fuera de géneros primarios
            reasons.append(
                f"Recomendación exploratoria de alta calidad en **{genre_name}** para diversificar tu catálogo."
            )

        summary_text = " ".join(reasons)

        return {
            "summary": summary_text,
            "genre_matched": (genre_info is not None),
            "platform_matched": (platform_info is not None),
            "similar_titles": similar_games_played
        }

    @staticmethod
    def explain_cold_start() -> Dict[str, Any]:
        """Explicación para nuevos jugadores sin historial de juego previo registrado."""
        return {
            "summary": "Recomendado como título destacado del catálogo general debido a que aún no has registrado suficientes interacciones previas (arranque en frío).",
            "genre_matched": False,
            "platform_matched": False,
            "similar_titles": []
        }
