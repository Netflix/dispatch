from datetime import datetime
import logging

from .models import (
    IncidentCostModel,
    IncidentCostModelRead,
    IncidentCostModelCreate,
    IncidentCostModelUpdate,
)
from dispatch.incident_cost_model_activity import service as incident_cost_model_activity_service
from dispatch.incident_cost_model_activity.models import IncidentCostModelActivityCreate
from dispatch.plugin import service as plugin_service
from dispatch.project import service as project_service

log = logging.getLogger(__name__)


def has_unique_event_ids(incident_cost_model_in: IncidentCostModelRead):
    seen = set()
    for activity in incident_cost_model_in.activities:
        if activity.event.id in seen:
            log.warning(
                f"Duplicate event id detected. Please ensure all events are unique for each cost model. Duplicate id: {activity.event.id}"
            )
            return False
        seen.add(activity.event.id)
    return True


def delete(*, db_session, incident_cost_model_id: int):
    """Deletes an incident cost model."""
    incident_cost_model = get_cost_model_by_id(
        db_session=db_session, incident_cost_model_id=incident_cost_model_id
    )
    if not incident_cost_model:
        raise ValueError(
            "Unable to delete incident cost model. No incident cost model found with that id."
        )

    for activity in incident_cost_model.activities:
        incident_cost_model_activity_service.delete(
            db_session=db_session, incident_cost_model_activity_id=activity.id
        )

    db_session.delete(incident_cost_model)
    db_session.commit()


def update(*, db_session, incident_cost_model_in: IncidentCostModelUpdate) -> IncidentCostModel:
    """Updates an incident cost model."""
    if not has_unique_event_ids(incident_cost_model_in):
        raise KeyError("Unable to update incident cost model. Duplicate event ids detected.")

    incident_cost_model = get_cost_model_by_id(
        db_session=db_session, incident_cost_model_id=incident_cost_model_in.id
    )
    if not incident_cost_model:
        raise ValueError(
            "Unable to update incident cost model. No incident cost model found with that id."
        )

    incident_cost_model.name = incident_cost_model_in.name
    incident_cost_model.description = incident_cost_model_in.description
    incident_cost_model.enabled = incident_cost_model_in.enabled
    incident_cost_model.created_at = incident_cost_model_in.created_at
    incident_cost_model.updated_at = (
        incident_cost_model_in.updated_at
        if incident_cost_model_in.updated_at
        else datetime.utcnow()
    )

    # Update all recognized activities. Delete all removed activites.
    update_activities = []
    delete_activities = []

    for activity in incident_cost_model.activities:
        updated = False
        for idx_in, activity_in in enumerate(incident_cost_model_in.activities):
            if activity.id == activity_in.id:
                update_activities.append((activity, activity_in))
                updated = True
                break
        if updated:
            continue

        # Delete activities that have been removed from the cost model.
        delete_activities.append(activity)

    for activity, activity_in in update_activities:
        activity.response_time_seconds = activity_in.response_time_seconds
        activity.enabled = activity_in.enabled
        activity.event = plugin_service.get_plugin_event_by_id(
            db_session=db_session, plugin_event_id=activity_in.event.id
        )
        incident_cost_model_in.activities.pop(idx_in)

    for activity in delete_activities:
        incident_cost_model_activity_service.delete(
            db_session=db_session, incident_cost_model_activity_id=activity.id
        )

    # Create new activities.
    for activity_in in incident_cost_model_in.activities:
        activity_out = incident_cost_model_activity_service.create_cost_model_activity(
            db_session=db_session, incident_cost_model_activity_in=activity_in
        )

        if not activity_out:
            log.error("Failed to create cost model activity. Continuing.")
            continue

        incident_cost_model.activities.append(activity_out)

    db_session.commit()
    return incident_cost_model


def create(*, db_session, incident_cost_model_in: IncidentCostModelCreate) -> IncidentCostModel:
    """Creates a new incident cost model."""
    if not has_unique_event_ids(incident_cost_model_in):
        raise KeyError("Unable to update incident cost model. Duplicate event ids detected.")

    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=incident_cost_model_in.project
    )

    incident_cost_model = IncidentCostModel(
        **incident_cost_model_in.dict(exclude={"activities", "project"}),
        activities=[],
        project=project,
    )

    db_session.add(incident_cost_model)
    db_session.commit()

    # Create activities after the incident cost model is created.
    # We need the incident cost model id to map to the activity.
    if incident_cost_model and incident_cost_model_in.activities:
        for activity_in in incident_cost_model_in.activities:
            activity_out = incident_cost_model_activity_service.create_cost_model_activity(
                db_session=db_session, incident_cost_model_activity_in=activity_in
            )
            if not activity_out:
                log.error("Failed to create cost model activity. . Continuing.")
                continue

            incident_cost_model.activities.append(activity_out)

    db_session.commit()
    return incident_cost_model


def get_cost_model_by_id(*, db_session, incident_cost_model_id: int) -> IncidentCostModel:
    """Returns an incident cost model based on the given incident cost model id."""
    return (
        db_session.query(IncidentCostModel)
        .filter(IncidentCostModel.id == incident_cost_model_id)
        .one()
    )
