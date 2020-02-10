from typing import Optional
from fastapi.encoders import jsonable_encoder

from .models import Application, ApplicationCreate, ApplicationUpdate


def get(*, db_session, app_id: int) -> Optional[Application]:
    return db_session.query(Application).filter(Application.id == app_id).one_or_none()


def get_by_name(*, db_session, name: str) -> Optional[Application]:
    return db_session.query(Application).filter(Application.name == name).one_or_none()


def get_all(*, db_session):
    return db_session.query(Application)


def create(*, db_session, app_in: ApplicationCreate) -> Application:
    app = Application(**app_in.dict())
    db_session.add(app)
    db_session.commit()
    return app


def update(*, db_session, app: Application, app_in: ApplicationUpdate) -> Application:
    app_data = jsonable_encoder(app)
    update_data = app_in.dict(skip_defaults=True)

    for field in app_data:
        if field in update_data:
            setattr(app, field, update_data[field])

    db_session.add(app)
    db_session.commit()
    return app


def delete(*, db_session, app_id: int):
    app = db_session.query(Application).filter(Application.id == app_id).one_or_none()
    db_session.delete(app)
    db_session.commit()
