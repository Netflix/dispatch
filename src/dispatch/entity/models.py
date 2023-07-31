from typing import Optional, List
from pydantic import Field

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import (
    DispatchBase,
    TimeStampMixin,
    ProjectMixin,
    PrimaryKey,
    Pagination,
)
from dispatch.project.models import ProjectRead
from dispatch.entity_type.models import (
    EntityTypeCreate,
    EntityTypeRead,
    EntityTypeReadMinimal,
    EntityTypeUpdate,
)


class Entity(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    # Columns
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    value = Column(String)
    source = Column(String)

    # Relationships
    entity_type_id = Column(Integer, ForeignKey("entity_type.id"), nullable=False)
    entity_type = relationship("EntityType", backref="entity")

    # the catalog here is simple to help matching "named entities"
    search_vector = Column(
        TSVectorType(
            "name",
            "description",
            weights={"name": "A", "description": "B"},
            regconfig="pg_catalog.simple",
        )
    )


# Pydantic models
class EntityBase(DispatchBase):
    name: Optional[str] = Field(None, nullable=True)
    source: Optional[str] = Field(None, nullable=True)
    value: Optional[str] = Field(None, nullable=True)
    description: Optional[str] = Field(None, nullable=True)


class EntityCreate(EntityBase):
    def __hash__(self):
        return hash((self.id, self.value))

    id: Optional[PrimaryKey]
    entity_type: EntityTypeCreate
    project: ProjectRead


class EntityUpdate(EntityBase):
    id: Optional[PrimaryKey]
    entity_type: Optional[EntityTypeUpdate]


class EntityRead(EntityBase):
    id: PrimaryKey
    entity_type: Optional[EntityTypeRead]
    project: ProjectRead


class EntityReadMinimal(DispatchBase):
    id: PrimaryKey
    name: Optional[str] = Field(None, nullable=True)
    source: Optional[str] = Field(None, nullable=True)
    value: Optional[str] = Field(None, nullable=True)
    description: Optional[str] = Field(None, nullable=True)
    entity_type: Optional[EntityTypeReadMinimal]


class EntityPagination(Pagination):
    items: List[EntityRead]
