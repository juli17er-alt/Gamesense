@echo off
TITLE GameSense - UNIMINUTO
COLOR 0A
echo ====================================================================
echo  GAMESENSE: SISTEMA DE RECOMENDACION DE VIDEOJUEGOS (MVP)
echo  UNIMINUTO - Ingenieria en Ciencia de Datos e Inteligencia Artificial
echo ====================================================================
echo.

REM 1. Verificar si Python esta instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se encontro Python en este equipo.
    echo Por favor instala Python 3.10 o superior desde https://www.python.org
    echo Recuerda marcar la casilla "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b
)

REM 2. Verificar o crear entorno virtual .venv
if not exist ".venv" (
    echo [1/3] Creando entorno virtual aislado (.venv)...
    python -m venv .venv
)

REM 3. Instalar / verificar dependencias
echo [2/3] Verificando dependencias necesarias (Streamlit, Pandas)...
.\.venv\Scripts\pip.exe install -r requirements.txt --quiet

REM 4. Ejecutar la aplicacion
echo [3/3] Iniciando GameSense en el navegador...
echo.
echo Presiona Ctrl+C en esta ventana para cerrar la aplicacion cuando termines.
echo.
.\.venv\Scripts\streamlit.exe run app.py
pause
