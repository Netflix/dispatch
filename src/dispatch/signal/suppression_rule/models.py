from datetime import datetime
from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table, PrimaryKeyConstraint

from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, EvergreenMixin, NameStr, ProjectMixin, PrimaryKey

from dispatch.enums import RuleMode
from dispatch.auth.models import DispatchUser, UserRead
from dispatch.signal.models import Signal, SignalRead
from dispatch.project.models import ProjectRead

assoc_suppression_tags = Table(
    "assoc_suppression_rule_tags",
    Base.metadata,
    Column("suppression_id", Integer, ForeignKey("suppression_rule.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("suppression_rule_id", "tag_id"),
)


class SuppressionRule(Base, ProjectMixin, EvergreenMixin):
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="suppression_rule")
    signal_id = Column(Integer, ForeignKey(Signal.id))
    signal = relationship("Signal", backref="suppression_rule")
    mode = Column(String, default=RuleMode.active, nullable=False)
    expiration = Column(DateTime, nullable=True)

    # the tags to use for suppression
    tags = relationship("TagType", secondary=assoc_suppression_tags, backref="suppression_rules")

    search_vector = Column(
        TSVectorType(
            "name",
            "description",
            weights={"name": "A", "description": "B"},
            regconfig="pg_catalog.simple",
        )
    )


# Pydantic models...
class SuppressionRuleBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    expression: Optional[List[dict]] = Field(None, nullable=True)
    mode: Optional[RuleMode]
    expiration: Optional[datetime] = Field(None, nullable=True)


class SuppressionRuleCreate(SuppressionRuleBase):
    project: ProjectRead


class SuppressionRuleUpdate(SuppressionRuleBase):
    id: PrimaryKey = None


class SuppressionRuleRead(SuppressionRuleBase):
    id: PrimaryKey
    creator: UserRead
    signals: List[SignalRead]


class SuppressionRulePagination(DispatchBase):
    items: List[SuppressionRuleRead]
    total: int
