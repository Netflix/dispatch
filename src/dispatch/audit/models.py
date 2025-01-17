from typing import Any, Optional

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from dispatch.auth.models import DispatchUser
from dispatch.database.base import Base
from sqlalchemy.dialects.postgresql import JSONB
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey


class Audit(TimeStampMixin, Base):
    # Columns
    id = Column(Integer, primary_key=True)
    record_id = Column(Integer, nullable=True)
    table_name = Column(String, nullable=True)
    changed_data = Column(JSONB, default={}, nullable=False, server_default="{}")
    # Relationships
    dispatch_user_id = Column(Integer, ForeignKey("dispatch_core.dispatch_user.id"), nullable=True)
    dispatch_user = relationship(
        "DispatchUser", back_populates="audits", foreign_keys=[dispatch_user_id], post_update=True
    )


# Pydantic models
class AuditBase(DispatchBase):
    record_id: int
    table_name: Optional[str]
    changed_data: Optional[dict[str, Any]] = {}


class AuditCreate(AuditBase):
    dispatch_user: Optional[DispatchUser]


class AuditBaseUpdate(AuditBase):
    dispatch_user = Optional[DispatchUser]


class AuditRead(AuditBase):
    id: PrimaryKey
    dispatch_user = Optional[DispatchUser]
