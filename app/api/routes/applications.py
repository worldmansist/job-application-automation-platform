from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate

router = APIRouter(prefix="/applications", tags=["applications"])

@router.get("")
def list_applications(db: Session = Depends(get_db)):
    return {"applications": db.scalars(select(Application).order_by(Application.id)).all()}


@router.get("/{application_id}")
def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.post("")
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    application = Application(**payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return {
        "message": "Application created",
        "application": application,
    }


@router.patch("/{application_id}")
def update_application(
    application_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)
):
    application = db.get(Application, application_id)
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(application, field, value)

    db.commit()
    db.refresh(application)
    return application
