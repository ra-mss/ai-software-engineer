# AI Software Engineering System (PROTOTYPE)

AI Software Engineering System 

Este proyecto es un sistema de orquestación multi-agente impulsado por inteligencia artificial. En palabras simples, es un **equipo virtual de desarrolladores de software automatizado**. En lugar de usar un solo chat de IA que adivina respuestas, este sistema puede dividir problemas complejos y pone a trabajar a varios "agentes" que colaboran, escriben código, lo revisan y se corrigen entre ellos antes de entregarte un resultado final.

---

## ¿Cómo funciona la arquitectura?

El sistema funciona con un flujo jerárquico estricto manejado por **LangGraph**. Nuestro equipo virtual consta de los siguientes roles:

1. **Supervisor (Gerente):** Recibe tu petición, analiza qué hay que hacer y decide a quién pasarle el turno.
2. **Researcher (Investigador):** Busca contexto o información técnica (RAG) en una base de datos (Qdrant) si la tarea requiere documentación específica.
3. **Coder (Programador):** Escribe el código fuente en Python y lo guarda físicamente en la carpeta `/workspace` del proyecto.
4. **Reviewer (Revisor):** Lee el archivo generado por el Coder. Si encuentra errores, rechaza el código y obliga al Coder a hacerlo de nuevo. Si todo está bien, lo aprueba.

Todo esto está construido sobre **FastAPI** (para la comunicación local) y monitoreado por **Langfuse** (para ver cuánto dinero y tiempo gasta la IA). El cerebro detrás de la generación es **Google Gemini (Flash)**.

---

## Guía de colaboración y seguridad (IMPORTANTE)

Antes de hacer tu primer commit o contribuir a este repositorio, es vital que tu entorno local esté protegido para no filtrar credenciales.

### 1. Archivo `.gitignore`
Asegúrate de que en la raíz del proyecto exista un archivo llamado `.gitignore` con este contenido exacto. Esto evitará que subas tus API Keys a GitHub:

```text
# Entornos virtuales
venv/
env/

# Variables de entorno 
.env

# Archivos compilados de Python
__pycache__/
*.pyc

# Carpeta de trabajo (ignoramos el código generado por la IA, pero mantenemos la carpeta)
workspace/*
!workspace/.gitkeep
```
*(Nota: Debe existir un archivo vacío llamado `.gitkeep` dentro de la carpeta `workspace/` para que GitHub respete la estructura del directorio).*

### 2. Archivo `.env.example`
Para que el sistema funcione, necesitas configurar tus variables de entorno. Copia el archivo `.env.example` (o créalo si no existe), renómbralo a `.env` e ingresa tus llaves reales:

```env
# Google AI Studio
GEMINI_API_KEY="API_KEY_1234"

# Observabilidad
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_HOST="https://cloud.langfuse.com"

# Base de datos (Para el Researcher)
QDRANT_URL=":memory:" # Cambiar a http://localhost:6333 cuando se use Docker
```

---

## Guía de instalación local

Sigue estos pasos al pie de la letra para correr el proyecto en tu computadora.

### Requisitos previos
* Tener **Python 3.11** o superior instalado.
* Obtener una API Key gratuita de [Google AI Studio](https://aistudio.google.com/).
* Crear una cuenta gratuita en [Langfuse Cloud](https://cloud.langfuse.com/) y obtener tus API Keys (Public y Secret).

### Clonar y preparar el entorno
Abre tu terminal y ejecuta los siguientes comandos paso a paso:

```bash
# 1. Clona este repositorio
git clone <URL_DEL_REPOSITORIO>
cd ai_software_engineer

# 2. Crea un entorno virtual 
python -m venv venv

# 3. Activa el entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# 4. Instala todas las dependencias
pip install -r requirements.txt
```

---

## Cómo ejecutar el sistema

Una vez que el `.env` está configurado y las dependencias instaladas, levantar el sistema es muy fácil:

1. Asegúrate de tener tu entorno virtual activado.
2. Corre el servidor con este comando:
```bash
python main.py
```
3. Abre tu navegador de internet y ve a: **http://localhost:8000/docs**
   *(Esta es la interfaz gráfica de Swagger que genera FastAPI automáticamente).*

### Enviando tu primera tarea
1. En la página de Swagger, busca el endpoint verde que dice `POST /execute`.
2. Dale clic al botón **"Try it out"** (Probar).
3. En la caja negra (Request body), escribe la tarea que quieres que el equipo de IA resuelva. Por ejemplo:
```json
{
  "task": "Escribe un script en Python que calcule la secuencia de Fibonacci hasta el número N de forma recursiva."
}
```
4. Dale clic al botón azul grande **"Execute"**. 
5. Espera unos segundos. Al terminar, la página te devolverá un JSON diciendo `"status": "success"`, y el código listo aparecerá mágicamente dentro de la carpeta `workspace/solucion_mvp.py` de tu proyecto.

---

## Interpretación de resultados y la pregunta clave

Este proyecto no solo escribe código, sino que es un experimento arquitectónico para responder una pregunta importante: **¿Cuándo se justifica utilizar un equipo de agentes, y cuándo es mejor usar un chat simple?**

Para responderla, usamos **Langfuse**. Entra a tu dashboard en Langfuse y busca la última "Traza" (Trace) generada tras tu ejecución. Aquí está la interpretación para el equipo:

### 1. ¿Cómo leer el dashboard?
* **Costos ($0.00):** Si usas el modelo gratuito de Gemini Flash, verás que el gasto en dólares se mantiene en 0, lo cual es excelente para pruebas.
* **Percentiles de latencia (Tiempo):** Verás una tabla que desglosa cuánto tardó toda la ejecución (`LangGraph`) y cuánto tardó cada agente (`Coder`, `Reviewer`).

### 2. La Conclusión del MVP
**Para tareas triviales (Ej: Hacer un Hola Mundo o un script corto):**
El sistema multi-agente es *ineficiente*. Verás que el Coder tarda 1 segundo en escribir el código, pero LangGraph añade varios segundos extras en coordinar al Supervisor y al Reviewer. El "overhead" (retraso burocrático) no vale la pena para problemas fáciles.

**Para tareas complejas (Ej: Crear una API con base de datos y pruebas unitarias):**
Aquí es donde el sistema se nota más. Se puede ver que la latencia total puede subir a 20 o 30 segundos. Sin embargo, en la pestaña de "Observaciones" notarás cómo el Reviewer detectó un error (por ejemplo, que al Coder se le olvidó importar una librería) y obligó al sistema a crear una **Iteración 2** de forma autónoma.
Esa lentitud extra es el "tiempo de pensamiento" necesario para que la arquitectura prevenga fallos y te entregue un código validado, probando que **para software complejo, el diseño multi-agente es indispensable**.