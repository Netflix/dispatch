from typing import List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy.sql.expression import true
from dispatch.database.manage import init_schema

from dispatch.enums import UserRoles
from dispatch.auth.models import DispatchUser, DispatchUserOrganization

from .models import Organization, OrganizationCreate, OrganizationUpdate


def get(*, db_session, organization_id: int) -> Optional[Organization]:
    return db_session.query(Organization).filter(Organization.id == organization_id).first()


def get_default(*, db_session) -> Optional[Organization]:
    return db_session.query(Organization).filter(Organization.default == true()).one_or_none()


def get_by_name(*, db_session, name: str) -> Optional[Organization]:
    return db_session.query(Organization).filter(Organization.name == name).one_or_none()


def get_all(*, db_session) -> List[Optional[Organization]]:
    return db_session.query(Organization)


def create(*, db_session, organization_in: OrganizationCreate) -> Organization:
    organization = Organization(
        **organization_in.dict(),
    )
    db_session.add(organization)
    db_session.commit()
    init_schema(organization=organization, schema_name=organization.name)
    return organization


def get_or_create(*, db_session, organization_in: OrganizationCreate) -> Organization:
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
    organization_data = jsonable_encoder(organization)

    update_data = organization_in.dict(skip_defaults=True)

    for field in organization_data:
        if field in update_data:
            setattr(organization, field, update_data[field])

    db_session.add(organization)
    db_session.commit()
    return organization


def delete(*, db_session, organization_id: int):
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
    """Adds the user to the organization."""
    db_session.add(
        DispatchUserOrganization(
            dispatch_user_id=user.id, organization_id=organization.id, role=role.value
        )
    )
    db_session.commit()
