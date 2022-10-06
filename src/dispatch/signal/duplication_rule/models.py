from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.sql.schema import UniqueConstraint

from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import JSON
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, EvergreenMixin, NameStr, ProjectMixin, PrimaryKey

from dispatch.enums import RuleMode
from dispatch.auth.models import DispatchUser, UserRead
from dispatch.signal.models import SignalRead
from dispatch.project.models import ProjectRead


class DuplicationRule(Base, ProjectMixin, EvergreenMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    expression = Column(JSON, nullable=False, default=[])
    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="duplication_rules")
    signals = relationship("Signal", backref="duplication_rule")
    mode = Column(String, default=RuleMode.active, nullable=False)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"}, regconfig="pg_catalog.simple")
    )


# Pydantic models...
class DuplicationRuleBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    expression: Optional[List[dict]]
    mode: Optional[RuleMode]


class DuplicationRuleCreate(DuplicationRuleBase):
    project: ProjectRead


class DuplicationRuleUpdate(DuplicationRuleBase):
    id: PrimaryKey = None


class DuplicationRuleRead(DuplicationRuleBase):
    id: PrimaryKey
    creator: UserRead
    signals: List[SignalRead]


class DuplicationRulePagination(DispatchBase):
    items: List[DuplicationRuleRead]
    total: int
