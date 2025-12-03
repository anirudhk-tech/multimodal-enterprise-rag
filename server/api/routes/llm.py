import logging

from config import openai_client
from eval_logging.eval_logger import log_evaluation
from fastapi import APIRouter, Form
from processing.graph_store import build_graph_context
from processing.vector_store import build_vector_context

logger = logging.getLogger(__name__)
router = APIRouter(tags=["llm"])


@router.post("/chat")
async def chat(message: str = Form(...)):
    system_msg = "You are a pokemon expert."

    graph_result = build_graph_context(message)
    vector_result = build_vector_context(message)

    graph_context_str = graph_result.get("context", "")
    node = graph_result.get("node")
    vector_context_str = vector_result.get("context", "")

    logger.info(f"Vector Context: {vector_context_str}")

    user_content = (
        f"{message}\n\n"
        f"Graph Context:\n{graph_context_str}\n\n"
        f"Vector Context:\n{vector_context_str}"
    )

    response = openai_client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        max_output_tokens=100,
    )

    answer = response.output[0].content[0].text

    retrieved_context = {
        "graph_context": graph_context_str,
        "vector_context": vector_context_str,
    }

    evaluation_scores = {
        "grounded_in_graph": bool(graph_context_str),
        "latency_ms": None,
    }

    log_evaluation(
        query=message,
        answer=answer,
        retrieved_context=retrieved_context,
        evaluation_scores=evaluation_scores,
        focused_pokemon=node,
    )

    return {"content": answer, "node": node}
