"""Research endpoint router."""

from fastapi import APIRouter

from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.research_agent import build_agent, run_query

router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchResponse)
def create_research(request: ResearchRequest) -> ResearchResponse:
    """Answer a financial research question using the Agno agent.

    Declared as a plain `def` (not `async def`) deliberately: `run_query`
    calls Agno's synchronous `agent.run()`, which performs blocking HTTP
    calls under the hood. A sync route lets Starlette offload this to its
    thread pool automatically, keeping the event loop free for other
    requests. Declaring this `async def` while calling a blocking function
    inside it would freeze the event loop for every concurrent request.

    Builds a fresh Agent per request rather than reusing a shared instance.
    Agno's Agent has documented thread-safety issues under concurrent reuse
    (see README's Known Issues section) — agent construction itself is
    cheap (no network call happens until .run()), so the safety margin is
    worth the small, likely-negligible overhead.
    """
    agent = build_agent()
    answer = run_query(agent, request.query)
    return ResearchResponse(answer=answer)
