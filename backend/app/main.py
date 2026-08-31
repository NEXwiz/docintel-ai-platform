from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base
from app.models import user, document, chat_message
from app.api import users, documents
from app.api import auth
from app.api import search
from app.api import qa
from app.api import evaluate
from app.api import chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run table creation at startup; log warning if DB is unavailable."""
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables verified/created")
    except Exception as e:
        print(f"[WARNING] Database unavailable at startup: {e}")
        print("  The app will start, but DB-dependent endpoints will fail until the database is reachable.")
    yield


app = FastAPI(title="Docintel-AI-Platform", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(users.router)
app.include_router(documents.router)
app.include_router(auth.router)
app.include_router(search.router)
app.include_router(qa.router)
app.include_router(evaluate.router)
app.include_router(chat.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}