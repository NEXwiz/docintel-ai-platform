from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base
from app.models import user,document
from app.api import users, documents
from app.api import auth
from app.api import search
from app.api import qa

app = FastAPI(title="Docintel-AI-Platform")
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = False,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(documents.router)
app.include_router(auth.router)
app.include_router(search.router)
app.include_router(qa.router)

@app.get("/health")
def health_check():
    return{"status":"ok"}