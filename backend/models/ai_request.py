"""AI request history — tracks explain, summary, compare, roadmap, and RAG usage."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.user import User


class AIRequest(Base):
    """Record of an AI feature invocation by a user."""

    __tablename__ = "ai_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    request_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    repo_identifier: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    user_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_mode: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="ai_requests")

    def __repr__(self) -> str:
        return f"<AIRequest type={self.request_type!r}>"
