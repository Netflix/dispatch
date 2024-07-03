import logging
from abc import ABC, abstractmethod

from fastapi import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from dispatch.auth.service import get_current_user
from dispatch.case import service as case_service
from dispatch.case.models import Case
from dispatch.incident.models import Incident
from dispatch.enums import UserRoles, Visibility
from dispatch.incident import service as incident_service
from dispatch.individual import service as individual_contact_service
from dispatch.models import PrimaryKeyModel
from dispatch.organization import service as organization_service
from dispatch.organization.models import OrganizationRead
from dispatch.participant_role.enums import ParticipantRoleType

log = logging.getLogger(__name__)


def any_permission(permissions: list, request: Request) -> bool:
    for p in permissions:
        try:
            p(request=request)
            return True
        except HTTPException:
            pass
    return False


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

    org_error_msg = [{"msg": "Organization not found. Please, contact your Dispatch admin."}]
    org_error_code = HTTP_404_NOT_FOUND

    user_error_msg = [{"msg": "User not found. Please, contact your Dispatch admin"}]
    user_error_code = HTTP_404_NOT_FOUND

    user_role_error_msg = [
        {
            "msg": "Your user doesn't have permissions to create, update, or delete this resource. Please, contact your Dispatch admin."
        }
    ]
    user_role_error_code = HTTP_403_FORBIDDEN

    role = None

    @abstractmethod
    def has_required_permissions(self, request: Request) -> bool:
        ...

    def __init__(self, request: Request):
        organization = None
        if request.path_params.get("organization"):
            organization = organization_service.get_by_slug_or_raise(
                db_session=request.state.db,
                organization_in=OrganizationRead(
                    slug=request.path_params["organization"],
                    name=request.path_params["organization"],
                ),
            )
        elif request.path_params.get("organization_id"):
            organization = organization_service.get(
                db_session=request.state.db, organization_id=request.path_params["organization_id"]
            )

        if not organization:
            raise HTTPException(status_code=self.org_error_code, detail=self.org_error_msg)

        user = get_current_user(request=request)
        if not user:
            raise HTTPException(status_code=self.user_error_code, detail=self.user_error_msg)

        self.role = user.get_organization_role(organization.slug)
        if not self.has_required_permissions(request):
            raise HTTPException(
                status_code=self.user_role_error_code, detail=self.user_role_error_msg
            )


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
    def has_required_permissions(self, request: Request) -> bool:
        return self.role == UserRoles.owner


class OrganizationManagerPermission(BasePermission):
    def has_required_permissions(self, request: Request) -> bool:
        permission = any_permission(
            permissions=[
                OrganizationOwnerPermission,
            ],
            request=request,
        )
        if not permission:
            if self.role == UserRoles.manager:
                return True
        return permission


class OrganizationAdminPermission(BasePermission):
    def has_required_permissions(self, request: Request) -> bool:
        permission = any_permission(
            permissions=[
                OrganizationOwnerPermission,
                OrganizationManagerPermission,
            ],
            request=request,
        )
        if not permission:
            if self.role == UserRoles.admin:
                return True
        return permission


class OrganizationMemberPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        permission = any_permission(
            permissions=[
                OrganizationOwnerPermission,
                OrganizationManagerPermission,
                OrganizationAdminPermission,
            ],
            request=request,
        )
        if not permission:
            if self.role == UserRoles.member:
                return True
        return permission


class SensitiveProjectActionPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        return any_permission(
            permissions=[
                OrganizationOwnerPermission,
                OrganizationManagerPermission,
                OrganizationAdminPermission,
            ],
            request=request,
        )


class IndividualContactUpdatePermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        permission = any_permission(
            permissions=[
                SensitiveProjectActionPermission,
            ],
            request=request,
        )
        if not permission:
            pk = PrimaryKeyModel(id=request.path_params["individual_contact_id"])
            individual_contact = individual_contact_service.get(
                db_session=request.state.db, individual_contact_id=pk.id
            )

            if not individual_contact:
                return False

            current_user = get_current_user(request=request)
            if individual_contact.email == current_user.email:
                return True

        return permission


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
                OrganizationAdminPermission,
            ],
            request=request,
        )


class IncidentJoinOrSubscribePermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        pk = PrimaryKeyModel(id=request.path_params["incident_id"])
        current_incident = incident_service.get(db_session=request.state.db, incident_id=pk.id)

        if current_incident.visibility == Visibility.restricted:
            return OrganizationAdminPermission(request=request)

        return True


class IncidentViewPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        pk = PrimaryKeyModel(id=request.path_params["incident_id"])
        current_incident = incident_service.get(db_session=request.state.db, incident_id=pk.id)

        if not current_incident:
            return False

        if current_incident.visibility == Visibility.restricted:
            return any_permission(
                permissions=[
                    OrganizationAdminPermission,
                    IncidentCommanderPermission,
                    IncidentReporterPermission,
                    IncidentParticipantPermission,
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
                OrganizationAdminPermission,
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
        current_user = get_current_user(request=request)
        pk = PrimaryKeyModel(id=request.path_params["incident_id"])
        current_incident = incident_service.get(db_session=request.state.db, incident_id=pk.id)

        if not current_incident:
            return False

        if current_incident.reporter:
            if current_incident.reporter.individual.email == current_user.email:
                return True

        return False


class IncidentCommanderPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_user = get_current_user(request=request)
        pk = PrimaryKeyModel(id=request.path_params["incident_id"])
        current_incident = incident_service.get(db_session=request.state.db, incident_id=pk.id)
        if not current_incident:
            return False

        if current_incident.commander:
            if current_incident.commander.individual.email == current_user.email:
                return True

        return False


class IncidentCommanderOrScribePermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_user = get_current_user(request=request)
        pk = PrimaryKeyModel(id=request.path_params["incident_id"])
        current_incident = incident_service.get(db_session=request.state.db, incident_id=pk.id)
        if not current_incident:
            return False

        if (
            current_incident.commander
            and current_incident.commander.individual.email == current_user.email
        ):
            return True

        scribes = [
            participant.individual.email
            for participant in current_incident.participants
            if ParticipantRoleType.scribe in [role.role for role in participant.participant_roles]
        ]
        if current_user.email in scribes:
            return True

        return False


class IncidentParticipantPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_user = get_current_user(request=request)
        pk = PrimaryKeyModel(id=request.path_params["incident_id"])
        current_incident: Incident = incident_service.get(
            db_session=request.state.db, incident_id=pk.id
        )
        if not current_incident:
            return False

        participant_emails: list[str] = [
            participant.individual.email for participant in current_incident.participants
        ]
        return current_user.email in participant_emails


# Cases


class CaseViewPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        pk = PrimaryKeyModel(id=request.path_params["case_id"])

        current_case = case_service.get(db_session=request.state.db, case_id=pk.id)

        if not current_case:
            return False

        if current_case.visibility == Visibility.restricted:
            return any_permission(
                permissions=[
                    OrganizationAdminPermission,
                    CaseParticipantPermission,
                ],
                request=request,
            )
        return True


class CaseEditPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        return any_permission(
            permissions=[
                OrganizationAdminPermission,
                CaseParticipantPermission,
            ],
            request=request,
        )


class CaseParticipantPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        current_user = get_current_user(request=request)
        pk = PrimaryKeyModel(id=request.path_params["case_id"])
        current_case: Case = case_service.get(db_session=request.state.db, case_id=pk.id)
        participant_emails: list[str] = [
            participant.individual.email for participant in current_case.participants
        ]
        return current_user.email in participant_emails


class CaseJoinPermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        pk = PrimaryKeyModel(id=request.path_params["case_id"])
        current_case = case_service.get(db_session=request.state.db, case_id=pk.id)

        if current_case.visibility == Visibility.restricted:
            return OrganizationAdminPermission(request=request)

        return True


class FeedbackDeletePermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        permission = any_permission(
            permissions=[
                SensitiveProjectActionPermission,
            ],
            request=request,
        )
        if not permission:
            individual_contact_id = request.path_params.get("individual_contact_id", "0")
            # "0" is passed if the feedback is anonymous
            if individual_contact_id != "0":
                pk = PrimaryKeyModel(id=individual_contact_id)
                individual_contact = individual_contact_service.get(
                    db_session=request.state.db, individual_contact_id=pk.id
                )

                if not individual_contact:
                    return False

                current_user = get_current_user(request=request)
                if individual_contact.email == current_user.email:
                    return True

        return permission
