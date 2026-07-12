"""Optional Langfuse tracing adapter for LLM calls.

Opt-in by construction: ``langfuse`` is the ``tracing`` optional dependency
group and :func:`build_llm_call_observer` returns a no-op observer whenever
the package is not installed or ``LANGFUSE_PUBLIC_KEY``/``LANGFUSE_SECRET_KEY``
are not set, so callers never need to branch on whether tracing is enabled.

Prompt and completion content is forwarded to Langfuse only when
``LANGFUSE_CAPTURE_CONTENT`` is explicitly set to ``true`` after the
data-handling review described in ``docs/LLM_OBSERVABILITY.md``. By default
only metadata (model, token counts, latency) is recorded, consistent with the
"do not log prompts or model responses" rule in
``.claude/rules/security-privacy.md``.
"""

import os
from typing import Any, Protocol


class LlmCallObserver(Protocol):
    """Port for recording the outcome of one completed LLM call."""

    def record(
        self,
        *,
        name: str,
        model: str,
        latency_seconds: float,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        prompt: str | None = None,
        completion: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record one completed LLM call."""
        ...


class NullLlmCallObserver:
    """No-op observer used when Langfuse tracing is not opted in."""

    def record(self, **_: Any) -> None:
        """Discard the call outcome."""
        return


class _LangfuseLlmCallObserver:
    """Observer that forwards call outcomes to a configured Langfuse client."""

    def __init__(self, client: Any, *, capture_content: bool) -> None:
        self._client = client
        self._capture_content = capture_content

    def record(
        self,
        *,
        name: str,
        model: str,
        latency_seconds: float,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        prompt: str | None = None,
        completion: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record one completed LLM call as a Langfuse generation."""
        usage_details: dict[str, int] = {}
        if input_tokens is not None:
            usage_details["input"] = input_tokens
        if output_tokens is not None:
            usage_details["output"] = output_tokens

        with self._client.start_as_current_observation(
            as_type="generation", name=name, model=model
        ) as generation:
            generation.update(
                input=prompt if self._capture_content else None,
                output=completion if self._capture_content else None,
                usage_details=usage_details or None,
                metadata={"latency_seconds": latency_seconds, **(metadata or {})},
            )


def build_llm_call_observer() -> LlmCallObserver:
    """Build a Langfuse observer, or a no-op observer if tracing is not opted in.

    Requires the ``tracing`` optional dependency group
    (``uv sync --extra tracing``) and ``LANGFUSE_PUBLIC_KEY``/
    ``LANGFUSE_SECRET_KEY``; returns :class:`NullLlmCallObserver` otherwise.
    """
    if not os.environ.get("LANGFUSE_PUBLIC_KEY") or not os.environ.get("LANGFUSE_SECRET_KEY"):
        return NullLlmCallObserver()

    try:
        from langfuse import get_client
    except ImportError:
        return NullLlmCallObserver()

    capture_content = os.environ.get("LANGFUSE_CAPTURE_CONTENT", "false").strip().lower() == "true"
    return _LangfuseLlmCallObserver(get_client(), capture_content=capture_content)
