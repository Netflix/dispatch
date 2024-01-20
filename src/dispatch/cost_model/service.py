from datetime import datetime
import logging
from typing import List

from .models import (
    CostModel,
    CostModelCreate,
    CostModelRead,
    CostModelUpdate,
    CostModelActivity,
    CostModelActivityCreate,
    CostModelActivityUpdate,
)
from dispatch.cost_model import service as cost_model_service
from dispatch.plugin import service as plugin_service
from dispatch.project import service as project_service

log = logging.getLogger(__name__)


def has_unique_plugin_event(cost_model_in: CostModelRead) -> bool:
    seen = set()
    for activity in cost_model_in.activities:
        if activity.plugin_event.id in seen:
            log.warning(
                f"Duplicate plugin event id detected. Please ensure all plugin events are unique for each cost model. Duplicate id: {activity.plugin_event.id}"
            )
            return False
        seen.add(activity.plugin_event.id)
    return True


def get_all(*, db_session, project_id: int) -> List[CostModel]:
    """Returns all cost models."""
    if project_id:
        return db_session.query(CostModel).filter(CostModel.project_id == project_id)
    return db_session.query(CostModel)


def get_cost_model_activity_by_id(*, db_session, cost_model_activity_id: int) -> CostModelActivity:
    """Returns a cost model activity based on the given cost model activity id."""
    return (
        db_session.query(CostModelActivity)
        .filter(CostModelActivity.id == cost_model_activity_id)
        .one()
    )


def delete_cost_model_activity(*, db_session, cost_model_activity_id: int):
    """Deletes a cost model activity."""
    cost_model_activity = get_cost_model_activity_by_id(
        db_session=db_session, cost_model_activity_id=cost_model_activity_id
    )
    db_session.delete(cost_model_activity)
    db_session.commit()


def update_cost_model_activity(*, db_session, cost_model_activity_in: CostModelActivityUpdate):
    """Updates a cost model activity."""
    cost_model_activity = get_cost_model_activity_by_id(
        db_session=db_session, cost_model_activity_id=cost_model_activity_in.id
    )

    cost_model_activity.response_time_seconds = cost_model_activity_in.response_time_seconds
    cost_model_activity.enabled = cost_model_activity_in.enabled
    cost_model_activity.plugin_event_id = cost_model_activity_in.plugin_event.id

    db_session.commit()
    return cost_model_activity


def create_cost_model_activity(
    *, db_session, cost_model_activity_in: CostModelActivityCreate
) -> CostModelActivity:
    cost_model_activity = CostModelActivity(
        response_time_seconds=cost_model_activity_in.response_time_seconds,
        enabled=cost_model_activity_in.enabled,
        plugin_event_id=cost_model_activity_in.plugin_event.id,
    )

    db_session.add(cost_model_activity)
    db_session.commit()
    return cost_model_activity


def delete(*, db_session, cost_model_id: int):
    """Deletes a cost model."""
    cost_model = get_cost_model_by_id(db_session=db_session, cost_model_id=cost_model_id)
    if not cost_model:
        raise ValueError(
            f"Unable to delete cost model. No cost model found with id {cost_model_id}."
        )

    db_session.delete(cost_model)
    db_session.commit()


def update(*, db_session, cost_model_in: CostModelUpdate) -> CostModel:
    """Updates a cost model."""
    if not has_unique_plugin_event(cost_model_in):
        raise KeyError("Unable to update cost model. Duplicate plugin event ids detected.")

    cost_model = get_cost_model_by_id(db_session=db_session, cost_model_id=cost_model_in.id)
    if not cost_model:
        raise ValueError("Unable to update cost model. No cost model found with that id.")

    cost_model.name = cost_model_in.name
    cost_model.description = cost_model_in.description
    cost_model.enabled = cost_model_in.enabled
    cost_model.created_at = cost_model_in.created_at
    cost_model.updated_at = (
        cost_model_in.updated_at if cost_model_in.updated_at else datetime.utcnow()
    )

    # Update all recognized activities. Delete all removed activites.
    update_activities = []
    delete_activities = []

    for activity in cost_model.activities:
        updated = False
        for idx_in, activity_in in enumerate(cost_model_in.activities):
            if activity.plugin_event.id == activity_in.plugin_event.id:
                update_activities.append((activity, activity_in))
                cost_model_in.activities.pop(idx_in)
                updated = True
                break
        if updated:
            continue

        # Delete activities that have been removed from the cost model.
        delete_activities.append(activity)

    for activity, activity_in in update_activities:
        activity.response_time_seconds = activity_in.response_time_seconds
        activity.enabled = activity_in.enabled
        activity.plugin_event = plugin_service.get_plugin_event_by_id(
            db_session=db_session, plugin_event_id=activity_in.plugin_event.id
        )

    for activity in delete_activities:
        cost_model_service.delete_cost_model_activity(
            db_session=db_session, cost_model_activity_id=activity.id
        )

    # Create new activities.
    for activity_in in cost_model_in.activities:
        activity_out = cost_model_service.create_cost_model_activity(
            db_session=db_session, cost_model_activity_in=activity_in
        )

        if not activity_out:
            log.error("Failed to create cost model activity. Continuing.")
            continue

        cost_model.activities.append(activity_out)

    db_session.commit()
    return cost_model


def create(*, db_session, cost_model_in: CostModelCreate) -> CostModel:
    """Creates a new cost model."""
    if not has_unique_plugin_event(cost_model_in):
        raise KeyError("Unable to update cost model. Duplicate plugin event ids detected.")

    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=cost_model_in.project
    )

    cost_model = CostModel(
        **cost_model_in.dict(exclude={"activities", "project"}),
        activities=[],
        project=project,
    )

    db_session.add(cost_model)
    db_session.commit()

    # Create activities after the cost model is created.
    # We need the cost model id to map to the activity.
    if cost_model and cost_model_in.activities:
        for activity_in in cost_model_in.activities:
            activity_out = cost_model_service.create_cost_model_activity(
                db_session=db_session, cost_model_activity_in=activity_in
            )
            if not activity_out:
                log.error("Failed to create cost model activity. Continuing.")
                continue

            cost_model.activities.append(activity_out)

    db_session.commit()
    return cost_model


def get_cost_model_by_id(*, db_session, cost_model_id: int) -> CostModel:
    """Returns a cost model based on the given cost model id."""
    return db_session.query(CostModel).filter(CostModel.id == cost_model_id).one()
