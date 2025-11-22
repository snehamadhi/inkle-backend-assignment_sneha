from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
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


# Swagger authentication configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Create DB tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Inkle Backend Assignment API",
    description="Full social activity backend including auth, feeds, follows, likes, admin access, and more.",
    version="1.0.0"
)


# ---------------------- CORS FIX ----------------------
# Allows external tools like Hoppscotch, Swagger & frontend apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all origins
    allow_credentials=True,
    allow_methods=["*"],        # allow GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],        # allow Authorization, Content-Type, etc.
)
# -------------------------------------------------------


# ---------------------- ROUTERS ------------------------
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(follow_router)
app.include_router(block_router)
app.include_router(feed_router)
app.include_router(admin_router)
app.include_router(like_router)
# -------------------------------------------------------


# Custom Swagger UI so Bearer token input works properly
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Inkle Backend Assignment",
        version="1.0.0",
        description="API documentation for the full backend system.",
        routes=app.routes,
    )

    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply security to all paths automatically
    for path in schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi


@app.get("/")
def home():
    return {
        "status": "running",
        "message": "🚀 Backend deployed successfully! Use /docs for API playground."
    }
