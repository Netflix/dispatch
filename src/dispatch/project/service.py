from typing import List, Optional

from sqlalchemy import MetaData
from sqlalchemy.schema import CreateSchema, DropSchema
from fastapi.encoders import jsonable_encoder

from dispatch.database import engine
from .models import Project, ProjectCreate, ProjectUpdate


def get(*, db_session, project_id: int) -> Optional[Project]:
    return db_session.query(Project).filter(Project.id == project_id).first()


def get_all(*, db_session) -> List[Optional[Project]]:
    return db_session.query(Project)


def create(*, db_session, project_in: ProjectCreate) -> Project:
    project = Project(
        **project_in.dict(exclude={}),
    )
    db_session.add(project)
    db_session.commit()

    # create a project specific schema
    schema_name = f"project.{project.name}"
    engine.execute(CreateSchema(schema_name))
    metadata = MetaData(schema=schema_name)
    metadata.create_all(engine)

    return project


def update(*, db_session, project: Project, project_in: ProjectUpdate) -> Project:
    project_data = jsonable_encoder(project)

    update_data = project_in.dict(skip_defaults=True, exclude={})

    for field in project_data:
        if field in update_data:
            setattr(project, field, update_data[field])

    db_session.commit()
    return project


def delete(*, db_session, project_id: int):
    project = db_session.query(Project).filter(Project.id == project_id).first()

    # drop our project specific schema
    schema_name = f"project.{project.name}"
    engine.execute(DropSchema(schema_name))

    db_session.delete(project)
    db_session.commit()
