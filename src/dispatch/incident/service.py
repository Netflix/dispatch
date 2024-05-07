"""
.. module: dispatch.incident.service
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""

import logging

from datetime import datetime, timedelta
from typing import List, Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.decorators import timer
from dispatch.case import service as case_service
from dispatch.database.core import SessionLocal
from dispatch.event import service as event_service
from dispatch.exceptions import NotFoundError
from dispatch.incident.priority import service as incident_priority_service
from dispatch.incident.severity import service as incident_severity_service
from dispatch.incident.type import service as incident_type_service
from dispatch.incident_cost import service as incident_cost_service
from dispatch.incident_role.service import resolve_role
from dispatch.participant import flows as participant_flows
from dispatch.participant_role.models import ParticipantRoleType
from dispatch.plugin import service as plugin_service
from dispatch.project import service as project_service
from dispatch.tag import service as tag_service
from dispatch.term import service as term_service

from .enums import IncidentStatus
from .models import Incident, IncidentCreate, IncidentRead, IncidentUpdate


log = logging.getLogger(__name__)


def resolve_and_associate_role(
    db_session: SessionLocal, incident: Incident, role: ParticipantRoleType
):
    """For a given role type resolve which individual email should be assigned that role."""
    email_address = None
    service_id = None

    incident_role = resolve_role(db_session=db_session, role=role, incident=incident)
    if not incident_role:
        log.info(
            f"We were not able to resolve the email address for {role} via incident role policies."
        )
        return email_address, service_id

    if incident_role.service:
        service_id = incident_role.service.id
        service_external_id = incident_role.service.external_id
        oncall_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="oncall"
        )
        if not oncall_plugin:
            log.warning("Resolved incident role associated with a plugin that is not active.")
            return email_address, service_id

        email_address = oncall_plugin.instance.get(service_id=service_external_id)

    return email_address, service_id


@timer
def get(*, db_session, incident_id: int) -> Optional[Incident]:
    """Returns an incident based on the given id."""
    return db_session.query(Incident).filter(Incident.id == incident_id).first()


def get_by_name(*, db_session, project_id: int, name: str) -> Optional[Incident]:
    """Returns an incident based on the given name."""
    return (
        db_session.query(Incident)
        .filter(Incident.name == name)
        .filter(Incident.project_id == project_id)
        .first()
    )


def get_all_open_by_incident_type(*, db_session, incident_type_id: int) -> List[Optional[Incident]]:
    """Returns all non-closed incidents based on the given incident type."""
    return (
        db_session.query(Incident)
        .filter(Incident.status != IncidentStatus.closed)
        .filter(Incident.incident_type_id == incident_type_id)
        .all()
    )


def get_by_name_or_raise(*, db_session, project_id: int, incident_in: IncidentRead) -> Incident:
    """Returns an incident based on a given name or raises ValidationError"""
    incident = get_by_name(db_session=db_session, project_id=project_id, name=incident_in.name)

    if not incident:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Incident not found.",
                        query=incident_in.name,
                    ),
                    loc="incident",
                )
            ],
            model=IncidentRead,
        )
    return incident


def get_all(*, db_session, project_id: int) -> List[Optional[Incident]]:
    """Returns all incidents."""
    return db_session.query(Incident).filter(Incident.project_id == project_id)


def get_all_by_status(*, db_session, status: str, project_id: int) -> List[Optional[Incident]]:
    """Returns all incidents based on the given status."""
    return (
        db_session.query(Incident)
        .filter(Incident.status == status)
        .filter(Incident.project_id == project_id)
        .all()
    )


def get_all_last_x_hours_by_status(
    *, db_session, status: str, hours: int, project_id: int
) -> List[Optional[Incident]]:
    """Returns all incidents of a given status in the last x hours."""
    now = datetime.utcnow()

    if status == IncidentStatus.active:
        return (
            db_session.query(Incident)
            .filter(Incident.status == IncidentStatus.active)
            .filter(Incident.created_at >= now - timedelta(hours=hours))
            .filter(Incident.project_id == project_id)
            .all()
        )

    if status == IncidentStatus.stable:
        return (
            db_session.query(Incident)
            .filter(Incident.status == IncidentStatus.stable)
            .filter(Incident.stable_at >= now - timedelta(hours=hours))
            .filter(Incident.project_id == project_id)
            .all()
        )

    if status == IncidentStatus.closed:
        return (
            db_session.query(Incident)
            .filter(Incident.status == IncidentStatus.closed)
            .filter(Incident.closed_at >= now - timedelta(hours=hours))
            .filter(Incident.project_id == project_id)
            .all()
        )


def create(*, db_session, incident_in: IncidentCreate) -> Incident:
    """Creates a new incident."""
    project = project_service.get_by_name_or_default(
        db_session=db_session, project_in=incident_in.project
    )

    incident_type = incident_type_service.get_by_name_or_default(
        db_session=db_session, project_id=project.id, incident_type_in=incident_in.incident_type
    )

    incident_priority = incident_priority_service.get_by_name_or_default(
        db_session=db_session,
        project_id=project.id,
        incident_priority_in=incident_in.incident_priority,
    )

    incident_severity = incident_severity_service.get_by_name_or_default(
        db_session=db_session,
        project_id=project.id,
        incident_severity_in=incident_in.incident_severity,
    )

    visibility = incident_type.visibility
    if incident_in.visibility:
        visibility = incident_in.visibility

    tag_objs = []
    for t in incident_in.tags:
        tag_objs.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    # We create the incident
    incident = Incident(
        description=incident_in.description,
        incident_priority=incident_priority,
        incident_severity=incident_severity,
        incident_type=incident_type,
        project=project,
        status=incident_in.status,
        tags=tag_objs,
        title=incident_in.title,
        visibility=visibility,
    )

    db_session.add(incident)
    db_session.commit()

    reporter_name = incident_in.reporter.individual.name if incident_in.reporter else ""

    event_service.log_incident_event(
        db_session=db_session,
        source="Dispatch Core App",
        description="Incident created",
        details={
            "title": incident.title,
            "description": incident.description,
            "type": incident.incident_type.name,
            "severity": incident.incident_severity.name,
            "priority": incident.incident_priority.name,
            "status": incident.status,
            "visibility": incident.visibility,
        },
        individual_id=incident_in.reporter.individual.id,
        incident_id=incident.id,
        owner=reporter_name,
        pinned=True,
    )

    # add reporter
    reporter_email = incident_in.reporter.individual.email
    participant_flows.add_participant(
        reporter_email,
        incident,
        db_session,
        role=ParticipantRoleType.reporter,
    )

    # add commander
    commander_email = commander_service_id = None
    if incident_in.commander_email:
        commander_email = incident_in.commander_email
    elif incident_in.commander:
        commander_email = incident_in.commander.individual.email
    else:
        commander_email, commander_service_id = resolve_and_associate_role(
            db_session=db_session, incident=incident, role=ParticipantRoleType.incident_commander
        )

    if not commander_email:
        # we make the reporter the commander if an email for the commander
        # was not provided or resolved via incident role policies
        commander_email = reporter_email

    participant_flows.add_participant(
        commander_email,
        incident,
        db_session,
        service_id=commander_service_id,
        role=ParticipantRoleType.incident_commander,
    )

    # add liaison
    liaison_email, liaison_service_id = resolve_and_associate_role(
        db_session=db_session, incident=incident, role=ParticipantRoleType.liaison
    )

    if liaison_email:
        # we only add the liaison if we are able to resolve its email
        # via incident role policies
        participant_flows.add_participant(
            liaison_email,
            incident,
            db_session,
            service_id=liaison_service_id,
            role=ParticipantRoleType.liaison,
        )

    # add scribe
    scribe_email, scribe_service_id = resolve_and_associate_role(
        db_session=db_session, incident=incident, role=ParticipantRoleType.scribe
    )

    if scribe_email:
        # we only add the scribe if we are able to resolve its email
        # via incident role policies
        participant_flows.add_participant(
            scribe_email,
            incident,
            db_session,
            service_id=scribe_service_id,
            role=ParticipantRoleType.scribe,
        )

    # add observer (if engage_next_oncall is enabled)
    incident_role = resolve_role(
        db_session=db_session, role=ParticipantRoleType.incident_commander, incident=incident
    )
    if incident_role and incident_role.engage_next_oncall:
        oncall_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=incident.project.id, plugin_type="oncall"
        )
        if not oncall_plugin:
            log.debug("Resolved observer role not available since oncall plugin is not active.")
        else:
            oncall_email = oncall_plugin.instance.get_next_oncall(
                service_id=incident_role.service.external_id
            )
            # no need to add as observer if already added as commander
            if oncall_email and commander_email != oncall_email:
                participant_flows.add_participant(
                    oncall_email,
                    incident,
                    db_session,
                    service_id=incident_role.service.id,
                    role=ParticipantRoleType.observer,
                )

    return incident


def update(*, db_session, incident: Incident, incident_in: IncidentUpdate) -> Incident:
    """Updates an existing incident."""
    incident_type = incident_type_service.get_by_name_or_default(
        db_session=db_session,
        project_id=incident.project.id,
        incident_type_in=incident_in.incident_type,
    )

    incident_severity = incident_severity_service.get_by_name_or_default(
        db_session=db_session,
        project_id=incident.project.id,
        incident_severity_in=incident_in.incident_severity,
    )

    if incident_in.status == IncidentStatus.stable and incident.project.stable_priority:
        incident_priority = incident.project.stable_priority
    else:
        incident_priority = incident_priority_service.get_by_name_or_default(
            db_session=db_session,
            project_id=incident.project.id,
            incident_priority_in=incident_in.incident_priority,
        )

    cases = []
    for c in incident_in.cases:
        cases.append(case_service.get(db_session=db_session, case_id=c.id))

    tags = []
    for t in incident_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    terms = []
    for t in incident_in.terms:
        terms.append(term_service.get_or_create(db_session=db_session, term_in=t))

    duplicates = []
    for d in incident_in.duplicates:
        duplicates.append(get(db_session=db_session, incident_id=d.id))

    incident_costs = []
    for incident_cost in incident_in.incident_costs:
        incident_costs.append(
            incident_cost_service.get_or_create(
                db_session=db_session, incident_cost_in=incident_cost
            )
        )

    # Update total incident reponse cost if incident type has changed.
    if incident_type.id != incident.incident_type.id:
        incident_cost_service.update_incident_response_cost(
            incident_id=incident.id, db_session=db_session
        )

    update_data = incident_in.dict(
        skip_defaults=True,
        exclude={
            "cases",
            "commander",
            "duplicates",
            "incident_costs",
            "incident_priority",
            "incident_severity",
            "incident_type",
            "project",
            "reporter",
            "status",
            "tags",
            "terms",
            "visibility",
        },
    )

    for field in update_data.keys():
        setattr(incident, field, update_data[field])

    incident.cases = cases
    incident.duplicates = duplicates
    incident.incident_costs = incident_costs
    incident.incident_priority = incident_priority
    incident.incident_severity = incident_severity
    incident.incident_type = incident_type
    incident.status = incident_in.status
    incident.tags = tags
    incident.terms = terms
    incident.visibility = incident_in.visibility

    db_session.commit()

    return incident


def delete(*, db_session, incident_id: int):
    """Deletes an existing incident."""
    db_session.query(Incident).filter(Incident.id == incident_id).delete()
    db_session.commit()
