from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from routers.chat import router as chat_router
from routers.users import router as users_router
from routers.character import router as character_router
from routers.conversations import router as conversations_router
from routers.conversation_character_summary import (router as conversation_character_summary_router)
from routers.character_summary import router as character_summary_router
from routers.short_term_memory import router as short_term_memory_router
from routers.long_term_memory import router as long_term_memory_router
from routers.message import router as message_router
from routers.uploads import router as uploads_router
from auth.router import router as auth_router
app = FastAPI()

app.include_router(users_router)
app.include_router(character_router)
app.include_router(conversations_router)
app.include_router(character_summary_router)
app.include_router(conversation_character_summary_router)
app.include_router(short_term_memory_router)
app.include_router(long_term_memory_router)
app.include_router(message_router)
app.include_router(uploads_router)
app.include_router(auth_router)
app.include_router(chat_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    return FileResponse("static/index.html")