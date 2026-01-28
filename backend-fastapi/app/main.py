"""
Fotolibros Argentina - Backend FastAPI
Entry point principal (SQLite, sin Redis)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.routers import pedidos, webhooks
from app.db import init_database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Iniciando Fotolibros Argentina Backend...")
    init_database()
    logger.info("✅ SQLite conectado")
    yield
    logger.info("👋 Cerrando backend...")


app = FastAPI(
    title="Fotolibros Argentina API",
    description="Sistema automatizado de creación de fotolibros artísticos",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pedidos.router, prefix="/api/pedidos", tags=["Pedidos"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["Webhooks"])


@app.get("/")
async def root():
    return {"status": "ok", "service": "Fotolibros Argentina", "version": "1.0.0"}


@app.get("/health")
async def health():
    from app.db import get_queue_stats
    stats = get_queue_stats()
    return {"status": "healthy", "database": "sqlite", "queue": stats, "clawdbot_url": settings.CLAWDBOT_URL}
