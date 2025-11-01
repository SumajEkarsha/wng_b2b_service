from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
from app.api.v1 import api_router

app = FastAPI(
    title="School Mental Health Platform API",
    description="B2B SaaS platform for K-12 school mental health management",
    version="1.0.0",
    redirect_slashes=False
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Gzip Compression Middleware - compress responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "School Mental Health Platform API", "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
