"""
.. module: dispatch.auth.service
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.
"""
import logging
from typing import Optional

from fastapi import HTTPException, Depends
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from sqlalchemy.exc import IntegrityError

from dispatch.config import (
    DISPATCH_AUTHENTICATION_PROVIDER_SLUG,
    DISPATCH_AUTHENTICATION_DEFAULT_USER,
)
from dispatch.enums import UserRoles
from dispatch.organization import service as organization_service
from dispatch.organization.models import OrganizationRead
from dispatch.plugins.base import plugins
from dispatch.project import service as project_service

from .models import (
    DispatchUser,
    DispatchUserOrganization,
    DispatchUserProject,
    UserOrganization,
    UserProject,
    UserRegister,
    UserUpdate,
)


log = logging.getLogger(__name__)

InvalidCredentialException = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED, detail=[{"msg": "Could not validate credentials"}]
)


def get(*, db_session, user_id: int) -> Optional[DispatchUser]:
    """Returns a user based on the given user id."""
    return db_session.query(DispatchUser).filter(DispatchUser.id == user_id).one_or_none()


def get_by_email(*, db_session, email: str) -> Optional[DispatchUser]:
    """Returns a user object based on user email."""
    return db_session.query(DispatchUser).filter(DispatchUser.email == email).one_or_none()


def create_or_update_project_role(*, db_session, user: DispatchUser, role_in: UserProject):
    """Creates a new project role or updates an existing role."""
    if not role_in.project.id:
        project = project_service.get_by_name(db_session=db_session, name=role_in.project.name)
        project_id = project.id
    else:
        project_id = role_in.project.id

    project_role = (
        db_session.query(DispatchUserProject)
        .filter(
            DispatchUserProject.dispatch_user_id == user.id,
        )
        .filter(DispatchUserProject.project_id == project_id)
        .one_or_none()
    )

    if not project_role:
        return DispatchUserProject(
            project_id=project_id,
            role=role_in.role,
        )
    project_role.role = role_in.role
    return project_role


def create_or_update_project_default(
    *, db_session, user: DispatchUser, user_project_in: UserProject
):
    """Creates a new user project or updates an existing one."""
    if user_project_in.project.id:
        project_id = user_project_in.project.id
    else:
        project = project_service.get_by_name(
            db_session=db_session, name=user_project_in.project.name
        )
        project_id = project.id

    user_project = (
        db_session.query(DispatchUserProject)
        .filter(
            DispatchUserProject.dispatch_user_id == user.id,
        )
        .filter(DispatchUserProject.project_id == project_id)
        .one_or_none()
    )

    if not user_project:
        user_project = DispatchUserProject(
            dispatch_user_id=user.id,
            project_id=project_id,
            default=True,
        )
        db_session.add(user_project)
        return user_project

    user_project.default = user_project_in.default
    return user_project


def create_or_update_organization_role(
    *, db_session, user: DispatchUser, role_in: UserOrganization
):
    """Creates a new organization role or updates an existing role."""
    if not role_in.organization.id:
        organization = organization_service.get_by_name(
            db_session=db_session, name=role_in.organization.name
        )
        organization_id = organization.id
    else:
        organization_id = role_in.organization.id

    organization_role = (
        db_session.query(DispatchUserOrganization)
        .filter(
            DispatchUserOrganization.dispatch_user_id == user.id,
        )
        .filter(DispatchUserOrganization.organization_id == organization_id)
        .one_or_none()
    )

    if not organization_role:
        return DispatchUserOrganization(
            organization_id=organization.id,
            role=role_in.role,
        )

    organization_role.role = role_in.role
    return organization_role


def create(*, db_session, organization: str, user_in: UserRegister) -> DispatchUser:
    """Creates a new dispatch user."""
    # pydantic forces a string password, but we really want bytes
    password = bytes(user_in.password, "utf-8")

    # create the user
    user = DispatchUser(
        **user_in.dict(exclude={"password", "organizations", "projects"}), password=password
    )

    org = organization_service.get_by_slug_or_raise(
        db_session=db_session,
        organization_in=OrganizationRead(name=organization, slug=organization),
    )

    # add the user to the default organization
    user.organizations.append(DispatchUserOrganization(organization=org, role=UserRoles.member))

    # get the default project
    default_project = project_service.get_default_or_raise(db_session=db_session)

    # add the user to the default project
    user.projects.append(
        DispatchUserProject(project=default_project, default=True, role=UserRoles.member)
    )
    db_session.add(user)
    db_session.commit()
    return user


def get_or_create(*, db_session, organization: str, user_in: UserRegister) -> DispatchUser:
    """Gets an existing user or creates a new one."""
    user = get_by_email(db_session=db_session, email=user_in.email)

    if not user:
        try:
            user = create(db_session=db_session, organization=organization, user_in=user_in)
        except IntegrityError:
            db_session.rollback()
            log.exception(f"Unable to create user with email address {user_in.email}.")

    return user


def update(*, db_session, user: DispatchUser, user_in: UserUpdate) -> DispatchUser:
    """Updates a user."""
    user_data = user.dict()

    update_data = user_in.dict(
        exclude={"password", "organizations", "projects"}, skip_defaults=True
    )
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])

    if user_in.password:
        password = bytes(user_in.password, "utf-8")
        user.password = password

    if user_in.organizations:
        roles = []

        for role in user_in.organizations:
            roles.append(
                create_or_update_organization_role(db_session=db_session, user=user, role_in=role)
            )

    if user_in.projects:
        # we reset the default value for all user projects
        for user_project in user.projects:
            user_project.default = False

        projects = []
        for user_project in user_in.projects:
            projects.append(
                create_or_update_project_default(
                    db_session=db_session, user=user, user_project_in=user_project
                )
            )

    db_session.commit()
    return user


def get_current_user(request: Request) -> DispatchUser:
    """Attempts to get the current user depending on the configured authentication provider."""
    if DISPATCH_AUTHENTICATION_PROVIDER_SLUG:
        auth_plugin = plugins.get(DISPATCH_AUTHENTICATION_PROVIDER_SLUG)
        user_email = auth_plugin.get_current_user(request)
    else:
        log.debug("No authentication provider. Default user will be used")
        user_email = DISPATCH_AUTHENTICATION_DEFAULT_USER

    if not user_email:
        log.exception(
            f"Unable to determine user email based on configured auth provider or no default auth user email defined. Provider: {DISPATCH_AUTHENTICATION_PROVIDER_SLUG}"
        )
        raise InvalidCredentialException

    return get_or_create(
        db_session=request.state.db,
        organization=request.state.organization,
        user_in=UserRegister(email=user_email),
    )


def get_current_role(
    request: Request, current_user: DispatchUser = Depends(get_current_user)
) -> UserRoles:
    """Attempts to get the current user depending on the configured authentication provider."""
    return current_user.get_organization_role(organization_slug=request.state.organization)
