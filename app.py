"""
GameSense: Entrypoint para ejecutar la aplicación interactiva.
Uso:
    streamlit run app.py
"""
import sys
from pathlib import Path

# Añadir raíz al path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ejecutar aplicación principal
import src.ui.app
