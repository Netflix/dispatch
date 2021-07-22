from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from dispatch.auth.permissions import (
    OrganizationOwnerPermission,
    OrganizationMemberPermission,
    PermissionsDependency,
)

from dispatch.models import PrimaryKey
from dispatch.organization.models import constrained_organization_str
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.organization.models import OrganizationRead

from .models import (
    UserLogin,
    UserOrganization,
    UserRegister,
    UserRead,
    UserUpdate,
    UserPagination,
    UserLoginResponse,
    UserRegisterResponse,
)
from .service import get, get_by_email, update, create, get_current_user


auth_router = APIRouter()
user_router = APIRouter()


@user_router.get(
    "",
    dependencies=[
        Depends(
            PermissionsDependency(
                [
                    OrganizationMemberPermission,
                ]
            )
        )
    ],
    response_model=UserPagination,
)
def get_users(
    *, organization: constrained_organization_str, common: dict = Depends(common_parameters)
):
    """Get all users."""
    common["filter_spec"] = {
        "and": [{"model": "Organization", "op": "==", "field": "name", "value": organization}]
    }
    items = search_filter_sort_paginate(model="DispatchUser", **common)

    # filtered users
    return {
        "total": items["total"],
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "projects": u.projects,
                "role": u.get_organization_role(organization),
            }
            for u in items["items"]
        ],
    }


@user_router.get("/{user_id}", response_model=UserRead)
def get_user(*, db_session: Session = Depends(get_db), user_id: int):
    """Get a user."""
    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail=[{"msg": "The user with this id does not exist."}]
        )

    return user


@auth_router.get("/me", response_model=UserRead)
def get_me(
    req: Request,
    db_session: Session = Depends(get_db),
):
    return get_current_user(request=req)


@user_router.put(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(PermissionsDependency([OrganizationOwnerPermission]))],
)
def update_user(
    *,
    db_session: Session = Depends(get_db),
    user_id: PrimaryKey,
    organization: constrained_organization_str,
    user_in: UserUpdate,
):
    """Update a user."""
    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404, detail=[{"msg": "The user with this id does not exist."}]
        )

    # add organization information
    user_in.organizations = [
        UserOrganization(role=user_in.role, organization=OrganizationRead(name=organization))
    ]

    return update(db_session=db_session, user=user, user_in=user_in)


@auth_router.post("/login", response_model=UserLoginResponse)
def login_user(
    user_in: UserLogin,
    db_session: Session = Depends(get_db),
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if user and user.check_password(user_in.password):
        return {"token": user.token}
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=[
            {
                "msg": "Invalid username or password",
                "loc": ["username"],
                "type": "BadUsernamePassword",
            }
        ],
    )


@auth_router.post("/register", response_model=UserRegisterResponse)
def register_user(
    user_in: UserRegister,
    organization: constrained_organization_str,
    db_session: Session = Depends(get_db),
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if not user:
        user = create(db_session=db_session, organization=organization, user_in=user_in)
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "User with that email address exists.",
                    "loc": ["email"],
                    "type": "UserExists",
                }
            ],
        )

    return user
