# Research Agent — Multi-Agent System with Persistent Memory

A multi-agent research assistant built with [Google ADK](https://google.github.io/adk-docs/) that searches the web, synthesizes findings, fact-checks results, and persists research history to a local SQLite database.

## Architecture

The system uses four coordinated agents managed by an orchestrator:

```
User Query
    │
    ▼
ManagerAgent (orchestrator)
    ├── SearchAgent       — web search via SerpApi / DuckDuckGo
    ├── SynthesizerAgent  — combines results into a cohesive draft
    └── FactCheckerAgent  — validates claims against sources
    │
    ▼
save_research → SQLite (research_data.db)
```

The `ManagerAgent` breaks user prompts into sub-questions, delegates to sub-agents, and stores the final output in session state via `save_research`. All session data is persisted to SQLite through `DatabaseSessionService`.

## Project Structure

```
agents/
├── agent.py       # Agent definitions (SearchAgent, SynthesizerAgent, FactCheckerAgent, ManagerAgent)
├── tools.py       # State tools: save_research, view_research_history
├── utils.py       # Async helpers: display_state, process_agent_response, call_agent_async
└── __init__.py
agents_main.py     # Runner entry point with interactive CLI loop
```

## Prerequisites

- Python 3.12+
- A Google Gemini API key
- A SerpApi API key

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables in `.env`:

```
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your_gemini_api_key
SERPAPI_KEY=your_serpapi_key
```

## Usage

```bash
python3 agents_main.py
```

This starts an interactive CLI session. Type your research query and the agent team will search, synthesize, and fact-check the results. Type `exit` or `quit` to end.

### Example

```
You: What are the latest developments in quantum computing?
```

The agent will:
1. Break the topic into sub-questions
2. Search the web for each sub-question
3. Synthesize the findings into a cohesive summary
4. Fact-check the draft against original sources
5. Return the final output and save it to session state

### Viewing Past Research

Ask the agent to recall previous research:

```
You: What have I researched before?
```

## Persistent Storage

Session state (including research history) is stored in `research_data.db` via SQLAlchemy's async SQLite driver (`aiosqlite`). Sessions survive across restarts — when you run the script again, it resumes your existing session automatically.

### Session State Schema

| Key                | Type   | Description                              |
|--------------------|--------|------------------------------------------|
| `user_name`        | string | Display name for the user                |
| `research_history` | list   | Array of `{topic, results}` entries      |

## State Tools

| Tool                     | Description                                      |
|--------------------------|--------------------------------------------------|
| `save_research`          | Saves a topic and its results to session state   |
| `view_research_history`  | Returns all past research entries from state      |
