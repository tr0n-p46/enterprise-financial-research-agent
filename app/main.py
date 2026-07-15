"""FastAPI application entry point."""

from agno.exceptions import ModelProviderError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import research

app = FastAPI(
    title="Enterprise Financial Research Agent",
    description=(
        "An agentic API combining DuckDuckGo search and Yahoo Finance "
        "data via a Groq-hosted LLM to answer financial research questions."
    ),
    version="0.1.0",
)

app.include_router(research.router)


@app.exception_handler(ModelProviderError)
async def model_provider_error_handler(
    request: Request, exc: ModelProviderError
) -> JSONResponse:
    """Return a structured, honest error when the LLM provider fails.

    Used 502 (Bad Gateway) rather than the default 500: our API is acting
    as a gateway to an upstream provider (Groq), and the upstream provider
    is what failed — 502 communicates that more accurately to the caller
    than a generic 500, which implies our own code is broken.

    By the time this handler runs, run_query() has already exhausted its
    retry attempts (see app/services/research_agent.py), so this represents
    a genuine, non-recovered failure worth surfacing clearly.
    """
    return JSONResponse(
        status_code=502,
        content={
            "error": "model_provider_error",
            "message": (
                "The upstream language model provider failed to process "
                "this request after retrying. This is typically a "
                "transient issue — please try again."
            ),
        },
    )
