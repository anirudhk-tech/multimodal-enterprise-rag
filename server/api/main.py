import logging

from fastapi import (  # type: ignore (local editor interpreter issue)
    FastAPI,
)
from fastapi.middleware.cors import (  # type: ignore (local editor interpreter issue)
    CORSMiddleware,
)

from api.routes import graph, ingest, llm, process

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(title="Pokemon Starter RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(process.router)
app.include_router(llm.router)
app.include_router(graph.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
