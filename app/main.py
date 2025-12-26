from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.config import settings
from app.database.graph import get_db, close_db
from app.routes import data, intelligence, system

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Ranchi Synapsters Intelligence Engine...")
    try:
        db = get_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    close_db()
    logger.info("✓ Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Ranchi Synapsters",
    description="🧠 Cybercrime Network Intelligence Engine | Law Enforcement Ready",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(system.router)
app.include_router(data.router)
app.include_router(intelligence.router)

@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "name": "Ranchi Synapsters",
        "description": "Cybercrime Network Intelligence Engine",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/api/v1/system/health",
            "graph_stats": "/api/v1/system/graph/stats",
            "graph_snapshot": "/api/v1/intelligence/graph",
            "upload_data": "/api/v1/data/upload",
            "fraud_rings": "/api/v1/intelligence/clusters",
            "kingpins": "/api/v1/intelligence/kingpins",
            "timeline": "/api/v1/intelligence/timeline/{entity_id}",
            "risk": "/api/v1/intelligence/risk/{entity_id}",
            "anomalies": "/api/v1/intelligence/anomalies/{entity_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.fastapi_host,
        port=settings.fastapi_port,
        reload=settings.debug
    )
