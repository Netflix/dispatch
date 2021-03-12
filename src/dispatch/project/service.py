from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from .models import Project, ProjectCreate, ProjectUpdate


def get(*, db_session, team_id: int) -> Optional[Project]:
    return db_session.query(Project).filter(Project.id == team_id).first()


def get_all(*, db_session) -> List[Optional[Project]]:
    return db_session.query(Project)


def create(*, db_session, project_in: ProjectCreate) -> Project:
    project = Project(
        **project_in.dict(exclude={}),
    )
    db_session.add(project)
    db_session.commit()
    return project


def create_all(*, db_session, projects_in: List[ProjectCreate]) -> List[Project]:
    contacts = [Project(**t.dict()) for t in projects_in]
    db_session.bulk_save_objects(contacts)
    db_session.commit()
    return contacts


def update(
    *, db_session, project: Project, project_in: ProjectUpdate
) -> Project:
    team_data = jsonable_encoder(project)

    update_data = project_in.dict(
        skip_defaults=True, exclude={}
    )

    for field in team_data:
        if field in update_data:
            setattr(project, field, update_data[field])

    db_session.commit()
    return project


def delete(*, db_session, project_id: int):
    project = db_session.query(Project).filter(Project.id == project_id).first()
    db_session.delete(project)
    db_session.commit()
