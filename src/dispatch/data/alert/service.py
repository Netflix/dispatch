from typing import Optional
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.exceptions import NotFoundError

from .models import Alert, AlertCreate, AlertUpdate, AlertRead


def get(*, db_session, alert_id: int) -> Optional[Alert]:
    """Gets an alert by its id."""
    return db_session.query(Alert).filter(Alert.id == alert_id).one_or_none()


def get_by_name(*, db_session, name: str) -> Optional[Alert]:
    """Gets a alert by its name."""
    return db_session.query(Alert).filter(Alert.name == name).one_or_none()


def get_by_name_or_raise(*, db_session, alert_in=AlertRead) -> AlertRead:
    """Returns the alert specified or raises ValidationError."""
    alert = get_by_name(db_session=db_session, name=alert_in.name)

    if not alert:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(
                        msg="Alert not found.",
                        alert=alert_in.name,
                    ),
                    loc="alert",
                )
            ],
            model=AlertRead,
        )

    return alert


def get_all(*, db_session):
    """Gets all alerts."""
    return db_session.query(Alert)


def create(*, db_session, alert_in: AlertCreate) -> Alert:
    """Creates a new alert."""
    alert = Alert(**alert_in.dict(exclude={}))
    db_session.add(alert)
    db_session.commit()
    return alert


def get_or_create(*, db_session, alert_in: AlertCreate) -> Alert:
    """Gets or creates a new alert."""
    # prefer the alert id if available
    if alert_in.id:
        q = db_session.query(Alert).filter(Alert.id == alert_in.id)
    else:
        q = db_session.query(Alert).filter_by(name=alert_in.name)

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, alert_in=alert_in)


def update(*, db_session, alert: Alert, alert_in: AlertUpdate) -> Alert:
    """Updates an existing alert."""
    alert_data = alert.dict()
    update_data = alert_in.dict(skip_defaults=True, exclude={})

    for field in alert_data:
        if field in update_data:
            setattr(alert, field, update_data[field])

    db_session.commit()
    return alert


def delete(*, db_session, alert_id: int):
    """Deletes an existing alert."""
    alert = db_session.query(Alert).filter(Alert.id == alert_id).one_or_none()
    db_session.delete(alert)
    db_session.commit()
