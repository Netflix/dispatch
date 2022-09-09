from datetime import datetime
from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
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


class SupressionRule(Base, ProjectMixin, EvergreenMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    expression = Column(JSON, nullable=False, default=[])
    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="supression_rule")
    signals = relationship("Signal", backref="supression_rule")
    mode = Column(String, default=RuleMode.active, nullable=False)

    expiration = Column(DateTime, nullable=True)

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic models...
class SupressionRuleBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    expression: List[dict]
    creator: UserRead
    signals: List[SignalRead]
    mode: Optional[RuleMode]
    expiration: Optional[datetime] = Field(None, nullable=True)


class SupressionRuleCreate(SupressionRuleBase):
    project: ProjectRead


class SupressionRuleUpdate(SupressionRuleBase):
    id: PrimaryKey = None


class SupressionRuleRead(SupressionRuleBase):
    id: PrimaryKey


class SupressionRulePagination(DispatchBase):
    items: List[SupressionRuleRead]
    total: int
