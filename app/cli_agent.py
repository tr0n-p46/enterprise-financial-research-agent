"""
Minimal CLI entry point for the Enterprise Financial Research Agent.

This is a deliberately thin, throwaway-quality script whose only purpose
is to prove the core Agno + Groq + tool-calling loop works end to end.
No architecture, no abstractions — that comes in later milestones once
this foundation is verified to actually function.
"""

import os

from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from dotenv import load_dotenv

# Load variables from .env into the process environment.
# Must happen before we read os.environ below.
load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GROQ_MODEL_ID = os.environ.get("GROQ_MODEL_ID", "llama-3.3-70b-versatile")


def build_agent() -> Agent:
    """Construct a two-tool research agent.

    Returns:
        An Agno Agent configured with a Groq-hosted model, DuckDuckGo web
        search for qualitative news, and Yahoo Finance for quantitative
        market data. company_news is deliberately disabled on YFinanceTools
        to avoid overlapping with DuckDuckGoTools — we want to observe the
        model choosing distinct tools for distinct question types, not two
        tools competing to answer the same thing.
    """
    return Agent(
        model=Groq(id=GROQ_MODEL_ID, api_key=GROQ_API_KEY),
        description=(
            "You are a financial research assistant. You answer questions "
            "using current, verifiable information rather than guessing, "
            "combining quantitative market data with qualitative news "
            "context where relevant."
        ),
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


if __name__ == "__main__":
    agent = build_agent()
    agent.print_response(
        "What's Nvidia's current stock price and analyst sentiment, "
        "and what recent news might be driving it?",
        stream=True,
    )