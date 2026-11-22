from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from poc_studio.routes import health, runs

app = FastAPI(title="PoC Studio API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")
api.include_router(health.router)
api.include_router(runs.router)
app.include_router(api)
