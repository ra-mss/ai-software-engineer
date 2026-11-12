import os
from dotenv import load_dotenv
from typing import Dict, Any
from langchain_core.messages import AIMessage
from google import genai
from app.core.state import AgentState, CodeSnippet
from app.tools.mcp_client import local_write_file

load_dotenv()

def generate_with_gemini(prompt: str) -> str:
    try:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            return "ERROR_API_EXTERNA: No se encontró la API Key en las variables de entorno."
            
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"ERROR_API_EXTERNA: {str(e)}"

def coder_node(state: AgentState) -> Dict[str, Any]:
    task = state.get("task_description", "")
    current_iteration = state.get("iteration_count", 0) + 1 
    
    prompt = (
        f"Eres un Desarrollador de Software Senior. Resuelve esta tarea: {task}\n"
        "Devuelve ÚNICAMENTE código Python válido. No incluyas explicaciones, " # Podríamos buscar que cambiara 
        "ni formato markdown, ni bloques de código. Solo el texto plano."       # el lenguaje según el que se
    )                                                                           # mencione en la tarea 
    
    raw_response = generate_with_gemini(prompt)
    raw_code = raw_response.strip().replace("```python", "").replace("```", "")
    
    target_filename = "solucion_mvp.py"
    
    try:
        write_result = local_write_file.invoke({"filename": target_filename, "content": raw_code})
    except Exception as e:
        write_result = f"Fallo al escribir en disco: {str(e)}"
    
    new_snippet = CodeSnippet(
        file_name=target_filename, 
        code=raw_code, 
        language="python"
    )
    
    message = AIMessage(
        content=f"Código generado (Iteración {current_iteration}). Archivo: {target_filename}. Log: {write_result}",
        name="Coder"
    )
    
    return {
        "messages": [message],
        "generated_code": [new_snippet],
        "iteration_count": current_iteration
    }