from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, advertisements, admin
from app.db.database import engine, Base
from app.core.config import settings

# Create database tables (using Alembic in production, this is for quick dev setup)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SafeAd AI Backend API",
    version="1.0.0"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the Streamlit origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(advertisements.router, prefix="/api/v1/advertisements", tags=["advertisements"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok", "message": "SafeAd Backend is running"}
