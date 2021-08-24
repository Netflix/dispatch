import logging

from typing import List, Optional
from operator import attrgetter

from dispatch.incident.models import Incident
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.tag import service as tag_service
from dispatch.incident_type import service as incident_type_service
from dispatch.incident_priority import service as incident_priority_service
from dispatch.individual import service as individual_contact_service
from dispatch.service import service as service_service

from .models import (
    IncidentRole,
    IncidentRoleUpdate,
)


log = logging.getLogger(__name__)


def get(*, db_session, incident_role_id: int) -> Optional[IncidentRole]:
    """Gets a notifcation by id."""
    return db_session.query(IncidentRole).filter(IncidentRole.id == incident_role_id).one_or_none()


def get_all(*, db_session):
    """Gets all incident_role_s."""
    return db_session.query(IncidentRole)


def get_all_by_role(*, db_session, role: str, project_id: int) -> Optional[List[IncidentRole]]:
    """Gets all policies for a given role."""
    return (
        db_session.query(IncidentRole)
        .filter(IncidentRole.role == role)
        .filter(IncidentRole.project_id == project_id)
        .all()
    )


def get_all_enabled(*, db_session, project_id: int) -> Optional[List[IncidentRole]]:
    """Gets all enabled incident_role_s."""
    return (
        db_session.query(IncidentRole)
        .filter(IncidentRole.enabled == True)  # noqa Flake8 E712
        .filter(IncidentRole.project_id == project_id)
    ).all()


def update(
    *,
    db_session,
    incident_role: IncidentRole,
    incident_role_in: IncidentRoleUpdate,
) -> IncidentRole:
    """Updates a incident_role_."""
    incident_role_data = incident_role.dict()
    update_data = incident_role_in.dict(
        skip_defaults=True,
        exclude={"tags", "incident_types", "incident_priorities", "service", "individual"},
    )

    for field in incident_role_data:
        if field in update_data:
            setattr(incident_role, field, update_data[field])

    if incident_role_in.tags:
        tags = [
            tag_service.get_by_name_or_raise(
                db_session=db_session, project_id=incident_role.project.id, tag_in=t
            )
            for t in incident_role_in.tags
        ]
        incident_role.tags = tags

    if incident_role_in.incident_types:
        incident_types = [
            incident_type_service.get_by_name_or_raise(
                db_session=db_session, project_id=incident_role.project.id, incident_type_in=i
            )
            for i in incident_role_in.incident_types
        ]
        incident_role.incident_types = incident_types

    if incident_role_in.incident_priorities:
        incident_priorities = [
            incident_priority_service.get_by_name_or_raise(
                db_session=db_session, project_id=incident_role.project.id, incident_priority_in=i
            )
            for i in incident_role_in.incident_priorities
        ]
        incident_role.incident_priorities = incident_priorities

    if incident_role_in.service:
        service = service_service.get_by_external_id_and_project_id_or_raise(
            db_session=db_session,
            project_id=incident_role.project.id,
            service_in=incident_role_in.service,
        )
        incident_role.service = service

    if incident_role_in.individual:
        individual = individual_contact_service.get_by_email_and_project_id_or_raise(
            db_session=db_session,
            project_id=incident_role.project.id,
            individual_contact_in=incident_role_in.individual,
        )
        incident_role.individual = individual

    db_session.commit()
    return incident_role


def resolve_role(
    *,
    db_session,
    role: ParticipantRoleType,
    incident: Incident,
):
    """Based on parameters currently associated to an incident determine who should be assigned which incident role."""
    incident_roles = get_all_enabled(db_session=db_session, project_id=incident.project.id)

    # get the subject role policies
    incident_roles = [p for p in incident_roles if p.role == role]

    # the order of evaluation of policies is as follows:
    # 1) Match any policy that includes the current priority
    # 2) Match any policy that includes the current incident type
    # 3) Match any policy that includes the current tag set (individually first and then as a group)
    # 4) If there are still multiple matches use order to determine who to resolve (lowest gets priority)

    incident_roles = [
        p for p in incident_roles if incident.incident_priority in p.incident_priorities
    ]
    incident_roles = [p for p in incident_roles if incident.incident_type in p.incident_types]

    for t in incident.tags:
        incident_roles += [p for p in incident_roles if t in p.tags]

    if len(incident_roles) == 1:
        return incident_roles[0]

    if len(incident_roles) > 1:
        return sorted(incident_roles, key=attrgetter("order"))[0]

    return
