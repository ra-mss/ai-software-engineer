import os
from langchain_core.tools import tool

# Definir ruta del workspace
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, "workspace")

@tool
def local_write_file(filename: str, content: str) -> str:
    """Guarda código fuente en el workspace local de forma síncrona y segura."""
    safe_path = os.path.join(WORKSPACE_DIR, os.path.basename(filename))
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    try:
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Éxito: Archivo '{os.path.basename(safe_path)}' guardado correctamente."
    except Exception as e:
        return f"Error interno al escribir en disco: {str(e)}"

@tool
def local_read_file(filename: str) -> str:
    """Lee el código del disco duro de forma síncrona."""
    safe_path = os.path.join(WORKSPACE_DIR, os.path.basename(filename))
    try:
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: El archivo '{os.path.basename(safe_path)}' no existe."
    except Exception as e:
        return f"Error interno al leer de disco: {str(e)}"