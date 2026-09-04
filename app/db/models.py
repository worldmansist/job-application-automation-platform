from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Application(Base):
	__tablename__ = "applications"

	id: Mapped[int] = mapped_column(primary_key=True)
	company: Mapped[str] = mapped_column(String(255))
	position: Mapped[str] = mapped_column(String(255))
	url: Mapped[str] = mapped_column(String(2048))
	description: Mapped[str] = mapped_column(Text)
	status: Mapped[str] = mapped_column(String(50), default="new")
	source: Mapped[str] = mapped_column(String(50), default="telegram")
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
	)
