from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState
from app.tools.rag import search_documentation

def researcher_node(state: AgentState) -> Dict[str, Any]:
    """
    Nodo del Agente Researcher.
    Su responsabilidad es expandir la tarea del usuario con contexto técnico
    recuperado a través de RAG antes de pasarle el control al Coder.
    """
    task = state.get("task_description", "")
    
    # Invocar la herramienta RAG de Qdrant
    rag_result = search_documentation.invoke({"query": task})
    
    # Construir el mensaje que quedará registrado en el shared state
    researcher_message = AIMessage(
        content=f"Soy el Researcher. He analizado la tarea y recuperado este contexto:\n{rag_result}",
        name="Researcher"
    )
    
    # Regresar el diccionario que LangGraph combinará con el estado global
    return {
        "messages": [researcher_message],
        # El supervisor determina que el siguiente paso es el coder
    }