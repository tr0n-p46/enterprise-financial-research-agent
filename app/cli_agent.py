"""
CLI entry point for the Enterprise Financial Research Agent.

Thin by design — all agent logic lives in app/services/research_agent.py.
This script's only job is to build an agent, run one query, and print
the result. Presentation concerns (printing) stay here; business logic
(agent construction, query execution) stays in the service layer.
"""

from app.services.research_agent import build_agent, run_query

if __name__ == "__main__":
    agent = build_agent()
    result = run_query(
        agent,
        "What's Nvidia's current stock price and analyst sentiment, "
        "and what recent news might be driving it?",
    )
    print(result)
