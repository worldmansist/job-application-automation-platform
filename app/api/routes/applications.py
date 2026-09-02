from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.application import ApplicationCreate, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])

applications: list[dict[str, Any]] = []


@router.get("")
async def list_applications():
    return {"applications": applications}


@router.get("/{application_id}")
async def get_application(application_id: int):
    for application in applications:
        if application["id"] == application_id:
            return application
    raise HTTPException(status_code=404, detail="Application not found")


@router.post("")
async def create_application(payload: ApplicationCreate):
    new_id = len(applications) + 1
    now = datetime.now(timezone.utc).isoformat()
    application = {
        "id": new_id,
        "company": payload.company,
        "position": payload.position,
        "url": payload.url,
        "description": payload.description,
        "status": payload.status,
        "source": payload.source,
        "created_at": now,
        "updated_at": now,
    }
    applications.append(application)
    return {
        "message": "Application created",
        "application": application,
    }


@router.patch("/{application_id}")
async def update_application(application_id: int, payload: ApplicationUpdate):
    for application in applications:
        if application["id"] == application_id:
            for field, value in payload.model_dump(exclude_unset=True).items():
                if value is not None:
                    application[field] = value

            application["updated_at"] = datetime.now(timezone.utc).isoformat()
            return application

    raise HTTPException(status_code=404, detail="Application not found")
