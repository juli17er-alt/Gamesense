"""
GameSense - Test Integral del Flujo Completo del MVP
UNIMINUTO - Ingeniería en Ciencia de Datos e Inteligencia Artificial
"""

import sys
import os
from pathlib import Path

# Configurar path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database.db_manager import DatabaseManager
from src.database.data_importer import SurveyDataImporter
from src.analysis.player_eda import PlayerBehaviorEDA
from src.recommender.engine import ContentBasedRecommender, CollaborativeFilteringRecommender


def run_full_flow_test():
    print("==================================================================")
    print("INICIANDO PRUEBA INTEGRAL DEL FLUJO DE GAMESENSE")
    print("==================================================================")

    # 1. Almacenamiento Relacional
    print("\n[Paso 1] Inicializando Base de Datos Relacional...")
    test_db_path = ROOT_DIR / "data" / "test_gamesense.db"
    if test_db_path.exists():
        test_db_path.unlink()

    db = DatabaseManager(db_path=test_db_path)
    db.seed_initial_data(force=True)

    players = db.get_all_players()
    games = db.get_all_games()
    print(f"-> Base de datos creada: {len(players)} jugadores demo, {len(games)} juegos en catálogo.")
    assert len(players) >= 5, "Deben existir al menos 5 jugadores demo."
    assert len(games) >= 30, "Deben existir al menos 30 juegos en el catálogo."

    # 2. Creación de Nuevo Jugador e Ingreso de Interacciones
    print("\n[Paso 2] Creando nuevo jugador de prueba y registrando comportamiento...")
    new_player_id = db.create_player("Jugador Validación MVP", is_demo=0)
    print(f"-> Jugador creado exitosamente con ID: {new_player_id}")

    # Registrar 3 juegos con perfil marcado de Survival Horror en PlayStation 5
    # Buscamos IDs de juegos relevantes
    re4 = [g for g in games if "Resident Evil 4" in g["title"]][0]
    dead_space = [g for g in games if "Dead Space" in g["title"]][0]
    silent_hill = [g for g in games if "Silent Hill 2" in g["title"]][0]

    db.add_or_update_interaction(new_player_id, re4["game_id"], rating=5.0, hours_played=45.0)
    db.add_or_update_interaction(new_player_id, dead_space["game_id"], rating=4.8, hours_played=30.0)
    db.add_or_update_interaction(new_player_id, silent_hill["game_id"], rating=4.7, hours_played=25.0)

    user_interactions = db.get_player_interactions(new_player_id)
    print(f"-> Interacciones registradas en BD: {len(user_interactions)} juegos.")
    assert len(user_interactions) == 3, "Deberían haberse guardado 3 interacciones."

    # 3. Análisis Exploratorio de Datos (EDA)
    print("\n[Paso 3] Ejecutando Análisis Exploratorio de Datos (EDA)...")
    eda = PlayerBehaviorEDA(db)
    summary = eda.get_player_summary(new_player_id)
    print(f"-> Resumen del Jugador: {summary}")
    assert summary["total_games"] == 3
    assert summary["total_hours"] == 100.0
    assert summary["top_genre"] == "Survival Horror"

    genre_breakdown = eda.get_genre_breakdown(new_player_id)
    print("-> Desglose de géneros:\n", genre_breakdown[["genre_name", "total_hours", "avg_rating", "affinity_score"]])
    assert genre_breakdown.iloc[0]["genre_name"] == "Survival Horror"
    assert genre_breakdown.iloc[0]["affinity_score"] == 1.0

    # 4. Generación de Recomendaciones Basadas en Contenido
    print("\n[Paso 4] Generando Recomendaciones Basadas en Contenido (CBF)...")
    cbf = ContentBasedRecommender(db)
    recommendations = cbf.recommend(new_player_id, top_n=3)
    
    print(f"-> Se generaron {len(recommendations)} recomendaciones personalizadas:")
    for idx, r in enumerate(recommendations, 1):
        print(f"   {idx}. {r['title']} [{r['genre_name']} - {r['platform_name']}] | Score: {r['match_score']}%")
        print(f"      Explicación: {r['explanation']}")

    # Debe recomendar Alan Wake 2 (el otro Survival Horror en el catálogo) como primera opción
    top_rec = recommendations[0]
    assert top_rec["genre_name"] == "Survival Horror", "El primer juego recomendado debería ser Survival Horror."
    assert "Survival Horror" in top_rec["explanation"], "La explicación debe justificar el género."

    # 5. Prueba de Filtrado Colaborativo
    print("\n[Paso 5] Evaluando Filtrado Colaborativo...")
    cf = CollaborativeFilteringRecommender(db)
    cf_res = cf.recommend(new_player_id, top_n=2)
    print(f"-> Estado Filtrado Colaborativo: {cf_res['status']}")

    # 6. Prueba de Importación de Encuesta Google Forms CSV
    print("\n[Paso 6] Probando importador de encuestas Google Forms CSV...")
    importer = SurveyDataImporter(db)
    template_path = ROOT_DIR / "data" / "survey_template.csv"
    import_result = importer.import_from_csv(template_path)
    print(f"-> Resultado importación CSV: {import_result}")
    assert import_result["imported_interactions"] > 0, "Se debieron importar interacciones desde el CSV."

    # Limpieza de archivo de prueba
    import gc
    gc.collect()
    try:
        if test_db_path.exists():
            test_db_path.unlink()
    except OSError:
        pass

    print("\n==================================================================")
    print("¡TODAS LAS PRUEBAS COMPLETADAS CON ÉXITO! EL MVP FUNCIONA AL 100%")
    print("==================================================================")


if __name__ == "__main__":
    run_full_flow_test()
