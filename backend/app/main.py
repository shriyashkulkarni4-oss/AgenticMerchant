"""
Main FastAPI Application for AgenticBuy.

Three-sided platform for merchant onboarding, autonomous negotiation,
and unified LLM agent shopping API powered by Gemma and Graphify.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.crawl import router as crawl_router
from app.api.graph import router as graph_router
from app.api.merchants import router as merchants_router
from app.api.negotiate import router as negotiate_router
from app.api.orders import router as orders_router
from app.api.products import router as products_router
from app.auth.router import router as auth_router
from app.config import get_settings
from app.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agenticbuy")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown hooks."""
    logger.info("Initializing AgenticBuy databases and tables...")
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.warning(
            f"Database initialization warning (will retry on incoming requests): {e}"
        )
    yield
    logger.info("Shutting down AgenticBuy.")


app = FastAPI(
    title="AgenticBuy API",
    description=(
        "Unified autonomous shopping & merchant platform. "
        "Allows merchants to ingest catalogs via crawling & Graphify, "
        "exposes a standardized API for external LLMs (Claude, GPT, etc.), "
        "and runs an open-weight Gemma agent for price negotiation and purchasing."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for merchant and user portals
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(merchants_router)
app.include_router(products_router)
app.include_router(negotiate_router)
app.include_router(orders_router)
app.include_router(crawl_router)
app.include_router(graph_router)
app.include_router(chat_router)


@app.get("/", tags=["system"])
async def root():
    """System information and links to documentation."""
    return {
        "service": "AgenticBuy Platform API",
        "version": "1.0.0",
        "status": "online",
        "documentation": "/docs",
        "gemma_model": settings.GEMMA_MODEL,
        "endpoints": {
            "auth": "/auth",
            "merchants": "/api/v1/merchants",
            "products": "/api/v1/products",
            "negotiate": "/api/v1/negotiate",
            "orders": "/api/v1/orders",
            "crawl": "/api/v1/crawl",
            "graph": "/api/v1/graph",
            "chat": "/api/v1/chat",
        },
    }


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for Docker / orchestration."""
    return {"status": "healthy", "service": "agenticbuy"}
