import logging
from abc import ABC, abstractmethod

from fastapi import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from dispatch.enums import UserRoles, Visibility
from dispatch.auth.service import get_current_user
from dispatch.incident import service as incident_service
from dispatch.organization import service as organization_service


log = logging.getLogger(__name__)


class BasePermission(ABC):
    """
    Abstract permission that all other Permissions must be inherited from.

    Defines basic error message, status & error codes.

    Upon initialization, calls abstract method  `has_required_permissions`
    which will be specific to concrete implementation of Permission class.

    You would write your permissions like this:

    .. code-block:: python

        class TeapotUserAgentPermission(BasePermission):

            def has_required_permissions(self, request: Request) -> bool:
                return request.headers.get('User-Agent') == "Teapot v1.0"

    """

    error_msg = "Forbidden."
    status_code = HTTP_403_FORBIDDEN

    @abstractmethod
    def has_required_permissions(self, request: Request) -> bool:
        ...

    def __init__(self, request: Request):
        if not self.has_required_permissions(request):
            raise HTTPException(status_code=self.status_code, detail=self.error_msg)


def any_permission(permissions: list, request: Request):
    for p in permissions:
        try:
            p(request=request)
            return True
        except HTTPException:
            pass
    return False


class PermissionsDependency(object):
    """
    Permission dependency that is used to define and check all the permission
    classes from one place inside route definition.

    Use it as an argument to FastAPI's `Depends` as follows:

    .. code-block:: python

        app = FastAPI()

        @app.get(
            "/teapot/",
            dependencies=[Depends(
                PermissionsDependency([TeapotUserAgentPermission]))]
        )
        async def teapot() -> dict:
            return {"teapot": True}
    """

    def __init__(self, permissions_classes: list):
        self.permissions_classes = permissions_classes

    def __call__(self, request: Request):
        for permission_class in self.permissions_classes:
            permission_class(request=request)


class OrganizationOwnerPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_organization = None
        if request.path_params.get("organization"):
            current_organization = organization_service.get_by_name(
                db_session=request.state.db, name=request.path_params["organization"]
            )
        elif request.path_params.get("organization_id"):
            current_organization = organization_service.get(
                db_session=request.state.db, organization_id=request.path_params["organization_id"]
            )

        if not current_organization:
            return

        current_user = get_current_user(db_session=request.state.db, request=request)

        for user_org in current_user.organizations:
            if user_org.organization.id == current_organization.id:
                if user_org.role == UserRoles.owner:
                    return True


class OrganizationManagerPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_organization = organization_service.get_by_name(
            db_session=request.state.db, name=request.path_params["organization"]
        )

        if not current_organization:
            return

        current_user = get_current_user(db_session=request.state.db, request=request)

        for user_org in current_user.organizations:
            if user_org.organization.id == current_organization.id:
                if user_org.role == UserRoles.manager:
                    return True


class SensitiveProjectActionPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        return any_permission(
            permissions=[
                OrganizationOwnerPermission,
                OrganizationManagerPermission,
                ProjectAdminPermission,
            ],
            request=request,
        )


# TODO try to deteremine how to get access the async request body
class ProjectAdminPermission(BasePermission):
    async def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        return False


#        current_project = None
#        request_json = await request.json()
#
#        if request_json.get("project", {}).get("name"):
#            current_project = project_service.get_by_name(
#                db_session=request.state.db, name=request_json["project"]["name"]
#            )
#
#        if not current_project:
#            return
#
#        current_user = get_current_user(db_session=request.state.db, request=request)
#
#        for p in current_user.projects:
#            if p.project_id == current_project.id:
#                if p.role == UserRoles.admin:
#                    return True


class ProjectCreatePermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        return any_permission(
            permissions=[OrganizationOwnerPermission, OrganizationManagerPermission],
            request=request,
        )


class ProjectUpdatePermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        return any_permission(
            permissions=[
                OrganizationOwnerPermission,
                OrganizationManagerPermission,
                ProjectAdminPermission,
            ],
            request=request,
        )


class IncidentJoinPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_incident = incident_service.get(
            db_session=request.state.db, incident_id=request.path_params["incident_id"]
        )

        if current_incident.visibility == Visibility.restricted:
            return ProjectAdminPermission(request=request)

        return True


class IncidentViewPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_incident = incident_service.get(
            db_session=request.state.db, incident_id=request.path_params["incident_id"]
        )

        if not current_incident:
            return False

        if current_incident.visibility == Visibility.restricted:
            return any_permission(
                permissions=[
                    ProjectAdminPermission,
                    IncidentCommanderPermission,
                    IncidentReporterPermission,
                ],
                request=request,
            )
        return True


class IncidentEditPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        return any_permission(
            permissions=[
                ProjectAdminPermission,
                IncidentCommanderPermission,
                IncidentReporterPermission,
            ],
            request=request,
        )


class IncidentReporterPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_user = get_current_user(db_session=request.state.db, request=request)
        current_incident = incident_service.get(
            db_session=request.state.db, incident_id=request.path_params["incident_id"]
        )

        if not current_incident:
            return False

        if current_incident.reporter.individual.email == current_user.email:
            return True


class IncidentCommanderPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_user = get_current_user(db_session=request.state.db, request=request)
        current_incident = incident_service.get(
            db_session=request.state.db, incident_id=request.path_params["incident_id"]
        )
        if not current_incident:
            return

        if current_incident.commander:
            if current_incident.commander.individual.email == current_user.email:
                return True
