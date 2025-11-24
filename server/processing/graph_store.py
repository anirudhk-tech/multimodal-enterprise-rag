import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

GRAPH_JSON = Path("graph/graph.json")

logger = logging.getLogger(__name__)


def load_graph() -> Dict[str, Any]:
    if not GRAPH_JSON.exists():
        return {
            "pokemon_nodes": [],
            "type_nodes": [],
            "pokemon_type_edges": [],
            "evolution_edges": [],
            "mentions_edges": [],
        }
    with GRAPH_JSON.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_related_pokemon(graph: Dict[str, Any], pokemon_name: str) -> Dict[str, Any]:
    """Return basic neighborhood: types, evolutions, mentions."""
    name = pokemon_name

    types = [
        e["to_type"]
        for e in graph.get("pokemon_type_edges", [])
        if e["from_pokemon"] == name
    ]

    evolves_to = [
        e["to_pokemon"]
        for e in graph.get("evolution_edges", [])
        if e["from_pokemon"] == name
    ]
    evolves_from = [
        e["from_pokemon"]
        for e in graph.get("evolution_edges", [])
        if e["to_pokemon"] == name
    ]

    mentioned_in = [
        e["from_media_id"]
        for e in graph.get("mentions_edges", [])
        if e["to_pokemon"] == name
    ]

    return {
        "types": types,
        "evolves_to": evolves_to,
        "evolves_from": evolves_from,
        "mentioned_in": mentioned_in,
    }


def find_pokemon_name_in_question(
    graph: Dict[str, Any], question: str
) -> Optional[str]:
    q = question.lower()
    tokens = {t for t in re.split(r"[^a-z0-9]+", q) if t}

    for p in graph.get("pokemon_nodes", []):
        name = p["name"]
        name_token = name.lower().replace(" ", "")

        if name.lower() in tokens or name_token in tokens:
            return name

    return None


def find_pokemon_nodes_by_name(
    graph: Dict[str, Any], query: str
) -> List[Dict[str, Any]]:
    tokens = {t for t in re.split(r"[^a-z0-9]+", query.lower()) if t}

    matches: List[Dict[str, Any]] = []
    for p in graph.get("pokemon_nodes", []):
        name = p["name"]
        name_token = name.lower()
        if name_token in tokens:
            matches.append(p)
            continue

    return matches


def build_graph_context(question: str) -> Dict[str, Any]:
    logger.info(f"Building graph context for question: {question}")

    graph = load_graph()
    if not graph["pokemon_nodes"]:
        logger.warning("No Pokémon data found in graph.json")
        return ""

    candidates = find_pokemon_nodes_by_name(graph, question)
    if not candidates:
        logger.warning(f"No Pokémon found for question: {question}")
        return ""

    primary = candidates[0]
    neighborhood = find_related_pokemon(graph, primary["name"])

    lines: List[str] = []

    lines.append("Known Pokémon fact (from graph.json):")
    lines.append(
        f"- Name: {primary.get('name')}, generation: {primary.get('generation')}, "
        f"primary_type: {primary.get('primary_type')}, "
        f"secondary_type: {primary.get('secondary_type')}"
    )

    if neighborhood["types"]:
        lines.append(f"- Types: {', '.join(neighborhood['types'])}")
    if neighborhood["evolves_from"]:
        lines.append(f"- Evolves from: {', '.join(neighborhood['evolves_from'])}")
    if neighborhood["evolves_to"]:
        lines.append(f"- Evolves to: {', '.join(neighborhood['evolves_to'])}")
    if neighborhood["mentioned_in"]:
        lines.append(
            f"- Mentioned in media IDs: {', '.join(neighborhood['mentioned_in'])}"
        )

    lines.append(
        "Only answer using these graph facts and general Pokémon knowledge; "
        "do not invent evolutions or types that conflict with the graph."
    )

    logger.info(f"Graph context built for question: {question}")

    return {"context": "\n".join(lines), "node": primary}
