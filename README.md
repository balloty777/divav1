# DivaV1

DivaV1 is a FastAPI-powered character-chat application built for immersive, persistent conversations. Create a character from a natural-language description, talk to them in a browser, and let the app retain both the recent scene and longer-term story details.

The project combines a lightweight static frontend, PostgreSQL persistence, LangGraph orchestration, and OpenRouter-compatible language models.
<img width="1917" height="972" alt="image" src="https://github.com/user-attachments/assets/021c5908-5802-481d-8f51-7326d14691ca" />
<img width="1917" height="975" alt="image" src="https://github.com/user-attachments/assets/4e71dd76-4082-4083-ad3f-4f587fe0ff92" />
<img width="683" height="756" alt="image" src="https://github.com/user-attachments/assets/9a091cc0-f391-43e6-8576-87291071aa9d" />
<img width="1917" height="973" alt="image" src="https://github.com/user-attachments/assets/0369e31a-fc34-4d9c-8cb5-f659a926fecb" />




## Features

- Character creation from a free-form summary
- Persistent conversations and message history
- Role-preserved context: user messages and character replies stay distinct
- Short-term memory for the current scene
- Long-term memory for durable facts, relationships, and story events
- Streaming chat responses using Server-Sent Events (SSE)
- JWT-based authentication
- Browser frontend served directly by FastAPI
- Responsive chat interface with a fixed sidebar and independently scrollable conversation area

## Architecture

```text
Browser frontend (static/)
        |
        v
FastAPI routes
        |
        v
LangGraph conversation workflow
  loader -> chat -> save messages -> STM -> LTM
        |
        v
PostgreSQL + OpenRouter-compatible model API
```

### Conversation workflow

1. The frontend sends a user message to `POST /conversations/{conversation_id}/chat`.
2. The graph loads the character profile, saved messages, short-term memory, and long-term memory.
3. The chat node sends the model the character identity plus recent messages with their real roles.
4. The reply streams back to the browser and is stored with the user message.
5. Short-term memory is refreshed periodically from recent exchanges.
6. Long-term memory is refreshed less often from durable conversation facts.

Memory updates are best-effort: if a roleplay model returns malformed structured output, the conversation response is still saved and the last valid memory remains in place.

## Project structure

```text
.
├── auth/                 # JWT authentication and password handling
├── character/            # Character-summary extraction schema
├── database/             # SQLAlchemy engine and request dependencies
├── graph/                # LangGraph workflow and nodes
├── memory/               # STM/LTM schemas, parsing, and update helpers
├── migrations/           # Alembic database migrations
├── models/               # SQLAlchemy database models
├── prompts/              # Character, memory, and roleplay prompt construction
├── repositories/         # Database access layer
├── routers/              # FastAPI endpoints
├── schemas/              # Request/response validation models
├── services/             # Application business logic
├── static/               # HTML, CSS, and browser JavaScript frontend
├── main.py               # FastAPI application entry point
└── alembic.ini           # Alembic configuration
```

## Requirements

- Python 3.11+
- PostgreSQL 15+ recommended
- An OpenRouter-compatible API key

Install the Python packages:

```powershell
pip install -r requirements.txt
```

If `requirements.txt` has not been created yet, use:

```txt
fastapi
uvicorn[standard]
sqlalchemy
psycopg[binary]
alembic
python-dotenv
pydantic
PyJWT
pwdlib[argon2]
langchain-core
langchain-openai
langgraph
```

## Configuration

Create a local `.env` file. Never commit it.

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/roleplay_db
OPENROUTER_API_KEY=your_openrouter_key
JWT_SECRET_KEY=use_a_random_value_of_at_least_32_bytes

# Optional LangSmith tracing
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=mygpt-roleplay
```

Generate a JWT secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

For local development, the application can generate a temporary JWT key when one is absent. Set `JWT_SECRET_KEY` for persistent sessions and any deployment.

## Database setup

Create a PostgreSQL database, update `DATABASE_URL`, then apply migrations:

```powershell
alembic upgrade head
```

To create a migration after changing SQLAlchemy models:

```powershell
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

## Run locally

Start the development server from the project root:

```powershell
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000).

## Using the app

1. Create an account or sign in.
2. Choose **Create new chat**.
3. Enter a character name and a detailed character summary.
4. Start the conversation.

Good character summaries include personality, background, speaking style, motivations, likes, dislikes, appearance, and relationship expectations. The richer and more internally consistent the summary, the stronger the roleplay.

## Memory model

### Short-term memory

Short-term memory represents the current scene: recent events, emotional tone, active topics, current location, goals, and unresolved threads. It is refreshed after every two complete exchanges to avoid wasting requests on greetings and minor messages.

### Long-term memory

Long-term memory stores information that should survive a long conversation: names, stable preferences, relationships, world facts, important events, locations, and established boundaries. It is refreshed every ten exchanges using a compact recent-history window plus the prior durable summary.

The actual role-labelled conversation always takes priority over memory if there is a conflict.

## Roleplay behavior

The prompt system directs each character to stay in-scene rather than respond as an assistant. Characters should react naturally, share opinions, take initiative, ask specific questions, and help advance the story. The system preserves user agency: characters do not decide the user's actions, thoughts, or consent.

## API overview

| Area | Example endpoints |
| --- | --- |
| Authentication | `POST /auth/login` |
| Users | `POST /users/` |
| Characters | `POST /characters/from-summary` |
| Conversations | `GET /conversations/`, `POST /conversations/` |
| Messages | `GET /conversations/{id}/messages/` |
| Streaming chat | `POST /conversations/{id}/chat` |

The streaming chat endpoint returns SSE events with `token`, `done`, or `error` payloads.

## Security checklist

- Keep `.env` out of Git.
- Use a unique, random `JWT_SECRET_KEY` of at least 32 bytes.
- Rotate any key that has been accidentally shared or committed.
- Use a dedicated PostgreSQL account with a strong password outside local development.
- Set restrictive CORS and HTTPS before deploying publicly.

## Git hygiene

Add a `.gitignore` before the first push:

```gitignore
.env
.env.*
!.env.example

.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
*.log
```
