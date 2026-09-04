from fastapi import FastAPI

from app.api.routes.applications import router as applications_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.db.database import init_db

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Job Application Automation Platform",
)

app.include_router(health_router)
app.include_router(applications_router)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "environment": settings.environment,
    }
