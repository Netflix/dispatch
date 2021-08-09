from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.auth.permissions import SensitiveProjectActionPermission, PermissionsDependency
from dispatch.models import PrimaryKey

from .models import (
    ParticipantRoleMappingCreate,
    ParticipantRoleMappingPagination,
    ParticipantRoleMappingRead,
    ParticipantRoleMappingUpdate,
)
from .service import create, delete, get, update


router = APIRouter()


@router.get("", response_model=ParticipantRoleMappingPagination)
def get_participant_role_mappings(*, common: dict = Depends(common_parameters)):
    """Get all participant role mappings, or only those matching a given search term."""
    return search_filter_sort_paginate(model="ParticipantRoleMapping", **common)


@router.get("/{participant_role_mapping_id}", response_model=ParticipantRoleMappingRead)
def get_participant_role_mapping(
    *, db_session: Session = Depends(get_db), participant_role_mapping_id: PrimaryKey
):
    """Get a participant role mapping by its id."""
    participant_role_mapping = get(
        db_session=db_session, participant_role_mapping_id=participant_role_mapping_id
    )
    if not participant_role_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A participant role mapping with this id does not exist."}],
        )
    return participant_role_mapping


@router.post(
    "",
    response_model=ParticipantRoleMappingRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def create_participant_role_mapping(
    *,
    db_session: Session = Depends(get_db),
    participant_role_mapping_in: ParticipantRoleMappingCreate,
):
    """Create a participant_role_mapping."""
    participant_role_mapping = create(
        db_session=db_session, participant_role_mapping_in=participant_role_mapping_in
    )
    return participant_role_mapping


@router.put(
    "/{participant_role_mapping_id}",
    response_model=ParticipantRoleMappingRead,
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def update_participant_role_mapping(
    *,
    db_session: Session = Depends(get_db),
    participant_role_mapping_id: PrimaryKey,
    participant_role_mapping_in: ParticipantRoleMappingUpdate,
):
    """Update a participant role mapping by its id."""
    participant_role_mapping = get(
        db_session=db_session, participant_role_mapping_id=participant_role_mapping_id
    )
    if not participant_role_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A participant role mapping with this id does not exist."}],
        )
    participant_role_mapping = update(
        db_session=db_session,
        participant_role_mapping=participant_role_mapping,
        participant_role_mapping_in=participant_role_mapping_in,
    )
    return participant_role_mapping


@router.delete(
    "/{participant_role_mapping_id}",
    dependencies=[Depends(PermissionsDependency([SensitiveProjectActionPermission]))],
)
def delete_participant_role_mapping(
    *, db_session: Session = Depends(get_db), participant_role_mapping_id: PrimaryKey
):
    """Delete a participant role mapping, returning only an HTTP 200 OK if successful."""
    participant_role_mapping = get(
        db_session=db_session, participant_role_mapping_id=participant_role_mapping_id
    )
    if not participant_role_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A participant role mapping with this id does not exist."}],
        )
    delete(db_session=db_session, participant_role_mapping_id=participant_role_mapping_id)
