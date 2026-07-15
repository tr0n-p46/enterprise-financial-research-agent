"""
Research agent service.

Owns agent construction and query execution. Deliberately has no
knowledge of *how* it's being called — CLI, HTTP route, or test —
so the same logic can be reused across all three without duplication.
"""

import os

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL_ID = os.environ.get("GROQ_MODEL_ID", "llama-3.3-70b-versatile")


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

    Args:
        agent: A pre-built Agent instance (see build_agent()). Passed in
            rather than constructed internally so callers control agent
            lifecycle — e.g., a long-running server builds one agent once
            and reuses it across many requests, rather than paying
            construction cost per query.
        query: The user's natural-language question.

    Returns:
        The agent's final response as plain text (markdown-formatted).
        Callers decide what to do with it — print it, wrap it in a JSON
        response, log it, etc. This function does not print or stream;
        that's presentation concern, not service concern.
    """
    response = agent.run(query)
    return response.content
