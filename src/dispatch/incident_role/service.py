import logging

from typing import List, Optional
from operator import attrgetter
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.exceptions import NotFoundError
from dispatch.incident.models import Incident, ProjectRead
from dispatch.incident.priority import service as incident_priority_service
from dispatch.incident.type import service as incident_type_service
from dispatch.individual import service as individual_contact_service
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.project import service as project_service
from dispatch.service import service as service_service
from dispatch.tag import service as tag_service

from .models import (
    IncidentRole,
    IncidentRoleCreateUpdate,
)


log = logging.getLogger(__name__)


def get(*, db_session, incident_role_id: int) -> Optional[IncidentRole]:
    """Gets an incident role by id."""
    return db_session.query(IncidentRole).filter(IncidentRole.id == incident_role_id).one_or_none()


def get_all(*, db_session):
    """Gets all incident role."""
    return db_session.query(IncidentRole)


def get_all_by_role(
    *, db_session, role: ParticipantRoleType, project_id: int
) -> Optional[List[IncidentRole]]:
    """Gets all policies for a given role."""
    return (
        db_session.query(IncidentRole)
        .filter(IncidentRole.role == role)
        .filter(IncidentRole.project_id == project_id)
        .all()
    )


def get_all_enabled_by_role(
    *, db_session, role: ParticipantRoleType, project_id: int
) -> Optional[List[IncidentRole]]:
    """Gets all enabled incident roles."""
    return (
        db_session.query(IncidentRole)
        .filter(IncidentRole.enabled == True)  # noqa Flake8 E712
        .filter(IncidentRole.role == role)
        .filter(IncidentRole.project_id == project_id)
    ).all()


def create_or_update(
    *,
    db_session,
    project_in: ProjectRead,
    role: ParticipantRoleType,
    incident_roles_in: List[IncidentRoleCreateUpdate],
) -> List[IncidentRole]:
    """Updates a list of incident role policies."""
    role_policies = []

    project = project_service.get_by_name_or_raise(db_session=db_session, project_in=project_in)

    # update/create everybody else
    for role_policy_in in incident_roles_in:
        if role_policy_in.id:
            role_policy = get(db_session=db_session, incident_role_id=role_policy_in.id)

            if not role_policy:
                raise ValidationError(
                    [
                        ErrorWrapper(
                            NotFoundError(msg="Role policy not found."),
                            loc="id",
                        )
                    ],
                    model=IncidentRoleCreateUpdate,
                )

        else:
            role_policy = IncidentRole(role=role, project=project)
            db_session.add(role_policy)

        role_policy_data = role_policy.dict()
        update_data = role_policy_in.dict(
            skip_defaults=True,
            exclude={
                "role",  # we don't allow role to be updated
                "tags",
                "incident_types",
                "incident_priorities",
                "service",
                "individual",
                "project",
            },
        )

        for field in role_policy_data:
            if field in update_data:
                setattr(role_policy, field, update_data[field])

        if role_policy_in.tags:
            tags = [
                tag_service.get_by_name_or_raise(
                    db_session=db_session, project_id=project.id, tag_in=t
                )
                for t in role_policy_in.tags
            ]
            role_policy.tags = tags

        if role_policy_in.incident_types:
            incident_types = [
                incident_type_service.get_by_name_or_raise(
                    db_session=db_session, project_id=project.id, incident_type_in=i
                )
                for i in role_policy_in.incident_types
            ]
            role_policy.incident_types = incident_types

        if role_policy_in.incident_priorities:
            incident_priorities = [
                incident_priority_service.get_by_name_or_raise(
                    db_session=db_session,
                    project_id=project.id,
                    incident_priority_in=i,
                )
                for i in role_policy_in.incident_priorities
            ]
            role_policy.incident_priorities = incident_priorities

        if role_policy_in.service:
            service = service_service.get_by_external_id_and_project_id_or_raise(
                db_session=db_session,
                project_id=project.id,
                service_in=role_policy_in.service,
            )
            role_policy.service = service

        if role_policy_in.individual:
            individual = individual_contact_service.get_by_email_and_project_id_or_raise(
                db_session=db_session,
                project_id=project.id,
                individual_contact_in=role_policy_in.individual,
            )
            role_policy.individual = individual

        role_policies.append(role_policy)

    # TODO Add projects
    # get all current policies in order to detect deletions
    existing_incident_roles = get_all_by_role(
        db_session=db_session, role=role, project_id=project.id
    )
    for existing_role_policy in existing_incident_roles:
        for current_role_policy in role_policies:
            if existing_role_policy.id == current_role_policy.id:
                break
        else:
            db_session.delete(existing_role_policy)

    db_session.commit()
    return role_policies


def resolve_role(
    *,
    db_session,
    role: ParticipantRoleType,
    incident: Incident,
) -> Optional[IncidentRole]:
    """Based on parameters currently associated to an incident determine who should be assigned which incident role."""
    incident_roles = get_all_enabled_by_role(
        db_session=db_session, role=role, project_id=incident.project.id
    )

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
