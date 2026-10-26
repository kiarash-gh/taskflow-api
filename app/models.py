from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Task(Base):
    __tablename__ = "tasks"
    
    __table_args__ = (
        CheckConstraint(
            "priority IN (1, 2, 3)",
            name="ck_tasks_priority",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    priority: Mapped[int] = mapped_column(
    Integer,
    default=3,
    server_default="3",
    nullable=False,
    )
    version: Mapped[int] = mapped_column(
    Integer,
    default=1,
    server_default="1",
    nullable=False,
    )