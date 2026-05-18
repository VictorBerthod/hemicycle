from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import deputes, ecarts, groupes, scrutins, search, stats, themes

app = FastAPI(title="Hemicycle API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(deputes.router)
app.include_router(scrutins.router)
app.include_router(groupes.router)
app.include_router(search.router)
app.include_router(stats.router)
app.include_router(ecarts.router)
app.include_router(themes.router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
