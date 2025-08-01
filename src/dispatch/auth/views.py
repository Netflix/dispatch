import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from dispatch.config import DISPATCH_AUTH_REGISTRATION_ENABLED

from dispatch.auth.permissions import (
    OrganizationMemberPermission,
    PermissionsDependency,
)
from dispatch.auth.service import CurrentUser
from dispatch.database.core import DbSession
from dispatch.database.service import CommonParameters, search_filter_sort_paginate
from dispatch.enums import UserRoles
from dispatch.models import OrganizationSlug, PrimaryKey
from dispatch.plugin import service as plugin_service
from dispatch.plugins.dispatch_core.exceptions import MfaException
from dispatch.organization.models import OrganizationRead

from .models import (
    MfaPayload,
    MfaPayloadResponse,
    UserLogin,
    UserLoginResponse,
    UserOrganization,
    UserPagination,
    UserRead,
    UserRegister,
    UserRegisterResponse,
    UserCreate,
    UserUpdate,
    UserPasswordUpdate,
    AdminPasswordReset,
    UserSettingsRead,
    UserSettingsUpdate,
)
from .service import (
    get,
    get_by_email,
    update,
    create,
    get_or_create_user_settings,
    update_user_settings,
)


log = logging.getLogger(__name__)

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
                {
                    "msg": "A user with this email already exists.",
                    "loc": "email",
                }
            ]
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


@user_router.get(
    "/{user_id}",
    dependencies=[
        Depends(
            PermissionsDependency(
                [
                    OrganizationMemberPermission,
                ]
            )
        )
    ],
    response_model=UserRead,
)
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
    """Check if Current_user is Owner and is trying to edit another user"""
    current_user_organization_role = current_user.get_organization_role(organization)
    if current_user_organization_role != UserRoles.owner and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=[{"msg": "A user that is not an Owner is trying to update another user."}],
        )
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

    return update(db_session=db_session, user=user, user_in=user_in)


@user_router.post("/{user_id}/change-password", response_model=UserRead)
def change_password(
    db_session: DbSession,
    user_id: PrimaryKey,
    password_update: UserPasswordUpdate,
    current_user: CurrentUser,
    organization: OrganizationSlug,
):
    """Change user password with proper validation"""
    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A user with this id does not exist."}],
        )

    # Only allow users to change their own password or owners to reset
    if user.id != current_user.id and not current_user.is_owner(organization):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=[{"msg": "Not authorized to change other user passwords"}],
        )

    # Validate current password if user is changing their own password
    if user.id == current_user.id:
        if not user.verify_password(password_update.current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=[{"msg": "Invalid current password"}],
            )

    # Set new password
    try:
        user.set_password(password_update.new_password)
        db_session.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": str(e)}],
        ) from e

    return user


@user_router.post("/{user_id}/reset-password", response_model=UserRead)
def admin_reset_password(
    db_session: DbSession,
    user_id: PrimaryKey,
    password_reset: AdminPasswordReset,
    current_user: CurrentUser,
    organization: OrganizationSlug,
):
    """Admin endpoint to reset user password"""
    # Verify current user is an owner
    if not current_user.is_owner(organization):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=[{"msg": "Only owners can reset passwords"}],
        )

    user = get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A user with this id does not exist."}],
        )

    try:
        user.set_password(password_reset.new_password)
        db_session.commit()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": str(e)}],
        ) from e

    return user


@auth_router.get("/me", response_model=UserRead)
def get_me(
    *,
    db_session: DbSession,
    current_user: CurrentUser,
):
    # Get user settings and include in response
    user_settings = get_or_create_user_settings(db_session=db_session, user_id=current_user.id)

    # Create a response dict that includes settings
    response_data = {
        "id": current_user.id,
        "email": current_user.email,
        "projects": current_user.projects,
        "organizations": current_user.organizations,
        "experimental_features": current_user.experimental_features,
        "settings": user_settings,
    }

    return response_data


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
    if user and user.verify_password(user_in.password):
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

    # Pydantic v2 compatible error handling
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=[
            {
                "msg": "Invalid username.",
                "loc": ["username"],
                "type": "value_error",
            },
            {
                "msg": "Invalid password.",
                "loc": ["password"],
                "type": "value_error",
            },
        ],
    )


def register_user(
    user_in: UserRegister,
    organization: OrganizationSlug,
    db_session: DbSession,
):
    user = get_by_email(db_session=db_session, email=user_in.email)
    if user:
        # Pydantic v2 compatible error handling
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "msg": "A user with this email already exists.",
                    "loc": ["email"],
                    "type": "value_error",
                }
            ],
        )

    user = create(db_session=db_session, organization=organization, user_in=user_in)
    return user


@auth_router.post("/mfa", response_model=MfaPayloadResponse)
def mfa_check(
    payload_in: MfaPayload,
    current_user: CurrentUser,
    db_session: DbSession,
):
    log.info(f"MFA check initiated for user: {current_user.email}")
    log.debug(f"Payload received: {payload_in.dict()}")

    try:
        log.info(f"Attempting to get active MFA plugin for project: {payload_in.project_id}")
        mfa_auth_plugin = plugin_service.get_active_instance(
            db_session=db_session, project_id=payload_in.project_id, plugin_type="auth-mfa"
        )

        if not mfa_auth_plugin:
            log.error(f"MFA plugin not enabled for project: {payload_in.project_id}")
            raise HTTPException(
                status_code=400, detail="MFA plugin is not enabled for the project."
            )

        log.info(f"MFA plugin found: {mfa_auth_plugin.__class__.__name__}")

        log.info("Validating MFA token")
        status = mfa_auth_plugin.instance.validate_mfa_token(payload_in, current_user, db_session)

        log.info("MFA token validation successful")
        return MfaPayloadResponse(status=status)

    except MfaException as e:
        log.error(f"MFA Exception occurred: {str(e)}")
        log.debug(f"MFA Exception details: {type(e).__name__}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e)) from e

    except Exception as e:
        log.critical(f"Unexpected error in MFA check: {str(e)}")
        log.exception("Full traceback:")
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

    finally:
        log.info("MFA check completed")


@auth_router.get("/me/settings", response_model=UserSettingsRead)
def get_my_settings(
    *,
    db_session: DbSession,
    current_user: CurrentUser,
):
    """Get current user's settings."""
    settings = get_or_create_user_settings(db_session=db_session, user_id=int(current_user.id))
    return settings


@auth_router.put("/me/settings", response_model=UserSettingsRead)
def update_my_settings(
    *,
    db_session: DbSession,
    current_user: CurrentUser,
    settings_in: UserSettingsUpdate,
):
    """Update current user's settings."""
    settings = get_or_create_user_settings(db_session=db_session, user_id=int(current_user.id))
    updated_settings = update_user_settings(
        db_session=db_session, settings=settings, settings_in=settings_in
    )
    return updated_settings


if DISPATCH_AUTH_REGISTRATION_ENABLED:
    register_user = auth_router.post("/register", response_model=UserRegisterResponse)(
        register_user
    )
