from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from database import SessionLocal, engine, Base
from models import User, StyleDNA, Outfit, Recommendation, TryOnHistory
from routers import auth, style_dna, catalog, recommendations, tryon, users
from ml.pipeline import MLPipeline

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Avaire API",
    description="Fashion AI platform with personalized recommendations and virtual try-on",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for storage
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize ML Pipeline
ml_pipeline = MLPipeline()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(style_dna.router, prefix="/api", tags=["Style DNA"])
app.include_router(catalog.router, prefix="/api", tags=["Catalog"])
app.include_router(recommendations.router, prefix="/api", tags=["Recommendations"])
app.include_router(tryon.router, prefix="/api", tags=["Virtual Try-On"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Avaire Fashion AI Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "ml_pipeline": "initialized" if ml_pipeline else "not_initialized"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )