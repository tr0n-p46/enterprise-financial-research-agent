"""
Research agent service.

Owns agent construction and query execution. Deliberately has no
knowledge of *how* it's being called — CLI, HTTP route, or test —
so the same logic can be reused across all three without duplication.
"""

import os
import time

from agno.agent import Agent
from agno.exceptions import ModelProviderError
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL_ID = os.environ.get("GROQ_MODEL_ID", "llama-3.3-70b-versatile")

# Groq's hosted Llama models occasionally emit a malformed tool call
# (wrapping JSON in a nonstandard <function=...> tag), which Groq's
# server-side parser rejects with a 400 tool_use_failed error. This is
# known, intermittent, non-deterministic model behavior — not a bug in
# our code. Observed failure rate in casual testing: roughly 2 in 3
# requests. A short retry loop resolves it in practice, since the same
# prompt often succeeds on a subsequent attempt.
#
# TEMPORARY: set to 1 to verify the 502 error path fires correctly when
# retries are exhausted. Revert to 3 once verified.
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1.0

if MAX_RETRY_ATTEMPTS < 1:
    raise ValueError("MAX_RETRY_ATTEMPTS must be at least 1")


def build_agent() -> Agent:
    """Construct a two-tool research agent.

    Returns:
        An Agno Agent configured with a Groq-hosted model, DuckDuckGo web
        search for qualitative news, and Yahoo Finance for quantitative
        market data. company_news is deliberately disabled on YFinanceTools
        to avoid overlapping with DuckDuckGoTools — this keeps tool
        selection meaningful rather than having two tools compete to
        answer the same kind of question.
    """
    return Agent(
        model=Groq(id=GROQ_MODEL_ID, api_key=GROQ_API_KEY),
        description=(
            "You are a financial research assistant. You answer questions "
            "using current, verifiable information rather than guessing, "
            "combining quantitative market data with qualitative news "
            "context where relevant."
        ),
        instructions=[
            "If a tool call fails or returns an error, explicitly tell the "
            "user that specific piece of information could not be "
            "retrieved. Do not substitute it with information from your "
            "own training data, and do not present anything as 'recent' "
            "or 'current' unless it came from a successful tool call in "
            "this conversation.",
            "Never fabricate URLs, article titles, or sources. Only cite "
            "sources that were actually returned by a tool call.",
        ],
        tools=[
            DuckDuckGoTools(),
            YFinanceTools(
                stock_price=True,
                company_info=True,
                analyst_recommendations=True,
            ),
        ],
        show_tool_calls=True,
        markdown=True,
    )


def run_query(agent: Agent, query: str) -> str:
    """Run a single query against an already-constructed agent.

    Retries up to MAX_RETRY_ATTEMPTS times if Groq raises a
    ModelProviderError (see module-level comment on tool_use_failed).
    Note: this retries on ANY ModelProviderError, not just the specific
    transient tool-calling failure — a genuinely permanent error (e.g.
    invalid API key) will also be retried uselessly before failing.
    Acceptable for now; refining this requires inspecting the error code
    inside the exception body, deferred until we have proper logging to
    justify and validate that refinement against real failure data.

    Args:
        agent: A pre-built Agent instance (see build_agent()). Passed in
            rather than constructed internally so callers control agent
            lifecycle.
        query: The user's natural-language question.

    Returns:
        The agent's final response as plain text (markdown-formatted).

    Raises:
        ModelProviderError: if all retry attempts are exhausted.
    """
    last_error: ModelProviderError | None = None

    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        try:
            response = agent.run(query)
            return response.content
        except ModelProviderError as e:
            last_error = e
            if attempt < MAX_RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)

    # All attempts exhausted — re-raise the last error so the caller
    # (e.g. the FastAPI route) can decide how to surface it.
    assert last_error is not None
    raise last_error
