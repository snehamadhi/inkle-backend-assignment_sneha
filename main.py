from fastapi import FastAPI
from app.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.posts import router as posts_router
from app.routers.follow import router as follow_router
from app.routers.block import router as block_router
from app.routers.feed import router as feed_router
from app.routers.admin import router as admin_router
from app.routers.like import router as like_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inkle Backend Assignment")

app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(follow_router)
app.include_router(block_router)
app.include_router(feed_router)
app.include_router(admin_router)
app.include_router(like_router)





@app.get("/")
def home():
    return {"status": "running", "message": "Welcome to the API 🚀"}

