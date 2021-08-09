import logging

from typing import List, Optional, Type

from dispatch.database.core import Base
from dispatch.incident.models import Incident
from dispatch.plugin import service as plugin_service
from dispatch.project import service as project_service
from dispatch.search_filter import service as search_filter_service

from .models import (
    ParticipantRoleMapping,
    ParticipantRoleMappingCreate,
    ParticipantRoleMappingUpdate,
)


log = logging.getLogger(__name__)


def get(*, db_session, participant_role_mapping_id: int) -> Optional[ParticipantRoleMapping]:
    """Gets a notifcation by id."""
    return (
        db_session.query(ParticipantRoleMapping)
        .filter(ParticipantRoleMapping.id == participant_role_mapping_id)
        .one_or_none()
    )


def get_all(*, db_session):
    """Gets all participant_role_mappings."""
    return db_session.query(ParticipantRoleMapping)


def get_all_enabled(*, db_session, project_id: int) -> Optional[List[ParticipantRoleMapping]]:
    """Gets all enabled participant_role_mappings."""
    return (
        db_session.query(ParticipantRoleMapping)
        .filter(ParticipantRoleMapping.enabled == True)  # noqa Flake8 E712
        .filter(ParticipantRoleMapping.project_id == project_id)
    ).all()


def create(
    *, db_session, participant_role_mapping_in: ParticipantRoleMappingCreate
) -> ParticipantRoleMapping:
    """Creates a new participant_role_mapping."""
    filters = []
    if participant_role_mapping_in.filters:
        filters = [
            search_filter_service.get(db_session=db_session, search_filter_id=f.id)
            for f in participant_role_mapping_in.filters
        ]

    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=participant_role_mapping_in.project
    )

    participant_role_mapping = ParticipantRoleMapping(
        **participant_role_mapping_in.dict(exclude={"filters", "project"}),
        filters=filters,
        project=project,
    )

    db_session.add(participant_role_mapping)
    db_session.commit()
    return participant_role_mapping


def update(
    *,
    db_session,
    participant_role_mapping: ParticipantRoleMapping,
    participant_role_mapping_in: ParticipantRoleMappingUpdate,
) -> ParticipantRoleMapping:
    """Updates a participant_role_mapping."""
    participant_role_mapping_data = participant_role_mapping.dict()
    update_data = participant_role_mapping_in.dict(
        skip_defaults=True,
        exclude={"filters"},
    )

    for field in participant_role_mapping_data:
        if field in update_data:
            setattr(participant_role_mapping, field, update_data[field])

    if participant_role_mapping_in.filters is not None:
        filters = [
            search_filter_service.get(db_session=db_session, search_filter_id=f.id)
            for f in participant_role_mapping_in.filters
        ]
        participant_role_mapping.filters = filters

    db_session.commit()
    return participant_role_mapping


def delete(*, db_session, participant_role_mapping_id: int):
    """Deletes a participant_role_mapping."""
    participant_role_mapping = (
        db_session.query(ParticipantRoleMapping)
        .filter(ParticipantRoleMapping.id == participant_role_mapping_id)
        .one_or_none()
    )
    db_session.delete(participant_role_mapping)
    db_session.commit()


def determine_participant(
    *,
    db_session,
    incident: Incident,
    class_instance: Type[Base],
    participant_role_mapping_params: dict,
):
    """Sends participant_role_mappings."""
    participant_role_mappings = get_all_enabled(
        db_session=db_session, project_id=incident.project.id
    )
    for participant_role_mapping in participant_role_mappings:
        for search_filter in participant_role_mapping.filters:
            match = search_filter_service.match(
                db_session=db_session,
                filter_spec=search_filter.expression,
                class_instance=class_instance,
            )
            if match:
                send(
                    db_session=db_session,
                    project_id=incident.project.id,
                    participant_role_mapping=participant_role_mapping,
                    participant_role_mapping_params=participant_role_mapping_params,
                )

        if not participant_role_mapping.filters:
            send(
                db_session=db_session,
                project_id=incident.project.id,
                participant_role_mapping=participant_role_mapping,
                participant_role_mapping_params=participant_role_mapping_params,
            )
