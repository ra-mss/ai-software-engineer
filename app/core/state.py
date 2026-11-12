import operator
from typing import Annotated, Sequence, TypedDict, List
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

class CodeSnippet(BaseModel):
    """Esquema para validar el código generado antes de guardarlo en el estado."""
    file_name: str = Field(description="Nombre del archivo a crear o modificar")
    code: str = Field(description="El código fuente funcional y completo")
    language: str = Field(description="Lenguaje de programación")

class AgentState(TypedDict):
    """
    Estado global del grafo de LangGraph.
    Annotated con operator.add indica que las listas se concatenan (reducen) 
    en lugar de sobrescribirse en cada paso.
    """
    # Historial de mensajes del usuario y los agentes
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # Orquestación
    next_agent: str       # Define quién tiene el turno, si Researcher, Coder, Reviewer o END
    task_description: str # La tarea original 
    plan: List[str]       # Pasos a seguir (pero definidos por el Supervisor)
    
    # Artefactos
    generated_code: List[CodeSnippet] # Código (pero producido por el Coder)
    
    # Telemetría y control de ciclos (para la pregunta clave)
    iteration_count: int  # Cuántas veces se ha pasado por el ciclo Coder-Reviewer
    validation_errors: Annotated[List[str], operator.add] # Errores detectados por el Reviewer
    final_result: str     # Respuesta final para entregar