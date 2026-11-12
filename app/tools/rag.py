import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.tools import tool
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# Configurar Embeddings locales 
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Inicializar cliente en Qdrant
qdrant_url = os.getenv("QDRANT_URL", ":memory:")
client = QdrantClient(location=qdrant_url)
collection_name = "software_docs"

# Crear la colección si no existe
if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)

# Ingesta de datos de prueba para el MVP
def ingest_sample_data():
    docs = [
        "Para LangGraph: El estado compartido se actualiza retornando diccionarios desde los nodos que se fusionan según los 'Reducers' (como operator.add).",
        "FastAPI: Los endpoints deben usar Pydantic para la validación de esquemas de entrada y salida.",
        "Model Context Protocol (MCP): Permite conectar a los LLMs de forma segura a recursos locales usando el modelo cliente-servidor."
    ]
    vector_store.add_texts(docs)

# Ejecutar ingesta de prueba al cargar el módulo
ingest_sample_data()

@tool
def search_documentation(query: str) -> str:
    """
    Busca en la base de conocimientos técnica interna.
    Usa esta herramienta cuando necesites contexto sobre frameworks, librerías o arquitectura.
    """
    # similarity_search para recuperar los 2 fragmentos más relevantes
    results = vector_store.similarity_search(query, k=2)
    
    if not results:
        return "No se encontró información relevante en la documentación."
    
    context = "\n\n".join([f"- {doc.page_content}" for doc in results])
    return f"Contexto técnico recuperado de Qdrant:\n{context}"