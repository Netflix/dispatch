from fastapi import APIRouter, Depends, Request, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import mode

from dispatch.auth.permissions import (
    OrganizationOwnerPermission,
    OrganizationMemberPermission,
    PermissionsDependency,
)
from dispatch.exceptions import InvalidConfigurationError, InvalidValueError

from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.database.core import get_db
from dispatch.database.service import common_parameters, search_filter_sort_paginate
from dispatch.organization.models import OrganizationRead

from .models import (
    DispatchUser,
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
def get_users(*, organization: OrganizationSlug, common: dict = Depends(common_parameters)):
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
def get_user(*, db_session: Session = Depends(get_db), user_id: PrimaryKey):
    """Get a user."""
    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The user with this id does not exist."}],
        )

    return user


@auth_router.get("/me", response_model=UserRead)
def get_me(
    req: Request,
    organization: OrganizationSlug,
    current_user: DispatchUser = Depends(get_current_user),
    db_session: Session = Depends(get_db),
):
    return current_user


@user_router.put(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(PermissionsDependency([OrganizationOwnerPermission]))],
)
def update_user(
    *,
    db_session: Session = Depends(get_db),
    user_id: PrimaryKey,
    organization: OrganizationSlug,
    user_in: UserUpdate,
):
    """Update a user."""
    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "The user with this id does not exist."}],
        )

    # add organization information
    user_in.organizations = [
        UserOrganization(role=user_in.role, organization=OrganizationRead(name=organization))
    ]

    return update(db_session=db_session, user=user, user_in=user_in)


@auth_router.post("/login", response_model=UserLoginResponse)
def login_user(
    user_in: UserLogin,
    organization: OrganizationSlug,
    db_session: Session = Depends(get_db),
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if user and user.check_password(user_in.password):
        return {"token": user.token}

    raise ValidationError(
        [
            ErrorWrapper(
                InvalidValueError(msg="Invalid username."),
                loc="username",
            ),
            ErrorWrapper(
                InvalidValueError(msg="Invalid password."),
                loc="password",
            ),
        ],
        model=UserLogin,
    )


@auth_router.post("/register", response_model=UserRegisterResponse)
def register_user(
    user_in: UserRegister,
    organization: OrganizationSlug,
    db_session: Session = Depends(get_db),
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if user:
        raise ValidationError(
            [
                ErrorWrapper(
                    InvalidConfigurationError(msg="A user with this email already exists."),
                    loc="email",
                )
            ],
            model=UserRegister,
        )

    user = create(db_session=db_session, organization=organization, user_in=user_in)
    return user
