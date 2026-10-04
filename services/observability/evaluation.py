from typing import Any
from uuid import uuid4

from services.observability.langsmith import (
    configure_langsmith,
    get_langsmith_client,
)


V1_DATASET_NAME = "ai-layer-v1-core"


def ensure_v1_dataset(
    client,
    dataset_name: str = V1_DATASET_NAME,
) -> str:
    if client.has_dataset(dataset_name=dataset_name):
        return dataset_name

    dataset = client.create_dataset(
        dataset_name,
        description=(
            "AI Layer V1 representative evaluation set for Chat, RAG, "
            "tool-driven Loop behavior, and mixed-language interaction."
        ),
    )

    examples = [
        {
            "inputs": {
                "question": "Calculate 8 multiplied by 944",
            },
            "outputs": {
                "contains": "7552",
            },
            "metadata": {
                "area": "loop",
                "language": "en",
            },
        },
        {
            "inputs": {
                "question": "What time is it right now?",
            },
            "outputs": {},
            "metadata": {
                "area": "loop",
                "language": "en",
            },
        },
        {
            "inputs": {
                "question": "What model represents customers in Odoo?",
            },
            "outputs": {
                "contains": "res.partner",
            },
            "metadata": {
                "area": "rag",
                "language": "en",
            },
        },
        {
            "inputs": {
                "question": "What is Python? Answer in one sentence.",
            },
            "outputs": {},
            "metadata": {
                "area": "chat",
                "language": "en",
            },
        },
        {
            "inputs": {
                "question": "اشرح لي ما هو API بجملة واحدة.",
            },
            "outputs": {},
            "metadata": {
                "area": "chat",
                "language": "ar",
            },
        },
    ]

    client.create_examples(
        dataset_id=dataset.id,
        examples=examples,
    )

    return dataset_name


def output_non_empty(run: Any, example: Any) -> dict:
    outputs = getattr(run, "outputs", None) or {}
    content = str(outputs.get("content", "")).strip()
    return {
        "key": "non_empty",
        "score": 1 if content else 0,
        "comment": (
            "Final content exists."
            if content
            else "Final content is empty."
        ),
    }


def valid_display_type(run: Any, example: Any) -> dict:
    outputs = getattr(run, "outputs", None) or {}
    display_type = outputs.get("display_type")
    valid = display_type in {
        "text",
        "card",
        "table",
    }
    return {
        "key": "display_type_valid",
        "score": 1 if valid else 0,
        "comment": f"display_type={display_type!r}",
    }


def expected_content(run: Any, example: Any) -> dict:
    outputs = getattr(run, "outputs", None) or {}
    content = str(
        outputs.get("content", "")
    ).strip().lower()

    example_outputs = getattr(example, "outputs", None) or {}
    expected = example_outputs.get("contains")

    if not expected:
        return {
            "key": "expected_content",
            "comment": "No expected substring configured.",
        }

    expected_lower = str(expected).lower()
    matched = expected_lower in content

    return {
        "key": "expected_content",
        "score": 1 if matched else 0,
        "comment": (
            "Expected substring found."
            if matched
            else f"Expected substring {expected!r} was not found."
        ),
    }


def run_v1_evaluation(
    brain,
    *,
    dataset_name: str = V1_DATASET_NAME,
    experiment_prefix: str = "ai-layer-v1",
    max_concurrency: int = 1,
):
    configure_langsmith()
    client = get_langsmith_client()

    if client is None:
        raise RuntimeError(
            "LangSmith is not configured. Set LANGSMITH_ENABLED=true "
            "and LANGSMITH_API_KEY."
        )

    ensure_v1_dataset(client, dataset_name)

    from langsmith import evaluate

    def target(inputs: dict[str, Any]) -> dict[str, Any]:
        response = brain.process(
            question=inputs["question"],
            session_id=f"langsmith-eval-{uuid4().hex}",
        )
        return {
            "content": response.content,
            "display_type": response.display_type,
        }

    return evaluate(
        target,
        data=dataset_name,
        evaluators=[
            output_non_empty,
            valid_display_type,
            expected_content,
        ],
        client=client,
        experiment_prefix=experiment_prefix,
        description="AI Layer V1 core evaluation.",
        max_concurrency=max_concurrency,
    )
