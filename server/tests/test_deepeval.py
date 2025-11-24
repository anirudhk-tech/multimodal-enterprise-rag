import requests
from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.test_case import LLMTestCase

API_BASE = "http://localhost:8000"


def call_chat(question: str) -> str:
    resp = requests.post(f"{API_BASE}/chat", data={"message": question})
    resp.raise_for_status()
    return resp.json()["content"]


def test_bulbasaur_types():
    question = "What types is Bulbasaur?"
    answer = call_chat(question)

    metric = AnswerRelevancyMetric(
        threshold=0.7,
        model="gpt-4o-mini",
        include_reason=True,
    )

    test_case = LLMTestCase(
        input=question,
        actual_output=answer,
        expected_output="Bulbasaur is a dual-type Grass/Poison Pokémon.",
    )

    evaluate(test_cases=[test_case], metrics=[metric])
