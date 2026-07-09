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