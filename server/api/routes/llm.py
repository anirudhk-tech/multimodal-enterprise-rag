import logging

from config import openai_client
from fastapi import APIRouter, Form  # type: ignore (safe to ignore, local editor quirk)
from processing.graph_store import build_graph_context

logger = logging.getLogger(__name__)

router = APIRouter(tags=["llm"])


@router.post("/chat")
async def chat(message: str = Form(...)):
    system_msg = "You are a pokemon expert."
    graph_context = build_graph_context(message)
    context = graph_context["context"]
    node = graph_context["node"]
    user_content = f"""
        {message}\n\n
        {context}
    """

    response = openai_client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content},
        ],
        temperature=0.7,
        max_output_tokens=100,
    )

    return {"content": response.output[0].content[0].text, "node": node}
