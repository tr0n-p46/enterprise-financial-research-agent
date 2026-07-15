"""Request/response schemas for the research endpoint."""

from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    """Incoming request body for a research query."""

    query: str = Field(
        ...,
        min_length=1,
        description="A natural-language financial research question.",
        examples=["What's Nvidia's current stock price and recent news?"],
    )


class ResearchResponse(BaseModel):
    """Response body containing the agent's answer."""

    answer: str = Field(..., description="The agent's markdown-formatted answer.")
