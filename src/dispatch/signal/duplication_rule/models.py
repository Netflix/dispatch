from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String, ForeignKey, Table, PrimaryKeyConstraint

from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, EvergreenMixin, NameStr, ProjectMixin, PrimaryKey

from dispatch.enums import RuleMode
from dispatch.auth.models import DispatchUser, UserRead
from dispatch.signal.models import SignalRead, Signal
from dispatch.project.models import ProjectRead

assoc_duplication_tag_types = Table(
    "assoc_duplication_rule_tag_types",
    Base.metadata,
    Column("duplication_id", Integer, ForeignKey("duplication_rule.id", ondelete="CASCADE")),
    Column("tag_type_id", Integer, ForeignKey("tag_type.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("duplication_rule33_id", "tag_type_id"),
)


class DuplicationRule(Base, ProjectMixin, EvergreenMixin):
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="duplication_rules")
    signal_id = Column(Integer, ForeignKey(Signal.id))
    signal = relationship("Signal", backref="duplication_rules")
    mode = Column(String, default=RuleMode.active, nullable=False)

    # number of seconds for duplication lookback default to 1 hour
    window = Column(int, default=(60 * 60))

    # the tag types to use for deduplication
    tag_types = relationship(
        "TagType", secondary=assoc_duplication_tag_types, backref="duplication_rules"
    )

    search_vector = Column(
        TSVectorType(
            "name",
            "description",
            weights={"name": "A", "description": "B"},
            regconfig="pg_catalog.simple",
        )
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
