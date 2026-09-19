import uvicorn
from fastapi import FastAPI
from app.routes import user
from app.routes import auth
from app.routes import rooms
from fastapi import APIRouter
from starlette.middleware.sessions import SessionMiddleware
import os
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.1.38:3000", "https://codeeye.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
api_router = APIRouter(prefix="/api") # API Router

# API Endpoints
api_router.include_router(auth.router)
api_router.include_router(user.router)
api_router.include_router(rooms.router)
app.add_middleware(SessionMiddleware, 
        secret_key=os.getenv("JWT_SECRET"),
        max_age=7 * 24 * 60 * 60, # cookie lives for 14 days
        same_site="none",           # CSRF protection
        https_only=True           # Set true in production
)

# Router Includes
app.include_router(api_router)

@app.on_event("startup")
async def startup():
    await init_db()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)