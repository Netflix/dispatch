def test_get(session, project):
    from dispatch.project.service import get

    t_project = get(db_session=session, project_id=project.id)
    assert t_project.id == project.id


def test_create(session, organization):
    from dispatch.project.service import create
    from dispatch.project.models import ProjectCreate

    name = "name"
    description = "description"
    default = True
    color = "red"

    project_in = ProjectCreate(
        name=name,
        description=description,
        default=default,
        color=color,
        organization=organization,
    )
    project = create(db_session=session, project_in=project_in)
    assert project


def test_update(session, project):
    from dispatch.project.service import update
    from dispatch.project.models import ProjectUpdate

    name = "Updated name"

    project_in = ProjectUpdate(
        name=name,
    )
    project = update(
        db_session=session,
        project=project,
        project_in=project_in,
    )
    assert project.name == name


def test_delete(session, project):
    from dispatch.project.service import delete, get

    delete(db_session=session, project_id=project.id)
    assert not get(db_session=session, project_id=project.id)
