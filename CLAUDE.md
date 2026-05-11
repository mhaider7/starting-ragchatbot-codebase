# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the application

Requires a `.env` file in the project root with `ANTHROPIC_API_KEY=...`.

```bash
uv sync          # install dependencies
./run.sh         # start server on port 8000
```

Or manually:
```bash
cd backend && uv run uvicorn app:app --reload --port 8000
```

The frontend is served as static files by FastAPI — open `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

## Architecture

Full-stack RAG app. FastAPI backend serves both the API and the static frontend. No build step for the frontend (plain HTML/CSS/JS).

### Query pipeline

Every user message follows this path:

1. **Frontend** (`frontend/script.js`) — POSTs `{ query, session_id }` to `/api/query`
2. **`app.py`** — creates a session if needed, delegates to `RAGSystem.query()`
3. **`rag_system.py`** — wraps the query, fetches conversation history, calls `AIGenerator`
4. **`ai_generator.py`** — makes a first Claude API call with the `search_course_content` tool available; if Claude calls the tool, executes it and makes a second call to synthesize the final answer
5. **`search_tools.py` → `vector_store.py`** — tool execution: optionally resolves a fuzzy course name via `course_catalog` collection, then semantic-searches `course_content` collection in ChromaDB
6. Sources and session history are updated; `{ answer, sources, session_id }` returned to the frontend

### Document ingestion

On startup, `app.py` loads all `.txt`/`.pdf`/`.docx` files from `../docs/`. Already-indexed courses (matched by title) are skipped.

`DocumentProcessor` expects this file format:
```
Course Title: ...
Course Link: ...
Course Instructor: ...

Lesson 0: Title
Lesson Link: ...
... content ...

Lesson 1: Title
...
```

Text is split into sentence-based chunks (800 chars, 100 overlap). Each chunk is stored in ChromaDB's `course_content` collection with `course_title` and `lesson_number` metadata for filtered search.

### ChromaDB collections

- `course_catalog` — one entry per course; used for fuzzy course name resolution via vector similarity
- `course_content` — one entry per chunk; queried at runtime to retrieve relevant passages

### Key configuration (`config.py`)

| Setting | Default |
|---|---|
| `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | 800 chars |
| `CHUNK_OVERLAP` | 100 chars |
| `MAX_RESULTS` | 5 chunks per search |
| `MAX_HISTORY` | 2 exchanges per session |
| `CHROMA_PATH` | `./chroma_db` (relative to `backend/`) |

### Adding a new tool

1. Subclass `Tool` in `search_tools.py`, implement `get_tool_definition()` and `execute()`
2. Register it: `tool_manager.register_tool(MyTool(...))`  in `rag_system.py`

The `ToolManager` handles passing definitions to Claude and routing `tool_use` responses back to the right tool.
