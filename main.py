from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.posts import router as posts_router
from app.routers.follow import router as follow_router
from app.routers.block import router as block_router
from app.routers.feed import router as feed_router
from app.routers.admin import router as admin_router
from app.routers.like import router as like_router


# ---- REMOVE OAuth2 Form ----
oauth2_scheme = None   # disables password login popup UI in Swagger


# ---- INIT DB ----
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Inkle Backend Assignment",
    description="Backend for Social Feed with Login, Posts, Likes, Follow, Block & Admin roles.",
    version="1.0.0"
)


# ---- CORS (Required for Hoppscotch / Web Apps) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- ROUTERS ----
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(follow_router)
app.include_router(block_router)
app.include_router(feed_router)
app.include_router(admin_router)
app.include_router(like_router)


# ---- CUSTOM SWAGGER AUTH (REAL BEARER INPUT) ----
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token (without 'Bearer')"
        }
    }

    # Apply BearerAuth to every secured route
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ---- ROOT CHECK ----
@app.get("/")
def home():
    return {
        "message": "Backend Running 🚀",
        "status": "OK",
        "docs": "/docs",
        "auth": "Use Bearer token in Swagger Authorize button"
    }
