from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.researcher import researcher_node
from app.agents.coder import coder_node
from app.agents.reviewer import reviewer_node

def build_graph():
    """
    Construye y compila la máquina de estados explícita del sistema multi-agente.
    """
    workflow = StateGraph(AgentState)
    
    # Registrar nodos
    workflow.add_node("Supervisor", supervisor_node)
    workflow.add_node("Researcher", researcher_node)
    workflow.add_node("Coder", coder_node)
    workflow.add_node("Reviewer", reviewer_node)
    
    # Configurar el punto de entrada inicial
    workflow.set_entry_point("Supervisor")
    
    # Añadir aristas estáticas hacia el Supervisor
    workflow.add_edge("Researcher", "Supervisor")
    workflow.add_edge("Coder", "Supervisor")
    workflow.add_edge("Reviewer", "Supervisor")
    
    # Lógica de ruteo condicional desde el Supervisor
    def route_from_supervisor(state: AgentState) -> str:
        agent = state.get("next_agent", "FIN")
        if agent == "FIN":
            return END
        return agent
        
    workflow.add_conditional_edges(
        "Supervisor",
        route_from_supervisor,
        {
            "Researcher": "Researcher",
            "Coder": "Coder",
            "Reviewer": "Reviewer",
            END: END
        }
    )
    
    # Compilar el grafo en una aplicación ejecutable
    return workflow.compile()