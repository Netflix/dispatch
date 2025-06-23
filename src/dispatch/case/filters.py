"""FastAPI-Filter implementation for Case filtering."""

from __future__ import annotations

from datetime import datetime

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field
from sqlalchemy.orm import Query
from sqlalchemy.orm.query import Query

from dispatch.case.enums import CaseResolutionReason, CaseStatus
from dispatch.case.models import Case
from dispatch.enums import Visibility


class CaseFilter(Filter):
    """FastAPI-Filter implementation for Case filtering."""

    # Basic field filters
    id__in: list[int] | None = Field(None, description="Filter by case IDs")
    name__ilike: str | None = Field(None, description="Search by case name (case-insensitive)")
    title__ilike: str | None = Field(None, description="Search by case title (case-insensitive)")
    description__ilike: str | None = Field(
        None, description="Search by case description (case-insensitive)"
    )
    resolution__ilike: str | None = Field(
        None, description="Search by resolution text (case-insensitive)"
    )

    # Enum filters
    resolution_reason__in: list[CaseResolutionReason] | None = Field(
        None, description="Filter by resolution reasons"
    )
    status__in: list[CaseStatus] | None = Field(None, description="Filter by case statuses")
    visibility__in: list[Visibility] | None = Field(None, description="Filter by visibility levels")

    # Location and team filters
    participants_team__ilike: str | None = Field(None, description="Search by participants team")
    participants_location__ilike: str | None = Field(
        None, description="Search by participants location"
    )

    # Boolean filters
    dedicated_channel: bool | None = Field(None, description="Filter by dedicated channel status")
    event: bool | None = Field(None, description="Filter by event status")

    # Date range filters for reported_at
    reported_at__gte: datetime | None = Field(
        None, description="Cases reported on or after this date"
    )
    reported_at__lte: datetime | None = Field(
        None, description="Cases reported on or before this date"
    )
    reported_at__gt: datetime | None = Field(None, description="Cases reported after this date")
    reported_at__lt: datetime | None = Field(None, description="Cases reported before this date")

    # Date range filters for triage_at
    triage_at__gte: datetime | None = Field(None, description="Cases triaged on or after this date")
    triage_at__lte: datetime | None = Field(
        None, description="Cases triaged on or before this date"
    )
    triage_at__gt: datetime | None = Field(None, description="Cases triaged after this date")
    triage_at__lt: datetime | None = Field(None, description="Cases triaged before this date")

    # Date range filters for escalated_at
    escalated_at__gte: datetime | None = Field(
        None, description="Cases escalated on or after this date"
    )
    escalated_at__lte: datetime | None = Field(
        None, description="Cases escalated on or before this date"
    )
    escalated_at__gt: datetime | None = Field(None, description="Cases escalated after this date")
    escalated_at__lt: datetime | None = Field(None, description="Cases escalated before this date")

    # Date range filters for closed_at
    closed_at__gte: datetime | None = Field(None, description="Cases closed on or after this date")
    closed_at__lte: datetime | None = Field(None, description="Cases closed on or before this date")
    closed_at__gt: datetime | None = Field(None, description="Cases closed after this date")
    closed_at__lt: datetime | None = Field(None, description="Cases closed before this date")

    # Date range filters for created_at
    created_at__gte: datetime | None = Field(
        None, description="Cases created on or after this date"
    )
    created_at__lte: datetime | None = Field(
        None, description="Cases created on or before this date"
    )
    created_at__gt: datetime | None = Field(None, description="Cases created after this date")
    created_at__lt: datetime | None = Field(None, description="Cases created before this date")

    # Date range filters for updated_at
    updated_at__gte: datetime | None = Field(
        None, description="Cases updated on or after this date"
    )
    updated_at__lte: datetime | None = Field(
        None, description="Cases updated on or before this date"
    )
    updated_at__gt: datetime | None = Field(None, description="Cases updated after this date")
    updated_at__lt: datetime | None = Field(None, description="Cases updated before this date")

    # Relationship filters
    case_type_id__in: list[int] | None = Field(None, description="Filter by case type IDs")
    case_priority_id__in: list[int] | None = Field(None, description="Filter by case priority IDs")
    case_severity_id__in: list[int] | None = Field(None, description="Filter by case severity IDs")

    # Participant relationship filters
    assignee_id__in: list[int] | None = Field(
        None, description="Filter by assignee participant IDs"
    )
    reporter_id__in: list[int] | None = Field(
        None, description="Filter by reporter participant IDs"
    )

    # Tag relationship filters
    tag_id__in: list[int] | None = Field(None, description="Filter by tag IDs")
    tag_type_id__in: list[int] | None = Field(None, description="Filter by tag type IDs")

    # Project filter
    project_id__in: list[int] | None = Field(None, description="Filter by project IDs")

    # Full-text search
    search: str | None = Field(None, description="Full-text search across multiple fields")

    class Constants(Filter.Constants):
        model: type = Case
        search_model_fields: list[str] = ["name", "title", "description"]

    def filter(self, query: Query[Case]) -> Query[Case]:
        """Enhanced filter method with custom email filtering and permission handling."""
        from sqlalchemy.orm import aliased

        # Apply standard FastAPI-Filter filtering first
        query = super().filter(query)

        # Custom email filtering logic (moved from views)
        if hasattr(self, "_assignee_emails") and self._assignee_emails:
            from dispatch.individual.models import IndividualContact
            from dispatch.participant.models import Participant

            assignee_participant = aliased(Participant)
            assignee_individual = aliased(IndividualContact)

            query = (
                query.join(assignee_participant, Case.assignee_id == assignee_participant.id)
                .join(
                    assignee_individual,
                    assignee_participant.individual_contact_id == assignee_individual.id,
                )
                .filter(assignee_individual.email.in_(self._assignee_emails))
            )

        if hasattr(self, "_reporter_emails") and self._reporter_emails:
            from dispatch.individual.models import IndividualContact
            from dispatch.participant.models import Participant

            reporter_participant = aliased(Participant)
            reporter_individual = aliased(IndividualContact)

            query = (
                query.join(reporter_participant, Case.reporter_id == reporter_participant.id)
                .join(
                    reporter_individual,
                    reporter_participant.individual_contact_id == reporter_individual.id,
                )
                .filter(reporter_individual.email.in_(self._reporter_emails))
            )

        return query

    def set_email_filters(
        self, assignee_emails: list[str] | None = None, reporter_emails: list[str] | None = None
    ):
        """Set email filters for participant filtering."""
        if assignee_emails:
            self._assignee_emails = assignee_emails
        if reporter_emails:
            self._reporter_emails = reporter_emails


# Alternative approach using separate filters for different concerns
class CaseBasicFilter(Filter):
    """Basic field filters for cases."""

    id__in: list[int] | None = None
    name__icontains: str | None = None
    title__icontains: str | None = None
    description__icontains: str | None = None
    resolution__icontains: str | None = None
    dedicated_channel: bool | None = None
    event: bool | None = None

    class Constants(Filter.Constants):
        model: type = Case


class CaseStatusFilter(Filter):
    """Status and enum-based filters for cases."""

    resolution_reason__in: list[CaseResolutionReason] | None = None
    status__in: list[CaseStatus] | None = None
    visibility__in: list[Visibility] | None = None

    class Constants(Filter.Constants):
        model: type = Case


class CaseDateFilter(Filter):
    """Date range filters for cases."""

    # Reported date filters
    reported_at__gte: datetime | None = None
    reported_at__lte: datetime | None = None
    reported_at__gt: datetime | None = None
    reported_at__lt: datetime | None = None

    # Triage date filters
    triage_at__gte: datetime | None = None
    triage_at__lte: datetime | None = None
    triage_at__gt: datetime | None = None
    triage_at__lt: datetime | None = None

    # Escalation date filters
    escalated_at__gte: datetime | None = None
    escalated_at__lte: datetime | None = None
    escalated_at__gt: datetime | None = None
    escalated_at__lt: datetime | None = None

    # Closure date filters
    closed_at__gte: datetime | None = None
    closed_at__lte: datetime | None = None
    closed_at__gt: datetime | None = None
    closed_at__lt: datetime | None = None

    # Creation date filters
    created_at__gte: datetime | None = None
    created_at__lte: datetime | None = None
    created_at__gt: datetime | None = None
    created_at__lt: datetime | None = None

    # Update date filters
    updated_at__gte: datetime | None = None
    updated_at__lte: datetime | None = None
    updated_at__gt: datetime | None = None
    updated_at__lt: datetime | None = None

    class Constants(Filter.Constants):
        model: type = Case


class CaseRelationshipFilter(Filter):
    """Relationship-based filters for cases."""

    # Core relationships
    case_type_id__in: list[int] | None = None
    case_priority_id__in: list[int] | None = None
    case_severity_id__in: list[int] | None = None
    project_id__in: list[int] | None = None

    # Participant relationships
    assignee_id__in: list[int] | None = None
    reporter_id__in: list[int] | None = None

    # Tag relationships
    tag_id__in: list[int] | None = None
    tag_type_id__in: list[int] | None = None

    class Constants(Filter.Constants):
        model: type = Case
