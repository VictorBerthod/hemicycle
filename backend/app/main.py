from fastapi import FastAPI

from app.database import init_db

app = FastAPI(title="Hemicycle API", version="0.1.0")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
