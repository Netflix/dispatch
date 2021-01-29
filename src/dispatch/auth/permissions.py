import logging
from abc import ABC, abstractmethod

from fastapi import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from dispatch.enums import UserRoles, Visibility
from dispatch.auth.service import get_current_user
from dispatch.incident import service as incident_service


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


class AdminPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_user = get_current_user(db_session=request.state.db, request=request)
        if current_user.role == UserRoles.admin:
            return True


class IncidentJoinPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_incident = incident_service.get(
            db_session=request.state.db, incident_id=request.path_params.id
        )

        if current_incident.visibility == Visibility.restricted:
            return AdminPermission(request=request).has_required_permissions()

        return True


class IncidentViewPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_incident = incident_service.get(
            db_session=request.state.db, incident_id=request.path_params.id
        )
        if current_incident.visibility == Visibility.restricted:
            return any(
                AdminPermission(request=request).has_required_permissions(),
                IncidentCommanderPermission(request=request).has_required_permissions(),
                IncidentReporterPermission(request=request).has_required_permissions(),
            )
        return True


class IncidentEditPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        return any(
            AdminPermission(request=request).has_required_permissions(),
            IncidentCommanderPermission(request=request).has_required_permissions(),
            IncidentReporterPermission(request=request).has_required_permissions(),
        )


class IncidentReporterPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_user = get_current_user(db_session=request.state.db, request=request)
        current_incident = incident_service.get(
            db_session=request.state.db, incident_id=request.path_params.id
        )

        if current_incident.reporter.individual.email == current_user.email:
            return True


class IncidentCommanderPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_user = get_current_user(db_session=request.state.db, request=request)
        current_incident = incident_service.get(
            db_session=request.state.db, incident_id=request.path_params.id
        )
        if current_incident.commander.individual.email == current_user.email:
            return True
