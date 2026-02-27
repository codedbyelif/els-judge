from fastapi import FastAPI
from api.routes import router as api_router
from core.database import engine, Base
from core.config import settings
import logging

logger = logging.getLogger("llm_consensus_engine.main")

# Auto-create tables (in production use Alembic migrations)
logger.info("Creating database tables if they do not exist...")
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    description="API for the LLM Consensus Engine",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.project_name}

if __name__ == "__main__":
    import uvicorn
    # Standalone run utility
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
