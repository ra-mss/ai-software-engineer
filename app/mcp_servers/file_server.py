import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LocalFileSystem")

# Definir ruta basada en el directorio del proyecto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
WORKSPACE_DIR = os.path.join(PROJECT_ROOT, "workspace")

@mcp.tool()
def write_file(filename: str, content: str) -> str:
    """Escribe código fuente en el workspace local."""
    # El archivo cae siempre en la carpeta segura
    safe_path = os.path.join(WORKSPACE_DIR, os.path.basename(filename))
    
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    try:
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Éxito: Archivo '{os.path.basename(safe_path)}' guardado correctamente vía MCP."
    except Exception as e:
        return f"Error de escritura de sistema: {str(e)}"

@mcp.tool()
def read_file(filename: str) -> str:
    """Lee el contenido de un archivo local en el workspace."""
    safe_path = os.path.join(WORKSPACE_DIR, os.path.basename(filename))
    try:
        with open(safe_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: El archivo '{os.path.basename(safe_path)}' no existe."
    except Exception as e:
        return f"Error al leer el archivo: {str(e)}"

if __name__ == "__main__":
    mcp.run()