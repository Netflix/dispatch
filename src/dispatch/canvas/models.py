"""Models and schemas for the Dispatch canvas management system."""

from datetime import datetime
from typing import Optional
from pydantic import Field
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from dispatch.database.core import Base
from dispatch.models import DispatchBase, PrimaryKey, ProjectMixin, TimeStampMixin


class Canvas(Base, TimeStampMixin, ProjectMixin):
    """SQLAlchemy model for a Canvas, representing a Slack canvas in the system."""

    id = Column(Integer, primary_key=True)
    canvas_id = Column(String, nullable=False)  # Slack canvas ID
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"), nullable=True)
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"), nullable=True)
    type = Column(String, nullable=False)  # CanvasType enum value

    # Relationships
    incident = relationship("Incident", back_populates="canvases")
    case = relationship("Case", back_populates="canvases")


# Pydantic models...
class CanvasBase(DispatchBase):
    """Base Pydantic model for canvas-related fields."""

    canvas_id: str = Field(..., description="The Slack canvas ID")
    incident_id: Optional[int] = Field(None, description="The associated incident ID")
    case_id: Optional[int] = Field(None, description="The associated case ID")
    type: str = Field(..., description="The type of canvas")


class CanvasCreate(CanvasBase):
    """Pydantic model for creating a new canvas."""

    project_id: int = Field(..., description="The project ID")


class CanvasUpdate(CanvasBase):
    """Pydantic model for updating an existing canvas."""

    pass


class CanvasRead(CanvasBase):
    """Pydantic model for reading canvas data."""

    id: PrimaryKey
    created_at: datetime
    updated_at: datetime
    project_id: int
