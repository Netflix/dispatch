from typing import Optional
from dispatch.project import service as project_service
from dispatch.tag import service as tag_service

from .models import Signal, SignalCreate


def get(*, db_session, signal_id: int) -> Optional[Signal]:
    """Gets a signal by id."""
    return db_session.query(Signal).filter(Signal.id == signal_id).first()


def create(*, db_session, signal_in: SignalCreate) -> Signal:
    """Creates a new signal."""
    project = project_service.get_by_name_or_raise(
        db_session=db_session, project_in=signal_in.project
    )

    signal = Signal(**signal_in.dict(exclude={"project", "tags"}), project=project)

    tags = []
    for t in signal_in.tags:
        tags.append(tag_service.get_or_create(db_session=db_session, tag_in=t))

    signal.tags = tags

    db_session.add(signal)
    db_session.commit()
    return signal
