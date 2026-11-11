"""
GameSense: Entrypoint para ejecutar la aplicación interactiva.
Uso:
    streamlit run app.py
"""
import sys
from pathlib import Path

# Añadir raíz y src al path
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
for p in (ROOT_DIR, SRC_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Ejecutar aplicación principal
try:
    import src.ui.app
except ImportError:
    import ui.app
