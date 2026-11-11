"""
GameSense - Datos de Prueba y Catálogo Inicial
Corporación Universitaria Minuto de Dios - UNIMINUTO
Ingeniería en Ciencia de Datos e Inteligencia Artificial
"""

GENRES = [
    "Action RPG",
    "Shooter / FPS",
    "Estrategia / MOBA",
    "Aventura / Acción",
    "Survival Horror",
    "Deportes / Carreras",
    "Plataformas / Metroidvania",
    "Simulación"
]

PLATFORMS = [
    "PC",
    "PlayStation 5",
    "Xbox Series X/S",
    "Nintendo Switch",
    "Mobile"
]

# Catálogo balanceado de videojuegos con género y plataforma principal
INITIAL_GAMES = [
    # Action RPG
    ("The Witcher 3: Wild Hunt", "Action RPG", "PC", 2015, "Aventura de rol en mundo abierto protagonizada por Geralt de Rivia."),
    ("Elden Ring", "Action RPG", "PC", 2022, "RPG de acción desafiante en las Tierras Intermedias creado por FromSoftware."),
    ("Cyberpunk 2077", "Action RPG", "PC", 2020, "RPG de acción futurista en mundo abierto ambientado en Night City."),
    ("Baldur's Gate 3", "Action RPG", "PC", 2023, "RPG de rol táctico basado en Dungeons & Dragons con narrativa ramificada."),
    ("Dark Souls III", "Action RPG", "PC", 2016, "Intenso juego de rol de acción con combate de alta precisión."),
    
    # Shooter / FPS
    ("DOOM Eternal", "Shooter / FPS", "PC", 2020, "FPS frenético y veloz contra hordas demoníacas."),
    ("Counter-Strike 2", "Shooter / FPS", "PC", 2023, "Táctico shooter en primera persona enfocado en competición de equipos."),
    ("Halo Infinite", "Shooter / FPS", "Xbox Series X/S", 2021, "Campaña y multijugador shooter de la legendaria saga del Jefe Maestro."),
    ("Apex Legends", "Shooter / FPS", "PC", 2019, "Battle royale en primera persona con personajes de habilidades únicas."),
    ("Overwatch 2", "Shooter / FPS", "PC", 2022, "Hero shooter competitivo por equipos 5v5."),

    # Estrategia / MOBA
    ("League of Legends", "Estrategia / MOBA", "PC", 2009, "MOBA competitivo de estrategia en tiempo real por equipos."),
    ("Age of Empires IV", "Estrategia / MOBA", "PC", 2021, "Estrategia clásica en tiempo real con civilizaciones históricas."),
    ("Civilization VI", "Estrategia / MOBA", "PC", 2016, "Estrategia por turnos para construir un imperio que resista el paso del tiempo."),
    ("Dota 2", "Estrategia / MOBA", "PC", 2013, "Profundo juego de estrategia y combate táctico multijugador en arena."),
    ("StarCraft II", "Estrategia / MOBA", "PC", 2010, "Estrategia bélica galáctica en tiempo real."),

    # Aventura / Acción
    ("Red Dead Redemption 2", "Aventura / Acción", "PlayStation 5", 2018, "Épica del salvaje oeste con narrativa profunda y mundo hiperrealista."),
    ("God of War Ragnarök", "Aventura / Acción", "PlayStation 5", 2022, "Kratos y Atreus exploran los nueve reinos de la mitología nórdica."),
    ("The Last of Us Part I", "Aventura / Acción", "PlayStation 5", 2022, "Intensa historia emocional de supervivencia en un mundo postapocalíptico."),
    ("Horizon Zero Dawn", "Aventura / Acción", "PlayStation 5", 2017, "Aloy explora un mundo dominado por máquinas colosales."),
    ("Grand Theft Auto V", "Aventura / Acción", "PC", 2013, "Mundo abierto criminal dinámico en Los Santos."),

    # Survival Horror
    ("Resident Evil 4 Remake", "Survival Horror", "PlayStation 5", 2023, "Remake del clásico juego de terror y acción de supervivencia."),
    ("Dead Space Remake", "Survival Horror", "PC", 2023, "Terror y aislamiento a bordo de la nave minera USG Ishimura."),
    ("Silent Hill 2", "Survival Horror", "PlayStation 5", 2024, "Terror psicológico profundo sobre la culpa y la búsqueda de la verdad."),
    ("Alan Wake 2", "Survival Horror", "PC", 2023, "Terror psicológico y misterio detectivesco entrelazados."),

    # Deportes / Carreras
    ("EA SPORTS FC 24", "Deportes / Carreras", "PlayStation 5", 2023, "Simulador de fútbol profesional con licencias oficiales."),
    ("Forza Horizon 5", "Deportes / Carreras", "Xbox Series X/S", 2021, "Festival de conducción en mundo abierto ambientado en México."),
    ("Rocket League", "Deportes / Carreras", "PC", 2015, "Híbrido de alta velocidad entre fútbol de estilo arcade y caos vehicular."),
    ("Gran Turismo 7", "Deportes / Carreras", "PlayStation 5", 2022, "Simulador real de conducción y colección de automóviles."),

    # Plataformas / Metroidvania
    ("Hollow Knight", "Plataformas / Metroidvania", "Nintendo Switch", 2017, "Aventura 2D desafiante en el reino subterráneo de Hallownest."),
    ("Hades", "Plataformas / Metroidvania", "Nintendo Switch", 2020, "Roguelike de acción dinámico ambientado en el inframundo griego."),
    ("Celeste", "Plataformas / Metroidvania", "Nintendo Switch", 2018, "Plataformas de alta precisión sobre la superación personal."),
    ("Super Mario Odyssey", "Plataformas / Metroidvania", "Nintendo Switch", 2017, "Aventura de plataformas 3D en diversos reinos mágicos."),
    ("Ori and the Will of the Wisps", "Plataformas / Metroidvania", "Xbox Series X/S", 2020, "Hermoso viaje de plataformas con combates y rompecabezas.")
]

# Jugadores de demostración académica con perfiles conductuales diferenciados
# Cada jugador tiene 3 juegos registrados (siguiendo el formato de la encuesta de Google Forms del anteproyecto)
SAMPLE_PLAYERS_INTERACTIONS = [
    # Jugador 1: Perfil entusiasta de Action RPG en PC (muchas horas y altas calificaciones)
    {
        "player_code": "Jugador 1 (Demo - Fan RPG)",
        "games": [
            ("The Witcher 3: Wild Hunt", 5.0, 145.0),
            ("Elden Ring", 4.8, 120.0),
            ("Cyberpunk 2077", 4.5, 80.0)
        ]
    },
    # Jugador 2: Perfil competitivo de Shooters / FPS en PC (muchas horas)
    {
        "player_code": "Jugador 2 (Demo - Fan Shooters)",
        "games": [
            ("Counter-Strike 2", 4.5, 320.0),
            ("DOOM Eternal", 4.8, 42.0),
            ("Apex Legends", 4.0, 190.0)
        ]
    },
    # Jugador 3: Perfil narrativo / Acción en PlayStation 5
    {
        "player_code": "Jugador 3 (Demo - Fan Narrativa)",
        "games": [
            ("Red Dead Redemption 2", 5.0, 115.0),
            ("God of War Ragnarök", 4.9, 58.0),
            ("The Last of Us Part I", 4.7, 32.0)
        ]
    },
    # Jugador 4: Perfil de Estrategia y Gestión en PC
    {
        "player_code": "Jugador 4 (Demo - Fan Estrategia)",
        "games": [
            ("Civilization VI", 4.9, 185.0),
            ("Age of Empires IV", 4.7, 90.0),
            ("League of Legends", 3.8, 280.0)
        ]
    },
    # Jugador 5: Perfil Indie / Plataformas en Nintendo Switch
    {
        "player_code": "Jugador 5 (Demo - Fan Plataformas)",
        "games": [
            ("Hollow Knight", 5.0, 68.0),
            ("Hades", 4.8, 75.0),
            ("Celeste", 4.5, 24.0)
        ]
    }
]
