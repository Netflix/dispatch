"""Service functions for canvas management."""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from dispatch.case.models import Case
from dispatch.incident.models import Incident

from .models import Canvas, CanvasCreate, CanvasUpdate

log = logging.getLogger(__name__)


def get(*, db_session: Session, canvas_id: int) -> Optional[Canvas]:
    """Returns a canvas based on the given id."""
    return db_session.query(Canvas).filter(Canvas.id == canvas_id).first()


def get_by_canvas_id(*, db_session: Session, slack_canvas_id: str) -> Optional[Canvas]:
    """Returns a canvas based on the Slack canvas ID."""
    return db_session.query(Canvas).filter(Canvas.canvas_id == slack_canvas_id).first()


def get_by_incident(*, db_session: Session, incident_id: int) -> list[Canvas]:
    """Returns all canvases associated with an incident."""
    return db_session.query(Canvas).filter(Canvas.incident_id == incident_id).all()


def get_by_case(*, db_session: Session, case_id: int) -> list[Canvas]:
    """Returns all canvases associated with a case."""
    return db_session.query(Canvas).filter(Canvas.case_id == case_id).all()


def get_by_project(*, db_session: Session, project_id: int) -> list[Canvas]:
    """Returns all canvases for a project."""
    return db_session.query(Canvas).filter(Canvas.project_id == project_id).all()


def get_by_type(*, db_session: Session, project_id: int, canvas_type: str) -> list[Canvas]:
    """Returns all canvases of a specific type for a project."""
    return (
        db_session.query(Canvas)
        .filter(Canvas.project_id == project_id)
        .filter(Canvas.type == canvas_type)
        .all()
    )


def create(*, db_session: Session, canvas_in: CanvasCreate) -> Canvas:
    """Creates a new canvas."""
    canvas = Canvas(
        canvas_id=canvas_in.canvas_id,
        incident_id=canvas_in.incident_id,
        case_id=canvas_in.case_id,
        type=canvas_in.type,
        project_id=canvas_in.project_id,
    )
    db_session.add(canvas)
    db_session.commit()
    return canvas


def update(*, db_session: Session, canvas_id: int, canvas_in: CanvasUpdate) -> Canvas | None:
    """Updates an existing canvas."""
    canvas = get(db_session=db_session, canvas_id=canvas_id)
    if not canvas:
        log.error(f"Canvas with id {canvas_id} not found")
        return None

    update_data = canvas_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(canvas, field, value)

    db_session.add(canvas)
    db_session.commit()
    db_session.refresh(canvas)
    return canvas


def delete(*, db_session: Session, canvas_id: int) -> bool:
    """Deletes a canvas."""
    canvas = db_session.query(Canvas).filter(Canvas.id == canvas_id).first()
    if not canvas:
        return False

    db_session.delete(canvas)
    db_session.commit()
    return True


def delete_by_slack_canvas_id(*, db_session: Session, slack_canvas_id: str) -> bool:
    """Deletes a canvas by its Slack canvas ID."""
    canvas = get_by_canvas_id(db_session=db_session, slack_canvas_id=slack_canvas_id)
    if not canvas:
        return False

    db_session.delete(canvas)
    db_session.commit()
    return True


def get_or_create_by_incident(
    *, db_session: Session, incident: Incident, canvas_type: str, slack_canvas_id: str
) -> Canvas:
    """Gets an existing canvas for an incident and type, or creates a new one."""
    canvas = (
        db_session.query(Canvas)
        .filter(Canvas.incident_id == incident.id)
        .filter(Canvas.type == canvas_type)
        .first()
    )

    if not canvas:
        canvas_in = CanvasCreate(
            canvas_id=slack_canvas_id,
            incident_id=incident.id,
            case_id=None,
            type=canvas_type,
            project_id=incident.project_id,
        )
        canvas = create(db_session=db_session, canvas_in=canvas_in)

    return canvas


def get_or_create_by_case(
    *, db_session: Session, case: Case, canvas_type: str, slack_canvas_id: str
) -> Canvas:
    """Gets an existing canvas for a case and type, or creates a new one."""
    canvas = (
        db_session.query(Canvas)
        .filter(Canvas.case_id == case.id)
        .filter(Canvas.type == canvas_type)
        .first()
    )

    if not canvas:
        canvas_in = CanvasCreate(
            canvas_id=slack_canvas_id,
            incident_id=None,
            case_id=case.id,
            type=canvas_type,
            project_id=case.project_id,
        )
        canvas = create(db_session=db_session, canvas_in=canvas_in)

    return canvas
