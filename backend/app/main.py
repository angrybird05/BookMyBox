"""
BookMyBox Backend Main Application Entrypoint.
Initializes FastAPI, configures middlewares, registers global exception handlers, and sets up routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.logging import configure_logging, get_logger
from app.core.responses import error_response, success_response
from app.database.redis import close_redis_pool, init_redis_pool
from app.middleware.logging import LoggingMiddleware
from app.middleware.request_id import RequestIdMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.api.v1.router import api_router


settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events for FastAPI application."""
    # Startup
    configure_logging()
    logger.info("application_startup", version=settings.APP_VERSION, env=settings.ENVIRONMENT)
    await init_redis_pool()
    yield
    # Shutdown
    logger.info("application_shutdown")
    await close_redis_pool()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

# ─── Middlewares ───
# NOTE: FastAPI/Starlette executes middlewares in REVERSE registration order.
# The last registered middleware runs FIRST (outermost layer).
# CORS must be outermost so it can attach Access-Control headers even when
# inner middlewares (rate limit, auth) return error responses.

# 5. Security Headers (innermost — runs last)
app.add_middleware(SecurityHeadersMiddleware)

# 3. Rate Limiting (Redis-backed)
app.add_middleware(RateLimitMiddleware)

# 2. Logging
app.add_middleware(LoggingMiddleware)

# 1. Request ID
app.add_middleware(RequestIdMiddleware)

# 4. CORS (outermost — registered last, runs first)
# This ensures CORS headers are always present, even on error responses.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ─── Exception Handlers ───


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.message,
            errors=exc.errors,
            request_id=request_id,
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI/Pydantic validation errors and format them to standard format."""
    request_id = getattr(request.state, "request_id", None)
    errors = []
    for error in exc.errors():
        # Clean up path formatting for response
        loc = ".".join(str(p) for p in error["loc"] if p != "body")
        errors.append({
            "field": loc,
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            message="Validation failed",
            errors=errors,
            request_id=request_id,
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTPExceptions (e.g. 404 Not Found, 405 Method Not Allowed)."""
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            message=exc.detail,
            request_id=request_id,
        ),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unhandled exceptions."""
    request_id = getattr(request.state, "request_id", None)
    logger.exception("unhandled_exception", error=str(exc), request_id=request_id)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            message="Internal server error",
            request_id=request_id,
        ),
    )


# ─── Routers ───
app.include_router(api_router, prefix=settings.API_PREFIX)


# ─── Base Routes ───



@app.get("/health", tags=["Health"])
async def health_check(request: Request):
    """Basic health check endpoint."""
    request_id = getattr(request.state, "request_id", None)
    return success_response(
        data={"status": "healthy", "version": settings.APP_VERSION},
        message="System is healthy",
        request_id=request_id,
    )
