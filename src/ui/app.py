"""
GameSense: Sistema Inteligente de Recomendación de Videojuegos Basado en el Comportamiento del Jugador
Corporación Universitaria Minuto de Dios - UNIMINUTO
Ingeniería en Ciencia de Datos e Inteligencia Artificial

Interfaz de Usuario Interactiva para el Producto Mínimo Viable (MVP).
Demuestra el flujo integral:
DATOS DEL JUGADOR -> ALMACENAMIENTO RELACIONAL -> ANÁLISIS CONDUCTUAL -> RECOMENDACIONES EXPLICABLES
"""

import os
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Asegurar que el directorio raíz y src estén en sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = ROOT_DIR / "src"
for p in (ROOT_DIR, SRC_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from src.database.db_manager import DatabaseManager
    from src.database.data_importer import SurveyDataImporter
    from src.analysis.player_eda import PlayerBehaviorEDA
    from src.recommender.engine import ContentBasedRecommender, CollaborativeFilteringRecommender
except ImportError:
    from ..database.db_manager import DatabaseManager
    from ..database.data_importer import SurveyDataImporter
    from ..analysis.player_eda import PlayerBehaviorEDA
    from ..recommender.engine import ContentBasedRecommender, CollaborativeFilteringRecommender

# Configuración de página
st.set_page_config(
    page_title="GameSense - Sistema de Recomendación",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar Base de Datos (Singleton en sesión)
@st.cache_resource
def get_db():
    db = DatabaseManager()
    db.seed_initial_data(force=False)
    return db

db = get_db()
eda = PlayerBehaviorEDA(db)
cbf_recommender = ContentBasedRecommender(db)
cf_recommender = CollaborativeFilteringRecommender(db)
importer = SurveyDataImporter(db)

# =============================================================================
# BARRA LATERAL: SELECCIÓN Y GESTIÓN DE JUGADOR
# =============================================================================
st.sidebar.title("🎮 GameSense")
st.sidebar.markdown(
    "**Sistema de Recomendación Basado en Comportamiento del Jugador**\n\n"
    "*UNIMINUTO - Fac. Ingeniería*\n\n"
    "*Ciencia de Datos e Inteligencia Artificial*"
)
st.sidebar.markdown("---")

# Cargar lista de jugadores
players = db.get_all_players()
if not players:
    db.seed_initial_data(force=True)
    players = db.get_all_players()

player_options = {
    p["player_id"]: f"{p['player_code']} {'[Demo]' if p['is_demo'] else '[Encuesta Real]'}"
    for p in players
}

selected_player_id = st.sidebar.selectbox(
    "👤 Seleccionar Jugador:",
    options=list(player_options.keys()),
    format_func=lambda x: player_options[x]
)

selected_player = db.get_player_by_id(selected_player_id) if selected_player_id else None
if not selected_player:
    st.warning("Seleccione o registre un jugador para comenzar.")
    st.stop()

# Crear nuevo jugador
with st.sidebar.expander("➕ Registrar Nuevo Jugador"):
    with st.form("new_player_form", clear_on_submit=True):
        new_code = st.text_input("Código / Identificador:", placeholder="Ej: Jugador 6")
        submit_player = st.form_submit_button("Crear Jugador")
        if submit_player:
            if new_code.strip():
                try:
                    new_id = db.create_player(new_code.strip(), is_demo=0)
                    st.success(f"¡Jugador creado con éxito! (ID: {new_id})")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al registrar: {e}")
            else:
                st.warning("Ingrese un código válido.")

# Opciones de administración de base de datos
with st.sidebar.expander("⚙️ Opciones de Datos"):
    if st.button("🔄 Reiniciar Datos Demo"):
        db.seed_initial_data(force=True)
        st.success("Base de datos restablecida con datos demo iniciales.")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Flujo Académico:**\n"
    "1. Registra o selecciona un jugador.\n"
    "2. Agrega sus juegos más jugados (calificación y horas).\n"
    "3. Explora el análisis de sus hábitos.\n"
    "4. Genera recomendaciones personalizadas con su explicación."
)

# =============================================================================
# ENCABEZADO PRINCIPAL
# =============================================================================
st.title("GameSense: Recomendación Inteligente de Videojuegos")
st.caption(
    f"Jugador Activo: **{selected_player['player_code']}** | "
    f"Tipo: **{'Demostración Académica' if selected_player['is_demo'] else 'Encuesta Real'}** | "
    f"ID: `{selected_player['player_id']}`"
)

# Pestañas principales de navegación
tab_history, tab_eda, tab_recs, tab_survey = st.tabs([
    "📋 Historial y Registro",
    "📊 Análisis de Comportamiento (EDA)",
    "💡 Recomendaciones Personalizadas",
    "📁 Importar Encuesta (Google Forms)"
])

# =============================================================================
# PESTAÑA 1: HISTORIAL Y REGISTRO DE VIDEOJUEGOS
# =============================================================================
with tab_history:
    st.subheader("Historial de Videojuegos del Jugador")
    st.markdown("Visualiza los títulos reportados y añade nuevas interacciones de juego.")

    col_hist, col_form = st.columns([3, 2])

    with col_hist:
        interactions = db.get_player_interactions(selected_player_id)
        if interactions:
            df_history = pd.DataFrame(interactions)
            display_df = df_history[[
                "game_title", "genre_name", "platform_name", "rating", "hours_played", "created_at"
            ]].rename(columns={
                "game_title": "Videojuego",
                "genre_name": "Género",
                "platform_name": "Plataforma",
                "rating": "Calificación (1-5)",
                "hours_played": "Horas Jugadas",
                "created_at": "Fecha Registro"
            })
            st.dataframe(display_df, width="stretch", hide_index=True)
        else:
            st.warning("Este jugador aún no tiene videojuegos registrados en su historial.")
            st.info("Utiliza el formulario contiguo para registrar sus títulos más jugados.")

    with col_form:
        st.markdown("##### ➕ Registrar / Actualizar Videojuego")
        
        # Obtener catálogos
        all_games = db.get_all_games()
        all_genres = db.get_all_genres()
        all_platforms = db.get_all_platforms()

        game_choice = st.radio(
            "Origen del Videojuego:",
            options=["Seleccionar del Catálogo", "Ingresar Nuevo Título"],
            horizontal=True
        )

        with st.form("interaction_form"):
            selected_genre_id = None
            selected_platform_id = None
            target_game_id = None

            if game_choice == "Seleccionar del Catálogo":
                game_options = {g["game_id"]: f"{g['title']} ({g['genre_name']} - {g['platform_name']})" for g in all_games}
                target_game_id = st.selectbox("Videojuego:", options=list(game_options.keys()), format_func=lambda x: game_options[x])
            else:
                new_game_title = st.text_input("Título del Videojuego:", placeholder="Ej: Persona 5 Royal")
                genre_map = {g["genre_id"]: g["name"] for g in all_genres}
                platform_map = {p["platform_id"]: p["name"] for p in all_platforms}
                selected_genre_id = st.selectbox("Género:", options=list(genre_map.keys()), format_func=lambda x: genre_map[x])
                selected_platform_id = st.selectbox("Plataforma:", options=list(platform_map.keys()), format_func=lambda x: platform_map[x])

            col_r, col_h = st.columns(2)
            with col_r:
                rating_input = st.slider("Calificación (1 a 5):", min_value=1.0, max_value=5.0, value=4.5, step=0.1)
            with col_h:
                hours_input = st.number_input("Horas Jugadas:", min_value=0.5, max_value=5000.0, value=25.0, step=5.0)

            submitted = st.form_submit_button("💾 Guardar en Base de Datos")

            if submitted:
                try:
                    if game_choice == "Ingresar Nuevo Título":
                        if not new_game_title.strip():
                            st.error("Debe ingresar el título del videojuego.")
                            st.stop()
                        # Verificar si ya existe
                        existing = [g for g in all_games if g["title"].lower() == new_game_title.strip().lower()]
                        if existing:
                            target_game_id = existing[0]["game_id"]
                        else:
                            target_game_id = db.add_game(new_game_title, selected_genre_id, selected_platform_id)
                    
                    db.add_or_update_interaction(selected_player_id, target_game_id, rating_input, hours_input)
                    st.success("¡Interacción guardada exitosamente en la base de datos relacional!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error al registrar: {ex}")


# =============================================================================
# PESTAÑA 2: ANÁLISIS EXPLORATORIO DE DATOS (EDA)
# =============================================================================
with tab_eda:
    st.subheader(f"Análisis de Comportamiento: {selected_player['player_code']}")
    st.markdown(
        "Esta sección analiza los patrones de comportamiento, tiempo invertido y "
        "preferencias del jugador a partir de las interacciones almacenadas."
    )

    summary = eda.get_player_summary(selected_player_id)

    if not summary["has_data"]:
        st.warning("No hay suficientes datos registrados para generar el análisis exploratorio de este jugador.")
    else:
        # Métricas Clave (KPIs)
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        kpi1.metric("🎮 Juegos Reportados", summary["total_games"])
        kpi2.metric("⏱️ Horas Totales", f"{summary['total_hours']} h")
        kpi3.metric("⭐ Calificación Media", f"{summary['avg_rating']} / 5.0")
        kpi4.metric("📈 Promedio Horas/Juego", f"{summary['avg_hours_per_game']} h")
        kpi5.metric("🎯 Género Favorito", summary["top_genre"])

        st.markdown("---")

        col_charts1, col_charts2 = st.columns(2)

        genre_df = eda.get_genre_breakdown(selected_player_id)
        plat_df = eda.get_platform_breakdown(selected_player_id)

        with col_charts1:
            st.markdown("##### ⏱️ Horas Invertidas por Género")
            if not genre_df.empty:
                chart_data = genre_df.set_index("genre_name")[["total_hours"]]
                st.bar_chart(chart_data)
            else:
                st.info("Sin datos de géneros.")

        with col_charts2:
            st.markdown("##### 💻 Horas Invertidas por Plataforma")
            if not plat_df.empty:
                chart_plat = plat_df.set_index("platform_name")[["total_hours"]]
                st.bar_chart(chart_plat)
            else:
                st.info("Sin datos de plataformas.")

        st.markdown("##### 🔍 Tabla Detallada de Afinidades Conductuales")
        st.markdown(
            "El puntaje de afinidad combina la calificación explícita y la intensidad de juego logarítmica: "
            "$W = \\text{rating} \\times \\ln(1 + \\text{horas})$."
        )
        if not genre_df.empty:
            eda_table = genre_df.rename(columns={
                "genre_name": "Género",
                "games_count": "N° Juegos",
                "total_hours": "Horas Totales",
                "avg_rating": "Calificación Media",
                "share_hours_pct": "% del Tiempo Total",
                "affinity_score": "Score de Afinidad Conductual"
            })
            st.dataframe(eda_table, width="stretch", hide_index=True)


# =============================================================================
# PESTAÑA 3: RECOMENDACIONES PERSONALIZADAS Y EXPLICABILIDAD
# =============================================================================
with tab_recs:
    st.subheader(f"Recomendaciones Personalizadas para {selected_player['player_code']}")
    st.markdown(
        "El motor analiza el perfil de afinidades del jugador para sugerir videojuegos no explorados, "
        "proporcionando una explicación transparente de cada recomendación."
    )

    col_algo, col_n = st.columns([3, 1])
    with col_algo:
        algo_choice = st.radio(
            "Técnica de Recomendación:",
            options=[
                "Filtrado Basado en Contenido con Ponderación Conductual (Recomendado)",
                "Filtrado Colaborativo Basado en Usuarios (Comparativa)"
            ],
            horizontal=True
        )
    with col_n:
        top_n = st.slider("Cantidad de Recomendaciones:", min_value=1, max_value=8, value=4)

    if "Contenido" in algo_choice:
        recommendations = cbf_recommender.recommend(selected_player_id, top_n=top_n)

        if not recommendations:
            st.info("No hay títulos disponibles para recomendar en este momento.")
        else:
            st.markdown(f"#### Top {len(recommendations)} Títulos Sugeridos")
            
            for idx, rec in enumerate(recommendations, start=1):
                with st.container(border=True):
                    head_col, score_col = st.columns([4, 1])
                    with head_col:
                        st.markdown(f"### {idx}. {rec['title']} ({rec['release_year'] or 'N/A'})")
                        st.caption(f"🎭 **Género:** {rec['genre_name']} | 🎮 **Plataforma:** {rec['platform_name']}")
                        if rec['description']:
                            st.write(rec['description'])
                    with score_col:
                        st.metric("Afinidad Estimada", f"{rec['match_score']}%")
                        st.progress(min(max(rec['match_score'] / 100.0, 0.0), 1.0))

                    st.info(f"💡 **¿Por qué te lo recomendamos?**\n\n{rec['explanation']}")

    else:
        # Modo Filtrado Colaborativo
        cf_result = cf_recommender.recommend(selected_player_id, top_n=top_n)
        st.caption(f"ℹ️ **Diagnóstico del Modelo Colaborativo:** {cf_result['status']}")

        cf_recs = cf_result["recommendations"]
        if not cf_recs:
            st.warning(
                "El modelo de filtrado colaborativo no encontró suficientes coincidencias directas con otros jugadores.\n\n"
                "**Nota Académica:** Este es un ejemplo clásico del problema de dispersión (sparsity) y arranque en frío "
                "cuando los encuestados reportan pocos títulos (3 juegos por encuesta). Por esta razón, el "
                "**Filtrado Basado en Contenido** resulta más robusto para este conjunto de datos inicial."
            )
        else:
            for idx, rec in enumerate(cf_recs, start=1):
                with st.container(border=True):
                    st.markdown(f"### {idx}. {rec['title']}")
                    st.caption(f"🎭 Género: {rec['genre_name']} | 🎮 Plataforma: {rec['platform_name']}")
                    st.metric("Calificación Predicha", f"{rec['predicted_rating']} / 5.0")
                    st.success(rec['explanation'])


# =============================================================================
# PESTAÑA 4: IMPORTACIÓN DE ENCUESTA GOOGLE FORMS Y COHORTE GLOBAL
# =============================================================================
with tab_survey:
    st.subheader("Integración de Encuestas (Google Forms / Google Sheets)")
    st.markdown(
        "Permite cargar respuestas reales de jugadores recogidas a través de la encuesta "
        "prevista en la propuesta del proyecto."
    )

    col_up, col_info = st.columns([3, 2])

    with col_up:
        uploaded_file = st.file_uploader(
            "Cargar archivo CSV de Respuestas de Encuesta:",
            type=["csv"],
            help="El archivo debe contener columnas: player_code, game_title, genre, platform, rating, hours_played"
        )

        if uploaded_file is not None:
            if st.button("🚀 Procesar e Importar a Base de Datos"):
                try:
                    import_res = importer.import_from_csv(uploaded_file)
                    st.success(
                        f"Importación completada con éxito:\n\n"
                        f"- Total filas leídas: {import_res['total_rows']}\n"
                        f"- Nuevos jugadores creados: {import_res['new_players']}\n"
                        f"- Nuevos videojuegos agregados al catálogo: {import_res['new_games']}\n"
                        f"- Interacciones registradas: {import_res['imported_interactions']}"
                    )
                    if import_res["errors"]:
                        with st.expander("Ver advertencias de importación"):
                            for err in import_res["errors"]:
                                st.write(err)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error durante la importación: {e}")

    with col_info:
        st.markdown("##### 📄 Plantilla de Ejemplo")
        st.markdown(
            "La encuesta solicita los 3 videojuegos más jugados por participante. "
            "Descarga la plantilla CSV con el formato requerido:"
        )
        sample_csv_path = ROOT_DIR / "data" / "survey_template.csv"
        if sample_csv_path.exists():
            with open(sample_csv_path, "r", encoding="utf-8") as f:
                template_data = f.read()
            st.download_button(
                label="📥 Descargar survey_template.csv",
                data=template_data,
                file_name="survey_template.csv",
                mime="text/csv"
            )

    st.markdown("---")
    st.subheader("🌐 Métricas Globales del Sistema (Catálogo y Cohorte de Jugadores)")
    global_eda = eda.get_global_catalog_eda()

    g1, g2, g3 = st.columns(3)
    g1.metric("👥 Total Jugadores en Sistema", global_eda["total_players"])
    g2.metric("🕹️ Total Videojuegos en Catálogo", global_eda["total_games"])
    g3.metric("📝 Total Interacciones Registradas", global_eda["total_interactions"])

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### 🎮 Juegos por Género en Catálogo")
        if not global_eda["catalog_genres"].empty:
            cg_chart = global_eda["catalog_genres"].set_index("genre_name")
            st.bar_chart(cg_chart)

    with col_g2:
        st.markdown("##### ⏱️ Total Horas Acumuladas por Género")
        if not global_eda["interactions_by_genre"].empty:
            ig_chart = global_eda["interactions_by_genre"].set_index("genre_name")[["total_hours"]]
            st.bar_chart(ig_chart)
