import base64
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import app.router.healthcheck as healthcheck
import app.router.organization as organization
import app.router.user as user

# import app.router.user_organization as user_organization
from app.config import settings
from app.router.error_handler import ErrorHandler

app = FastAPI(
    title="Product",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
)

app.add_middleware(ErrorHandler)


# Basic 認証の Middleware（/docs, /redoc, /openapi.json のみ適用）
@app.middleware("http")
async def basic_auth_middleware(request: Request, call_next: Any) -> Any:
    """
    /docs, /redoc, /openapi.json へのアクセス時に Basic 認証を要求する Middleware
    """
    if settings.SERVICE_ENV != "local" and request.url.path in [
        "/docs",
        "/redoc",
        "/openapi.json",
    ]:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Basic "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"},
                headers={"WWW-Authenticate": "Basic"},
            )

        # Basic 認証の検証
        try:
            decoded = base64.b64decode(auth.split(" ")[1]).decode("utf-8")
            username, password = decoded.split(":", 1)
            if (
                username != settings.BASIC_USERNAME
                or password != settings.BASIC_PASSWORD
            ):
                raise ValueError
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid credentials"},
                headers={"WWW-Authenticate": "Basic"},
            )

    response = await call_next(request)
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck.router, prefix="/health", tags=["health_check"])

app.include_router(
    organization.router, prefix="/api/organization", tags=["organization"]
)

app.include_router(user.router, prefix="/api/user", tags=["user"])

# app.include_router(
#     user_organization.router,
#     prefix="/api/user_organization",
#     tags=["user_organization"],
# )
