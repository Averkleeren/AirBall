from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routes.auth import router as auth_router
from .routes.videos import router as videos_router
from . import models

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AirBall API",
    description="Backend API for AirBall application",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(videos_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}