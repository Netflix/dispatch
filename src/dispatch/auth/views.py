from fastapi import APIRouter, Depends, HTTPException, status
from pydantic.error_wrappers import ErrorWrapper, ValidationError

from dispatch.config import DISPATCH_AUTH_REGISTRATION_ENABLED

from dispatch.auth.permissions import (
    OrganizationMemberPermission,
    PermissionsDependency,
)
from dispatch.auth.service import CurrentUser
from dispatch.exceptions import (
    InvalidConfigurationError,
    InvalidPasswordError,
    InvalidUsernameError,
)
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.enums import UserRoles
from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.organization.models import OrganizationRead

from .models import (
    UserLogin,
    UserLoginResponse,
    UserOrganization,
    UserPagination,
    UserRead,
    UserRegister,
    UserRegisterResponse,
    UserCreate,
    UserUpdate,
)
from .service import get, get_by_email, update, create


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
def get_users(organization: OrganizationSlug, common: CommonParameters):
    """Gets all organization users."""
    common["filter_spec"] = {
        "and": [{"model": "Organization", "op": "==", "field": "slug", "value": organization}]
    }

    items = search_filter_sort_paginate(model="DispatchUser", **common)

    return {
        "items": [
            {
                "id": u.id,
                "email": u.email,
                "projects": u.projects,
                "role": u.get_organization_role(organization),
            }
            for u in items["items"]
        ],
        "itemsPerPage": items["itemsPerPage"],
        "page": items["page"],
        "total": items["total"],
    }


@user_router.post(
    "",
    response_model=UserRead,
)
def create_user(
    user_in: UserCreate,
    organization: OrganizationSlug,
    db_session: DbSession,
    current_user: CurrentUser,
):
    """Creates a new user."""
    user = get_by_email(db_session=db_session, email=user_in.email)
    if user:
        raise ValidationError(
            [
                ErrorWrapper(
                    InvalidConfigurationError(msg="A user with this email already exists."),
                    loc="email",
                )
            ],
            model=UserCreate,
        )

    current_user_organization_role = current_user.get_organization_role(organization)
    if current_user_organization_role != UserRoles.owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=[
                {
                    "msg": "You don't have permissions to create a new user for this organization. Please, contact the organization's owner."
                }
            ],
        )

    user = create(db_session=db_session, organization=organization, user_in=user_in)
    return user


@user_router.get("/{user_id}", response_model=UserRead)
def get_user(db_session: DbSession, user_id: PrimaryKey):
    """Get a user."""
    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A user with this id does not exist."}],
        )

    return user


@user_router.put(
    "/{user_id}",
    response_model=UserRead,
)
def update_user(
    db_session: DbSession,
    user_id: PrimaryKey,
    organization: OrganizationSlug,
    user_in: UserUpdate,
    current_user: CurrentUser,
):
    """Update a user."""
    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A user with this id does not exist."}],
        )

    if user_in.role:
        # New user role is provided
        user_organization_role = user.get_organization_role(organization)
        if user_organization_role != user_in.role:
            # New user role provided is different than current user role
            current_user_organization_role = current_user.get_organization_role(organization)
            if current_user_organization_role != UserRoles.owner:
                # We don't allow the role change if user requesting the change does not have owner role
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=[
                        {
                            "msg": "You don't have permissions to update the user's role. Please, contact the organization's owner."
                        }
                    ],
                )

    # add organization information
    user_in.organizations = [
        UserOrganization(role=user_in.role, organization=OrganizationRead(name=organization))
    ]

    # we currently only allow user password changes via CLI, not UI/API.
    user_in.password = None

    return update(db_session=db_session, user=user, user_in=user_in)


@auth_router.get("/me", response_model=UserRead)
def get_me(
    *,
    db_session: DbSession,
    current_user: CurrentUser,
):
    return current_user


@auth_router.get("/myrole")
def get_my_role(
    *,
    db_session: DbSession,
    current_user: CurrentUser,
    organization: OrganizationSlug,
):
    return current_user.get_organization_role(organization)


@auth_router.post("/login", response_model=UserLoginResponse)
def login_user(
    user_in: UserLogin,
    organization: OrganizationSlug,
    db_session: DbSession,
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if user and user.check_password(user_in.password):
        projects = []
        for user_project in user.projects:
            projects.append(
                {
                    "project": user_project.project,
                    "default": user_project.default,
                    "role": user_project.role,
                }
            )
        return {"projects": projects, "token": user.token}

    raise ValidationError(
        [
            ErrorWrapper(
                InvalidUsernameError(msg="Invalid username."),
                loc="username",
            ),
            ErrorWrapper(
                InvalidPasswordError(msg="Invalid password."),
                loc="password",
            ),
        ],
        model=UserLogin,
    )


def register_user(
    user_in: UserRegister,
    organization: OrganizationSlug,
    db_session: DbSession,
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


if DISPATCH_AUTH_REGISTRATION_ENABLED:
    register_user = auth_router.post("/register", response_model=UserRegisterResponse)(
        register_user
    )
