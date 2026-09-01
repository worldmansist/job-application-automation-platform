from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Job Application Automation Platform",
)

app.include_router(health_router)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "environment": settings.environment,
    }
