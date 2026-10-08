import sys
import os

# Ensure project root is in Python module search path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.database import engine, Base
from backend.app.api.v1 import auth, age, advertisements, moderation, admin

# Auto-create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SafeAd AI (SAFE-VISION) Multimodal Trust & Safety Backend API",
    version="2.0.0",
    openapi_url="/openapi.json"
)

@app.on_event("startup")
def on_startup():
    from backend.app.db.database import SessionLocal
    from backend.app.api.v1.auth import seed_demo_users
    db = SessionLocal()
    try:
        seed_demo_users(db)
    finally:
        db.close()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API V1 Router Registrations
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(age.router, prefix=f"{settings.API_V1_STR}/age", tags=["Age Verification"])
app.include_router(advertisements.router, prefix=f"{settings.API_V1_STR}/advertisements", tags=["Advertisements"])
app.include_router(moderation.router, prefix=f"{settings.API_V1_STR}/moderation", tags=["Moderation & Audit"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin Control"])

# Direct Logical API Endpoint Aliases for standard integration
app.include_router(moderation.router, prefix="/api", tags=["Direct Moderation API"])

@app.get("/api/health", tags=["System"])
@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint returning system status and DB type."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "database": settings.DATABASE_URL.split("://")[0]
    }
