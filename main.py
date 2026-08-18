import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.logging_config import logger
from backend.app.api.endpoints import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} Backend API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Persistent Storage: {settings.DATA_DIR}")
    logger.info(f"Vector Collection Persist Dir: {settings.CHROMA_PERSIST_DIR}")
    logger.info("=" * 60)
    yield
    logger.info("Shutting down RAG Enterprise Assistant API server.")


app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade RAG-based AI Enterprise Assistant API with exact source citations and persistent vector database.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logs HTTP request duration and status code."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.3f}s")
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled Exception at {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred.", "error_message": str(exc)}
    )


# Mount API Router
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
