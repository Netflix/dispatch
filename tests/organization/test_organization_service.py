import pytest


def test_get_organization(session, organization):
    from dispatch.organization.service import get

    t_organization = get(db_session=session, organization_id=organization.id)
    assert t_organization.id == organization.id


def test_get_all(session, organizations):
    from dispatch.organization.service import get_all

    t_organizations = get_all(db_session=session).all()
    assert len(t_organizations) > 1


def test_create(session):
    from dispatch.organization.service import create
    from dispatch.organization.models import OrganizationCreate

    name = "name"
    description = "description"
    default = True
    banner_enabled = True
    banner_color = "red"
    banner_text = "banner"

    organization_in = OrganizationCreate(
        name=name,
        description=description,
        default=default,
        banner_enabled=banner_enabled,
        banner_color=banner_color,
        banner_text=banner_text,
    )
    organization = create(db_session=session, organization_in=organization_in)
    assert organization


@pytest.mark.skip
def test_update(session, organization):
    from dispatch.organization.service import update
    from dispatch.organization.models import OrganizationUpdate

    name = "Updated name"

    organization_in = OrganizationUpdate(
        name=name,
    )
    organization = update(
        db_session=session,
        organization=organization,
        organization_in=organization_in,
    )
    assert organization.name == name


def test_delete(session, organization):
    from dispatch.organization.service import delete, get

    delete(db_session=session, organization_id=organization.id)
    assert not get(db_session=session, organization_id=organization.id)
