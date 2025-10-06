from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.api.routes import cases
from app.utils.exceptions import JagritiAPIException
from app.services.cache_service import cache
from app.utils.logging_config import logger
import logging
import time

# Get settings
settings = get_settings()

# Application logger
app_logger = logging.getLogger("app.main")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API wrapper for Jagriti Consumer Courts portal",
    docs_url="/docs",
    redoc_url="/redoc"
)

app_logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
app_logger.info(f"📊 Debug mode: {settings.DEBUG}")
app_logger.info(f"🌐 Jagriti API base URL: {settings.JAGRITI_BASE_URL}")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    app_logger.info(f"📥 {request.method} {request.url.path} - Client: {client_ip}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    app_logger.info(f"📤 {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.3f}s")
    
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app_logger.info("🔧 CORS middleware configured")


@app.exception_handler(JagritiAPIException)
async def jagriti_exception_handler(request: Request, exc: JagritiAPIException):
    """Handle Jagriti API exceptions"""
    app_logger.error(f"🚨 Jagriti API Exception: {exc.message} - Status: {exc.status_code} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error": str(exc)
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    app_logger.error(f"💥 Unhandled Exception: {str(exc)} - Path: {request.url.path}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


app.include_router(cases.router)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "message": "Jagriti API Wrapper",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "cache_stats": cache.get_stats()
    }


@app.post("/admin/cache/clear", tags=["Admin"])
async def clear_cache():
    """Clear all caches (admin endpoint)"""
    cache.clear_all()
    return {
        "success": True,
        "message": "All caches cleared"
    }


@app.get("/admin/cache/stats", tags=["Admin"])
async def get_cache_stats():
    """Get cache statistics"""
    return cache.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )