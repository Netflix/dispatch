from typing import Optional
from fastapi.encoders import jsonable_encoder

from .models import Tag, TagCreate, TagUpdate


def get(*, db_session, app_id: int) -> Optional[Tag]:
    return db_session.query(Tag).filter(Tag.id == app_id).one_or_none()


def get_by_name(*, db_session, name: str) -> Optional[Tag]:
    return db_session.query(Tag).filter(Tag.name == name).one_or_none()


def get_all(*, db_session):
    return db_session.query(Tag)


def create(*, db_session, app_in: TagCreate) -> Tag:
    app = Tag(**app_in.dict())
    db_session.add(app)
    db_session.commit()
    return app


def update(*, db_session, app: Tag, app_in: TagUpdate) -> Tag:
    app_data = jsonable_encoder(app)
    update_data = app_in.dict(skip_defaults=True)

    for field in app_data:
        if field in update_data:
            setattr(app, field, update_data[field])

    db_session.add(app)
    db_session.commit()
    return app


def delete(*, db_session, app_id: int):
    app = db_session.query(Tag).filter(Tag.id == app_id).one_or_none()
    db_session.delete(app)
    db_session.commit()
