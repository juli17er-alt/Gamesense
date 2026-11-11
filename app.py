"""
GameSense: Entrypoint para ejecutar la aplicación interactiva.
Uso:
    streamlit run app.py
"""
import sys
import runpy
from pathlib import Path

# Añadir raíz y src al path de Python
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"
for p in (ROOT_DIR, SRC_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Ejecutar el script principal de la interfaz de Streamlit
ui_script = SRC_DIR / "ui" / "app.py"
runpy.run_path(str(ui_script), run_name="__main__")
