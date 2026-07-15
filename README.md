# Enterprise Financial Research Agent

A production-grade agentic AI system for financial research, built with Agno, Groq, FastAPI, 
and deployed via Docker/Kubernetes.

## Status
🚧 Under active development — built incrementally, milestone by milestone.

## Tech Stack
- Python 3.12
- Agno (agent framework)
- Groq (LLM inference)
- FastAPI (API layer)
- Docker / Kubernetes (deployment)

## Setup
See `.env.example` for required environment variables.

\`\`\`bash
pyenv local 3.12.8
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # then fill in your GROQ_API_KEY
\`\`\`

## Development Log
- **Milestone 0**: Project bootstrap — repo structure, dependency management, environment config.
## Known Issues / Design Notes

- **DuckDuckGo search reliability**: `agno.tools.duckduckgo.DuckDuckGoTools` (Agno 1.7.7) 
  wraps the `duckduckgo_search` package, which is an unofficial scraper against 
  duckduckgo.com — there is no official free DuckDuckGo search API. This means:
  - No API key required (good for a portfolio project — zero setup friction)
  - No SLA and no rate-limit guarantees; `403 Ratelimit` errors are expected 
    under repeated/rapid querying and typically self-resolve within a few minutes
  - `duckduckgo_search` (the package Agno imports) has been superseded by `ddgs` 
    upstream, but as of Agno 1.7.7 the import is still hardcoded to the old 
    package name; `ddgs` is pinned in `requirements.txt` as a transitive 
    dependency in preparation for a future Agno upgrade
  - **Future consideration**: if this project needs reliable search in a 
    production context, evaluate a keyed provider (Tavily, Serper, Brave 
    Search API) as a replacement tool. Deferred for now — out of scope until 
    we have a concrete reliability requirement driving it.

- **Partial tool failure handling**: observed that when one tool call fails 
  mid-response (e.g., DuckDuckGo rate limit) while others succeed, the agent 
  reports the partial failure honestly rather than hallucinating a substitute 
  answer. This is model behavior, not something we've engineered — not 
  guaranteed to happen consistently, but a positive signal about the 
  underlying model's reliability under partial context.

- **Hallucination on tool failure (fixed)**: initial testing revealed that 
  when a tool call failed (e.g., DuckDuckGo rate limit), the model would 
  sometimes fabricate plausible-looking news articles and URLs from its 
  training data instead of reporting the failure — a serious correctness 
  risk for a research agent. Mitigated via explicit `instructions` on the 
  Agent telling it to report tool failures honestly and never fabricate 
  sources. Validated against a real rate-limit failure; behavior now 
  reports the failure correctly. Note: this is a probabilistic mitigation 
  (prompt-level), not a hard guarantee — a more robust fix (programmatically 
  detecting failed tool calls before allowing final response synthesis) is 
  deferred to a future hardening milestone.

- **Groq tool-calling retry logic**: observed a ~66% failure rate on 
  tool-calling requests due to Groq's `tool_use_failed` error (see earlier 
  entries). Since this now affects a real HTTP API (not just a CLI script 
  a developer can manually retry), `run_query()` implements a 3-attempt 
  retry loop with a 1-second delay. This retries on any `ModelProviderError`, 
  not just the specific transient failure — a genuinely permanent error 
  (e.g. bad API key) would also be retried uselessly. Refining this to 
  distinguish transient vs. permanent errors is deferred to a future 
  observability/hardening milestone, once real production logging exists 
  to validate the refinement against actual failure data.
- **Error surfacing**: unhandled `ModelProviderError`s are caught by a 
  global FastAPI exception handler and returned as a structured `502 Bad 
  Gateway` response (not the default opaque `500`), since the failure 
  originates from an upstream provider, not our own code. Verified by 
  temporarily forcing `MAX_RETRY_ATTEMPTS=1` to reliably trigger the 
  failure path — confirmed correct status code and response body before 
  reverting to the production setting of 3.
