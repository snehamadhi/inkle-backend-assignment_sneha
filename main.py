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


# OAuth system (Swagger expects tokenUrl WITHOUT slash)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Inkle Backend Assignment",
    description="Backend for Social Feed with authentication, posts, follows, blocks, likes, and admin roles.",
    version="1.0.0"
)

# ---- CORS FIX -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- ROUTERS -----
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(follow_router)
app.include_router(block_router)
app.include_router(feed_router)
app.include_router(admin_router)
app.include_router(like_router)


# ---- CUSTOM SWAGGER WITH GLOBAL TOKEN SUPPORT ----
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
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/")
def home():
    return {"status": "running", "message": "Welcome to the API 🚀"}
