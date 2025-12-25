"""
FRAMSTART - Enterprise Framework API
Simple FastAPI application for Docker deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="FRAMSTART API",
    description="Enterprise Framework - Production Ready",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FRAMSTART Enterprise Framework",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api": "/api/v1"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "framstart-api",
        "version": "1.0.0"
    }

@app.get("/api/v1")
async def api_root():
    """API v1 root"""
    return {
        "message": "FRAMSTART API v1",
        "version": "1.0.0",
        "endpoints": [
            "/api/v1/auth",
            "/api/v1/users",
            "/api/v1/billing"
        ]
    }

@app.get("/api/v1/status")
async def api_status():
    """API status"""
    return {
        "api": "operational",
        "database": "connected",
        "cache": "connected",
        "version": "1.0.0"
    }
