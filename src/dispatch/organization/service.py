from typing import List, Optional

from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.sql.expression import true

from dispatch.auth.models import DispatchUser, DispatchUserOrganization
from dispatch.database.core import engine
from dispatch.database.manage import init_schema
from dispatch.enums import UserRoles
from dispatch.exceptions import NotFoundError

from .models import Organization, OrganizationCreate, OrganizationRead, OrganizationUpdate


def get(*, db_session, organization_id: int) -> Optional[Organization]:
    """Gets an organization."""
    return db_session.query(Organization).filter(Organization.id == organization_id).first()


def get_default(*, db_session) -> Optional[Organization]:
    """Gets the default organization."""
    return db_session.query(Organization).filter(Organization.default == true()).one_or_none()


def get_default_or_raise(*, db_session) -> Organization:
    """Returns the default organization or raise a ValidationError if one doesn't exist."""
    organization = get_default(db_session=db_session)

    if not organization:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="No default organization defined."),
                    loc="organization",
                )
            ],
            model=OrganizationRead,
        )
    return organization


def get_by_name(*, db_session, name: str) -> Optional[Organization]:
    """Gets an organization by its name."""
    return db_session.query(Organization).filter(Organization.name == name).one_or_none()


def get_by_name_or_raise(*, db_session, organization_in=OrganizationRead) -> Organization:
    """Returns the organization specified or raises ValidationError."""
    organization = get_by_name(db_session=db_session, name=organization_in.name)

    if not organization:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="Organization not found.", organization=organization_in.name),
                    loc="organization",
                )
            ],
            model=OrganizationRead,
        )

    return organization


def get_by_slug(*, db_session, slug: str) -> Optional[Organization]:
    """Gets an organization by its slug."""
    return db_session.query(Organization).filter(Organization.slug == slug).one_or_none()


def get_by_slug_or_raise(*, db_session, organization_in=OrganizationRead) -> Organization:
    """Returns the organization specified or raises ValidationError."""
    organization = get_by_slug(db_session=db_session, slug=organization_in.slug)

    if not organization:
        raise ValidationError(
            [
                ErrorWrapper(
                    NotFoundError(msg="Organization not found.", organization=organization_in.name),
                    loc="organization",
                )
            ],
            model=OrganizationRead,
        )

    return organization


def get_by_name_or_default(*, db_session, organization_in=OrganizationRead) -> Organization:
    """Returns a organization based on a name or the default if not specified."""
    if organization_in.name:
        return get_by_name_or_raise(db_session=db_session, organization_in=organization_in)
    else:
        return get_default_or_raise(db_session=db_session)


def get_all(*, db_session) -> List[Optional[Organization]]:
    """Gets all organizations."""
    return db_session.query(Organization)


def create(*, db_session, organization_in: OrganizationCreate) -> Organization:
    """Creates an organization."""
    organization = Organization(
        **organization_in.dict(exclude={"banner_color"}),
    )

    if organization_in.banner_color:
        organization.banner_color = organization_in.banner_color.as_hex()

    # we let the new schema session create the organization
    organization = init_schema(engine=engine, organization=organization)
    return organization


def get_or_create(*, db_session, organization_in: OrganizationCreate) -> Organization:
    """Gets an existing or creates a new organization."""
    if organization_in.id:
        q = db_session.query(Organization).filter(Organization.id == organization_in.id)
    else:
        q = db_session.query(Organization).filter_by(**organization_in.dict(exclude={"id"}))

    instance = q.first()
    if instance:
        return instance

    return create(db_session=db_session, organization_in=organization_in)


def update(
    *, db_session, organization: Organization, organization_in: OrganizationUpdate
) -> Organization:
    """Updates an organization."""
    organization_data = organization.dict()

    update_data = organization_in.dict(skip_defaults=True, exclude={"banner_color"})

    for field in organization_data:
        if field in update_data:
            setattr(organization, field, update_data[field])

    if organization_in.banner_color:
        organization.banner_color = organization_in.banner_color.as_hex()

    db_session.commit()
    return organization


def delete(*, db_session, organization_id: int):
    """Deletes an organization."""
    organization = db_session.query(Organization).filter(Organization.id == organization_id).first()
    db_session.delete(organization)
    db_session.commit()


def add_user(
    *,
    db_session,
    user: DispatchUser,
    organization: Organization,
    role: UserRoles = UserRoles.member,
):
    """Adds a user to an organization."""
    db_session.add(
        DispatchUserOrganization(
            dispatch_user_id=user.id, organization_id=organization.id, role=role
        )
    )
    db_session.commit()
