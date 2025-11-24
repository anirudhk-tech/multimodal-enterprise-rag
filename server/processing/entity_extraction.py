import json
import logging
from typing import Any, Union, cast

from config import openai_client

from processing.graph_schema import JSON_GRAPH_SCHEMA

logger = logging.getLogger(__name__)


def extract_entities(text: str, media_id: str, pokemon_hint: Union[str, None] = None):
    """
    Call the OpenAI Responses API to extract Pokémon entities and relations
    from a single document's text.

    Returns a dict with keys:
    - pokemon_nodes
    - type_nodes
    - pokemon_type_edges
    - evolution_edges
    - mentions_edges
    """
    system_msg = (
        "You extract structured Pokémon knowledge graph data from text. "
        "Return ONLY a single JSON object with the following top-level keys: "
        "'pokemon_nodes', 'type_nodes', 'pokemon_type_edges', "
        "'evolution_edges', 'mentions_edges'. "
        "Do not include explanations, comments, or any text outside the JSON object."
    )
    user_content = (
        f"Media ID: {media_id}\n\n"
        f"Text:\n{text}\n\n"
        "Extract Pokémon entities, their types, evolutions, and cross-references "
        "to other Pokémon mentioned in this text."
    )

    if pokemon_hint:
        user_content += f"\n\nPrimary Pokémon for this media is: {pokemon_hint}."

    response = openai_client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content},
        ],
        temperature=0.1,
        text=cast(
            Any,
            {
                "format": {
                    "type": "json_schema",
                    "name": "PokemonGraphExtraction",
                    "strict": True,
                    "schema": JSON_GRAPH_SCHEMA,
                }
            },
        ),
    )

    data = json.loads(response.output[0].content[0].text)

    for key in [
        "pokemon_nodes",
        "type_nodes",
        "pokemon_type_edges",
        "evolution_edges",
        "mentions_edges",
    ]:
        data.setdefault(key, [])

    return data
