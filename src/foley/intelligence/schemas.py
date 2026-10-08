"""What an intelligence implementation is asked to do, and what it answers with."""

from typing import Any

from pydantic import BaseModel, Field

from foley.schemas import ReasoningEffort


class AgentRequest(BaseModel):
    """One bounded scene design run with no filesystem or shell authority."""

    prompt: str
    provider: str = "openai"
    model: str
    output_schema: dict[str, Any] | None = Field(
        default=None, description="JSON schema the structured output must satisfy"
    )
    reasoning_effort: ReasoningEffort = "medium"
    timeout_seconds: int = Field(gt=0)


class AgentResult(BaseModel):
    """The run's outcome; in-flight agent failures set `error` instead of raising."""

    output: dict[str, Any] | None = Field(
        default=None, description="The structured output, conforming to the request's schema when one was given"
    )
    text: str = Field(default="", description="The agent's final message")
    error: str | None = None
    session_id: str | None = Field(
        default=None, description="Identifies this run's session so a later request can resume it"
    )
    provenance: dict[str, Any] = Field(default_factory=dict)
