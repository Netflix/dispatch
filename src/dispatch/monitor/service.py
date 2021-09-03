from typing import List, Optional

from sqlalchemy.sql.expression import true
from dispatch.project import service as project_service
from dispatch.plugin import service as plugin_service

from .models import (
    Monitor,
    MonitorCreate,
    MonitorUpdate,
)


def get(*, db_session, monitor_id: int) -> Optional[Monitor]:
    """Returns a monitor based on the given monitor id."""
    return db_session.query(Monitor).filter(Monitor.id == monitor_id).one_or_none()


def get_all(*, db_session) -> List[Optional[Monitor]]:
    """Returns all monitors."""
    return db_session.query(Monitor)


def get_enabled(*, db_session) -> List[Optional[Monitor]]:
    """Fetches all enabled monitors."""
    return db_session.query(Monitor).filter(Monitor.enabled == true()).all()


def get_instance_enabled(*, db_session) -> List[Optional[Monitor]]:
    """Fetches all enabled instance monitors."""
    return db_session.query(Monitor).filter(Monitor.enabled == true()).all()


def get_instance_by_weblink(*, db_session, weblink: str) -> Optional[Monitor]:
    """Fetches a monitor by it's weblink"""
    return db_session.query(Monitor).filter(Monitor.weblink == weblink).one_or_none()


def create(*, db_session, monitor_in: MonitorCreate) -> Monitor:
    """Creates a new monitor."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=monitor_in.project
    )
    plugin_instance = plugin_service.get_instance(
        db_session=db_session, plugin_instance_id=monitor_in.plugin_instance.id
    )
    monitor = Monitor(
        **monitor_in.dict(exclude={"plugin_instance", "project"}),
        plugin_instance=plugin_instance,
        project=project,
    )

    db_session.add(monitor)
    db_session.commit()
    return monitor


def update(*, db_session, monitor: Monitor, monitor_in: MonitorUpdate) -> Monitor:
    """Updates a monitor."""
    monitor_data = monitor.dict()
    update_data = monitor_in.dict(skip_defaults=True, exclude={"plugin_instance"})

    for field in monitor_data:
        if field in update_data:
            setattr(monitor, field, update_data[field])

    plugin_instance = plugin_service.get_instance(
        db_session=db_session, plugin_instance_id=monitor_in.plugin_instance.id
    )

    monitor.plugin_instance = plugin_instance

    db_session.commit()
    return monitor


def delete(*, db_session, monitor_id: int):
    """Deletes a monitor."""
    db_session.query(Monitor).filter(Monitor.id == monitor_id).delete()
    db_session.commit()
