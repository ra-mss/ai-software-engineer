import json
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState
from app.agents.coder import generate_with_gemini

def supervisor_node(state: AgentState) -> Dict[str, Any]:
    task = state.get("task_description", "")
    messages = state.get("messages", [])
    iteration = state.get("iteration_count", 0)
    
    has_research = any(m.name == "Researcher" for m in messages)
    last_agent = messages[-1].name if messages else "User"

    if not has_research:
        prompt = (
            f"La tarea es: '{task}'. "
            "Devuelve un arreglo JSON válido con 3 pasos lógicos para resolver esto. "
            "Ejemplo: [\"1. Investigar\", \"2. Programar\", \"3. Revisar\"]."
        )
        try:
            raw_plan = generate_with_gemini(prompt)
            plan_text = raw_plan.strip()
            
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0].strip()
            plan = json.loads(plan_text)
        except Exception:
            plan = ["1. Investigar contexto", "2. Generar código", "3. Revisar y corregir"]
            
        return {
            "next_agent": "Researcher",
            "plan": plan,
            "messages": [AIMessage(content="Plan creado. Asignando responsabilidad al Researcher.", name="Supervisor")]
        }

    if last_agent == "Researcher":
        next_agent = "Coder"
        msg = "Contexto recuperado. Asignando responsabilidad de escritura al Coder."
    elif last_agent == "Coder":
        next_agent = "Reviewer"
        msg = "Código generado. Asignando responsabilidad de inspección al Reviewer."
    elif last_agent == "Reviewer":
        if "Aprobado" in messages[-1].content:
            next_agent = "FIN"
            msg = f"Flujo completado exitosamente tras {iteration} iteración(es). Fin de la ejecución."
        else:
            if iteration >= 3:
                next_agent = "FIN"
                msg = f"Límite de {iteration} iteraciones alcanzado. Abortando para evitar sobrecostos."
            else:
                next_agent = "Coder"
                msg = "El Reviewer detectó errores. Solicitando correcciones al Coder."
    else:
        next_agent = "FIN"
        msg = "Estado desconocido, forzando cierre de seguridad."

    if next_agent == "FIN":
        return {
            "next_agent": "FIN",
            "final_result": msg,
            "messages": [AIMessage(content=msg, name="Supervisor")]
        }

    return {
        "next_agent": next_agent,
        "messages": [AIMessage(content=msg, name="Supervisor")]
    }