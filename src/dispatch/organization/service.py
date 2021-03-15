from typing import List, Optional

from fastapi.encoders import jsonable_encoder

from .models import Organization, OrganizationCreate, OrganizationUpdate


def get(*, db_session, organization_id: int) -> Optional[Organization]:
    return db_session.query(Organization).filter(Organization.id == organization_id).first()


def get_all(*, db_session) -> List[Optional[Organization]]:
    return db_session.query(Organization)


def create(*, db_session, organization_in: OrganizationCreate) -> Organization:
    team = Organization(
        **organization_in.dict(),
    )
    db_session.add(team)
    db_session.commit()
    return team


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
    db_session.delete(team)
    db_session.commit()
