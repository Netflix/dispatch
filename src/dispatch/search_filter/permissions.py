from starlette.requests import Request

from dispatch.auth.service import get_current_user
from dispatch.auth.permissions import BasePermission, OrganizationAdminPermission, any_permission

from .service import get


class SearchFilterEditDeletePermission(BasePermission):
    def has_required_permissions(
        self,
        request: Request,
    ) -> bool:
        """
        Permissions class that checks if the user is the filter creator
        or has Dispatch admin or greater permissions.
        """
        search_filter = get(
            db_session=request.state.db, search_filter_id=request.path_params["search_filter_id"]
        )

        if not search_filter:
            return False

        current_user = get_current_user(request=request)

        if current_user.email == search_filter.creator.email:
            return True

        return any_permission(
            permissions=[
                OrganizationAdminPermission,
            ],
            request=request,
        )
