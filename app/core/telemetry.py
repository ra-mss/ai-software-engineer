import os
from langfuse.langchain import CallbackHandler
from dotenv import load_dotenv

# Variables de entorno cargadas
load_dotenv()

def get_langfuse_handler() -> CallbackHandler:
    """
    Inicializa el manejador de eventos de Langfuse.
    En las versiones actuales de langfuse-python, el CallbackHandler lee 
    automáticamente las variables LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY 
    y LANGFUSE_HOST desde el entorno (o archivo .env).
    """
    # Instanciar sin argumentos
    return CallbackHandler()