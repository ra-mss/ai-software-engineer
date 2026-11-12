import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from app.core.telemetry import get_langfuse_handler
from app.core.graph import build_graph

load_dotenv()
app_graph = build_graph()

app = FastAPI(
    title="AI Software Engineering System MVP",
    description="Sistema multi-agente con orquestación vía LangGraph",
    version="1.0.0"
)

class TaskRequest(BaseModel):
    task: str

class TaskResponse(BaseModel):
    status: str
    final_result: str | None = None
    trace_url: str | None = None
    iterations: int = 0
    errors_detected: list[str] = []

@app.post("/execute", response_model=TaskResponse)
def execute_task(request: TaskRequest):
    langfuse_handler = get_langfuse_handler()
    
    initial_state = {
        "task_description": request.task,
        "messages": [HumanMessage(content=request.task, name="User")],
        "iteration_count": 0,
        "validation_errors": [],
        "plan": [],
        "generated_code": []
    }
    
    config = {"callbacks": [langfuse_handler]}
    
    def get_safe_trace_url():
        if hasattr(langfuse_handler, "get_trace_url"):
            return langfuse_handler.get_trace_url()
        return "Traza registrada. Revisa tu dashboard en cloud.langfuse.com"

    try:
        final_state = app_graph.invoke(initial_state, config=config)
        
        return TaskResponse(
            status="success",
            final_result=final_state.get("final_result", "Ejecución finalizada sin mensaje final."),
            trace_url=get_safe_trace_url(),
            iterations=final_state.get("iteration_count", 0),
            errors_detected=final_state.get("validation_errors", [])
        )
    except Exception as e:
        return TaskResponse(
            status="error",
            final_result=f"Fallo en la ejecución del grafo: {str(e)}",
            trace_url=get_safe_trace_url()
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)