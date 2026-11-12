from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState
from app.tools.mcp_client import local_read_file
from app.agents.coder import generate_with_gemini

def reviewer_node(state: AgentState) -> Dict[str, Any]:
    target_filename = "solucion_mvp.py"
    task = state.get("task_description", "")
    
    try:
        code_content = local_read_file.invoke({"filename": target_filename})
    except Exception as e:
        code_content = f"Error crítico: {str(e)}"
    
    if code_content.startswith("Error:") or code_content.startswith("Error interno"):
        return {
            "messages": [AIMessage(content=f"Error del sistema de archivos: {code_content}", name="Reviewer")],
            "validation_errors": ["Error de lectura/escritura en disco."]
        }
    
    if "ERROR_API_EXTERNA" in code_content:
         return {
            "messages": [AIMessage(content="El Coder falló por problemas de API.", name="Reviewer")],
            # Ver el error del Coder
            "validation_errors": [code_content] 
        }

    prompt = (
        f"Eres un Revisor de Código. La tarea era: {task}.\n"
        f"El código propuesto es:\n\n{code_content}\n\n"
        "Si es correcto, responde exactamente 'APPROVE'. "
        "Si tiene fallas, responde 'REJECT:' seguido de la explicación."
    )
    
    raw_review = generate_with_gemini(prompt)
    review_result = raw_review.strip()
    
    errors = []
    if "REJECT" in review_result.upper():
        error_msg = review_result.replace("REJECT:", "").strip()
        errors = [error_msg]
        status_msg = f"Rechazado: {error_msg}"
    elif "ERROR_API_EXTERNA" in review_result:
        # Ver el error del Reviewer
        errors = [review_result]
        status_msg = "Rechazado por fallo de conexión del Reviewer."
    else:
        status_msg = "Aprobado: El código cumple los requisitos."
    
    message = AIMessage(
        content=f"He revisado {target_filename}. Resultado: {status_msg}", 
        name="Reviewer"
    )
    
    return {
        "messages": [message],
        "validation_errors": errors
    }