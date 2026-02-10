from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import email_checker, history, url_checker, website_scanner, password_checker
from app.db.database import Base, engine
from app.db import models  # noqa: F401

app = FastAPI(title="CyberGuardX")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(email_checker.router)
app.include_router(history.router)
app.include_router(url_checker.router)
app.include_router(website_scanner.router)
app.include_router(password_checker.router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"project": "CyberGuardX", "status": "running"}
