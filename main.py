from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router as api_router
from core.database import engine, Base
from core.config import settings
from models.domain import Submission, ModelSuggestion  # noqa: F401 - register models
import logging

logger = logging.getLogger("llm_consensus_engine.main")

# Auto-create tables (in production use Alembic migrations)
logger.info("Creating database tables if they do not exist...")
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    description="AI-powered code improvement using multiple LLMs as judges.",
    version="1.0.0"
)

# CORS - allow dashboard and external requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Structured validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "type": "Validation Error",
            "title": "Your request parameters didn't validate.",
            "detail": [str(e) for e in exc.errors()]
        }
    )


app.include_router(api_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok", "project": settings.project_name}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
